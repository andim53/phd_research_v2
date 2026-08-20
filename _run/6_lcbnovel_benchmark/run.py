#!/usr/bin/env python3
"""
Benchmark: Novelty-LCB vs Regular LCB on Ni8 / Au(4,4,2) fcc100 surface.

Compares how many DISTINCT surface configurations each acquisitor finds
when optimizing Ni8 on Au(4,4,2) using the EMT calculator.

Both runs use identical system setup, generators, sampler, evaluators, and
seeds.  The only difference is the acquisitor.

Novelty-LCB acquisition (to MAXIMIZE):
    a(x) = sigma(x) + lambda * Novelty(x)
    Novelty(x) = min_{i in DB} ||fingerprint(x) - fingerprint(x_i)||_2
    subject to:  E_target - delta_E <= mu(x) <= E_target + delta_E

Metrics
-------
- Number of distinct surface configurations found (fingerprint-distance clustering)
- Best adsorption energy found
- Energy range of found minima
- Number of evaluations spent on duplicate (near-identical) structures
- Statistical comparison (paired differences across independent runs)
- Discovery curves: distinct configurations vs cumulative evaluations

IMPORTANT — energy window calibration
--------------------------------------
The novelty_lcb parameters (target_energy, delta_E) MUST be calibrated for
this system BEFORE running the full benchmark.  Run a short standard-LCB
search first to see the energy range, then set:

    target_energy = centre of the desired band  [eV]
    delta_E       = half-width of the band       [eV]

The values below (target_energy=0.0, delta_E=2.0) are a BROAD initial guess
and will likely need adjustment.  See BENCHMARK_CONFIG below.

Run:
    /home/miniconda3/envs/agox_v2/bin/python run.py
"""

import matplotlib

matplotlib.use("Agg")

import json
import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

# ── Ensure local novelty_lcb imports ─────────────────────────────────────────
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

# ── Local novelty_lcb ────────────────────────────────────────────────────────
from novelty_lcb import NoveltyLCBAcquisitor


# =============================================================================
# BENCHMARK CONFIGURATION  (edit per system / calibration)
# =============================================================================

# --- System ---
SEED_LIST = [41, 101, 201, 301, 401]       # independent seeds for statistics
N_ITERATIONS = 30                              # iterations per run (×2 × N_RUNS)
SYMBOLS = "Ni8"
TEMPLATE_SIZE = (4, 4, 2)
VACUUM = 5.0
CONFINEMENT_Z = 4.0
SAMPLE_SIZE = 10

# --- Standard LCB ---
KAPPA = 2.0

# --- Novelty-LCB  ⚠ CALIBRATE BEFORE RUNNING ---
# These are initial guesses.  Run a short standard-LCB search first to see
# the energy range explored by Ni8/Au(4,4,2) + EMT, then set:
#   target_energy = centre of the band (eV)
#   delta_E       = half-width (eV)
NOVELTY_TARGET_ENERGY = 0.0                   # eV — TODO: calibrate
NOVELTY_DELTA_E = 2.0                         # eV — half-width (broad start)
NOVELTY_WEIGHT = 1.0                          # lambda

# --- Shared search settings ---
NUM_CANDIDATES = {0: [10, 0], 5: [3, 7]}
RELAX_STEPS = 5
START_RELAX = 8
OPT_FMAX = 0.05
OPT_STEPS = 1

# --- Analysis ---
DUP_THRESHOLD = 1.5                            # fingerprint-distance threshold
                                        # for "distinct configuration" clustering.
                                        # Lower = stricter.
                                        # For a surface system, 1.0-2.0 is a
                                        # reasonable starting range.

# --- Output ---
OUTDIR = os.path.join(_HERE, "benchmark_results_surface")
os.makedirs(OUTDIR, exist_ok=True)


# =============================================================================
# Helpers
# =============================================================================

