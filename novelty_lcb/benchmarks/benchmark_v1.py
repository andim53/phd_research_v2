#!/usr/bin/env python3
"""
Benchmark v1 — Novelty-LCB vs Regular LCB (broad energy window).

Compares how many DISTINCT local minima each acquisitor finds when
optimizing a free Au10 cluster using the EMT calculator (Erfeld Embedded
Atom Model).  Both runs use identical generators, samplers, evaluators,
and seeds.  The only difference is the acquisitor.

Metrics
-------
- Number of distinct minima found (using fingerprint-distance clustering)
- Energy range of found minima
- Number of evaluations spent on duplicate structures
- Discovery curve: distinct minima vs cumulative evaluation
- Statistical comparison (paired differences across independent runs)

Parameters
----------
Au10 free cluster, EMT calculator, 60 iterations per run,
5 independent seeds, broad energy window [3.5, 8.5] eV.
"""

from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Ensure the package root is importable (same trick as the original script)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ase import Atoms
from ase.calculators.emt import EMT

from novelty_lcb.acquisitor import NoveltyLCBAcquisitor
from novelty_lcb.benchmark_helpers import (
    DEFAULT,
    build_agox,
    make_template,
    make_environment,
)
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from novelty_lcb.utils import fingerprint_distance


# ── Parameters ───────────────────────────────────────────────────────────────

N_ITERATIONS = 60          # per run (×2 acquisitors × N_RUNS = 120 total)
N_RUNS = 5                 # independent seeds for statistics
RANDOM_SEEDS = [42, 123, 456, 789, 1024]

