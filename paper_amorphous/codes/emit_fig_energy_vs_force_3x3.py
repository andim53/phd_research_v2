#!/usr/bin/env python3
"""emit_fig_energy_vs_force_3x3.py — relative energy vs stored max|F| per leaf.

PLOTS FROM JSON (analysis/energy_vs_force/*.json), produced by
extract_energy_force.py — it does NOT re-read the AGOX DBs.

3x3 grid of hexbin density plots. Rows = cell expansion (+0/+3/+5%), columns =
P loading (0P/20P/30P); each panel is ONE leaf (pooled over that leaf's seeds).

Same data + filters as emit_fig_energy_vs_force.py (iteration >= 10, per-leaf
e_max = 0.3 eV/atom cap, applied at extraction), same log-force hexbin axis
and 0.05 eV/A convergence line. This layout keeps the cell dimension visible.

Reading: rows should look similar for a given P column (weak cell-dependence,
MT-3); columns differ strongly (0P converged near F~0.02-0.05, P pinned at
F~0.7-3) (MT-1).

Writes analysis/figures/fig_energy_vs_force_3x3.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_energy_vs_force_3x3.py

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

FMAX = 0.05

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONDIR = os.path.join(ROOT, "analysis", "energy_vs_force")

# row = cell, col = P  ->  leaf dataset dir (relative to data/17_PPt/)
GRID = {
    ("+0", "0P"): "1_plus0cell/0_0P", ("+0", "20P"): "1_plus0cell/2_20P",
    ("+0", "30P"): "1_plus0cell/3_30P",
    ("+3", "0P"): "2_plus3cell/0_0P", ("+3", "20P"): "2_plus3cell/2_20P",
    ("+3", "30P"): "2_plus3cell/3_30P",
    ("+5", "0P"): "0_plus5cell/3_3x3_0P", ("+5", "20P"): "0_plus5cell/1_3x3_20P",
    ("+5", "30P"): "0_plus5cell/2_3x3_30P",
}
CELL_ROWS = ["+0", "+3", "+5"]
P_COLS = ["0P", "20P", "30P"]


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
    fig, axes = plt.subplots(3, 3, figsize=(12, 10), sharex=True, sharey=True,
                             layout="constrained")
    logfmt = FuncFormatter(lambda v, p: fmt(v))
    for r, cell in enumerate(CELL_ROWS):
        for c, p in enumerate(P_COLS):
            ax = axes[r][c]
            dE, fm = load_leaf(GRID[(cell, p)])
            # hexbin in LOG-FORCE space so the converged sub-0.05 region keeps resolution
            hb = ax.hexbin(dE, np.log10(fm), gridsize=40, mincnt=1,
                           cmap="viridis", linewidths=0.1)
            ax.axhline(np.log10(FMAX), color="red", ls="--", lw=1.0)
            ax.set_ylim(np.log10(0.005), np.log10(60))
            if r == 0:
                ax.set_title(f"{p}", loc="center")
            if c == 0:
                ax.set_ylabel(f"{cell}% cell\nmax $|\\mathbf{{F}}|$ (eV/Å)")
            if r == 2:
                ax.set_xlabel(r"$E_i - E_{\rm glob}$ (eV/atom)")
    for row in axes:
        for ax in row:
            ax.yaxis.set_major_formatter(logfmt)
    axes[0][0].text(0.29, np.log10(FMAX) + 0.15, "fmax=0.05", color="red",
                    fontsize=8, ha="right", va="bottom")
    cb = fig.colorbar(axes[2][2].collections[0], ax=axes, fraction=0.02, pad=0.02)
    cb.set_label("count")

    out = os.path.join(ROOT, "analysis", "figures", "fig_energy_vs_force_3x3.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)


if __name__ == "__main__":
    main()
