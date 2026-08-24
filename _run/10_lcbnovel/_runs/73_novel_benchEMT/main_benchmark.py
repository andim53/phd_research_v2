#!/usr/bin/env python3
"""
Benchmark: Novelty-LCB (auto global-minimum window) vs Regular LCB
on Ni8 / Au(4,4,2) fcc100 surface, EMT calculator.

EXTENDED GRID BENCHMARK (replaces the single-config 30-iter / lambda=1.5 / 5-seed run):

    SEED_LIST          = 10 independent seeds
    N_ITERATIONS_LIST  = [100, 200, 300, 400, 500]   (iterations per run)
    NOVELTY_WEIGHT_LIST= [2.0, 3.0, 4.0, 5.0]        (lambda in a(x) = sigma + lambda*Novelty)

Full grid, all 10 seeds, both acquisitors:
    Regular LCB : once per (iterations x seed)         = 5 x 10 =  50 runs
    Novelty-LCB : once per (iterations x weight x seed)= 5 x 4 x 10 = 200 runs
    TOTAL       = 250 AGOX runs  (a large compute job - run on the HPC node)

Modeled on _run/6_lcbnovel_benchmark/run.py, but the Novelty-LCB acquisitor uses the
NEW auto global-minimum energy window (no manual calibration / regular-LCB-first step):

    window (per atom) = (-inf, E_min/N + X]   with X = energy_above_min (eV/atom)

where E_min is the live lowest DFT(EMT) energy in the database (recomputed each
acquisition round) and N is the atom count. No lower bound, so a new global minimum
can still be found.

The two acquisitors run on the SAME seeds and identical system/generator/sampler/
relaxer/evaluator stack; only the acquisitor differs.

Novelty-LCB acquisition (to MAXIMIZE):
    a(x) = sigma(x) + lambda * Novelty(x)
    Novelty(x) = min_{i in DB} ||fingerprint(x) - fingerprint(x_i)||_2
    window: E/N <= E_min/N + energy_above_min

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python main_benchmark.py
"""

import matplotlib

matplotlib.use("Agg")

import json
import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

# ── Ensure local novelty_lcb imports (this project's package, has energy_above_min/per_atom) ──
_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ── ASE ──────────────────────────────────────────────────────────────────────
from ase.build import fcc100
from ase.calculators.emt import EMT

# ── AGOX ─────────────────────────────────────────────────────────────────────
from agox import AGOX
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.collectors import ParallelCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RandomGenerator, RattleGenerator
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import KMeansSampler

# ── Local novelty_lcb (this project; auto global-min window) ────────────────
from novelty_lcb import NoveltyLCBAcquisitor


# =============================================================================
# BENCHMARK CONFIGURATION  (EXTENDED GRID)
# =============================================================================

# --- System ---
SEED_LIST = [41, 101, 201, 301, 401, 501, 601, 701, 801, 901]  # 10 independent seeds
N_ITERATIONS_LIST = [100, 200, 300, 400, 500]                    # iterations per run
NOVELTY_WEIGHT_LIST = [2.0, 3.0, 4.0, 5.0]                       # lambda in a(x) = sigma + lambda*Novelty
SYMBOLS = "Ni8"
TEMPLATE_SIZE = (4, 4, 2)
VACUUM = 5.0
CONFINEMENT_Z = 4.0
SAMPLE_SIZE = 10

# --- Standard LCB ---
KAPPA = 2.0

# --- Novelty-LCB (auto global-minimum window, per-atom) ---
# window (per atom) = (-inf, E_min/N + X], X = NOVELTY_ENERGY_ABOVE_MIN (eV/atom)
# Ni8/Au(4,4,2): 8 Ni + 32 Au = 40 atoms -> cap = 0.1*40 = 4 eV above global min.
NOVELTY_ENERGY_ABOVE_MIN = 0.1        # eV/atom -- per-atom window height above global min
NOVELTY_ENERGY_PER_ATOM = True        # interpret energy_above_min in eV/atom