# Override default energy window for the broad benchmark
WINDOW_PARAMS = dict(
    target_energy=6.0,       # eV — centre of energy window
    delta_E=2.5,             # eV — half-width → [3.5, 8.5] eV
)

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "benchmark_results_v1")
os.makedirs(OUTDIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_distinct_minima(db: Database, descriptor: Fingerprint,
                        threshold: float = DEFAULT["dup_threshold"]):
    """Cluster DB structures into distinct minima using fingerprint distance.

    Greedy clustering: pick lowest-energy structure, then repeatedly pick
    the next structure farthest from all already-selected ones.

    Returns list of (candidate, energy) for each distinct minimum.
    """
    structures = db.get_all_candidates()
    if not structures:
        return []

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

    selected_indices = []
    remaining = list(np.argsort(energies))  # lowest energy first

    while remaining:
        idx = remaining.pop(0)
        selected_indices.append(idx)
        remaining = [
            j for j in remaining
            if np.linalg.norm(features[j] - features[idx]) > threshold
        ]

    return [(valid_structures[i], energies[i]) for i in selected_indices]


def run_single_benchmark(seed: int, run_label: str,
                         acquisitor_type: str) -> dict:
    """Run one AGOX optimization with the given seed and acquisitor type."""
    np.random.seed(seed)

    acq_label = "novelty" if acquisitor_type == "novelty_lcb" else "regular"
    full_label = f"{run_label}_{acq_label}"
    agox = build_agox(seed, OUTDIR, full_label, acquisitor_type,
                      params=WINDOW_PARAMS)

    agox.run(N_iterations=N_ITERATIONS, verbose=False, hide_log=True)

    # Analyse results
    db = Database(filename=os.path.join(OUTDIR, f"{full_label}_db.db"),
                  initialize=False)
    db.restore_to_memory()

    # Build descriptor fresh (same as in build_agox)
    env = make_environment(make_template())
    desc = Fingerprint(
        environment=env,
        rc1=6, rc2=4, binwidth=0.2, Nbins=30,
        use_angular=True,
    )

    all_candidates = db.get_all_candidates()
    all_energies = []
    for c in all_candidates:
        try:
            e = c.get_potential_energy()
            if np.isfinite(e):
                all_energies.append(e)
        except Exception:
            pass

    distinct = get_distinct_minima(db, desc, DEFAULT["dup_threshold"])
    distinct_energies = [e for _, e in distinct]
    n_distinct = len(distinct)
    n_evals = len(all_energies)
    n_duplicates = n_evals - n_distinct

    if distinct_energies:
        e_min = min(distinct_energies)
        e_max = max(distinct_energies)
        e_range = e_max - e_min
    else:
        e_min = e_max = e_range = np.nan

    best_energy = min(all_energies) if all_energies else np.nan

    return {
        "seed": seed,
        "label": full_label,
        "acquisitor": acquisitor_type,
        "n_evals": n_evals,
        "n_distinct": n_distinct,
        "n_duplicates": n_duplicates,
        "best_energy": best_energy,
        "e_min": e_min,
        "e_max": e_max,
        "e_range": e_range,
        "distinct_energies": distinct_energies,
        "db_file": os.path.join(OUTDIR, f"{full_label}_db.db"),
        "all_energies": all_energies,
    }


# ── Discovery-curve helper ───────────────────────────────────────────────────

def compute_discovery_curve(results: list, desc: Fingerprint,
                            threshold: float) -> tuple:
    """Return (cum_total, cum_distinct) averaged over runs.

    Simulates incremental storage by walking the DB candidates in order
    and tracking how many are new (fingerprint distance > threshold).
    """
    all_curves = []
    for r in results:
        db_path = r["db_file"]
        if not os.path.exists(db_path):
            continue
        db = Database(filename=db_path, initialize=False)
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

    # Average (interpolate to common x grid)
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK V1: Novelty-LCB vs Regular LCB (broad window)")
    print("=" * 70)
    print(f"System: free {DEFAULT['symbols']}")
    print(f"Calculator: EMT (Erfeld Embedded Atom Model)")
    print(f"Iterations per run: {N_ITERATIONS}")
    print(f"Number of independent runs: {N_RUNS}")
    print(f"Seeds: {RANDOM_SEEDS}")
    print(f"Regular LCB kappa: {DEFAULT['kappa']}")
    print(f"Novelty LCB lambda: {DEFAULT['novelty_weight']}")
    print(f"Energy window: "
          f"[{WINDOW_PARAMS['target_energy'] - WINDOW_PARAMS['delta_E']:.1f}, "
          f"{WINDOW_PARAMS['target_energy'] + WINDOW_PARAMS['delta_E']:.1f}] eV")
    print(f"Distinctness threshold: {DEFAULT['dup_threshold']} "
          f"(fingerprint distance)")
    print(f"Output directory: {OUTDIR}")
    print("=" * 70)

    results = {"regular_lcb": [], "novelty_lcb": []}

    for i, seed in enumerate(RANDOM_SEEDS):
        print(f"\n{'='*70}")
        print(f"RUN {i+1}/{N_RUNS}  seed={seed}")
        print(f"{'='*70}")

        # Regular LCB
        label_r = f"run{i+1:02d}_regular"
        print(f"\n--- Regular LCB (kappa={DEFAULT['kappa']}) ---")
        r = run_single_benchmark(seed, label_r, "regular_lcb")
        results["regular_lcb"].append(r)
        print(f"  Done. distinct={r['n_distinct']}, "
              f"best E={r['best_energy']:.3f} eV")

        # Novelty LCB
        label_n = f"run{i+1:02d}_novelty"
        print(f"\n--- Novelty LCB "
              f"(λ={DEFAULT['novelty_weight']}, "
              f"window=[{WINDOW_PARAMS['target_energy']-WINDOW_PARAMS['delta_E']:.1f}, "
              f"{WINDOW_PARAMS['target_energy']+WINDOW_PARAMS['delta_E']:.1f}]) ---")
        n = run_single_benchmark(seed, label_n, "novelty_lcb")
        results["novelty_lcb"].append(n)
        print(f"  Done. distinct={n['n_distinct']}, "
              f"best E={n['best_energy']:.3f} eV")

    # ── Aggregate results ────────────────────────────────────────────────────
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
        print(f"  Best energy:     mean={np.mean(best_e):.3f} ± "
              f"{np.std(best_e):.3f} eV")
        print(f"  Energy range:    mean={np.mean(e_range):.3f} ± "
              f"{np.std(e_range):.3f} eV")

        for r in runs:
            print(f"    seed={r['seed']:5d}: distinct={r['n_distinct']:2d}, "
                  f"evals={r['n_evals']:2d}, dup={r['n_duplicates']:2d}, "
                  f"best E={r['best_energy']:.3f}")

    # ── Statistical comparison ───────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STATISTICAL COMPARISON")
    print("=" * 70)

    rd = [r["n_distinct"] for r in results["regular_lcb"]]
    nd = [r["n_distinct"] for r in results["novelty_lcb"]]
    r_dup = [r["n_duplicates"] for r in results["regular_lcb"]]
    n_dup = [r["n_duplicates"] for r in results["novelty_lcb"]]
    r_best = [r["best_energy"] for r in results["regular_lcb"]]
    n_best = [r["best_energy"] for r in results["novelty_lcb"]]

    diff_distinct = np.array(nd) - np.array(rd)
    diff_dup = np.array(n_dup) - np.array(r_dup)
    diff_best = np.array(n_best) - np.array(r_best)

    print(f"\nDistinct minima (novelty - regular):")
    print(f"  Per-run differences: {diff_distinct}")
    print(f"  Mean difference:     {np.mean(diff_distinct):+.1f} ± "
          f"{np.std(diff_distinct):.1f}")
    print(f"  Novelty finds more:  {sum(diff_distinct > 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_distinct == 0)}/{N_RUNS} runs")
    print(f"  Regular finds more:  {sum(diff_distinct < 0)}/{N_RUNS} runs")

    print(f"\nDuplicates (novelty - regular):")
    print(f"  Per-run differences: {diff_dup}")
    print(f"  Mean difference:     {np.mean(diff_dup):+.1f} ± "
          f"{np.std(diff_dup):.1f}")
    print(f"  Novelty has fewer:   {sum(diff_dup < 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_dup == 0)}/{N_RUNS} runs")
    print(f"  Regular has fewer:   {sum(diff_dup > 0)}/{N_RUNS} runs")

    print(f"\nBest energy (novelty - regular):")
    print(f"  Per-run differences: {diff_best}")
    print(f"  Mean difference:     {np.mean(diff_best):+.3f} ± "
          f"{np.std(diff_best):.3f} eV")
    print(f"  Novelty finds lower: {sum(diff_best < 0)}/{N_RUNS} runs")
    print(f"  Tie:                 {sum(diff_best == 0)}/{N_RUNS} runs")
    print(f"  Regular finds lower: {sum(diff_best > 0)}/{N_RUNS} runs")

    # ── Save results to JSON ──────────────────────────────────────────────────
    out_data = {
        "parameters": {
            "N_ATOMS": 10,
            "SYMBOLS": DEFAULT["symbols"],
            "N_ITERATIONS": N_ITERATIONS,
            "N_RUNS": N_RUNS,
            "RANDOM_SEEDS": RANDOM_SEEDS,
            "TEMPERATURE": DEFAULT["temperature"],
            "RATTLE_AMPLITUDE": DEFAULT["rattle_amplitude"],
            "RATTLE_N": DEFAULT["rattle_n"],
            "KAPPA": DEFAULT["kappa"],
            "NOVELTY_WEIGHT": DEFAULT["novelty_weight"],
            "TARGET_ENERGY": WINDOW_PARAMS["target_energy"],
            "DELTA_E": WINDOW_PARAMS["delta_E"],
            "DUP_THRESHOLD": DEFAULT["dup_threshold"],
        },
        "results": {
            "regular_lcb": results["regular_lcb"],
            "novelty_lcb": results["novelty_lcb"],
        },
    }

    json_path = os.path.join(OUTDIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nResults saved to {json_path}")

    # ── Plot comparison ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    x = np.arange(N_RUNS)
    w = 0.35

    # Panel 1: Distinct minima per run
    ax = axes[0]
    ax.bar(x - w/2, rd, w, label="Regular LCB", color="steelblue")
    ax.bar(x + w/2, nd, w, label="Novelty LCB", color="coral")
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
    plot_path = os.path.join(OUTDIR, "benchmark_comparison.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {plot_path}")
    plt.close()

    # ── Discovery curve ──────────────────────────────────────────────────────
    print("\nComputing discovery curves...")
    env = make_environment(make_template())
    desc = Fingerprint(
        environment=env,
        rc1=6, rc2=4, binwidth=0.2, Nbins=30,
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for idx, (acq_type, color) in enumerate([
        ("regular_lcb", "steelblue"),
        ("novelty_lcb", "coral"),
    ]):
        ax = axes[idx]
        x_avg, y_avg = compute_discovery_curve(
            results[acq_type], desc, DEFAULT["dup_threshold"]
        )
        if len(x_avg):
            ax.plot(x_avg, y_avg, "-o", color=color, linewidth=2,
                   label="Average")
        for run_idx, r in enumerate(results[acq_type]):
            db_path = r["db_file"]
            if not os.path.exists(db_path):
                continue
            db = Database(filename=db_path, initialize=False)
            all_c = db.get_all_candidates()
            cum_distinct = []
            cum_total = []
            seen_features = []
            for i, c in enumerate(all_c):
                try:
                    e = c.get_potential_energy()
                    if not np.isfinite(e):
                        cum_distinct.append(
                            cum_distinct[-1] if cum_distinct else 0)
                        cum_total.append(i + 1)
                        continue
                    f = desc.get_features(c).ravel()
                    is_new = True
                    for sf in seen_features:
                        if np.linalg.norm(f - sf) <= DEFAULT["dup_threshold"]:
                            is_new = False
                            break
                    if is_new:
                        seen_features.append(f)
                    cum_distinct.append(len(seen_features))
                    cum_total.append(i + 1)
                except Exception:
                    cum_distinct.append(
                        cum_distinct[-1] if cum_distinct else 0)
                    cum_total.append(i + 1)
            if cum_distinct:
                ax.plot(cum_total, cum_distinct, "-o", color=color,
                       alpha=0.4, markersize=3, linewidth=1,
                       label=f"Run {run_idx+1} (seed={r['seed']})")
        ax.set_xlabel("Cumulative evaluations")
        ax.set_ylabel("Cumulative distinct minima")
        ax.set_title(f"{acq_type.replace('_', ' ').title()}: "
                     "Discovery Curve")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    curve_path = os.path.join(OUTDIR, "discovery_curves.png")
    plt.savefig(curve_path, dpi=150, bbox_inches="tight")
    print(f"Discovery curves saved to {curve_path}")
    plt.close()

    print("\n" + "=" * 70)
    print("BENCHMARK V1 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