def build_system():
    """Build the shared parts of the AGOX stack (everything except
    the database and acquisitor — those are set per-run).

    Returns a named-tuple-like dict of the reusable components.
    """
    # Template surface
    template = fcc100("Au", size=TEMPLATE_SIZE, vacuum=VACUUM)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    # Confinement
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = CONFINEMENT_Z
    z0 = template.positions[:, 2].max()
    confinement_corner = np.array([0, 0, z0])

    environment = Environment(
        template=template,
        symbols=SYMBOLS,
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],
    )

    # Calculator
    calc = EMT()

    # Descriptor
    descriptor = Fingerprint(environment=environment)

    # GPR kernel (shared recipe)
    beta = 0.01
    k0 = C(beta, (beta, beta)) * RBF()
    k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
    kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))

    # Sampler
    sampler = KMeansSampler(descriptor=descriptor, database=None,
                            sample_size=SAMPLE_SIZE)

    # Generators (created without sampler — sampler added later in build_stack)
    rattle_generator = RattleGenerator(**environment.get_confinement())
    random_generator = RandomGenerator(**environment.get_confinement(),
                                       contiguous=False)
    generators = [random_generator, rattle_generator]

    # Return raw components; collector is built in build_stack() with the
    # database-wired sampler.
    return dict(
        environment=environment,
        descriptor=descriptor,
        kernel=kernel,
        sampler=sampler,           # will be re-wired with database in build_stack
        generators=generators,
        calc=calc,
    )


def build_stack(acq_type, db_path, seed):
    """Build a complete, ready-to-run AGOX instance for one acquisitor type."""
    sys_ij = build_system()

    # Database
    database = Database(filename=db_path, order=5)

    # Model (wires in database)
    model = GPR(descriptor=sys_ij["descriptor"], kernel=sys_ij["kernel"],
                database=database, prior=Repulsive())

    # Sampler (wires in database)
    sampler = KMeansSampler(descriptor=sys_ij["descriptor"],
                            database=database, sample_size=SAMPLE_SIZE)

    # Collector — built here with the database-wired sampler
    collector = ParallelCollector(
        generators=sys_ij["generators"],
        sampler=sampler,
        environment=sys_ij["environment"],
        num_candidates=NUM_CANDIDATES,
        order=1,
    )

    # Relaxer kwargs
    relaxer_kwargs = dict(
        constraints=sys_ij["environment"].get_constraints(),
        optimizer_run_kwargs={"steps": RELAX_STEPS},
        start_relax=START_RELAX,
        order=2,
    )

    # Evaluator kwargs
    evaluator_kwargs = dict(
        calc=sys_ij["calc"],
        gets={"get_key": "prioritized_candidates"},
        optimizer_kwargs={"logfile": None},
        optimizer_run_kwargs={"fmax": OPT_FMAX, "steps": OPT_STEPS},
        constraints=sys_ij["environment"].get_constraints(),
        store_trajectory=True,
        order=4,
    )
    if acq_type == "regular_lcb":
        acquisitor = LowerConfidenceBoundAcquisitor(
            model=model, kappa=KAPPA, order=3)
    elif acq_type == "novelty_lcb":
        acquisitor = NoveltyLCBAcquisitor(
            model=model,
            descriptor=sys_ij["descriptor"],
            database=database,
            target_energy=NOVELTY_TARGET_ENERGY,
            delta_E=NOVELTY_DELTA_E,
            novelty_weight=NOVELTY_WEIGHT,
            order=3,
        )
    else:
        raise ValueError(f"Unknown acq_type: {acq_type!r}")

    # Relaxer
    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        **relaxer_kwargs)

    # Evaluator
    evaluator = LocalOptimizationEvaluator(**evaluator_kwargs)

    # Orchestrate
    agox = AGOX(collector, relaxer, acquisitor, evaluator,
                database, seed=seed)

    return agox, database, sys_ij["environment"]


def get_distinct_configurations(db, descriptor, threshold=DUP_THRESHOLD):
    """Cluster DB candidates into distinct surface configurations.

    Greedy clustering: pick lowest-energy structure first, then iteratively
    pick the next structure whose fingerprint distance to ALL already-selected
    structures exceeds *threshold*.

    Returns list of (candidate, energy) for each distinct configuration.
    """
    structures = db.get_all_candidates()
    if not structures:
        return []

    features = []
    energies = []
    valid = []
    for s in structures:
        try:
            e = s.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = descriptor.get_features(s).ravel()
            features.append(f)
            energies.append(e)
            valid.append(s)
        except Exception:
            continue

    if not features:
        return []

    features = np.array(features)
    energies = np.array(energies)

    selected = []
    remaining = list(np.argsort(energies))  # lowest energy first

    while remaining:
        idx = remaining.pop(0)
        selected.append(idx)
        remaining = [
            j for j in remaining
            if np.linalg.norm(features[j] - features[idx]) > threshold
        ]

    return [(valid[i], energies[i]) for i in selected]


