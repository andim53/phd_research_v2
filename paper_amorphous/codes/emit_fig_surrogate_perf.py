#!/usr/bin/env python3
"""emit_fig_surrogate_perf.py — paper1 M-1e surrogate predictive-performance figure.

Serves M-1e (GPR surrogate predictive performance) from
analysis/surrogate_perf/surrogate_perf.json (produced by
codes/extract_surrogate_perf.py).

Two panels, one line per leaf (all 9 leaves), colored by P loading with a
distinct line style per cell expansion (+0/+3/+5), x-axis 0 -> 0.3 eV/atom:

  (a) MAE vs E_i - E_glob — mean absolute error (eV/atom) per 0.1 eV/atom
      window, line per leaf. Carries the headline: surrogate error grows with
      distance from the minimum and with P loading.
  (b) GPR uncertainty vs E_i - E_glob — mean GPR sigma (eV/atom) per window,
      line per leaf. Carries the predicted-uncertainty story (what the LCB
      acquisition uses). Comparing (a) and (b) shows whether the predicted
      uncertainty tracks the actual error.

Relative-energy axis: E_i - E_glob (eV/atom), where E_glob is the energy of the
leaf's global minimum (defined in the CLAIMS figure caption).

Writes analysis/figures/fig_surrogate_perf.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_surrogate_perf.py
"""
from __future__ import annotations

__version__ = "2.1.0"

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
COLORS = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}
# line style per cell expansion, so the 3 leaves of a P loading are distinct
CELL_STYLE = {"+0": "-", "+3": "--", "+5": ":"}

XLABEL = r"$E_i - E_{\rm glob}$ (eV/atom)"
XMAX = 0.3  # eV/atom, low-energy regime


def load():
    d = json.load(open(os.path.join(ANALYSIS, "surrogate_perf", "surrogate_perf.json")))
    return d["leaves"]


def leaf_series(rec):
    """Per-window (x, mae, sigma) for one leaf, restricted to x < XMAX."""
    x, mae, sigma = [], [], []
    for w in rec["windows"]:
        lo = w["window_lo_eV_per_atom"]
        if lo >= XMAX:
            continue
        x.append(lo + 0.05)
        mae.append(w["mae_eV_per_atom"])
        sigma.append(w["mean_sigma_eV_per_atom"])
    return x, mae, sigma


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    leaves = load()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2), layout="constrained")

    for rec in leaves:
        p = rec["P_loading"]
        cell = rec["cell"]
        c = COLORS[p]
        ls = CELL_STYLE[cell]
        x, mae, sigma = leaf_series(rec)
        ax1.plot(x, mae, color=c, ls=ls, lw=1.4, marker="o", ms=3)
        ax2.plot(x, sigma, color=c, ls=ls, lw=1.4, marker="o", ms=3)

    ax1.set_xlabel(XLABEL)
    ax1.set_ylabel(r"MAE (eV/atom)")
    ax1.set_xlim(0, XMAX)
    ax1.text(0.5, -0.22, "(a)", transform=ax1.transAxes, ha="center", va="bottom", fontsize=12)

    ax2.set_xlabel(XLABEL)
    ax2.set_ylabel(r"mean GPR $\sigma$ (eV/atom)")
    ax2.set_xlim(0, XMAX)
    ax2.text(0.5, -0.22, "(b)", transform=ax2.transAxes, ha="center", va="bottom", fontsize=12)

    # legend: P loading (color) + cell (line style)
    for ax in (ax1, ax2):
        handles = [plt.Line2D([0], [0], color=COLORS[p], lw=1.6, label=p) for p in P_ORDER]
        handles += [plt.Line2D([0], [0], color="k", ls=ls, lw=1.4, label=f"{cell}% cell")
                    for cell, ls in CELL_STYLE.items()]
        ax.legend(handles=handles, frameon=False, fontsize=9, loc="best")

    out = os.path.join(OUTDIR, "fig_surrogate_perf.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)
    for rec in leaves:
        x, mae, sigma = leaf_series(rec)
        print(f"  {rec['leaf']:<24} {rec['P_loading']:<4} {rec['cell']:<4} "
              f"MAE@0-0.1={mae[0]:.4f} sigma@0-0.1={sigma[0]:.4f}")


if __name__ == "__main__":
    main()
