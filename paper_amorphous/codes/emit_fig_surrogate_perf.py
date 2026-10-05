#!/usr/bin/env python3
"""emit_fig_surrogate_perf.py — paper1 M-1e surrogate predictive-performance figure.

Serves M-1e (GPR surrogate predictive performance) from
analysis/surrogate_perf/surrogate_perf.json (produced by
codes/extract_surrogate_perf.py):

  (a) MAE vs relative energy — mean absolute error (eV/atom) binned across the
      0 -> 0.3 eV/atom range, line per P loading. Carries the headline: surrogate
      error grows with distance from the minimum and with P loading.
  (b) Spearman rho vs relative energy — rank correlation per window, line per P
      loading. Carries the selection-relevance claim: the surrogate ranks
      candidates well near the minimum (where selection matters).
  (c) Uncertainty calibration — mean |error| vs mean GPR sigma per window, line
      per P loading (1:1 dashed). Carries the claim that the GPR uncertainty
      tracks the error (validates the LCB acquisition, kappa=2).

Relative-energy axis: E_i - E_glob (eV/atom), where E_glob is the energy of the
leaf's global minimum (defined in the CLAIMS figure caption). Panels (a) and (b)
are scaled to 0 -> 0.3 eV/atom (the low-energy regime where selection matters).

Per-window R^2 is NOT plotted: within 0.1 eV/atom windows the energy variance is
tiny relative to the error, so R^2 is negative and uninformative (noted in
CLAIMS M-1e). MAE and Spearman rho are the meaningful metrics.

Writes analysis/figures/fig_surrogate_perf.png (paper-standard figure).

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/emit_fig_surrogate_perf.py
"""
from __future__ import annotations

__version__ = "1.0.1"

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

# representative +0-cell leaves, one per P loading
LEAVES = ["1_plus0cell/0_0P", "1_plus0cell/2_20P", "1_plus0cell/3_30P"]
COLORS = {"0P": "tab:blue", "20P": "tab:orange", "30P": "tab:green"}

XLABEL = r"$E_i - E_{\rm glob}$ (eV/atom)"
XMAX = 0.3  # eV/atom, low-energy regime


def load():
    d = json.load(open(os.path.join(ANALYSIS, "surrogate_perf", "surrogate_perf.json")))
    return {l["leaf"]: l for l in d["leaves"]}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    data = load()

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13.5, 4.2), layout="constrained")

    for leaf in LEAVES:
        rec = data[leaf]
        p = rec["P_loading"]
        c = COLORS[p]
        wins = rec["windows"]
        x = [(w["window_lo_eV_per_atom"] + w["window_hi_eV_per_atom"]) / 2 for w in wins]
        mae = [w["mae_eV_per_atom"] for w in wins]
        rho = [w["spearman_rho"] for w in wins]
        sig = [w["mean_sigma_eV_per_atom"] for w in wins]
        abserr = [w["mean_abs_err_eV_per_atom"] for w in wins]

        # (a) MAE vs relative energy
        ax1.plot(x, mae, color=c, lw=1.6, marker="o", ms=3, label=p)
        # (b) Spearman rho vs relative energy
        ax2.plot(x, rho, color=c, lw=1.6, marker="o", ms=3, label=p)
        # (c) uncertainty calibration: mean |error| vs mean sigma
        ax3.plot(sig, abserr, color=c, lw=1.6, marker="o", ms=3, label=p)

    ax1.set_xlabel(XLABEL)
    ax1.set_ylabel(r"MAE (eV/atom)")
    ax1.set_xlim(0, XMAX)
    ax1.text(0.5, -0.22, "(a)", transform=ax1.transAxes, ha="center", va="bottom", fontsize=12)

    ax2.set_xlabel(XLABEL)
    ax2.set_ylabel(r"Spearman $\rho$")
    ax2.set_xlim(0, XMAX)
    ax2.set_ylim(-1.05, 1.05)
    ax2.axhline(0, color="k", lw=0.8, ls=":")
    ax2.text(0.5, -0.22, "(b)", transform=ax2.transAxes, ha="center", va="bottom", fontsize=12)

    ax3.set_xlabel(r"mean GPR $\sigma$ (eV/atom)")
    ax3.set_ylabel(r"mean $|$error$|$ (eV/atom)")
    lim = max(ax3.get_xlim()[1], ax3.get_ylim()[1])
    ax3.plot([0, lim], [0, lim], color="k", lw=0.8, ls="--", label="1:1")
    ax3.set_xlim(0, lim)
    ax3.set_ylim(0, lim)
    ax3.text(0.5, -0.22, "(c)", transform=ax3.transAxes, ha="center", va="bottom", fontsize=12)

    for ax in (ax1, ax2, ax3):
        ax.legend(frameon=False, fontsize=10, loc="best")

    out = os.path.join(OUTDIR, "fig_surrogate_perf.png")
    fig.savefig(out)
    plt.close(fig)
    print("figures ->", out)
    for leaf in LEAVES:
        o = data[leaf]["overall_0_1_eV_per_atom"]
        print(f"  {leaf}: MAE={o['mae_eV_per_atom']:.4f} R2={o['r2']:.3f} rho={o['spearman_rho']:.3f}")


if __name__ == "__main__":
    main()