def run_single(seed, label, acq_type):
    """Run one AGOX optimization and return results dict."""
    np.random.seed(seed)

    acq_label = "novelty" if acq_type == "novelty_lcb" else "regular"
    full_label = f"{label}_{acq_label}"
    db_path = os.path.join(OUTDIR, f"{full_label}_db.db")

    print(f"    Building AGOX stack ({acq_label} LCB, seed={seed})...")
    t0 = time.time()
    agox, database, environment = build_stack(acq_type, db_path, seed)
    t_build = time.time() - t0

    print(f"    Running {N_ITERATIONS} iterations...")
    t1 = time.time()
    agox.run(N_iterations=N_ITERATIONS, verbose=False, hide_log=True)
    t_run = time.time() - t1

    # Analyse
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

    # Also get all energies for discovery curve
    all_energies = []
    for c in all_c:
        try:
            e = c.get_potential_energy()
            if np.isfinite(e):
                all_energies.append(e)
        except Exception:
            pass

    t_analysis = time.time() - t2

    print(f"    Done. distinct={n_distinct}, evals={n_evals}, "
          f"best_E={best_E:.3f} eV, "
          f"time: build={t_build:.1f}s run={t_run:.1f}s analysis={t_analysis:.1f}s")

    return dict(
        seed=seed,
        label=full_label,
        acq=acq_type,
        db_file=db_path,
        n_evals=n_evals,
        n_distinct=n_distinct,
        n_duplicates=n_duplicates,
        best_E=best_E,
        e_range=e_range,
        distinct_energies=[float(e) for e in distinct_energies],
        all_energies=[float(e) for e in all_energies],
        build_time=t_build,
        run_time=t_run,
        analysis_time=t_analysis,
        total_time=t_build + t_run + t_analysis,
    )


# =============================================================================
# Discovery curve helper
# =============================================================================

