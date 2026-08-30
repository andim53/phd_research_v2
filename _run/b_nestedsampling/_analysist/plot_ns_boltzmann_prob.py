#!/usr/bin/env python3
"""
Plot the Boltzmann probability P(E) vs per-atom relative energy for a
temperature-free nested-sampling (NS) run, using the NS result directly.

For each temperature T (100, 200, 300, 500, 1000 K) the NS Boltzmann
probability of each discarded sample is

    P_i(T) = w_i * exp(-beta*(E_i - E_ref)) / Z(T)

where:
  - w_i   = prior_weight (the NS prior-volume shell weight, from samples.csv),
  - beta  = 1/(k_B T),
  - E_ref = min sample energy (per-atom relative energy = (E - E_ref)/n_atoms),
  - Z(T)  = sum_i w_i * exp(-beta*(E_i - E_ref))  (partition function).

This is the physically correct NS Boltzmann probability (it uses the NS prior
weights directly, rather than a KDE of the energies). Energies are plotted as
per-atom relative energy (E - E_ref)/n_atoms, matching the other analyses.

Usage (needs numpy + scipy + matplotlib + agox_v2 for load_samples):
  /home/think/miniconda3/envs/agox_v2/bin/python plot_ns_boltzmann_prob.py \
      --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outdir  b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outname binding_probability_vs_temperature.png \
      --n-atoms 75
"""

from __future__ import annotations

__version__ = "1.0.1"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

    fig, ax = plt.subplots(figsize=(5, 4))
    # colors: a perceptually ordered set for the temperatures
    colors = ["#0d0887", "#47039f", "#7301a8", "#9c176d", "#bd3752",
              "#d8546a", "#ed7953", "#fb9f4a", "#fdca42", "#f0f928"]

    print("=" * 60)
    print("NS Boltzmann probability (prior-weight weighted)")
    print("=" * 60)
    for i, T in enumerate(args.temperatures):
        beta = 1.0 / (K_B * T)
        log_w = np.log(np.maximum(Ws, 1e-300))
        log_num = log_w - beta * (Es - E_ref)          # log of numerator
        log_Z = np.log(np.sum(np.exp(log_num)))        # log partition function
        probs = np.exp(log_num - log_Z)                # P_i(T), normalized
        # Peak-normalize each curve to its own max (=1) so it is visible on a 0-1 axis
        # (raw NS Boltzmann probabilities are tiny ~1e-2; this matches the reference
        # Stage 3 which divides by probs.max()).
        probs_plot = probs / probs.max()
        order = np.argsort(rel)
        ax.plot(rel[order], probs_plot[order], color=colors[i % len(colors)],
                lw=1.6, label=f"{T} K")
        print(f"  T={T:6.1f} K  Z={np.exp(log_Z):.4e}  max P={probs.max():.3e}")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E) (peak-normalized)")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, rel.max() + 0.02)
    ax.legend(frameon=False, loc="upper right", fontsize=9)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")
    print(f"  n_atoms = {args.n_atoms}; temperatures = {args.temperatures}")


if __name__ == "__main__":
    main()
