#!/usr/bin/env python3
"""emit_fig_surrogate_perf.py — paper1 M-1e surrogate predictive-performance figure.

Serves M-1e (GPR surrogate predictive performance) from
analysis/surrogate_perf/surrogate_perf.json (produced by
codes/extract_surrogate_perf.py).

Two panels, all 9 leaves pooled per P loading (n-weighted across the +0/+3/+5
cells), x-axis 0 -> 0.3 eV/atom:

  (a) MAE vs E_i - E_glob — mean absolute error (eV/atom) per 0.1 eV/atom
      window, line per P loading. Carries the headline: surrogate error grows
      with distance from the minimum and with P loading.
  (b) GPR uncertainty vs E_i - E_glob — mean GPR sigma (eV/atom) per window,
      line per P loading. Carries the predicted-uncertainty story (what the LCB
      acquisition uses). Comparing (a) and (b) shows whether the predicted
      uncertainty tracks the actual error.

Relative-energy axis: E_i - E_glob (eV/atom), where E_glob is the energy of the
leaf's global minimum (defined in the CLAIMS figure caption).

Writes analysis/figures/fig_surrogate_perf.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_surrogate_perf.py
"""
from __future__ import annotations

__version__ = "2.0.0"

import json
import os
from collections import defaultdict

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

XLABEL = r"$E_i - E_{\rm glob}$ (eV/atom)"
XMAX = 0.3  # eV/atom, low-energy regime


def load():
    d = json.load(open(os.path.join(ANALYSIS, "surrogate_perf", "surrogate_perf.json")))
    return d["leaves"]


def pool_by_p(leaves):
    """n-weighted pool of per-window MAE and GPR sigma across all leaves of a P loading."""
    # by_p[P][window_lo] = [n, mae_sum, sigma_sum]
    by_p = {p: defaultdict(lambda: [0, 0.0, 0.0]) for p in P_ORDER}
    for l in leaves:
        p = l["P_loading"]
        for w in l["windows"]:
            lo = w["window_lo_eV_per_atom"]
            if lo >= XMAX:
                continue
            acc = by_p[p][lo]
            acc[0] += w["n"]
            acc[1] += w["n"] * w["mae_eV_per_atom"]
            acc[2] += w["n"] * w["mean_sigma_eV_per_atom"]
    out = {}
    for p in P_ORDER:
        wins = sorted(by_p[p].keys())
        out[p] = {
            "x": [lo + 0.05 for lo in wins],
            "mae": [by_p[p][lo][1] / by_p[p][lo][0] for lo in wins],
            "sigma": [by_p[p][lo][2] / by_p[p][lo][0] for lo in wins],
            "n": [by_p[p][lo][0] for lo in wins],
        }
    return out


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    leaves = load()
    pooled = pool_by_p(leaves)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2), layout="constrained")

    for p in P_ORDER:
        c = COLORS[p]
        d = pooled[p]
        ax1.plot(d["x"], d["mae"], color=c, lw=1.6, marker="o", ms=3, label=p)
        ax2.plot(d["x"], d["sigma"], color=c, lw=1.6, marker="o", ms=3, label=p)

    ax1.set_xlabel(XLABEL)
    ax1.set_ylabel(r"MAE (eV/atom)")
    ax1.set_xlim(0, XMAX)
    ax1.text(0.5, -0.22, "(a)", transform=ax1.transAxes, ha="center", va="bottom", fontsize=12)

    ax2.set_xlabel(XLABEL)
    ax2.set_ylabel(r"mean GPR $\sigma$ (eV/atom)")
    ax2.set_xlim(0, XMAX)
    ax2.text(0.5, -0.22, "(b)", transform=ax2.transAxes, ha="center", va="bottom", fontsize=12)

    for ax in (ax1, ax2):
        ax.legend(frameon=False, fontsize=10, loc="best")

    out = os.path.join(OUTDIR, "fig_surrogate_perf.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)
    for p in P_ORDER:
        d = pooled[p]
        print(f"  {p}: n={sum(d['n']):,}  "
              f"MAE@0-0.1={d['mae'][0]:.4f} sigma@0-0.1={d['sigma'][0]:.4f}  "
              f"MAE@0.2-0.3={d['mae'][-1]:.4f} sigma@0.2-0.3={d['sigma'][-1]:.4f}")


if __name__ == "__main__":
    main()
