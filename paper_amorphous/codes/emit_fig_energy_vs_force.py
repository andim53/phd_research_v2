#!/usr/bin/env python3
"""emit_fig_energy_vs_force.py — relative energy vs stored max|F| (hexbin).

PLOTS FROM JSON (analysis/energy_vs_force/*.json), produced by
extract_energy_force.py — it does NOT re-read the AGOX DBs. The JSON carries
the per-structure (ΔE, max|F|) pairs for each leaf (iteration >= 10, per-leaf
e_max = 0.3 eV/atom cap applied at extraction).

Three panels, one per P loading (0P / 20P / 30P), pooled over the +0/+3/+5
cells. x = ΔE (eV/atom), y = max|F| (eV/Å, hexbinned in LOG-FORCE space so the
converged sub-0.05 region keeps resolution). Annotated with the 0.05 eV/Å
force-convergence criterion (the LocalOptimizationEvaluator fmax target).

Reading: 0P panels show a dense cloud pinned near F ~ 0.01-0.05 (converged);
P panels show a cloud pinned at F ~ 0.7-3 for every energy (never converged
under the single-DFT-step scheme).

Writes analysis/figures/fig_energy_vs_force.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_energy_vs_force.py

Run extract_energy_force.py first to (re)build the JSON cache.
"""
from __future__ import annotations

__version__ = "1.1.1"
# 1.1.0: plot from analysis/energy_vs_force/*.json (extract_energy_force.py)
#        instead of re-reading the AGOX DBs.
# 1.1.1: fix y-tick formatter — value-dependent decimals so sub-unity forces
#        (0.005, 0.05, 0.5) no longer render as "0".

import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- figure style (match _analysist + emit_cna_rdf.py) ---
plt.rcParams.update({
    "font.family": "serif", "font.size": 12,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "axes.grid": False, "figure.autolayout": True, "savefig.dpi": 300,
})

E_MAX = 0.3
FMAX = 0.05

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONDIR = os.path.join(ROOT, "analysis", "energy_vs_force")

# leaf dataset dir (relative to data/17_PPt/) -> P loading
LEAVES = {
    "1_plus0cell/0_0P": "0P", "1_plus0cell/2_20P": "20P", "1_plus0cell/3_30P": "30P",
    "2_plus3cell/0_0P": "0P", "2_plus3cell/2_20P": "20P", "2_plus3cell/3_30P": "30P",
    "0_plus5cell/3_3x3_0P": "0P", "0_plus5cell/1_3x3_20P": "20P", "0_plus5cell/2_3x3_30P": "30P",
}
CELL_ORDER = ["0P", "20P", "30P"]


def fmt(v):
    """Label a log10-force tick with the physical eV/A value, decimals as needed."""
    F = 10 ** v
    if F >= 1:
        return f"{F:.0f}"
    if F >= 0.01:
        return f"{F:.2f}"
    return f"{F:.3g}"


def load_leaf(leaf: str):
    """Per-structure (dE, fmax) arrays for a leaf, from its JSON cache."""
    jpath = os.path.join(JSONDIR, f"{leaf.replace('/', '_')}.json")
    with open(jpath) as f:
        d = json.load(f)
    dE = np.asarray([s["dE_eV_per_atom"] for s in d["structures"]], float)
    fm = np.asarray([s["fmax_eV_A"] for s in d["structures"]], float)
    return dE, fm


def main():
    by_p = {p: ([], []) for p in CELL_ORDER}
    n_ret = {p: 0 for p in CELL_ORDER}
    for leaf, p in LEAVES.items():
        dE, fm = load_leaf(leaf)
        n_ret[p] += len(dE)
        by_p[p] = (np.concatenate([by_p[p][0], dE]),
                   np.concatenate([by_p[p][1], fm]))

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True,
                             layout="constrained")
    logfmt = FuncFormatter(lambda v, p: fmt(v))
    for ax, p in zip(axes, CELL_ORDER):
        x, y = by_p[p]
        # hexbin in LOG-FORCE space so the converged sub-0.05 region keeps resolution
        hb = ax.hexbin(x, np.log10(y), gridsize=60, mincnt=1, cmap="viridis",
                       linewidths=0.1)
        ax.axhline(np.log10(FMAX), color="red", ls="--", lw=1.2)
        ax.set_title(f"{p} (n={n_ret[p]:,})", loc="left")
        ax.set_xlim(0, E_MAX)
        ax.set_ylim(np.log10(0.005), np.log10(60))
        ax.yaxis.set_major_formatter(logfmt)
        ax.set_xlabel(r"$\Delta E$ (eV/atom)")
    axes[0].set_ylabel(r"max $|\mathbf{F}|$ (eV/Å)")
    axes[0].text(0.29, np.log10(FMAX) + 0.15, r"fmax = 0.05", color="red",
                 fontsize=9, ha="right", va="bottom")
    cb = fig.colorbar(hb, ax=axes, fraction=0.02, pad=0.02)
    cb.set_label("count")

    out = os.path.join(ROOT, "analysis", "figures", "fig_energy_vs_force.png")
    fig.savefig(out)
    plt.close(fig)
    for p in CELL_ORDER:
        print(f"{p}: n_retained={n_ret[p]:,}")
    print("figures ->", out)


if __name__ == "__main__":
    main()
