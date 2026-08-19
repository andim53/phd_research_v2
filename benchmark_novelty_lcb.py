#!/usr/bin/env python3
"""
Benchmark: Novelty-LCB vs Regular LCB acquisition for AGOX.

Compares how many DISTINCT local minima each acquisitor finds when
optimizing a free Au10 cluster using the EMT calculator.

Both runs use identical generators, samplers, evaluators, and seeds.
The only difference is the acquisitor.

Metrics:
  - Number of distinct minima found (using fingerprint distance clustering)
  - Energy range of found minima
  - Number of evaluations spent on duplicate structures
  - Discovery curve: distinct minima vs iteration

Requirements: agox_v2 conda env (AGOX 3.10.2 + ASE 3.25.0)
"""
import sys
sys.path.insert(0, "/home/think/Desktop/research")

import os
import shutil
import numpy as np
from ase import Atoms
from ase.calculators.emt import EMT
from ase.io import write

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.samplers import MetropolisSampler
from agox.models import GPR
from agox.models.descriptors import Fingerprint
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

from novelty_lcb_acquisitor import NoveltyLCBAcquisitor
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from novelty_lcb_acquisitor import is_distinct, fingerprint_distance

# ── Parameters ───────────────────────────────────────────────────────────────

N_ATOMS = 10
SYMBOLS = "Au10"
N_ITERATIONS = 60          # per run (×2 = 120 total)
N_RUNS = 5                 # independent seeds for statistics
TEMPERATURE = 0.2          # Metropolis sampler temperature
RATTLE_AMPLITUDE = 2.5     # generator rattle amplitude
RATTLE_N = 5               # rattle attempts per candidate
KAPPA = 2.0                # LCB kappa
NOVELTY_WEIGHT = 1.5       # novelty LCB lambda
# Energy window: set to cover the expected EMT energy range for Au10.
# EMT gives positive energies (~5-8 eV for Au10 clusters).
# Using a broad window that captures the interesting low-energy region.
TARGET_ENERGY = 6.0        # eV — centre of energy window
DELTA_E = 2.5              # eV — half-width → window [3.5, 8.5] eV
DUP_THRESHOLD = 0.15       # fingerprint distance threshold for "distinct"
RANDOM_SEEDS = [42, 123, 456, 789, 1024]  # for N_RUNS

