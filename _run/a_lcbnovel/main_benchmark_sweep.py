#!/usr/bin/env python3
"""
Benchmark: impact of kappa and novelty_weight on Novelty-LCB
(Ni8 / Au(4,4,2) fcc100 surface, EMT calculator).

Same system/stack as main_benchmark.py (reuses its build_system / build_stack /
get_distinct_configurations / run_single helpers by importing the module), but here we
sweep a GRID of kappa x novelty_weight on the Novelty-LCB acquisitor only, to study how
each parameter affects search behavior.

Grid:
    kappa          in KAPPA_LIST
    novelty_weight in NOVELTY_WEIGHT_LIST
    (all combinations; Novelty-LCB only; auto global-minimum per-atom window)

The acquisitor is Novelty-LCB with:
    a(x) = sigma(x) + lambda * Novelty(x)
    window (per atom) = (-inf, E_min/N + X], X = energy_above_min (eV/atom)

One fixed seed per combo (SEED) for speed. Outputs to a subdir of benchmark_results/.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python main_benchmark_sweep.py
"""



__version__ = "1.0.0"

import matplotlib

matplotlib.use("Agg")

import itertools
import json
import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

# ── Reuse helpers from main_benchmark (same system/stack/metrics) ───────────
_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import main_benchmark as mb  # provides build_system, build_stack, get_distinct_configurations, run_single


# =============================================================================
# SWEEP CONFIGURATION
# =============================================================================

# --- Grid to sweep (Novelty-LCB only) ---
KAPPA_LIST = [0.5, 1.0, 2.0, 4.0]
NOVELTY_WEIGHT_LIST = [0.0, 0.5, 1.0, 1.5, 2.0]

# --- Fixed system settings (reuse main_benchmark) ---
# Uses mb.SEED_LIST, mb.N_ITERATIONS, mb.NUM_CANDIDATES, mb.RELAX_STEPS, ...
# mb.SYMBOLS = "Ni8", mb.TEMPLATE_SIZE = (4,4,2), mb.VACUUM, mb.CONFINEMENT_Z, ...

# --- Fixed per-combo settings ---
SEED = 41            # single fixed seed per combo (fast)
N_ITERATIONS = 30    # iterations per run (match main_benchmark)

# --- Novelty-LCB auto window (per-atom, same as main_benchmark) ---
ENERGY_ABOVE_MIN = 0.1   # eV/atom
PER_ATOM = True

# --- Analysis ---
DUP_THRESHOLD = 1.5   # reuse mb.DUP_THRESHOLD (same value)

# --- Output ---
OUTDIR = os.path.join(_HERE, "benchmark_results", "sweep_kappa_lambda")
os.makedirs(OUTDIR, exist_ok=True)


# =============================================================================
# Sweep runner
# =============================================================================

def run_combo(kappa, novelty_weight, seed=SEED, n_iterations=N_ITERATIONS):
    """Run one Novelty-LCB combo with the given kappa & novelty_weight.

    Temporarily overrides mb.KAPPA / mb.NOVELTY_WEIGHT so the shared build_stack
    uses them, runs one AGOX search, and returns the metrics dict.
    """
    # Save originals
    old_kappa = mb.KAPPA
    old_w = mb.NOVELTY_WEIGHT
    old_outdir = mb.OUTDIR
    old_energy_above = mb.NOVELTY_ENERGY_ABOVE_MIN
    old_per_atom = mb.NOVELTY_ENERGY_PER_ATOM
    old_dup = mb.DUP_THRESHOLD
    old_n_iter = mb.N_ITERATIONS

    mb.KAPPA = kappa
    mb.NOVELTY_WEIGHT = novelty_weight
    mb.N_ITERATIONS = n_iterations
    mb.NOVELTY_ENERGY_ABOVE_MIN = ENERGY_ABOVE_MIN
    mb.NOVELTY_ENERGY_PER_ATOM = PER_ATOM
    mb.DUP_THRESHOLD = DUP_THRESHOLD
    # Route the DB into this sweep's output dir with a descriptive label
    combo_out = os.path.join(OUTDIR, f"k{kappa}_l{novelty_weight}")
    os.makedirs(combo_out, exist_ok=True)
    mb.OUTDIR = combo_out

    label = f"k{kappa}_l{novelty_weight}"
    try:
        # build_stack(acq_type, db_path, seed) with novelty_lcb
        result = mb.run_single(seed, label, "novelty_lcb")
        result["kappa"] = kappa
        result["novelty_weight"] = novelty_weight
        return result
    finally:
        # Restore
        mb.KAPPA = old_kappa
        mb.NOVELTY_WEIGHT = old_w
        mb.N_ITERATIONS = old_n_iter
        mb.NOVELTY_ENERGY_ABOVE_MIN = old_energy_above
        mb.NOVELTY_ENERGY_PER_ATOM = old_per_atom
        mb.DUP_THRESHOLD = old_dup
        mb.OUTDIR = old_outdir


