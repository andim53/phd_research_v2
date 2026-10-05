#!/usr/bin/env python3
"""emit_fig_surrogate_perf.py — paper1 M-1e surrogate predictive-performance figure.

Serves M-1e (GPR surrogate predictive performance) from
analysis/surrogate_perf/surrogate_perf.json (produced by
codes/extract_surrogate_perf.py).

Two panels, one bar per leaf (all 9 leaves) at the 0 -> 0.1 eV/atom window,
colored by P loading with a distinct hatch per cell expansion (+0/+3/+5):

  (a) MAE — mean absolute error (eV/atom) between the surrogate prediction and
      the DFT energy, at the 0-0.1 eV/atom window.
  (b) GPR uncertainty — mean GPR sigma (eV/atom) at the same window.

The x-axis is the 9 leaves grouped by P loading (0P / 20P / 30P). Comparing
(a) and (b) shows whether the predicted uncertainty tracks the actual error
(validating the LCB acquisition, kappa=2).

Relative-energy window: structures within 0.1 eV/atom of the leaf's global
minimum (E_glob), matching the crystalline-fraction cap (CLAIMS v6).

Writes analysis/figures/fig_surrogate_perf.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_surrogate_perf.py
"""
from __future__ import annotations

__version__ = "3.0.0"

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- figure style (match _analysist + emit_fig_explore_exploit.py) ---
plt.rcParams.update({
    "font.family": "serif", "font.size": 12,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "axes.grid": False, "figure.autolayout": True, "savefig.dpi": 300,
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")
OUTDIR = os.path.join(ANALYSIS, "figures")

P_ORDER = ["0P", "20P", "30P"]
CELL_ORDER = ["+0", "+3", "+5"]
COLORS = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}
# hatch per cell expansion, so the 3 leaves of a P loading are distinct
CELL_HATCH = {"+0": "", "+3": "//", "+5": "xx"}

WINDOW_LO = 0.0  # eV/atom, the single 0-0.1 window


def load():
    d = json.load(open(os.path.join(ANALYSIS, "surrogate_perf", "surrogate_perf.json")))
    return d["leaves"]


def window_metrics(rec):
    """(mae, sigma) at the 0-0.1 eV/atom window for one leaf."""
    for w in rec["windows"]:
        if w["window_lo_eV_per_atom"] == WINDOW_LO:
            return w["mae_eV_per_atom"], w["mean_sigma_eV_per_atom"]
    return None, None


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    leaves = load()

    # order leaves: group by P loading, then cell
    by_p = {p: [] for p in P_ORDER}
    for rec in leaves:
        by_p[rec["P_loading"]].append(rec)
    for p in P_ORDER:
        by_p[p].sort(key=lambda r: CELL_ORDER.index(r["cell"]))

    # x positions: 9 leaves, grouped by P loading
    x = list(range(9))
    labels = []
    mae_vals, sigma_vals, colors, hatches = [], [], [], []
    for p in P_ORDER:
        for rec in by_p[p]:
            mae, sigma = window_metrics(rec)
            labels.append(f"{rec['cell']}")
            mae_vals.append(mae)
            sigma_vals.append(sigma)
            colors.append(COLORS[p])
            hatches.append(CELL_HATCH[rec["cell"]])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2), layout="constrained")

    for ax, vals, ylab in ((ax1, mae_vals, r"MAE (eV/atom)"),
                               (ax2, sigma_vals, r"mean GPR $\sigma$ (eV/atom)")):
        bars = ax.bar(x, vals, color=colors, edgecolor="k", lw=0.6)
        for b, h in zip(bars, hatches):
            b.set_hatch(h)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_xlabel("cell expansion")
        ax.set_ylabel(ylab)
        ax.set_ylim(0, max(vals) * 1.15)
        ax.text(0.5, -0.22, "(a)" if ax is ax1 else "(b)",
                transform=ax.transAxes, ha="center", va="bottom", fontsize=12)

        # group separators between P-loading groups
        for gx in (2.5, 5.5):
            ax.axvline(gx + 0.5, color="k", lw=0.6, ls=":")

    # legend: P loading (color) + cell (hatch)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[p], edgecolor="k", lw=0.6,
                             label=p) for p in P_ORDER]
    handles += [plt.Rectangle((0, 0), 1, 1, facecolor="w", edgecolor="k", lw=0.6,
                              hatch=CELL_HATCH[c], label=f"{c}% cell")
                for c in CELL_ORDER]
    for ax in (ax1, ax2):
        ax.legend(handles=handles, frameon=False, fontsize=9, loc="upper right")

    out = os.path.join(OUTDIR, "fig_surrogate_perf.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)
    for p in P_ORDER:
        for rec in by_p[p]:
            mae, sigma = window_metrics(rec)
            print(f"  {rec['leaf']:<24} {rec['P_loading']:<4} {rec['cell']:<4} "
                  f"MAE@0-0.1={mae:.4f} sigma@0-0.1={sigma:.4f}")


if __name__ == "__main__":
    main()
