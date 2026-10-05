#!/usr/bin/env python3
"""emit_fig2_2panel.py — paper1 Figure 2: crystallinity 2-panel figure.

Panel (a): partial radial distribution functions g_PtP(r) and g_PP(r) for a
representative P-loaded leaf (cell expansion is weak/directionally consistent
per MT-3, and 0P leaves have no P-P/Pt-P pairs). Representative = 20P +0% leaf
(1_plus0cell_2_20P). Plots the Pt-P and P-P first coordination shells.

Panel (b): Steinhardt q6 crystalline fraction (mean, +-std as error bars) vs
cell expansion (+0/+3/+5%) for the three P loadings (0P, 20P, 30P). Shows
MT-1 (0P -> 20/30P collapse), MT-3 (mild cell-dependence), MT-4 (P amplifies
the relative cell-expansion effect).

Writes analysis/figures/fig2_crystallinity_2panel.png (paper1 standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig2_2panel.py
"""
from __future__ import annotations

__version__ = "1.1.1"

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # paper_amorphous/
ANALYSIS = os.path.join(ROOT, "analysis")
OUTDIR = os.path.join(ANALYSIS, "figures")

# leaf basename (under analysis/cna_rdf/) -> (cell, P-loading)
LEAVES = {
    "1_plus0cell_0_0P":   ("+0", "0P"),
    "1_plus0cell_2_20P":  ("+0", "20P"),
    "1_plus0cell_3_30P":  ("+0", "30P"),
    "2_plus3cell_0_0P":   ("+3", "0P"),
    "2_plus3cell_2_20P":  ("+3", "20P"),
    "2_plus3cell_3_30P":  ("+3", "30P"),
    "0_plus5cell_3_3x3_0P":  ("+5", "0P"),
    "0_plus5cell_1_3x3_20P": ("+5", "20P"),
    "0_plus5cell_2_3x3_30P": ("+5", "30P"),
}


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
    cells = ["+0", "+3", "+5"]
    labels = ["20P", "30P", "0P"]  # legend order rows below

    # assemble crystalline-fraction grid: mean/std per (cell, P)
    mean = {c: {} for c in cells}
    std = {c: {} for c in cells}
    frac_data = {}
    for leaf, (cell, p) in LEAVES.items():
        s = load_stats(leaf)
        mean[cell][p] = s["frac_mean"]
        std[cell][p] = s["frac_std"]
        frac_data[leaf] = s

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # ---- Panel (a): partial RDF (representative 20P +0% leaf) ----
    rep = "1_plus0cell_2_20P"
    s = frac_data[rep]
    r = np.asarray(s["r"])
    g_ptp = np.asarray(s["g_PtP"])
    g_pp = np.asarray(s["g_PP"])
    ax1.plot(r, g_ptp, color="tab:red", label=r"$g_{\mathrm{Pt-P}}(r)$")
    ax1.plot(r, g_pp, color="tab:purple", label=r"$g_{\mathrm{P-P}}(r)$")
    ax1.set_xlabel(r"$r$ (Å)")
    ax1.set_ylabel(r"$g(r)$")
    ax1.set_xlim(0, 5.0)
    ax1.legend(frameon=False)
    # panel label at bottom-center, just below the axes (paper convention)
    ax1.text(0.5, -0.22, "(a)", transform=ax1.transAxes, ha="center",
             va="bottom", fontsize=12)

    # ---- Panel (b): crystalline fraction vs cell expansion ----
    x = np.arange(len(cells))
    width = 0.25
    colors = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}
    for i, p in enumerate(labels):
        m = [mean[c][p] for c in cells]
        e = [std[c][p] for c in cells]
        ax2.bar(x + (i - 1) * width, m, width, yerr=e, capsize=3,
                label=f"{p}", color=colors[p], edgecolor="k", linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels([r"+0%", r"+3%", r"+5%"])
    ax2.set_xlabel("cell expansion")
    ax2.set_ylabel("crystalline fraction")
    ax2.set_ylim(0, 1.1)
    ax2.legend(frameon=False, ncol=3, loc="upper right")
    # panel label at bottom-center, just below the axes (paper convention)
    ax2.text(0.5, -0.22, "(b)", transform=ax2.transAxes, ha="center",
             va="bottom", fontsize=12)

    out = os.path.join(OUTDIR, "fig2_2panel.png")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("figures ->", out)


if __name__ == "__main__":
    main()
