#!/usr/bin/env python3
"""emit_fig_xrd_crystallinity.py — paper1 XRD crystallinity cross-check figure.

Serves MT-1 (0P->P collapse) and MT-3 (mild cell dependence) from the XRD
integrated crystallinity index, cross-checking the Steinhardt q6 crystalline
fraction (fig_crystallinity_3panel).

Reads data/17_PPt/<cell>/<leaf>/xrd_out/crystallinity.csv for the 9 paper
leaves (0P/20P/30P x +0/+3/+5), takes the integrated CI at the lowest-energy
window (0.05 eV/atom, the most crystalline reference), and plots integrated
CI vs cell expansion, one line per P loading.

Writes:
  analysis/xrd_crystallinity/xrd_crystallinity.json  (aggregated data)
  analysis/figures/fig_xrd_crystallinity.png         (paper figure)

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_xrd_crystallinity.py
"""
from __future__ import annotations

__version__ = "1.0.0"

import csv
import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- figure style (match emit_fig_crystallinity_3panel.py) ---
plt.rcParams.update({
    "font.family": "serif", "font.size": 12,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "axes.grid": False, "figure.autolayout": True, "savefig.dpi": 300,
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "17_PPt")
ANALYSIS = os.path.join(ROOT, "analysis")
OUTDIR = os.path.join(ANALYSIS, "figures")
JSONDIR = os.path.join(ANALYSIS, "xrd_crystallinity")

# leaf path (under data/17_PPt/) -> (cell, P)
LEAVES = {
    "1_plus0cell/0_0P": ("+0", "0P"), "1_plus0cell/2_20P": ("+0", "20P"),
    "1_plus0cell/3_30P": ("+0", "30P"),
    "2_plus3cell/0_0P": ("+3", "0P"), "2_plus3cell/2_20P": ("+3", "20P"),
    "2_plus3cell/3_30P": ("+3", "30P"),
    "0_plus5cell/3_3x3_0P": ("+5", "0P"), "0_plus5cell/1_3x3_20P": ("+5", "20P"),
    "0_plus5cell/2_3x3_30P": ("+5", "30P"),
}
CELLS = ["+0", "+3", "+5"]
P_ORDER = ["0P", "20P", "30P"]
COLORS = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}
MARKERS = {"0P": "o", "20P": "s", "30P": "^"}


def load_integrated_ci(leaf: str):
    """Integrated CI at the lowest-energy window (most crystalline reference)."""
    p = os.path.join(DATA, leaf, "xrd_out", "crystallinity.csv")
    with open(p) as f:
        rows = list(csv.DictReader(f))
    # lowest window centre = most crystalline reference
    row = min(rows, key=lambda r: float(r["center"]))
    return {
        "window": row["window"], "center": float(row["center"]),
        "n": int(row["n"]),
        "peak_fraction_ci": float(row["peak_fraction_ci"]),
        "integrated_ci": float(row["integrated_ci"]),
    }


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(JSONDIR, exist_ok=True)

    stats = {leaf: load_integrated_ci(leaf) for leaf in LEAVES}

    # integrated-CI grid per (cell, P)
    ci = {c: {} for c in CELLS}
    for leaf, (cell, p) in LEAVES.items():
        ci[cell][p] = stats[leaf]["integrated_ci"]

    # ---- figure: integrated CI vs cell expansion, one line per P ----
    x = np.arange(len(CELLS))
    fig, ax = plt.subplots(figsize=(6, 4))
    for p in P_ORDER:
        y = [ci[c][p] for c in CELLS]
        ax.plot(x, y, marker=MARKERS[p], color=COLORS[p], lw=1.5, label=p)
    ax.set_xticks(x)
    ax.set_xticklabels([r"+0%", r"+3%", r"+5%"])
    ax.set_xlabel("cell expansion")
    ax.set_ylabel("XRD integrated crystallinity index")
    ax.set_ylim(0, 1.0)
    ax.legend(frameon=False, ncol=3, loc="upper right")

    out = os.path.join(OUTDIR, "fig_xrd_crystallinity.png")
    fig.savefig(out)
    plt.close(fig)

    # ---- JSON ----
    result = {
        "metric": "XRD integrated crystallinity index at lowest-energy window "
                  "(0.05 eV/atom, most crystalline reference)",
        "source": "data/17_PPt/<cell>/<leaf>/xrd_out/crystallinity.csv",
        "leaves": {leaf: stats[leaf] for leaf in LEAVES},
        "grid": {c: ci[c] for c in CELLS},
    }
    jpath = os.path.join(JSONDIR, "xrd_crystallinity.json")
    with open(jpath, "w") as f:
        json.dump(result, f, indent=2)

    print("figures ->", out)
    print("json    ->", jpath)
    for p in P_ORDER:
        print(f"  {p}: " + ", ".join(f"{c}={ci[c][p]:.3f}" for c in CELLS))


if __name__ == "__main__":
    main()