def compute_discovery_curve(results, desc, threshold):
    """Return (cum_total, cum_distinct) — average over runs.

    Simulates incremental storage: walk DB candidates in order, track how
    many are new (fingerprint distance > threshold).
    """
    all_curves = []
    for r in results:
        if not os.path.exists(r["db_file"]):
            continue
        db = Database(filename=r["db_file"], initialize=False)
        all_c = db.get_all_candidates()
        cum_distinct = []
        cum_total = []
        seen_features = []
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
    print("=" * 72)
    print("BENCHMARK: Novelty-LCB vs Regular LCB")
    print("System: Ni8 on Au(4,4,2) fcc100 surface  (EMT calculator)")
    print("=" * 72)
    print(f"  Independent runs (seeds):  {n_runs}  {SEED_LIST}")
    print(f"  Iterations per run:        {N_ITERATIONS}")
    print(f"  Total AGOX runs:           {n_runs * 2}")
    print()
    print(f"  Standard LCB:              kappa = {KAPPA}")
    print(f"  Novelty-LCB:")
    print(f"    target_energy = {NOVELTY_TARGET_ENERGY:.3f} eV")
    print(f"    delta_E       = {NOVELTY_DELTA_E:.3f} eV")
    print(f"    window        = [{NOVELTY_TARGET_ENERGY - NOVELTY_DELTA_E:.3f}, "
          f"{NOVELTY_TARGET_ENERGY + NOVELTY_DELTA_E:.3f}] eV")
    print(f"    novelty_weight= {NOVELTY_WEIGHT}")
    print()
    print(f"  Distinctness threshold:    {DUP_THRESHOLD} "
          f"(fingerprint Euclidean distance)")
    print(f"  Output directory:          {OUTDIR}")
    print("=" * 72)
    print()
    print("⚠  If target_energy=0.0 and delta_E=2.0 are not yet calibrated,")
    print("   the novelty_lcb runs may exclude most/all candidates.")
    print("   Run a short standard-LCB search first to calibrate.")
    print()

    results = {"regular_lcb": [], "novelty_lcb": []}

    for i, seed in enumerate(SEED_LIST):
        print(f"\n{'=' * 72}")
        print(f"RUN {i+1}/{n_runs}  seed={seed}")
        print(f"{'=' * 72}")

        label = f"surface_run{i+1:02d}"

        # --- Regular LCB ---
        print(f"\n--- Regular LCB (kappa={KAPPA}) ---")
        r = run_single(seed, label, "regular_lcb")
        results["regular_lcb"].append(r)

        # --- Novelty LCB ---
        print(f"\n--- Novelty-LCB "
              f"(λ={NOVELTY_WEIGHT}, "
              f"window=[{NOVELTY_TARGET_ENERGY - NOVELTY_DELTA_E:.3f}, "
              f"{NOVELTY_TARGET_ENERGY + NOVELTY_DELTA_E:.3f}] eV) ---")
        n = run_single(seed, label, "novelty_lcb")
        results["novelty_lcb"].append(n)

    # =========================================================================
    # Aggregate
    # =========================================================================
    print(f"\n{'=' * 72}")
    print("AGGREGATE RESULTS")
    print(f"{'=' * 72}")

    for acq_type in ["regular_lcb", "novelty_lcb"]:
        runs = results[acq_type]
        nd = [r["n_distinct"] for r in runs]
        ne = [r["n_evals"] for r in runs]
        ndu = [r["n_duplicates"] for r in runs]
        be = [r["best_E"] for r in runs]
        er = [r["e_range"] for r in runs]
        tt = [r["total_time"] for r in runs]

        print(f"\n{acq_type.replace('_', ' ').title()}:")
        print(f"  Distinct configurations:  mean={np.mean(nd):.1f}, "
              f"std={np.std(nd):.1f}, "
              f"min={min(nd)}, max={max(nd)}")
        print(f"  Total evaluations:        mean={np.mean(ne):.1f}, "
              f"std={np.std(ne):.1f}")
        print(f"  Duplicate evaluations:    mean={np.mean(ndu):.1f}, "
              f"std={np.std(ndu):.1f} "
              f"({np.mean(ndu) / np.mean(ne) * 100:.0f}% of evals)")
        print(f"  Best energy:              mean={np.mean(be):.3f} ± "
              f"{np.std(be):.3f} eV")
        print(f"  Energy range:             mean={np.mean(er):.3f} ± "
              f"{np.std(er):.3f} eV")
        print(f"  Wall-clock time:          mean={np.mean(tt):.1f} ± "
              f"{np.std(tt):.1f} s")
        for r in runs:
            print(f"    seed={r['seed']:5d}: distinct={r['n_distinct']:2d}, "
                  f"evals={r['n_evals']:2d}, dup={r['n_duplicates']:2d}, "
                  f"best_E={r['best_E']:.3f}, time={r['total_time']:.1f}s")

    # =========================================================================
    # Statistical comparison
    # =========================================================================
    print(f"\n{'=' * 72}")
    print("STATISTICAL COMPARISON (Novelty − Regular)")
    print(f"{'=' * 72}")

    rd = [r["n_distinct"] for r in results["regular_lcb"]]
    nd = [r["n_distinct"] for r in results["novelty_lcb"]]
    r_dup = [r["n_duplicates"] for r in results["regular_lcb"]]
    n_dup = [r["n_duplicates"] for r in results["novelty_lcb"]]
    r_best = [r["best_E"] for r in results["regular_lcb"]]
    n_best = [r["best_E"] for r in results["novelty_lcb"]]

    diff_distinct = np.array(nd) - np.array(rd)
    diff_dup = np.array(n_dup) - np.array(r_dup)
    diff_best = np.array(n_best) - np.array(r_best)

    print(f"\nDistinct configurations (novelty − regular):")
    print(f"  Per-run: {diff_distinct}")
    print(f"  Mean:    {np.mean(diff_distinct):+.1f} ± {np.std(diff_distinct):.1f}")
    print(f"  Novelty finds more:  {np.sum(diff_distinct > 0)}/{n_runs} runs")
    print(f"  Tie:                 {np.sum(diff_distinct == 0)}/{n_runs} runs")
    print(f"  Regular finds more:  {np.sum(diff_distinct < 0)}/{n_runs} runs")

    print(f"\nDuplicate evaluations (novelty − regular):")
    print(f"  Per-run: {diff_dup}")
    print(f"  Mean:    {np.mean(diff_dup):+.1f} ± {np.std(diff_dup):.1f}")
    print(f"  Novelty has fewer:   {np.sum(diff_dup < 0)}/{n_runs} runs")
    print(f"  Tie:                 {np.sum(diff_dup == 0)}/{n_runs} runs")
    print(f"  Regular has fewer:   {np.sum(diff_dup > 0)}/{n_runs} runs")

    print(f"\nBest energy (novelty − regular), eV:")
    print(f"  Per-run: {diff_best}")
    print(f"  Mean:    {np.mean(diff_best):+.3f} ± {np.std(diff_best):.3f}")
    print(f"  Novelty finds lower: {np.sum(diff_best < 0)}/{n_runs} runs")
    print(f"  Tie:                 {np.sum(diff_best == 0)}/{n_runs} runs")
    print(f"  Regular finds lower: {np.sum(diff_best > 0)}/{n_runs} runs")

    # =========================================================================
    # Save JSON
    # =========================================================================
    out_data = {
        "parameters": {
            "SYSTEM": f"{SYMBOLS} on Au(TEMPLATE_SIZE) fcc100",
            "TEMPLATE_SIZE": TEMPLATE_SIZE,
            "SYMBOLS": SYMBOLS,
            "VACUUM": VACUUM,
            "CONFINEMENT_Z": CONFINEMENT_Z,
            "CALCULATOR": "EMT",
            "N_ITERATIONS": N_ITERATIONS,
            "N_RUNS": n_runs,
            "SEED_LIST": SEED_LIST,
            "SAMPLE_SIZE": SAMPLE_SIZE,
            "NUM_CANDIDATES": NUM_CANDIDATES,
            "KAPPA": KAPPA,
            "NOVELTY_TARGET_ENERGY": NOVELTY_TARGET_ENERGY,
            "NOVELTY_DELTA_E": NOVELTY_DELTA_E,
            "NOVELTY_WEIGHT": NOVELTY_WEIGHT,
            "DUP_THRESHOLD": DUP_THRESHOLD,
            "RELAX_STEPS": RELAX_STEPS,
            "START_RELAX": START_RELAX,
            "OPT_FMAX": OPT_FMAX,
            "OPT_STEPS": OPT_STEPS,
            "NOTE": ("target_energy=0.0 is an uncalibrated placeholder. "
                     "Calibrate before drawing conclusions from novelty_lcb "
                     "results.  Run a short standard-LCB search first."),
        },
        "results": {
            "regular_lcb": results["regular_lcb"],
            "novelty_lcb": results["novelty_lcb"],
        },
    }

    json_path = os.path.join(OUTDIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # =========================================================================
    # Plots
    # =========================================================================
    print("Generating plots...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    x = np.arange(n_runs)
    w = 0.35

    rd_arr = np.array(rd)
    nd_arr = np.array(nd)
    r_dup_arr = np.array(r_dup)
    n_dup_arr = np.array(n_dup)
    r_best_arr = np.array(r_best)
    n_best_arr = np.array(n_best)

    # --- Panel (0,0): Distinct configurations per run ---
    ax = axes[0, 0]
    ax.bar(x - w / 2, rd_arr, w, label="Regular LCB", color="steelblue")
    ax.bar(x + w / 2, nd_arr, w, label="Novelty-LCB", color="coral")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Distinct configurations")
    ax.set_title("Distinct Surface Configurations per Run")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed={s}" for s in SEED_LIST], rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # --- Panel (0,1): Duplicate evaluations per run ---
    ax = axes[0, 1]
    ax.bar(x - w / 2, r_dup_arr, w, label="Regular LCB", color="steelblue")
    ax.bar(x + w / 2, n_dup_arr, w, label="Novelty-LCB", color="coral")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Duplicate evaluations")
    ax.set_title("Duplicate Evaluations per Run")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed={s}" for s in SEED_LIST], rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # --- Panel (1,0): Best energy per run ---
    ax = axes[1, 0]
    ax.plot(x, r_best_arr, "o-", color="steelblue", label="Regular LCB",
            markersize=8)
    ax.plot(x, n_best_arr, "s-", color="coral", label="Novelty-LCB",
            markersize=8)
    ax.set_xlabel("Run index")
    ax.set_ylabel("Best energy [eV]")
    ax.set_title("Best Energy Found per Run")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed={s}" for s in SEED_LIST], rotation=30, ha="right")
    ax.legend()
    ax.grid(alpha=0.3)

    # --- Panel (1,1): Discovery curves (average) ---
    ax = axes[1, 1]
    env = build_system()["environment"]
    desc = Fingerprint(environment=env)

    for acq_type, color, lbl in [
        ("regular_lcb", "steelblue", "Regular LCB"),
        ("novelty_lcb", "coral", "Novelty-LCB"),
    ]:
        xv, yv = compute_discovery_curve(results[acq_type], desc, DUP_THRESHOLD)
        if len(xv):
            ax.plot(xv, yv, "-", color=color, linewidth=2.5, label=lbl)
            for ri, r in enumerate(results[acq_type]):
                db_path = r["db_file"]
                if not os.path.exists(db_path):
                    continue
                db = Database(filename=db_path, initialize=False)
                all_c = db.get_all_candidates()
                cum_d = []
                cum_t = []
                seen = []
                for ci, c in enumerate(all_c):
                    try:
                        e = c.get_potential_energy()
                        if not np.isfinite(e):
                            cum_d.append(cum_d[-1] if cum_d else 0)
                            cum_t.append(ci + 1)
                            continue
                        f = desc.get_features(c).ravel()
                        is_new = True
                        for sf in seen:
                            if np.linalg.norm(f - sf) <= DUP_THRESHOLD:
                                is_new = False
                                break
                        if is_new:
                            seen.append(f)
                        cum_d.append(len(seen))
                        cum_t.append(ci + 1)
                    except Exception:
                        cum_d.append(cum_d[-1] if cum_d else 0)
                        cum_t.append(ci + 1)
                if cum_d:
                    ax.plot(cum_t, cum_d, "-", color=color, alpha=0.25,
                            linewidth=1, label=None)
    ax.set_xlabel("Cumulative evaluations")
    ax.set_ylabel("Cumulative distinct configurations")
    ax.set_title("Discovery Curves (average ± individual runs)")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(OUTDIR, "benchmark_comparison.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot: {plot_path}")
    plt.close()

    # --- Pair-difference plot ---
    fig2, ax2 = plt.subplots(1, 3, figsize=(14, 4.5))

    diff_d = nd_arr - rd_arr
    diff_dup = n_dup_arr - r_dup_arr
    diff_be = n_best_arr - r_best_arr

    titles = ["Distinct configs\n(novelty − regular)",
              "Duplicates\n(novelty − regular)",
              "Best energy [eV]\n(novelty − regular)"]
    diffs = [diff_d, diff_dup, diff_be]
    colors = ["steelblue" if v > 0 else ("coral" if v < 0 else "grey")
              for v in diff_d]

    for axi, (title, diff, c) in enumerate(zip(titles, diffs, colors)):
        bars = ax2[axi].bar(x, diff, color=[
            "steelblue" if d > 0 else ("coral" if d < 0 else "grey")
            for d in diff
        ])
        ax2[axi].axhline(0, color="black", linewidth=0.8)
        ax2[axi].set_title(title)
        ax2[axi].set_xlabel("Run index")
        ax2[axi].set_xticks(x)
        ax2[axi].set_xticklabels([f"seed={s}" for s in SEED_LIST],
                                 rotation=30, ha="right")
        ax2[axi].grid(axis="y", alpha=0.3)

        # Annotate
        for xi, d in enumerate(diff):
            ax2[axi].text(xi, d + (0.05 * np.sign(d) if d != 0 else 0.1),
                           f"{d:+.1f}" if abs(d) >= 0.01 else "0",
                           ha="center", va="bottom" if d >= 0 else "top",
                           fontsize=9)

    plt.tight_layout()
    diff_path = os.path.join(OUTDIR, "benchmark_differences.png")
    plt.savefig(diff_path, dpi=150, bbox_inches="tight")
    print(f"Plot: {diff_path}")
    plt.close()

    print(f"\n{'=' * 72}")
    print("BENCHMARK COMPLETE")
    print(f"{'=' * 72}")
    print(f"Results:  {json_path}")
    print(f"Plot:     {plot_path}")
    print(f"Diff plot:{diff_path}")
    print()


if __name__ == "__main__":
    main()