# --- Shared search settings (run-6 defaults) ---
NUM_CANDIDATES = {0: [10, 0], 5: [3, 7]}
RELAX_STEPS = 5
START_RELAX = 8
OPT_FMAX = 0.05
OPT_STEPS = 1

# --- Model ---
# use_ray=False runs GPR hyperparameter optimization single-process (no Ray actors).
# Required on low-RAM nodes (the default use_ray=True spawns one actor per CPU and
# OOMs -> ActorUnavailableError). No effect on the sampling math.
USE_RAY = True

# --- Analysis ---
DUP_THRESHOLD = 1.5   # fingerprint-distance threshold for "distinct configuration"

# --- Output ---
OUTDIR = os.path.join(_HERE, "benchmark_results")
os.makedirs(OUTDIR, exist_ok=True)


# =============================================================================
# Helpers (same shape as run 6)
# =============================================================================

def build_system():
    """Shared AGOX stack components (everything except database + acquisitor)."""
    template = fcc100("Au", size=TEMPLATE_SIZE, vacuum=VACUUM)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = CONFINEMENT_Z
    z0 = template.positions[:, 2].max()
    confinement_corner = np.array([0, 0, z0])

    environment = Environment(
        template=template, symbols=SYMBOLS, confinement_cell=confinement_cell,
        confinement_corner=confinement_corner, box_constraint_pbc=[True, True, False],
    )

    calc = EMT()
    descriptor = Fingerprint(environment=environment)

    beta = 0.01
    kernel = C(5000, (1, 1e5)) * (
        C(beta, (beta, beta)) * RBF() + C(1 - beta, (1 - beta, 1 - beta)) * RBF()
    ) + Noise(0.01, (0.01, 0.01))

    rattle_generator = RattleGenerator(**environment.get_confinement())
    random_generator = RandomGenerator(**environment.get_confinement(), contiguous=False)
    generators = [random_generator, rattle_generator]

    return dict(environment=environment, descriptor=descriptor, kernel=kernel,
                generators=generators, calc=calc)


def build_stack(acq_type, db_path, seed, kappa=KAPPA, novelty_weight=None):
    """Complete AGOX stack for one acquisitor type + seed.

    Parameters
    ----------
    acq_type : "regular_lcb" | "novelty_lcb"
    db_path : str -- output database file
    seed : int
    kappa : float -- LCB / relaxation-surface parameter
    novelty_weight : float | None -- lambda for Novelty-LCB; unused for regular
    """
    sys_ij = build_system()

    database = Database(filename=db_path, order=5)
    model = GPR(descriptor=sys_ij["descriptor"], kernel=sys_ij["kernel"],
                database=database, prior=Repulsive(), use_ray=USE_RAY)
    sampler = KMeansSampler(descriptor=sys_ij["descriptor"], database=database,
                            sample_size=SAMPLE_SIZE)
    collector = ParallelCollector(generators=sys_ij["generators"], sampler=sampler,
                                  environment=sys_ij["environment"],
                                  num_candidates=NUM_CANDIDATES, order=1)

    relaxer_kwargs = dict(constraints=sys_ij["environment"].get_constraints(),
                          optimizer_run_kwargs={"steps": RELAX_STEPS},
                          start_relax=START_RELAX, order=2)
    evaluator_kwargs = dict(calculator=sys_ij["calc"],
                            gets={"get_key": "prioritized_candidates"},
                            optimizer_kwargs={"logfile": None},
                            optimizer_run_kwargs={"fmax": OPT_FMAX, "steps": OPT_STEPS},
                            constraints=sys_ij["environment"].get_constraints(),
                            store_trajectory=True, order=4)

    if acq_type == "regular_lcb":
        acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=kappa, order=3)
    elif acq_type == "novelty_lcb":
        acquisitor = NoveltyLCBAcquisitor(
            model=model, descriptor=sys_ij["descriptor"], database=database,
            energy_above_min=NOVELTY_ENERGY_ABOVE_MIN,
            per_atom=NOVELTY_ENERGY_PER_ATOM,
            novelty_weight=novelty_weight,
            kappa=kappa, order=3,
        )
    else:
        raise ValueError(f"Unknown acq_type: {acq_type!r}")

    relaxer = ParallelRelaxPostprocess(model=acquisitor.get_acquisition_calculator(),
                                       **relaxer_kwargs)
    evaluator = LocalOptimizationEvaluator(**evaluator_kwargs)

    agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
    return agox, database, sys_ij["environment"]


