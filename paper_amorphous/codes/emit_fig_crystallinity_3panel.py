#!/usr/bin/env python3
"""emit_fig_crystallinity_3panel.py — paper1 crystallinity 3-panel figure.

Serves MT-1..MT-4 (and M-2) from analysis/cna_rdf/*/cna_rdf.json:

  (a) Partial RDF g_PtP(r)/g_PP(r) for a representative 20P +0% leaf
      (1_plus0cell_2_20P) — illustrative of the disordered P coordination (M-2).
  (b) Steinhardt q6 crystalline fraction (mean +- std) vs cell expansion
      (+0/+3/+5%), one line per P loading (0P/20P/30P). Serves MT-1 (0P->P
      collapse), MT-3 (mild cell-dependence), and MT-2 (20P~30P overlap).
  (c) Relative drop in crystalline fraction vs +0% cell, one line per P.
      Serves MT-4 (P amplifies the cell-expansion effect) and MT-2.

Writes analysis/figures/fig_crystallinity_3panel.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_crystallinity_3panel.py
"""
from __future__ import annotations

__version__ = "1.0.3"

import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- figure style (match _analysist + emit_cna_rdf.py) ---
plt.rcParams.update({
    "font.family": "serif", "font.size": 12,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "axes.grid": False, "figure.autolayout": True, "savefig.dpi": 300,
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")
OUTDIR = os.path.join(ANALYSIS, "figures")

# leaf basename (under analysis/cna_rdf/) -> (cell, P)
LEAVES = {
    "1_plus0cell_0_0P": ("+0", "0P"), "1_plus0cell_2_20P": ("+0", "20P"),
    "1_plus0cell_3_30P": ("+0", "30P"),
    "2_plus3cell_0_0P": ("+3", "0P"), "2_plus3cell_2_20P": ("+3", "20P"),
    "2_plus3cell_3_30P": ("+3", "30P"),
    "0_plus5cell_3_3x3_0P": ("+5", "0P"), "0_plus5cell_1_3x3_20P": ("+5", "20P"),
    "0_plus5cell_2_3x3_30P": ("+5", "30P"),
}
CELLS = ["+0", "+3", "+5"]
P_ORDER = ["0P", "20P", "30P"]
COLORS = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}
MARKERS = {"0P": "o", "20P": "s", "30P": "^"}


def load_stats(leaf: str):
    p = os.path.join(ANALYSIS, "cna_rdf", leaf, "cna_rdf.json")
    d = json.load(open(p))
    cf = d["crystalline_fraction"]
    return {
        "frac_mean": cf["mean"], "frac_std": cf["std"], "n": d["n_structures"],
        "r": d["partial_rdf"]["r"], "g_PtP": d["partial_rdf"]["g_PtP"],
        "g_PP": d["partial_rdf"]["g_PP"],
    }


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    stats = {leaf: load_stats(leaf) for leaf in LEAVES}

    # crystalline-fraction grid: mean/std per (cell, P)
    mean = {c: {} for c in CELLS}
    std = {c: {} for c in CELLS}
    for leaf, (cell, p) in LEAVES.items():
        mean[cell][p] = stats[leaf]["frac_mean"]
        std[cell][p] = stats[leaf]["frac_std"]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4.2),
                                        layout="constrained")

    # ---- Panel (a): partial RDF (representative 20P +0% leaf) ----
    rep = "1_plus0cell_2_20P"
    s = stats[rep]
    r = np.asarray(s["r"])
    ax1.plot(r, np.asarray(s["g_PtP"]), color="tab:red",
             label=r"$g_{\mathrm{Pt-P}}(r)$")
    ax1.plot(r, np.asarray(s["g_PP"]), color="tab:purple",
             label=r"$g_{\mathrm{P-P}}(r)$")
    ax1.set_xlabel(r"$r$ (Å)")
    ax1.set_ylabel(r"$g(r)$")
    ax1.set_xlim(0, 5.0)
    ax1.legend(frameon=False)
    # panel label at bottom-middle (title moved to CLAIMS)
    ax1.text(0.5, -0.22, "(a)", transform=ax1.transAxes, ha="center",
             va="bottom", fontsize=12)

    # ---- Panel (b): crystalline fraction vs cell expansion ----
    x = np.arange(len(CELLS))
    for p in P_ORDER:
        m = [mean[c][p] for c in CELLS]
        e = [std[c][p] for c in CELLS]
        ax2.errorbar(x, m, yerr=e, marker=MARKERS[p], color=COLORS[p],
                     capsize=3, lw=1.5, label=p)
    ax2.set_xticks(x)
    ax2.set_xticklabels([r"+0%", r"+3%", r"+5%"])
    ax2.set_xlabel("cell expansion")
    ax2.set_ylabel("crystalline fraction")
    ax2.set_ylim(0, 1.1)
    ax2.legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, 0.30))
    # panel label at bottom-middle (title moved to CLAIMS)
    ax2.text(0.5, -0.22, "(b)", transform=ax2.transAxes, ha="center",
             va="bottom", fontsize=12)

    # ---- Panel (c): relative drop vs +0% cell ----
    for p in P_ORDER:
        base = mean["+0"][p]
        rel = [100 * (mean[c][p] - base) / base for c in CELLS]
        ax3.plot(x, rel, marker=MARKERS[p], color=COLORS[p], lw=1.5, label=p)
    ax3.axhline(0, color="k", lw=0.8, ls=":")
    ax3.set_xticks(x)
    ax3.set_xticklabels([r"+0%", r"+3%", r"+5%"])
    ax3.set_xlabel("cell expansion")
    ax3.set_ylabel(r"$\Delta$ crystalline fraction vs +0% (%)")
    ax3.legend(frameon=False, ncol=3, loc="lower left")
    # panel label at bottom-middle (title moved to CLAIMS)
    ax3.text(0.5, -0.22, "(c)", transform=ax3.transAxes, ha="center",
             va="bottom", fontsize=12)

    out = os.path.join(OUTDIR, "fig_crystallinity_3panel.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)


if __name__ == "__main__":
    main()
