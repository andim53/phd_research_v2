#!/usr/bin/env python3
"""
Plot the Boltzmann probability P(E) vs per-atom relative energy for a
temperature-free nested-sampling (NS) run, using the NS result.

For each temperature T (100, 200, 300, 500, 1000 K) the probability on a smooth
energy grid E is

    P(E, T) = g(E) * exp(-beta*(E - E_ref)) / Z(T)

where:
  - g(E)   = the KDE-smoothed NS state density (prior-weight-weighted gaussian
             KDE of the samples.csv energies), same as the NS g(E) smoothed with
             KDE in compare_state_density_gE.py,
  - beta   = 1/(k_B T),
  - E_ref  = min sample energy (per-atom relative energy = (E - E_ref)/n_atoms),
  - Z(T)   = sum_E g(E) * exp(-beta*(E - E_ref))  (partition function from g(E)).

This multiplies by g(E) and divides by the total Z from g(E), matching the
reference `analysis_indices/binding_probability_vs_temperature.png` (which uses
rho(E) = gaussian KDE) but with the NS KDE-smoothed g(E) as rho. Energies are
plotted as per-atom relative energy (E - E_ref)/n_atoms.

Usage (needs numpy + scipy + matplotlib + agox_v2 for load_samples):
  /home/think/miniconda3/envs/agox_v2/bin/python plot_ns_boltzmann_prob.py \
      --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outdir  b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outname binding_probability_vs_temperature.png \
      --n-atoms 75
"""

from __future__ import annotations

__version__ = "1.1.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

import analyze_tfree_outputs as ato  # reuse load_samples

# --- Plotting style: same rcParams as the reference pipeline ---
plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif",
    "axes.linewidth": 1.0,
    "axes.edgecolor": "black",
    "axes.facecolor": "white",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "axes.grid": False,
    "figure.autolayout": True,
    "figure.dpi": 300,
})

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"   # matches the other analyses
K_B = 8.617333262e-5                       # eV/K


def main():
    p = argparse.ArgumentParser(
        description="Plot NS Boltzmann probability P(E) vs relative energy at several T")
    p.add_argument("--ns-output", required=True,
                   help="ns_output dir containing samples.csv (the NS run's output)")
    p.add_argument("--outdir", required=True,
                   help="output dir for the PNG")
    p.add_argument("--outname", default="binding_probability_vs_temperature.png",
                   help="output filename (default binding_probability_vs_temperature.png)")
    p.add_argument("--n-atoms", type=int, default=75,
                   help="atoms per structure, for the per-atom relative energy (eV/atom). "
                        "Default 75 (Fe/MgO).")
    p.add_argument("--temperatures", type=float, nargs="+",
                   default=[100, 200, 300, 500, 1000],
                   help="temperatures (K) to plot. Default 100 200 300 500 1000.")
    args = p.parse_args()

    # --- load NS samples (energy_eV + prior_weight) ---
    iters, Es, Ws = ato.load_samples(os.path.join(args.ns_output, "samples.csv"))
    print(f"  NS samples: {Es.size}")

    E_ref = Es.min()
    rel = (Es - E_ref) / args.n_atoms           # per-atom relative energy (eV/atom)

    # --- KDE-smoothed NS state density g(E) (prior-weight-weighted) ---
    ns_kde = gaussian_kde(rel, weights=Ws)       # same as the NS g(E) KDE in compare_state_density_gE.py
    grid = np.linspace(0, rel.max() + 0.02, 400)
    gE = ns_kde.evaluate(grid)                   # config./eV

    fig, ax = plt.subplots(figsize=(5, 4))
    # colors: a perceptually ordered set for the temperatures
    colors = ["#0d0887", "#47039f", "#7301a8", "#9c176d", "#bd3752",
              "#d8546a", "#ed7953", "#fb9f4a", "#fdca42", "#f0f928"]

    print("=" * 60)
    print("NS Boltzmann probability (g(E) * exp(-beta*E) / Z from g(E)))")
    print("=" * 60)
    for i, T in enumerate(args.temperatures):
        beta = 1.0 / (K_B * T)
        # P(E,T) = g(E)*exp(-beta*(E-E_ref))/Z, Z = sum_E g(E)*exp(-beta*(E-E_ref))
        log_num = np.log(np.maximum(gE, 1e-300)) - beta * (grid - grid.min())
        log_Z = np.log(np.sum(np.exp(log_num)))
        probs = np.exp(log_num - log_Z)          # P(E,T), normalized over the grid
        # Peak-normalize each curve to its own max (=1) for visibility (like the reference)
        probs_plot = probs / probs.max()
        ax.plot(grid, probs_plot, color=colors[i % len(colors)],
                lw=1.6, label=f"{T} K")
        print(f"  T={T:6.1f} K  Z={np.exp(log_Z):.4e}  max P={probs.max():.3e}")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E) (peak-normalized)")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, grid.max())
    ax.legend(frameon=False, loc="upper right", fontsize=9)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")
    print(f"  n_atoms = {args.n_atoms}; temperatures = {args.temperatures}")


if __name__ == "__main__":
    main()
