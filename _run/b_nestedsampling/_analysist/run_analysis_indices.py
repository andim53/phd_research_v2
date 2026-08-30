#!/usr/bin/env python3
"""
Unified AGOX analysis for the GPR+LCB-only dataset (e.g. b11 boron seed DBs).

Adapted from `_archive/_analysist/run_analysis_indices.py` for the b_nestedsampling
project's flat dataset layout. Instead of an index/folder map + Stage-1 DB
processing, this loads ALL seed databases directly (like main.py's load_all_seeds)
and runs the same analyses:

  Stage 2 — Landscape analysis & evaluation (scripts/plot_structure_landscape.py):
            PCA landscape (Fingerprint PC1) + per-atom KDE state density.
  Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z), vs T.

Produces, under <outdir>:
  conf_space.png                          (Stage 2 landscape + state density)
  binding_probability_vs_temperature.png  (Stage 3 Boltzmann P(T))

Usage (needs agox_v2 conda env for AGOX Fingerprint + ASE + scipy):
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
      --dataset b11_boron_walk_emax04_exclworst_noxsf_novelty/dataset \
      --outdir b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_indices \
      [--e-max 0.8] [--normalize-density]
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from scipy.stats import gaussian_kde

# --- paths: make the self-contained scripts/ importable ----------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from scripts.plot_structure_landscape import plot_structure_landscape

# ---------------------------------------------------------------------------
# Plotting style — same rcParams as the reference pipeline
# ---------------------------------------------------------------------------
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

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"
E_LIMIT_DEFAULT = (0.0 - 0.1, 1.5 + 0.1, 5)

# --- Temperatures & colours (mirrors the reference Stage 3) -----------------
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


# ---------------------------------------------------------------------------
# Data loading — all seed DBs -> structures + DFT energies
# ---------------------------------------------------------------------------
def load_all_seeds(dataset_dir: str):
    """Load every structure/energy from dataset/seed_*/1_db/db_*.db."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    structures, energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        print(f"  {os.path.relpath(p)}: {len(traj)} structures")
    energies = np.asarray(energies, dtype=float)
    return structures, energies


# ---------------------------------------------------------------------------
# Stage 2 — Landscape analysis (PCA + state density)
# ---------------------------------------------------------------------------
def step2_landscape(structures, energies, outdir, e_max=None, normalize_density=False):
    print("\n[STAGE 2] Landscape analysis")
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms

    # PCA via Fingerprint descriptors
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    os.makedirs(outdir, exist_ok=True)

    if e_max is not None:
        e_limit = (0.0 - 0.1, e_max, 5)
    else:
        e_limit = E_LIMIT_DEFAULT

    density_x_label = ("State Density\n(a.u.)" if normalize_density
                       else "State Density\n(config./eV)")

    fig = plot_structure_landscape(
        X_eigen, rel, z_data=None,
        save_path=outdir,
        animate_scatter=False,
        figsize=(3, 3),
        wspace=0.1,
        fontsize=10,
        e_limit=e_limit,
        fill_density=True,
        dens_line_weight=0.9,
        show_limits=False,
        custom_peak_labels=None,
        cmap="PuBu",
        show_colorbar=False,
        cbar_pad=0.02,
        z_limit=(5.85, 0, 5),
        black_seed_zero=True,
        s=15,
        normalize_density=normalize_density,
        density_x_label=density_x_label,
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {outdir}/conf_space.png")


# ---------------------------------------------------------------------------
# Stage 3 — Boltzmann probability vs temperature
# ---------------------------------------------------------------------------
def calculate_boltzmann_probs(energies, kde_model, T):
    """Normalized Pi = rho(E)*exp(-dE/kbT)/Z, then scaled so peak = 1."""
    kb = 8.6173e-5  # eV/K
    rho_i = kde_model.evaluate(energies) + 1e-15
    relative_e = energies - np.min(energies)
    weights = np.exp(-relative_e / (kb * T))
    numerator = rho_i * weights
    Z = np.sum(numerator)
    probs = numerator / Z
    return probs / probs.max()


def step3_probability(structures, energies, outdir, e_max=None):
    print("\n[STAGE 3] Boltzmann probability analysis")
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms
    kde = gaussian_kde(rel)

    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(rel, kde, T)
        ax.scatter(rel, probs, color=color, s=15, alpha=0.5,
                   edgecolors="none", label=f"{T} K")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(0, 1 + 0.05)
    ax.set_xlim(0, e_max if e_max is not None else rel.max() + 0.05)
    plt.tight_layout()

    out_path = os.path.join(outdir, "binding_probability_vs_temperature.png")
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AGOX analysis (Stage 2 landscape + Stage 3 Boltzmann P(T)) "
                    "for the GPR+LCB-only dataset (e.g. b11 boron seed DBs)")
    parser.add_argument("--dataset", required=True,
                        help="path to the dataset dir containing seed_*/1_db/db_*.db")
    parser.add_argument("--outdir", required=True,
                        help="output dir for the analysis figures")
    parser.add_argument("--e-max", type=float, default=None,
                        help="custom upper energy limit (eV/atom) for the Stage 2 "
                             "landscape and Stage 3 probability plots. Default = "
                             "each stage's default.")
    parser.add_argument("--normalize-density", action="store_true",
                        help="normalize the Stage 2 state-density panel to [0,1]")
    args = parser.parse_args()

    print("=" * 70)
    print("AGOX ANALYSIS PIPELINE (GPR+LCB-only dataset)")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    if args.e_max is not None:
        print(f"e-max  : {args.e_max} eV/atom")
    if args.normalize_density:
        print("normalize-density: True")
    print("=" * 70)

    structures, energies = load_all_seeds(args.dataset)
    print(f"\nTotal: {len(structures)} structures, {len(structures[0])} atoms each")

    os.makedirs(args.outdir, exist_ok=True)
    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max)

    print(f"\nDONE. Outputs under: {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