def get_distinct_configurations(db, descriptor, threshold=DUP_THRESHOLD):
    """Greedy cluster of DB candidates into distinct configurations (lowest-E first)."""
    structures = db.get_all_candidates()
    if not structures:
        return []
    features, energies, valid = [], [], []
    for s in structures:
        try:
            e = s.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = descriptor.get_features(s).ravel()
            features.append(f); energies.append(e); valid.append(s)
        except Exception:
            continue
    if not features:
        return []
    features = np.array(features); energies = np.array(energies)
    selected, remaining = [], list(np.argsort(energies))
    while remaining:
        idx = remaining.pop(0)
        selected.append(idx)
        remaining = [j for j in remaining
                     if np.linalg.norm(features[j] - features[idx]) > threshold]
    return [(valid[i], energies[i]) for i in selected]


def run_single(seed, label, acq_type, n_iterations=N_ITERATIONS_LIST[0],
               novelty_weight=None):
    """Run one AGOX search for one acquisitor type + seed + (iterations, weight).

    Parameters
    ----------
    seed : int
    label : str -- base label (should include iteration; weight appended for novelty)
    acq_type : "regular_lcb" | "novelty_lcb"
    n_iterations : int -- AGOX iterations for this run
    novelty_weight : float | None -- lambda for Novelty-LCB
    """
    np.random.seed(seed)
    acq_label = "novelty" if acq_type == "novelty_lcb" else "regular"
    full_label = f"{label}_{acq_label}"
    db_path = os.path.join(OUTDIR, f"{full_label}_db.db")

    print(f"    Building AGOX stack ({acq_label} LCB, seed={seed}, "
          f"n_iter={n_iterations}, lambda={novelty_weight})...")
    t0 = time.time()
    agox, database, environment = build_stack(acq_type, db_path, seed,
                                              kappa=KAPPA,
                                              novelty_weight=novelty_weight)
    t_build = time.time() - t0

    print(f"    Running {n_iterations} iterations...")
    t1 = time.time()
    agox.run(N_iterations=n_iterations, verbose=False, hide_log=True)
    t_run = time.time() - t1

    print(f"    Analysing results...")
    t2 = time.time()
    db_read = Database(filename=db_path, initialize=False)
    db_read.restore_to_memory()
    all_c = db_read.get_all_candidates()

    env = build_system()["environment"]
    desc = Fingerprint(environment=env)
    distinct = get_distinct_configurations(db_read, desc, DUP_THRESHOLD)
    distinct_energies = [e for _, e in distinct]
    n_distinct = len(distinct)
    n_evals = len(all_c)
    n_duplicates = n_evals - n_distinct

    if distinct_energies:
        best_E = min(distinct_energies)
        e_range = max(distinct_energies) - min(distinct_energies)
    else:
        best_E = e_range = np.nan

    all_energies = []
    for c in all_c:
        try:
            e = c.get_potential_energy()
            if np.isfinite(e):
                all_energies.append(e)
        except Exception:
            pass
    t_analysis = time.time() - t2

    print(f"    Done. distinct={n_distinct}, evals={n_evals}, best_E={best_E:.3f} eV, "
          f"time: build={t_build:.1f}s run={t_run:.1f}s analysis={t_analysis:.1f}s")
    return dict(seed=seed, label=full_label, acq=acq_type, db_file=db_path,
                n_iterations=n_iterations, novelty_weight=novelty_weight, kappa=KAPPA,
                n_evals=n_evals, n_distinct=n_distinct, n_duplicates=n_duplicates,
                best_E=best_E, e_range=e_range,
                distinct_energies=[float(e) for e in distinct_energies],
                all_energies=[float(e) for e in all_energies],
                build_time=t_build, run_time=t_run, analysis_time=t_analysis,
                total_time=t_build + t_run + t_analysis)


