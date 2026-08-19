#!/usr/bin/env python3
"""
Benchmark v2 — Novelty-LCB vs Regular LCB (tight energy window).

With a narrow energy window, the novelty LCB must find structurally
diverse candidates within a restricted energy range, while the regular
LCB simply minimizes E − κ·σ globally.

Key hypothesis: With a tight window, regular LCB will tend to find
fewer distinct minima (focusing on the lowest-E basin), while novelty
LCB will discover more distinct structures within the window.

Parameters
----------
Au10 free cluster, EMT calculator, 80 iterations per run,
5 independent seeds, tight energy window [5.0, 6.5] eV.
"""

from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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


# ── Parameters ───────────────────────────────────────────────────────────────

N_ITERATIONS = 80
N_RUNS = 5
RANDOM_SEEDS = [42, 123, 456, 789, 1024]

# Tight window: only accept candidates in [5.0, 6.5] eV
TIGHT_WINDOW = dict(
    target_energy=5.75,
    delta_E=0.75,
)

# Use a larger distinctness threshold for the tight-window clustering
# (structures are closer together in energy, so the fingerprint clusters
# are also expected to be tighter)
DUP_THRESHOLD = 1.0

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "benchmark_results_v2")
os.makedirs(OUTDIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_distinct_minima(db: Database, descriptor: Fingerprint,
                        threshold: float = DUP_THRESHOLD):
    """Cluster DB structures into distinct minima (greedy, energy-first)."""
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
    remaining = list(np.argsort(energies))

    while remaining:
        idx = remaining.pop(0)
        selected_indices.append(idx)
        remaining = [
            j for j in remaining
            if np.linalg.norm(features[j] - features[idx]) > threshold
        ]

    return [(valid_structures[i], energies[i]) for i in selected_indices]


def run_single(seed: int, label: str, acq_type: str) -> dict:
    """Run one AGOX optimization and return results dict."""
    np.random.seed(seed)

    acq_label = "novelty" if acq_type == "novelty_lcb" else "regular"
    full_label = f"{label}_{acq_label}"
    agox = build_agox(seed, OUTDIR, full_label, acq_type,
                      params=TIGHT_WINDOW)

    agox.run(N_iterations=N_ITERATIONS, verbose=False, hide_log=True)

    # Analyse
    db2 = Database(filename=os.path.join(OUTDIR, f"{full_label}_db.db"),
                   initialize=False)
    db2.restore_to_memory()
    all_c = db2.get_all_candidates()

    env = make_environment(make_template())
    desc = Fingerprint(
        environment=env, rc1=6, rc2=4, binwidth=0.2, Nbins=30,
        use_angular=True,
    )

    features, energies = [], []
    for c in all_c:
        try:
            e = c.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = desc.get_features(c).ravel()
            features.append(f)
            energies.append(e)
        except Exception:
            pass

    if not features:
        return {
            "seed": seed, "label": full_label, "acq": acq_type,
            "n_evals": 0, "n_distinct": 0, "best_E": np.nan,
            "e_range": 0.0, "all_energies": [],
        }

    features = np.array(features)
    energies = np.array(energies)

    order = np.argsort(energies)
    remaining = list(order)
    selected = []
    while remaining:
        idx = remaining.pop(0)
        selected.append(idx)
        remaining = [
            j for j in remaining
            if np.linalg.norm(features[j] - features[idx]) > DUP_THRESHOLD
        ]

    return {
        "seed": seed,
        "label": full_label,
        "acq": acq_type,
        "n_evals": len(energies),
        "n_distinct": len(selected),
        "best_E": float(energies.min()),
        "e_range": float(energies.max() - energies.min()),
        "distinct_energies": [float(energies[i]) for i in selected],
        "all_energies": [float(e) for e in energies],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK 2: Tight Energy Window")
    print("=" * 70)
    print(f"Window: [{TIGHT_WINDOW['target_energy'] - TIGHT_WINDOW['delta_E']:.2f}, "
          f"{TIGHT_WINDOW['target_energy'] + TIGHT_WINDOW['delta_E']:.2f}] eV")
    print(f"Distinctness threshold: {DUP_THRESHOLD}")
    print(f"Iterations: {N_ITERATIONS}, Runs: {N_RUNS}")
    print("=" * 70)

    results = {"regular_lcb": [], "novelty_lcb": []}

    for i, seed in enumerate(RANDOM_SEEDS):
        print(f"\nRun {i+1}/{N_RUNS} (seed={seed})")

        label_r = f"tight_run{i+1:02d}_regular"
        print("  Regular LCB...")
        r = run_single(seed, label_r, "regular_lcb")
        results["regular_lcb"].append(r)
        print(f"    evals={r['n_evals']}, distinct={r['n_distinct']}, "
              f"best_E={r['best_E']:.3f}")

        label_n = f"tight_run{i+1:02d}_novelty"
        print("  Novelty LCB...")
        n = run_single(seed, label_n, "novelty_lcb")
        results["novelty_lcb"].append(n)
        print(f"    evals={n['n_evals']}, distinct={n['n_distinct']}, "
              f"best_E={n['best_E']:.3f}")

    # Aggregate
    print("\n" + "=" * 70)
    print("AGGREGATE RESULTS (tight window)")
    print("=" * 70)
    for acq_type in ["regular_lcb", "novelty_lcb"]:
        runs = results[acq_type]
        nd = [r["n_distinct"] for r in runs]
        ne = [r["n_evals"] for r in runs]
        be = [r["best_E"] for r in runs]
        print(f"\n{acq_type}:")
        print(f"  Distinct minima: mean={np.mean(nd):.1f}, "
              f"std={np.std(nd):.1f}, min={min(nd)}, max={max(nd)}")
        print(f"  Evaluations:     mean={np.mean(ne):.1f}, "
              f"std={np.std(ne):.1f}")
        print(f"  Best energy:     mean={np.mean(be):.3f} ± "
              f"{np.std(be):.3f} eV")
        for r in runs:
            print(f"    seed={r['seed']:5d}: distinct={r['n_distinct']:2d}, "
                  f"evals={r['n_evals']:2d}, best_E={r['best_E']:.3f}")

    # Comparison
    rd = [r["n_distinct"] for r in results["regular_lcb"]]
    nd = [r["n_distinct"] for r in results["novelty_lcb"]]
    diff = np.array(nd) - np.array(rd)
    print(f"\nDifference (novelty - regular) in distinct minima:")
    print(f"  Per-run: {diff}")
    print(f"  Mean:   {np.mean(diff):+.1f} ± {np.std(diff):.1f}")
    print(f"  Novelty finds more: {np.sum(diff > 0)}/{N_RUNS} runs")
    print(f"  Tie:                {np.sum(diff == 0)}/{N_RUNS} runs")
    print(f"  Regular finds more: {np.sum(diff < 0)}/{N_RUNS} runs")

    # Save JSON
    import json as _json
    with open(os.path.join(OUTDIR, "benchmark2_results.json"), "w") as f:
        _json.dump({
            "parameters": {
                "N_ATOMS": 10,
                "SYMBOLS": DEFAULT["symbols"],
                "N_ITERATIONS": N_ITERATIONS,
                "N_RUNS": N_RUNS,
                "KAPPA": DEFAULT["kappa"],
                "NOVELTY_WEIGHT": DEFAULT["novelty_weight"],
                "TARGET_ENERGY": TIGHT_WINDOW["target_energy"],
                "DELTA_E": TIGHT_WINDOW["delta_E"],
                "DUP_THRESHOLD": DUP_THRESHOLD,
            },
            "results": results,
        }, f, indent=2, default=str)
    print(f"\nResults saved to {OUTDIR}/benchmark2_results.json")

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    x = np.arange(N_RUNS)

    # Panel 1: distinct minima
    ax = axes[0]
    ax.bar(x - 0.2, rd, 0.4, label="Regular LCB", color="steelblue")
    ax.bar(x + 0.2, nd, 0.4, label="Novelty LCB", color="coral")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Distinct minima found")
    ax.set_title("Distinct Minima per Run (tight window)")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Panel 2: best energy
    ax = axes[1]
    ax.plot(x, rd, "o-", color="steelblue", label="Regular LCB")
    ax.plot(x, nd, "s-", color="coral", label="Novelty LCB")
    ax.set_xlabel("Run index")
    ax.set_ylabel("Best energy [eV]")
    ax.set_title("Best Energy per Run (tight window)")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(OUTDIR, "benchmark2_comparison.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {plot_path}")
    plt.close()

    print("\n" + "=" * 70)
    print("BENCHMARK V2 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