OUTDIR = "/home/think/Desktop/research/benchmark_results"
os.makedirs(OUTDIR, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_template():
    """Create an empty template with a reasonable cell for Au10."""
    cell = np.eye(3) * 16.0  # large enough for free cluster
    return Atoms("", cell=cell, pbc=False)


def get_distinct_minima(db, descriptor, threshold=DUP_THRESHOLD):
    """Cluster database structures into distinct minima using fingerprint distance.

    Returns list of (candidate, energy) for each distinct minimum.
    """
    structures = db.get_all_candidates()
    if not structures:
        return []

    # Get features for all — skip structures that fail
    features = []
    energies = []
    valid_structures = []
    for s in structures:
        try:
            e = s.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = descriptor.get_features(s).ravel()
            features.append(f)
            energies.append(e)
            valid_structures.append(s)
        except Exception:
            continue

    if not features:
        return []

    features = np.array(features)
    energies = np.array(energies)

    # Greedy clustering: pick lowest-energy structure, then repeatedly pick
    # the next structure farthest from all already-selected ones.
    selected_indices = []
    remaining = list(range(len(features)))

    # Sort by energy (lowest first)
    order = np.argsort(energies)
    remaining = list(order)

    while remaining:
        idx = remaining.pop(0)  # lowest energy remaining
        selected_indices.append(idx)
        # Remove all within threshold of the selected one
        remaining = [
            j for j in remaining
            if np.linalg.norm(features[j] - features[idx]) > threshold
        ]

    return [(valid_structures[i], energies[i]) for i in selected_indices]


def run_single_benchmark(seed, run_label, acquisitor_type):
    """Run one AGOX optimization with the given seed and acquisitor type.

    Returns dict with results.
    """
    np.random.seed(seed)

    # Clean db file
    db_file = f"{OUTDIR}/{run_label}_db.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    # Template + environment
    template = make_template()
    environment = Environment(
        template=template,
        symbols=SYMBOLS,
        confinement_cell=np.eye(3) * 14,
        confinement_corner=np.array([4, 4, 4]),
        print_report=False,
    )

    calculator = EMT()

    # Database
    database = Database(filename=db_file, order=5)

    # Descriptor
    descriptor = Fingerprint(
        environment=environment,
        rc1=6, rc2=4, binwidth=0.2, Nbins=30,
        use_angular=True,
    )

    # Model — train after first 5 iterations, update every 3
    model = GPR(
        descriptor=descriptor,
        kernel=RBF(),
        prior=Repulsive(),
        database=database,
        order=0,
        iteration_start_training=5,
        update_period=3,
    )

    # Sampler
    sampler = MetropolisSampler(temperature=TEMPERATURE, order=3)

    # Generator
    generator = RattleGenerator(
        **environment.get_confinement(),
        environment=environment,
        sampler=sampler,
        n_rattle=RATTLE_N,
        rattle_amplitude=RATTLE_AMPLITUDE,
        order=1,
    )

    # Evaluator — local optimization
    evaluator = LocalOptimizationEvaluator(
        calculator,
        gets={"get_key": "candidates"},
        store_trajectory=False,
        optimizer_run_kwargs={"fmax": 0.05, "steps": 100},
        order=2,
        constraints=environment.get_constraints(),
    )

    # Acquisitor
    if acquisitor_type == "novelty_lcb":
        acq = NoveltyLCBAcquisitor(
            model=model,
            descriptor=descriptor,
            database=database,
            target_energy=TARGET_ENERGY,
            delta_E=DELTA_E,
            novelty_weight=NOVELTY_WEIGHT,
            order=4,
        )
    elif acquisitor_type == "regular_lcb":
        acq = LowerConfidenceBoundAcquisitor(
            model=model,
            kappa=KAPPA,
            order=4,
        )
    else:
        raise ValueError(f"Unknown acquisitor: {acquisitor_type}")

    # Run AGOX
    agox = AGOX(generator, database, sampler, evaluator, acq, seed=seed)
    agox.run(N_iterations=N_ITERATIONS, verbose=True, hide_log=False)

    # Analyze results
    db = Database(filename=db_file, initialize=False)

    # All evaluated candidates
    all_candidates = db.get_all_candidates()
    all_energies = []
    for c in all_candidates:
        try:
            e = c.get_potential_energy()
            if np.isfinite(e):
                all_energies.append(e)
        except Exception:
            pass

    # Distinct minima
    distinct = get_distinct_minima(db, descriptor, DUP_THRESHOLD)
    distinct_energies = [e for _, e in distinct]
    n_distinct = len(distinct)

    # Number of evaluations (finite energy candidates)
    n_evals = len(all_energies)

    # Number of duplicates (total - distinct)
    n_duplicates = n_evals - n_distinct

    # Energy range
    if distinct_energies:
        e_min = min(distinct_energies)
        e_max = max(distinct_energies)
        e_range = e_max - e_min
    else:
        e_min = e_max = e_range = np.nan

    # Best energy found
    best_energy = min(all_energies) if all_energies else np.nan

    return {
        "seed": seed,
        "label": run_label,
        "acquisitor": acquisitor_type,
        "n_evals": n_evals,
        "n_distinct": n_distinct,
        "n_duplicates": n_duplicates,
        "best_energy": best_energy,
        "e_min": e_min,
        "e_max": e_max,
        "e_range": e_range,
        "distinct_energies": distinct_energies,
        "db_file": db_file,
        "all_energies": all_energies,
    }


def main():
    print("=" * 70)
    print("BENCHMARK: Novelty-LCB vs Regular LCB")
    print("=" * 70)
    print(f"System: free {SYMBOLS}")
    print(f"Calculator: EMT (Erfeld Embedded Atom Model)")
    print(f"Iterations per run: {N_ITERATIONS}")
    print(f"Number of independent runs: {N_RUNS}")
    print(f"Seeds: {RANDOM_SEEDS}")
    print(f"Regular LCB kappa: {KAPPA}")
    print(f"Novelty LCB lambda: {NOVELTY_WEIGHT}")
    print(f"Energy window: [{TARGET_ENERGY - DELTA_E}, {TARGET_ENERGY + DELTA_E}] eV")
    print(f"Distinctness threshold: {DUP_THRESHOLD} (fingerprint distance)")
    print(f"Output directory: {OUTDIR}")
    print("=" * 70)

    results = {"regular_lcb": [], "novelty_lcb": []}

    for i, seed in enumerate(RANDOM_SEEDS):
        print(f"\n{'='*70}")
        print(f"RUN {i+1}/{N_RUNS}  seed={seed}")
        print(f"{'='*70}")

        # Regular LCB
        label_r = f"run{i+1:02d}_regular"
        print(f"\n--- Regular LCB (kappa={KAPPA}) ---")
        r = run_single_benchmark(seed, label_r, "regular_lcb")
        results["regular_lcb"].append(r)
        print(f"  Done. distinct={r['n_distinct']}, best E={r['best_energy']:.3f} eV")

        # Novelty LCB
        label_n = f"run{i+1:02d}_novelty"
        print(f"\n--- Novelty LCB (λ={NOVELTY_WEIGHT}, window=[{TARGET_ENERGY-DELTA_E:.1f}, {TARGET_ENERGY+DELTA_E:.1f}]) ---")
        n = run_single_benchmark(seed, label_n, "novelty_lcb")
        results["novelty_lcb"].append(n)
        print(f"  Done. distinct={n['n_distinct']}, best E={n['best_energy']:.3f} eV")

    # ── Aggregate results ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("AGGREGATE RESULTS")
    print("=" * 70)

    for acq_type in ["regular_lcb", "novelty_lcb"]:
        runs = results[acq_type]
        n_distinct = [r["n_distinct"] for r in runs]
        n_evals = [r["n_evals"] for r in runs]
        n_dup = [r["n_duplicates"] for r in runs]
        best_e = [r["best_energy"] for r in runs]
        e_range = [r["e_range"] for r in runs]

        print(f"\n{acq_type}:")
        print(f"  Distinct minima:  mean={np.mean(n_distinct):.1f}, "
              f"std={np.std(n_distinct):.1f}, "
              f"min={min(n_distinct)}, max={max(n_distinct)}")
        print(f"  Total evals:     mean={np.mean(n_evals):.1f}, "
              f"std={np.std(n_evals):.1f}")
        print(f"  Duplicates:      mean={np.mean(n_dup):.1f}, "
              f"std={np.std(n_dup):.1f} "
              f"({np.mean(n_dup)/np.mean(n_evals)*100:.0f}% of evals)")
        print(f"  Best energy:     mean={np.mean(best_e):.3f} ± {np.std(best_e):.3f} eV")
        print(f"  Energy range:    mean={np.mean(e_range):.3f} ± {np.std(e_range):.3f} eV")

        # Per-run detail
        for r in runs:
            print(f"    seed={r['seed']:5d}: distinct={r['n_distinct']:2d}, "
                  f"evals={r['n_evals']:2d}, dup={r['n_duplicates']:2d}, "
                  f"best E={r['best_energy']:.3f}")

    # ── Statistical comparison ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STATISTICAL COMPARISON")
    print("=" * 70)

    r_distinct = [r["n_distinct"] for r in results["regular_lcb"]]
    n_distinct = [r["n_distinct"] for r in results["novelty_lcb"]]
    r_dup = [r["n_duplicates"] for r in results["regular_lcb"]]
    n_dup = [r["n_duplicates"] for r in results["novelty_lcb"]]
    r_best = [r["best_energy"] for r in results["regular_lcb"]]
    n_best = [r["best_energy"] for r in results["novelty_lcb"]]

    # Paired t-test-like comparison (just descriptive since N is small)
    diff_distinct = np.array(n_distinct) - np.array(r_distinct)
    diff_dup = np.array(n_dup) - np.array(r_dup)
    diff_best = np.array(n_best) - np.array(r_best)

    print(f"\nDistinct minima (novelty - regular):")
    print(f"  Per-run differences: {diff_distinct}")
    print(f"  Mean difference:     {np.mean(diff_distinct):+.1f} ± {np.std(diff_distinct):.1f}")
    print(f"  Novelty finds more:  {sum(diff_distinct > 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_distinct == 0)}/{N_RUNS} runs")
    print(f"  Regular finds more:  {sum(diff_distinct < 0)}/{N_RUNS} runs")

    print(f"\nDuplicates (novelty - regular):")
    print(f"  Per-run differences: {diff_dup}")
    print(f"  Mean difference:     {np.mean(diff_dup):+.1f} ± {np.std(diff_dup):.1f}")
    print(f"  Novelty has fewer:   {sum(diff_dup < 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_dup == 0)}/{N_RUNS} runs")
    print(f"  Regular has fewer:   {sum(diff_dup > 0)}/{N_RUNS} runs")

    print(f"\nBest energy (novelty - regular):")
    print(f"  Per-run differences: {diff_best}")
    print(f"  Mean difference:     {np.mean(diff_best):+.3f} ± {np.std(diff_best):.3f} eV")
    print(f"  Novelty finds lower: {sum(diff_best < 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_best == 0)}/{N_RUNS} runs")
    print(f"  Regular finds lower: {sum(diff_best > 0)}/{N_RUNS} runs")

    # ── Save results to JSON ───────────────────────────────────────────────────
    import json
    out_data = {
        "parameters": {
            "N_ATOMS": N_ATOMS,
            "SYMBOLS": SYMBOLS,
            "N_ITERATIONS": N_ITERATIONS,
            "N_RUNS": N_RUNS,
            "RANDOM_SEEDS": RANDOM_SEEDS,
            "TEMPERATURE": TEMPERATURE,
            "RATTLE_AMPLITUDE": RATTLE_AMPLITUDE,
            "RATTLE_N": RATTLE_N,
            "KAPPA": KAPPA,
            "NOVELTY_WEIGHT": NOVELTY_WEIGHT,
            "TARGET_ENERGY": TARGET_ENERGY,
            "DELTA_E": DELTA_E,
            "DUP_THRESHOLD": DUP_THRESHOLD,
        },
        "results": {
            "regular_lcb": results["regular_lcb"],
            "novelty_lcb": results["novelty_lcb"],
        },
    }

    json_path = f"{OUTDIR}/benchmark_results.json"
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nResults saved to {json_path}")

    # ── Plot comparison ────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # Panel 1: Distinct minima per run
    ax = axes[0]
    x = np.arange(N_RUNS)
    w = 0.35
    ax.bar(x - w/2, r_distinct, w, label="Regular LCB", color="steelblue")
    ax.bar(x + w/2, n_distinct, w, label="Novelty LCB", color="coral")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Distinct minima found")
    ax.set_title("Distinct Minima per Run")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Panel 2: Duplicates per run
    ax = axes[1]
    ax.bar(x - w/2, r_dup, w, label="Regular LCB", color="steelblue")
    ax.bar(x + w/2, n_dup, w, label="Novelty LCB", color="coral")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Duplicate evaluations")
    ax.set_title("Duplicate Evaluations per Run")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Panel 3: Best energy per run
    ax = axes[2]
    ax.plot(x, r_best, "o-", color="steelblue", label="Regular LCB")
    ax.plot(x, n_best, "s-", color="coral", label="Novelty LCB")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Best energy [eV]")
    ax.set_title("Best Energy Found per Run")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plot_path = f"{OUTDIR}/benchmark_comparison.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {plot_path}")
    plt.close()

    # ── Discovery curve (distinct minima vs iteration) ────────────────────────
    # For this we need to track cumulative distinct minima over iterations.
    # We'll compute this from the database by simulating incremental storage.
    print("\nComputing discovery curves...")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for idx, (acq_type, color) in enumerate([
        ("regular_lcb", "steelblue"),
        ("novelty_lcb", "coral"),
    ]):
        ax = axes[idx]  # 2 panels in 1 row

        for run_idx, r in enumerate(results[acq_type]):
            db_path = r["db_file"]
            if not os.path.exists(db_path):
                continue

            db = Database(filename=db_path, initialize=False)
            all_c = db.get_all_candidates()

            cum_distinct = []
            cum_total = []
            seen_features = []

            # Create descriptor for this database
            fp_desc = Fingerprint(
                environment=Environment(
                    template=make_template(),
                    symbols=SYMBOLS,
                    confinement_cell=np.eye(3) * 14,
                    confinement_corner=np.array([4, 4, 4]),
                    print_report=False,
                ),
                rc1=6, rc2=4, binwidth=0.2, Nbins=30,
            )

            for i, c in enumerate(all_c):
                try:
                    e = c.get_potential_energy()
                    if not np.isfinite(e):
                        cum_distinct.append(cum_distinct[-1] if cum_distinct else 0)
                        cum_total.append(i + 1)
                        continue
                    f = fp_desc.get_features(c).ravel()
                    is_new = True
                    for sf in seen_features:
                        if np.linalg.norm(f - sf) <= DUP_THRESHOLD:
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
                ax.plot(cum_total, cum_distinct, "-o", color=color,
                       alpha=0.5, markersize=3, linewidth=1,
                       label=f"Run {run_idx+1} (seed={r['seed']})")

        ax.set_xlabel("Cumulative evaluations")
        ax.set_ylabel("Cumulative distinct minima")
        ax.set_title(f"{acq_type.replace('_', ' ').title()}: Discovery Curve")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    curve_path = f"{OUTDIR}/discovery_curves.png"
    plt.savefig(curve_path, dpi=150, bbox_inches="tight")
    print(f"Discovery curves saved to {curve_path}")
    plt.close()

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