def compute_discovery_curve(results, desc, threshold):
    all_curves = []
    for r in results:
        if not os.path.exists(r["db_file"]):
            continue
        db = Database(filename=r["db_file"], initialize=False)
        all_c = db.get_all_candidates()
        cum_distinct, cum_total, seen_features = [], [], []
        for i, c in enumerate(all_c):
            try:
                e = c.get_potential_energy()
                if not np.isfinite(e):
                    cum_distinct.append(cum_distinct[-1] if cum_distinct else 0)
                    cum_total.append(i + 1)
                    continue
                f = desc.get_features(c).ravel()
                is_new = True
                for sf in seen_features:
                    if np.linalg.norm(f - sf) <= threshold:
                        is_new = False
                        break
                if is_new:
                    seen_features.append(f)
                cum_distinct.append(len(seen_features))
                cum_total.append(i + 1)
            except Exception:
                cum_distinct.append(cum_distinct[-1] if cum_distinct else 0)
                cum_total.append(i + 1)
        if cum_distinct:
            all_curves.append((cum_total, cum_distinct))
    if not all_curves:
        return np.array([]), np.array([])
    max_len = max(len(x) for x, _ in all_curves)
    xs = np.arange(1, max_len + 1)
    ys = np.zeros_like(xs, dtype=float)
    counts = np.zeros_like(xs, dtype=float)
    for x, y in all_curves:
        for xi, yi in zip(x, y):
            if xi <= max_len:
                ys[xi - 1] += yi
                counts[xi - 1] += 1
    valid = counts > 0
    ys[valid] /= counts[valid]
    return xs, ys


# =============================================================================
# Main
# =============================================================================

