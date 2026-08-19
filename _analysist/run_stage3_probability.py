#!/usr/bin/env python3
"""
Stage 3 (standalone): Boltzmann probability (statistical mechanics) for a single index.

Uses the per-atom relative-energy KDE + Boltzmann formulation from
codes/76_plot_probability / the tutorial reference:

    Pi = [rho(E) * exp(-dE / kb T)] / Z

Reads the combined trajectory produced by Stage 1:
  0_analy/idx_N/1_xsf_traj/traj_N.traj
and writes:
  0_analy/idx_N/2_im/binding_probability_vs_temperature.png

Usage:
  /home/miniconda3/envs/agox_v2/bin/python run_stage3_probability.py --idx 22

Environment: agox_v2 (ASE 3.25.0, AGOX 3.10.2, scipy, matplotlib)
"""
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ase.io import read
from scipy.stats import gaussian_kde

# ---------------------------------------------------------------------------
OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')
IM_DIR = '2_im'
XSF_TRAJ_DIR = '1_xsf_traj'

# Temperatures and colours (matches the tutorial reference loop)
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
# plasma-like colour sequence (mirrors codes/76 style)
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']

# Energy axis label — matches the researcher style used everywhere
E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'


# ---------------------------------------------------------------------------
def calculate_boltzmann_probs(energies, kde_model, T):
    """
    Calculates normalized Pi = [rho(E) * exp(-dE/kbT)] / Z

    Parameters
    ----------
    energies : ndarray
        Per-atom relative energies (E_i - E_glob) in eV/atom.
    kde_model : scipy.stats.gaussian_kde
        Fitted KDE over the same energy grid.
    T : float
        Temperature in Kelvin.

    Returns
    -------
    probs : ndarray
        Normalized probabilities Pi on the same grid as `energies`.
    """
    kb = 8.6173e-5  # eV/K

    # Adding epsilon to avoid zero
    rho_i = kde_model.evaluate(energies) + 1e-15

    # 2. Calculate Boltzmann Weights
    relative_e = energies - np.min(energies)
    exponent = -relative_e / (kb * T)
    weights = np.exp(exponent)

    # 3. Calculate Partition Function Z
    # Z must be the sum of (Density * Weights)
    numerator = rho_i * weights
    Z = np.sum(numerator)

    # 4. Return Normalized Probabilities (sum to 1 via Z), then scale
    #    to a 0-1 range so the y-axis spans 1 (peak) to 0.
    probs = numerator / Z
    return probs / probs.max()


# ---------------------------------------------------------------------------
# Plotting style for Stage 3 figures — same rcParams used by the main
# runner (codes/07 + run_analysis_indices).  Inherits the Stage 2 style
# so every figure matches.
# ---------------------------------------------------------------------------
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1.0,
    'axes.edgecolor': 'black',
    'axes.facecolor': 'white',
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    'axes.grid': False,
    'figure.autolayout': True,
    'figure.dpi': 300,
})


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 3: Boltzmann probability analysis for one AGOX index")
    parser.add_argument('--idx', type=int, required=True,
                        help="Simulation index (e.g. 22)")
    parser.add_argument('--e-max', type=float, default=None,
                        help="Custom upper limit for the energy (x) axis in eV/atom. "
                             "If omitted, uses the data maximum + 0.05.")
    args = parser.parse_args()
    idx = args.idx

    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    traj_path = os.path.join(dir_out, XSF_TRAJ_DIR, f'traj_{idx}.traj')

    if not os.path.exists(traj_path):
        print(f"WARNING: {traj_path} missing — run Stage 1 first.")
        sys.exit(0)

    print(f"Stage 3 — index {idx}")
    print(f"  reading : {traj_path}")

    structures = read(traj_path, index=':')

    raw_energies = [atoms.get_potential_energy() for atoms in structures]
    num_atoms = len(structures[0])

    # Defining U = E_i - E_glob (normalized per atom)
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
    kde = gaussian_kde(energies)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)

    # 1. Plot Boltzmann Probabilities for each Temp
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(energies, kde, T)

        peak_idx = np.argmax(probs)
        peak_energy = energies[peak_idx]

        note_label = f'{T} K'
        ax.scatter(energies, probs, color=color, s=5, alpha=0.5,
                   edgecolors='none', label=note_label)

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E)')
    ax.legend(frameon=False, loc='upper right')
    ax.set_ylim(0, 1 + 0.05)
    if args.e_max is not None:
        ax.set_xlim(0, args.e_max)
    else:
        ax.set_xlim(0, energies.max() + 0.05)
    plt.tight_layout()

    out_path = os.path.join(dir_out, IM_DIR,
                            'binding_probability_vs_temperature.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


if __name__ == '__main__':
    main()
