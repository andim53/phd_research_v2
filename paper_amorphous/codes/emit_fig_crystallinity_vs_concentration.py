#!/usr/bin/env python3
"""emit_fig_crystallinity_vs_concentration.py — paper1 comparative-validation figure.

Plots the Steinhardt q6 crystalline fraction vs P concentration (0/20/30 at% P),
one line per cell expansion (+0/+3/+5%), from analysis/cna_rdf/*/cna_rdf.json.
Overlays the experimental amorphization onset of Shashank et al. 2025
(NPG Asia Materials 17:15) converted from ion dose to at% P by the box model
(hpc_runs/convert_dose_concentration.py): onset ~36 at% P (4.0e16 ions/cm^2
@30 keV), with a shaded band spanning the box-model range of their
amorphization regime (~35-66 at% P).

Serves MT-6 (comparative validation): our 20-30 at% P onset is consistent
with Shashank's converted ~36 at% P onset, both locating the amorphous
transition in the ~20-40 at% P range.

Writes analysis/figures/fig_crystallinity_vs_concentration.png.

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_crystallinity_vs_concentration.py
"""
from __future__ import annotations

__version__ = "1.0.1"

import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects

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
P_AT = {"0P": 0.0, "20P": 20.0, "30P": 30.0}
COLORS = {"+0": "tab:blue", "+3": "tab:orange", "+5": "tab:green"}
MARKERS = {"+0": "o", "+3": "s", "+5": "^"}

# Shashank et al. 2025 amorphization onset, converted dose -> at% P (box model)
SHASHANK_ONSET_AT = 36.0   # 4.0e16 ions/cm^2 @30 keV
SHASHANK_BAND = (35.0, 66.0)  # box-model range of their amorphization regime


def load_frac(leaf: str):
    p = os.path.join(ANALYSIS, "cna_rdf", leaf, "cna_rdf.json")
    d = json.load(open(p))
    return d["crystalline_fraction"]["mean"]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    mean = {c: {} for c in CELLS}
    for leaf, (cell, p) in LEAVES.items():
        mean[cell][p] = load_frac(leaf)

    fig, ax = plt.subplots(figsize=(6.2, 4.2), layout="constrained")

    # Shashank amorphization band + onset marker
    ax.axvspan(SHASHANK_BAND[0], SHASHANK_BAND[1], color="tab:red",
               alpha=0.12, label="Shashank amorphization regime")
    ax.axvline(SHASHANK_ONSET_AT, color="tab:red", ls="--", lw=1.5)
    # white outline so the onset label pops over the shaded band / lines
    outline = [patheffects.withStroke(linewidth=3, foreground="white")]
    ax.text(SHASHANK_ONSET_AT + 0.5, 0.95, "Shashank onset\n(~36 at% P)",
            color="tab:red", fontsize=9, va="top", ha="left",
            path_effects=outline)

    # crystalline fraction vs P concentration, one line per cell
    x = [P_AT[p] for p in P_ORDER]
    for c in CELLS:
        m = [mean[c][p] for p in P_ORDER]
        ax.plot(x, m, marker=MARKERS[c], color=COLORS[c], lw=1.5, label=c)

    ax.set_xlabel("P concentration (at%)")
    ax.set_ylabel("crystalline fraction")
    ax.set_xlim(-2, 40)
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=False, ncol=2, loc="upper right")

    out = os.path.join(OUTDIR, "fig_crystallinity_vs_concentration.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)


if __name__ == "__main__":
    main()