def main():
    n_runs = len(SEED_LIST)
    n_iter = len(N_ITERATIONS_LIST)
    n_w = len(NOVELTY_WEIGHT_LIST)
    n_regular = n_iter * n_runs
    n_novelty = n_iter * n_w * n_runs
    n_total = n_regular + n_novelty

    print("=" * 72)
    print("EXTENDED BENCHMARK: Novelty-LCB (auto global-min) vs Regular LCB")
    print("System: Ni8 on Au(4,4,2) fcc100 surface  (EMT calculator)")
    print("=" * 72)
    print(f"  Independent seeds:        {n_runs}  {SEED_LIST}")
    print(f"  Iterations per run:       {N_ITERATIONS_LIST}")
    print(f"  Novelty weight (lambda):  {NOVELTY_WEIGHT_LIST}")
    print(f"  Regular LCB runs:         {n_regular}   (iterations x seeds)")
    print(f"  Novelty-LCB runs:         {n_novelty}   (iterations x weights x seeds)")
    print(f"  TOTAL AGOX runs:          {n_total}")
    print()
    print(f"  Standard LCB:              kappa = {KAPPA}")
    print(f"  Novelty-LCB:")
    print(f"    energy_above_min = {NOVELTY_ENERGY_ABOVE_MIN} eV/atom "
          f"(per_atom={NOVELTY_ENERGY_PER_ATOM})")
    print(f"    -> window cap = E_min/N + {NOVELTY_ENERGY_ABOVE_MIN} "
          f"per atom (40 atoms -> +{NOVELTY_ENERGY_ABOVE_MIN * 40:.1f} eV)")
    print(f"  Distinctness threshold:    {DUP_THRESHOLD}")
    print(f"  Output directory:          {OUTDIR}")
    print("=" * 72)
    print()

    results = []  # flat list; each entry carries seed/iter/weight/acq + metrics

    for niter in N_ITERATIONS_LIST:
        for i, seed in enumerate(SEED_LIST):
            base_label = f"i{niter}_run{i + 1:02d}"

            # Regular LCB: once per (iterations x seed), independent of weight
            print(f"\n{'=' * 72}")
            print(f"REGULAR LCB  n_iter={niter}  seed={seed}  "
                  f"({i + 1}/{n_runs} of iteration block {niter})")
            print(f"{'=' * 72}")
            r = run_single(seed, base_label, "regular_lcb", n_iterations=niter)
            results.append(r)

            # Novelty-LCB: once per (iterations x weight x seed)
            for w in NOVELTY_WEIGHT_LIST:
                wlabel = f"{base_label}_l{w}"
                print(f"\n--- Novelty-LCB (lambda={w}, n_iter={niter}, seed={seed}) ---")
                n = run_single(seed, wlabel, "novelty_lcb", n_iterations=niter,
                               novelty_weight=w)
                results.append(n)

    # ---- Save JSON (flat results list) ----
    out_data = {
        "parameters": {
            "SYSTEM": f"{SYMBOLS} on Au{TEMPLATE_SIZE} fcc100",
            "TEMPLATE_SIZE": TEMPLATE_SIZE, "SYMBOLS": SYMBOLS,
            "VACUUM": VACUUM, "CONFINEMENT_Z": CONFINEMENT_Z,
            "CALCULATOR": "EMT",
            "SEED_LIST": SEED_LIST, "N_ITERATIONS_LIST": N_ITERATIONS_LIST,
            "NOVELTY_WEIGHT_LIST": NOVELTY_WEIGHT_LIST,
            "N_RUNS_REGULAR": n_regular, "N_RUNS_NOVELTY": n_novelty,
            "N_RUNS_TOTAL": n_total, "SAMPLE_SIZE": SAMPLE_SIZE,
            "NUM_CANDIDATES": NUM_CANDIDATES, "KAPPA": KAPPA,
            "NOVELTY_ENERGY_ABOVE_MIN": NOVELTY_ENERGY_ABOVE_MIN,
            "NOVELTY_ENERGY_PER_ATOM": NOVELTY_ENERGY_PER_ATOM,
            "DUP_THRESHOLD": DUP_THRESHOLD,
            "RELAX_STEPS": RELAX_STEPS, "START_RELAX": START_RELAX,
            "OPT_FMAX": OPT_FMAX, "OPT_STEPS": OPT_STEPS, "USE_RAY": USE_RAY,
            "NOTE": ("Extended grid benchmark: Novelty-LCB uses auto global-minimum "
                     "window (E_min/N + X per atom). Full grid of 10 seeds x "
                     "iterations {100..500} x weights {2..5} = 250 AGOX runs. "
                     "Run on a node with enough RAM for the AGOX Ray parallel pool "
                     "(the ParallelCollector/ParallelRelaxPostprocess need it)."),
        },
        "results": results,
    }
    json_path = os.path.join(OUTDIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # ---- Aggregate: per (iterations, weight) mean over seeds ----
    # Build lookup arrays
    reg = {niter: [] for niter in N_ITERATIONS_LIST}        # -> list of per-seed dicts
    nov = {(niter, w): [] for niter in N_ITERATIONS_LIST for w in NOVELTY_WEIGHT_LIST}
    for r in results:
        if r["acq"] == "regular_lcb":
            reg[r["n_iterations"]].append(r)
        else:
            nov[(r["n_iterations"], r["novelty_weight"])].append(r)

    print(f"\n{'=' * 72}")
    print("AGGREGATE (mean over seeds, by iteration and weight)")
    print(f"{'=' * 72}")
    for niter in N_ITERATIONS_LIST:
        rnd = [r["n_distinct"] for r in reg[niter]]
        rbe = [r["best_E"] for r in reg[niter]]
        print(f"\n  n_iter={niter}: Regular LCB  distinct={np.mean(rnd):.2f}, "
              f"best_E={np.mean(rbe):.3f} eV")
        for w in NOVELTY_WEIGHT_LIST:
            rs = nov[(niter, w)]
            nd = [r["n_distinct"] for r in rs]
            be = [r["best_E"] for r in rs]
            dup = [r["n_duplicates"] for r in rs]
            print(f"    lambda={w}: distinct={np.mean(nd):.2f}, "
                  f"best_E={np.mean(be):.3f} eV, dup={np.mean(dup):.0f}")

    # ---- Plots ----
    print("\nGenerating plots...")
    env = build_system()["environment"]
    desc = Fingerprint(environment=env)

    # --- Plot 1: grid of panels by iterations, metric vs novelty_weight ---
    # 5 rows (iterations) x 3 cols (Best energy / Distinct / Duplicates)
    metrics = [
        ("best_E", "Best energy [eV]", True),        # lower better
        ("n_distinct", "Distinct configs", False),   # higher better
        ("n_duplicates", "Duplicate evals", True),   # lower better
    ]
    fig, axes = plt.subplots(n_iter, 3, figsize=(18, 5 * n_iter), sharex=True)
    for row, niter in enumerate(N_ITERATIONS_LIST):
        # Regular reference: mean over seeds at this iteration (weight-independent)
        reg_mean = {
            "best_E": np.mean([r["best_E"] for r in reg[niter]]),
            "n_distinct": np.mean([r["n_distinct"] for r in reg[niter]]),
            "n_duplicates": np.mean([r["n_duplicates"] for r in reg[niter]]),
        }
        for col, (key, ylab, lower_better) in enumerate(metrics):
            ax = axes[row, col]
            nov_means, nov_stds = [], []
            for w in NOVELTY_WEIGHT_LIST:
                vals = [r[key] for r in nov[(niter, w)]]
                nov_means.append(np.mean(vals))
                nov_stds.append(np.std(vals))
            ax.errorbar(NOVELTY_WEIGHT_LIST, nov_means, yerr=nov_stds,
                        marker="o", color="coral", label="Novelty-LCB", capsize=3)
            ax.axhline(reg_mean[key], color="steelblue", linestyle="--",
                       label="Regular LCB (ref)")
            ax.set_title(f"n_iter={niter}  ({ylab})")
            ax.set_xlabel("novelty_weight (lambda)")
            if col == 0:
                ax.set_ylabel(ylab)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=7)
    plt.tight_layout()
    grid_path = os.path.join(OUTDIR, "benchmark_grid.png")
    plt.savefig(grid_path, dpi=150, bbox_inches="tight")
    print(f"Grid plot: {grid_path}")
    plt.close()

    # --- Plot 2: discovery curves per iteration (avg distinct vs cumulative evals) ---
    fig2, axes2 = plt.subplots(1, n_iter, figsize=(5 * n_iter, 5), sharey=True)
    for row, niter in enumerate(N_ITERATIONS_LIST):
        ax = axes2[row]
        # Regular (one curve per seed -> average)
        xv, yv = compute_discovery_curve(reg[niter], desc, DUP_THRESHOLD)
        if len(xv):
            ax.plot(xv, yv, "-", color="steelblue", linewidth=2.0,
                    label="Regular LCB")
        # Novelty per weight (average over seeds)
        for w in NOVELTY_WEIGHT_LIST:
            xv, yv = compute_discovery_curve(nov[(niter, w)], desc, DUP_THRESHOLD)
            if len(xv):
                ax.plot(xv, yv, "-", linewidth=1.5, label=f"lambda={w}")
        ax.set_title(f"n_iter={niter}")
        ax.set_xlabel("Cumulative evaluations")
        if row == 0:
            ax.set_ylabel("Cumulative distinct configs")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    plt.tight_layout()
    disc_path = os.path.join(OUTDIR, "benchmark_discovery.png")
    plt.savefig(disc_path, dpi=150, bbox_inches="tight")
    print(f"Discovery plot: {disc_path}")
    plt.close()

    print(f"\n{'=' * 72}")
    print("EXTENDED BENCHMARK COMPLETE")
    print(f"  JSON:      {json_path}")
    print(f"  Grid plot: {grid_path}")
    print(f"  Discovery: {disc_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