def main():
    combos = list(itertools.product(KAPPA_LIST, NOVELTY_WEIGHT_LIST))
    print("=" * 72)
    print("SWEEP BENCHMARK: kappa x novelty_weight impact on Novelty-LCB")
    print("System: Ni8 on Au(4,4,2) fcc100 surface  (EMT calculator)")
    print("=" * 72)
    print(f"  kappa:           {KAPPA_LIST}")
    print(f"  novelty_weight:  {NOVELTY_WEIGHT_LIST}")
    print(f"  Combos:          {len(combos)} (grid)")
    print(f"  Seed per combo:  {SEED}")
    print(f"  Iterations:      {N_ITERATIONS}")
    print(f"  Auto window:     energy_above_min={ENERGY_ABOVE_MIN} eV/atom (per_atom={PER_ATOM})")
    print(f"  Acquisitor:      Novelty-LCB only")
    print(f"  Output:          {OUTDIR}")
    print("=" * 72)
    print()

    results = []
    for kappa, w in combos:
        print(f"--- combo kappa={kappa}, novelty_weight={w} ---")
        t0 = time.time()
        r = run_combo(kappa, w)
        dt = time.time() - t0
        results.append(r)
        print(f"    done in {dt:.1f}s: distinct={r['n_distinct']}, "
              f"best_E={r['best_E']:.3f} eV, dup={r['n_duplicates']}")

    # ---- Summary table ----
    print("\n" + "=" * 72)
    print("SUMMARY (mean over runs; here 1 seed per combo)")
    print("=" * 72)
    hdr = f"{'kappa':>6} {'lambda':>6} {'distinct':>9} {'best_E':>10} {'dup':>6} {'evals':>6}"
    print(hdr)
    for r in results:
        print(f"{r['kappa']:>6} {r['novelty_weight']:>6} {r['n_distinct']:>9} "
              f"{r['best_E']:>10.3f} {r['n_duplicates']:>6} {r['n_evals']:>6}")

    # ---- Save JSON ----
    out_data = {
        "parameters": {
            "SYSTEM": f"{mb.SYMBOLS} on Au{mb.TEMPLATE_SIZE} fcc100",
            "CALCULATOR": "EMT", "KAPPA_LIST": KAPPA_LIST,
            "NOVELTY_WEIGHT_LIST": NOVELTY_WEIGHT_LIST,
            "SEED": SEED, "N_ITERATIONS": N_ITERATIONS,
            "ENERGY_ABOVE_MIN": ENERGY_ABOVE_MIN, "PER_ATOM": PER_ATOM,
            "DUP_THRESHOLD": DUP_THRESHOLD,
            "NOTE": "Impact of kappa & novelty_weight on Novelty-LCB (auto global-min window).",
        },
        "results": results,
    }
    json_path = os.path.join(OUTDIR, "sweep_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # ---- Plots ----
    print("Generating plots...")
    kap = np.array([r["kappa"] for r in results])
    lam = np.array([r["novelty_weight"] for r in results])
    nd = np.array([r["n_distinct"] for r in results])
    be = np.array([r["best_E"] for r in results])
    dup = np.array([r["n_duplicates"] for r in results])

    # 2D heatmaps: distinct / best_E / duplicates as function of kappa x lambda
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    kvals = np.array(KAPPA_LIST)
    lvals = np.array(NOVELTY_WEIGHT_LIST)
    Z_dist = np.full((len(kvals), len(lvals)), np.nan)
    Z_best = np.full((len(kvals), len(lvals)), np.nan)
    Z_dup = np.full((len(kvals), len(lvals)), np.nan)
    for r in results:
        i = list(kvals).index(r["kappa"])
        j = list(lvals).index(r["novelty_weight"])
        Z_dist[i, j] = r["n_distinct"]
        Z_best[i, j] = r["best_E"]
        Z_dup[i, j] = r["n_duplicates"]

    titles = ["Distinct configs", "Best energy [eV]", "Duplicates"]
    Zs = [Z_dist, Z_best, Z_dup]
    for ax, Z, title in zip(axes, Zs, titles):
        im = ax.imshow(Z, origin="lower", aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(lvals)))
        ax.set_xticklabels([f"{v:.1f}" for v in lvals])
        ax.set_yticks(range(len(kvals)))
        ax.set_yticklabels([f"{v:.1f}" for v in kvals])
        ax.set_xlabel("novelty_weight (lambda)")
        ax.set_ylabel("kappa")
        ax.set_title(title)
        # annotate
        for i in range(len(kvals)):
            for j in range(len(lvals)):
                val = Z[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            color="white", fontsize=8)
        plt.colorbar(im, ax=ax)
    plt.tight_layout()
    heat_path = os.path.join(OUTDIR, "sweep_heatmaps.png")
    plt.savefig(heat_path, dpi=150, bbox_inches="tight")
    print(f"Heatmap plot: {heat_path}")
    plt.close()

    # Curves: distinct / best_E / dup vs novelty_weight, one line per kappa
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
    for ax2, metric, ylab in [(axes2[0], "n_distinct", "Distinct configs"),
                              (axes2[1], "best_E", "Best energy [eV]"),
                              (axes2[2], "n_duplicates", "Duplicates")]:
        for kappa in KAPPA_LIST:
            ys = [next(r[metric] for r in results if r["kappa"] == kappa and r["novelty_weight"] == l)
                  for l in NOVELTY_WEIGHT_LIST]
            ax2.plot(NOVELTY_WEIGHT_LIST, ys, "o-", label=f"kappa={kappa}")
        ax2.set_xlabel("novelty_weight (lambda)")
        ax2.set_ylabel(ylab)
        ax2.set_title(f"{ylab} vs lambda (per kappa)")
        ax2.legend()
        ax2.grid(alpha=0.3)
    plt.tight_layout()
    curve_path = os.path.join(OUTDIR, "sweep_curves.png")
    plt.savefig(curve_path, dpi=150, bbox_inches="tight")
    print(f"Curve plot: {curve_path}")
    plt.close()

    # Discovery curves (average distinct vs cumulative evals) per combo
    fig3, ax3 = plt.subplots(1, 1, figsize=(10, 7))
    fdesc = mb.build_system()["descriptor"]  # reuse the shared Fingerprint descriptor
    for kappa in KAPPA_LIST:
        for l in NOVELTY_WEIGHT_LIST:
            r = next(x for x in results if x["kappa"] == kappa and x["novelty_weight"] == l)
            xv, yv = mb.compute_discovery_curve([r], fdesc, DUP_THRESHOLD)
            if len(xv):
                ax3.plot(xv, yv, "-", alpha=0.7,
                         label=f"k={kappa}, l={l}")
    ax3.set_xlabel("Cumulative evaluations")
    ax3.set_ylabel("Cumulative distinct configurations")
    ax3.set_title("Discovery curves (all combos)")
    ax3.legend(fontsize=7, ncol=2)
    ax3.grid(alpha=0.3)
    plt.tight_layout()
    disc_path = os.path.join(OUTDIR, "sweep_discovery.png")
    plt.savefig(disc_path, dpi=150, bbox_inches="tight")
    print(f"Discovery plot: {disc_path}")
    plt.close()

    print("\n" + "=" * 72)
    print("SWEEP BENCHMARK COMPLETE")
    print(f"  JSON:      {json_path}")
    print(f"  Heatmaps:  {heat_path}")
    print(f"  Curves:    {curve_path}")
    print(f"  Discovery: {disc_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
