#!/usr/bin/env python3
"""
Run the Stage-2 landscape and Stage-3 probability analyses on EVERY threshold's
filtered (distinct) structure set from the novel filter.

For each threshold `thr_<v>/` under --outdir:
  1. Landscape: PCA on AGOX Fingerprint descriptors (top eigenvector) vs
     per-atom relative energy, + KDE state-density panel  -> conf_space.png
  2. Probability: Boltzmann P(E) = rho(E)*exp(-dE/kT)/Z at several temperatures
     -> binding_probability_vs_temperature.png

Structures are read from thr_<v>/novel_structures/ (rank-ordered .xsf files);
their energies come from thr_<v>/novel_structures_summary.csv (xsf files carry
no energy). Outputs go to <--outdir>/analysis/thr_<v>/.

This is a per-threshold loop over the SAME logic as
/.../_analysist/run_stage2_landscape.py and run_stage3_probability.py, reusing
their plotting function `plot_structure_landscape` and the same style.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py [options]
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# --- agox / ase / analysist paths ---------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ANALYSIST = "/home/think/Desktop/research/_analysist"
for _p in (_HERE, _ANALYSIST, os.path.join(_ANALYSIST, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ase.io import read
from agox.models.descriptors.fingerprint import Fingerprint
from scripts.plot_structure_landscape import plot_structure_landscape

# ---------------------------------------------------------------------------
# Shared plotting style (identical to the Stage-2/Stage-3 reference scripts)
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

# Stage-3 temperatures / colours (from the reference script)
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']

E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'


# ---------------------------------------------------------------------------
def load_threshold_set(thr_dir: str):
    """Load structures (rank-ordered .xsf) + energies (summary CSV) for one threshold.

    Returns
    -------
    structures : list of ase.Atoms, ordered by rank (lowest energy first)
    energies   : np.ndarray, same length/order, absolute potential energy (eV)
    """
    ns_dir = os.path.join(thr_dir, "novel_structures")
    struct_files = sorted(glob.glob(os.path.join(ns_dir, "novel_*.xsf")))
    if not struct_files:
        raise FileNotFoundError(f"No novel_*.xsf in {ns_dir}")

    # order by rank parsed from filename
    def _rank(p):
        b = os.path.basename(p)            # novel_0000_E-436.909.xsf
        return int(b.split("_")[1])
    struct_files.sort(key=_rank)

    structures = [read(p) for p in struct_files]

    # energies from the summary CSV (rank,dataset_index,energy_eV,source,min_dist)
    csv_path = os.path.join(thr_dir, "novel_structures_summary.csv")
    energies = {}
    with open(csv_path) as fh:
        next(fh)  # header
        for line in fh:
            parts = line.strip().split(",")
            energies[int(parts[0])] = float(parts[2])   # rank -> energy_eV

    e_arr = np.array([energies[r] for r in range(len(structures))], dtype=float)
    return structures, e_arr


# ---------------------------------------------------------------------------
# Landscape (Stage 2)
# ---------------------------------------------------------------------------
def make_landscape(structures, energies, save_path, e_limit, normalize_density=False):
    """Replicates run_stage2_landscape.py on a structure set."""
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms      # per-atom relative energy

    # PCA on fingerprint descriptors (top eigenvector of covariance)
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    os.makedirs(save_path, exist_ok=True)
    fig = plot_structure_landscape(
        X_eigen, rel, z_data=None,
        save_path=save_path,
        animate_scatter=False,
        figsize=(3, 3),
        wspace=0.1,
        fontsize=10,
        e_limit=e_limit,
        fill_density=True,
        dens_line_weight=0.9,
        show_limits=False,
        custom_peak_labels=None,
        cmap='PuBu',
        show_colorbar=False,
        cbar_pad=0.02,
        z_limit=(5.85, 0, 5),
        black_seed_zero=True,
        s=5,
        normalize_density=normalize_density,
        density_x_label='State Density\n(a.u.)' if normalize_density else 'State Density\n(config./eV)',
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {save_path}/conf_space.png")


# ---------------------------------------------------------------------------
# Probability (Stage 3)
# ---------------------------------------------------------------------------
def calculate_boltzmann_probs(energies, kde_model, T):
    """Pi = [rho(E)*exp(-dE/kbT)] / Z, normalised to a 0-1 peak (reference logic)."""
    kb = 8.6173e-5  # eV/K
    rho_i = kde_model.evaluate(energies) + 1e-15
    relative_e = energies - np.min(energies)
    weights = np.exp(-relative_e / (kb * T))
    numerator = rho_i * weights
    Z = np.sum(numerator)
    probs = numerator / Z
    return probs / probs.max()


def make_probability(energies, save_path, e_max=None):
    """Replicates run_stage3_probability.py on a structure set."""
    rel = (energies - energies.min()) / len(energies)   # per-atom relative
    kde = gaussian_kde(rel)

    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(rel, kde, T)
        ax.scatter(rel, probs, color=color, s=5, alpha=0.5,
                   edgecolors='none', label=f'{T} K')

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E)')
    ax.legend(frameon=False, loc='upper right')
    ax.set_ylim(0, 1 + 0.05)
    xmax = e_max if e_max is not None else rel.max() + 0.05
    ax.set_xlim(0, xmax)
    plt.tight_layout()

    os.makedirs(save_path, exist_ok=True)
    out_path = os.path.join(save_path, 'binding_probability_vs_temperature.png')
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability saved to {out_path}")


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default=os.path.join(_HERE, "novel_output"),
                   help="Run output dir containing thr_<v>/ folders (default novel_output)")
    p.add_argument("--prefix", default="thr_",
                   help="Folder-name prefix to discover (e.g. 'thr_' for novel, "
                        "'force_' for force-filtered sets). Default 'thr_'.")
    p.add_argument("--thresholds", default=None,
                   help="Comma-separated thresholds to analyse (folder name suffixes, "
                        "e.g. '0.25,1,2'). Default: all <prefix>* folders found.")
    p.add_argument("--e-max", type=float, default=None,
                   help="Common upper energy limit (eV/atom) for all landscape & "
                        "probability plots. If omitted, each threshold uses its own max.")
    p.add_argument("--normalize-density", action="store_true",
                   help="Normalize the landscape state-density panel to 0-1.")
    args = p.parse_args()

    if args.thresholds:
        thr_names = [f"{args.prefix}{v.strip()}" for v in args.thresholds.split(",") if v.strip()]
    else:
        thr_names = sorted(
            d for d in os.listdir(args.outdir)
            if d.startswith(args.prefix) and os.path.isdir(os.path.join(args.outdir, d))
        )
    if not thr_names:
        raise SystemExit(f"No {args.prefix}* folders under {args.outdir!r}")

    print(f"Analysing {len(thr_names)} thresholds: {thr_names}")

    # common energy axis if requested / default per-threshold
    for name in thr_names:
        thr_dir = os.path.join(args.outdir, name)
        print(f"\n=== {name} ===")
        structures, energies = load_threshold_set(thr_dir)
        num_atoms = len(structures[0])
        rel_max = (energies.max() - energies.min()) / num_atoms
        print(f"  {len(structures)} structures, {num_atoms} atoms, "
              f"rel-E max = {rel_max:.4f} eV/atom")

        e_limit = (0.0 - 0.1, (args.e_max if args.e_max is not None else rel_max) + 0.1, 5)
        save_path = os.path.join(args.outdir, "analysis", name)

        make_landscape(structures, energies, save_path, e_limit,
                       normalize_density=args.normalize_density)
        make_probability(energies, save_path, e_max=args.e_max)

    print("\nDone.")


if __name__ == "__main__":
    main()
