#!/usr/bin/env python3
"""
Unified AGOX Analysis Pipeline for selected simulation indices.

Mirrors the sibling analysis runner at
/home/think/Desktop/research/_analysist/run_analysis_indices.py, adapted to
project 10_lcbnovel. This copy is self-contained: it imports only the local
scripts/ dependencies (process_database.py, plot_structure_landscape.py,
calculate_relative_energy.py) copied next to it.

Applies, in order:
  Stage 1 — Database processing (scripts/process_database.py)
  Stage 2 — Landscape analysis & evaluation (scripts/plot_structure_landscape.py)
  Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z)

Scoped to the Fe/MgO Novelty-LCB heavy runs in this project:
  idx 71 -> 1_result/71_novel_runEWindow/output
  idx 72 -> 1_result/72_novel_AutoGlob_1eVperAtomAboveGlob/output
(each contains seed_3/1_db/db_3.db, matching the reference seed_*/1_db layout).

The EMT benchmark dirs 73/74 have a flat benchmark_results/ layout that does NOT
fit the seed_*/1_db structure, so they are intentionally excluded here.

All arguments from the individual run_stage{1,2,3}.py scripts are supported:
  --e-max         : custom energy upper limit (eV/atom) for Stage 2 & Stage 3
  --normalize-density : normalize state-density panel to [0,1] (Stage 2 only)

Group:
  novel_lcb_femgo : 71, 72

Run from /home/think/Desktop/research/_run/10_lcbnovel/_analysist with the
agox_v2 conda env:
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices novel_lcb_femgo --e-max 0.8
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --idx 71 --normalize-density
"""
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'scripts'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from ase.io import read
from scripts.process_database import process_database
from scripts.plot_structure_landscape import plot_structure_landscape
from scipy.stats import gaussian_kde

# ---------------------------------------------------------------------------
# Paths — resolved relative to this script's location
# ---------------------------------------------------------------------------
RESULT_DIR = os.path.join(SCRIPT_DIR, '1_result')
OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')
IM_DIR = '2_im'
XSF_TRAJ_DIR = '1_xsf_traj'
XSF_DIR = '1_xsf'

# ---------------------------------------------------------------------------
# Groups of target indices
# ---------------------------------------------------------------------------
GROUPS = {
    'novel_lcb_femgo': [71, 72],
}
ALL_INDICES = [i for g in GROUPS.values() for i in g]

# ---------------------------------------------------------------------------
# folder_map — single-source mirror of db_paths_for()
# Each value is the DB root dir under 1_result/ that contains the seed_*/ dirs
# (the actual .db files sit at <root>/seed_<N>/1_db/db_<N>.db).
# ---------------------------------------------------------------------------
FOLDER_MAP = {
    71: '71_novel_runEWindow/output',
    72: '72_novel_AutoGlob_1eVperAtomAboveGlob/output',
}

# ---------------------------------------------------------------------------
# Landscape defaults (mirrors stage2)
# ---------------------------------------------------------------------------
E_LIMIT_DEFAULT = (0.0 - 0.1, 1.5 + 0.1, 5)

# ---------------------------------------------------------------------------
# Plotting style for Stages 2 & 3 — same rcParams as run_stage2_landscape.py
# and run_stage3_probability.py (so every figure matches).
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

E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'

# ---------------------------------------------------------------------------
# Temperatures & colours (mirrors stage3)
# ---------------------------------------------------------------------------
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


# ===========================================================================
# Stage 1 — Database processing (mirrors run_stage1_database.py)
# ===========================================================================
def step1_database_processing(idx):
    """Database processing loop for index `idx`."""
    print(f"\n[STEP 1] Database processing for index {idx}")
    if idx not in FOLDER_MAP:
        print(f"  -> index {idx} not in folder_map, skipping")
        return
    folder = FOLDER_MAP[idx]
    dir_path = os.path.join(RESULT_DIR, folder)
    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')

    if not os.path.isdir(dir_path):
        print(f"  -> input directory not found: {dir_path}, skipping")
        return

    print(f"  input : {dir_path}")
    print(f"  output: {dir_out}")

    process_database(
        dir_path=dir_path,
        file_idx=idx,
        dir_out=dir_out,
        dir_xsf_traj=XSF_TRAJ_DIR,
        dir_xsf=XSF_DIR,
        individual_seeds_dir_name='seeds',
        save_individual_trajectories=True,
        plot_best_so_far=True,
        plot_by_seed=True,
        figsize=(8, 5),
        custom_max_x=None,
        custom_max_y=None,
        start_iter=10,
    )
    print(f"  -> done. outputs under {dir_out}")


# ===========================================================================
# Stage 2 — Landscape analysis (mirrors run_stage2_landscape.py)
# ===========================================================================
def step2_landscape(idx, e_max=None, normalize_density=False):
    """Landscape analysis & evaluation for index `idx`."""
    print(f"[STEP 2] Landscape analysis for index {idx}")

    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    traj_path = os.path.join(dir_out, XSF_TRAJ_DIR, f'traj_{idx}.traj')

    if not os.path.exists(traj_path):
        print(f"  -> WARNING: {traj_path} missing, skipping landscape")
        return

    structures = read(traj_path, index=':')

    raw_energies, valid = [], []
    for atoms in structures:
        try:
            raw_energies.append(atoms.get_potential_energy())
            valid.append(atoms)
        except Exception:
            continue
    if not valid:
        print("  -> no valid structures with energies")
        return

    num_atoms = len(valid[0])
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms

    # --- PCA via Fingerprint descriptors ---
    fp = Fingerprint.from_atoms(valid[0])
    data = np.array([fp.create_features(s).flatten() for s in valid])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    save_path = os.path.join(dir_out, IM_DIR)
    os.makedirs(save_path, exist_ok=True)

    # e_limit — custom or default
    if e_max is not None:
        e_limit = (0.0 - 0.1, e_max, 5)
    else:
        e_limit = E_LIMIT_DEFAULT

    # density x-label — a.u. when normalized, config./eV otherwise
    density_x_label = 'State Density\n(a.u.)' if normalize_density \
        else 'State Density\n(config./eV)'

    fig = plot_structure_landscape(
        X_eigen, energies, z_data=None,
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
        s=15,
        normalize_density=normalize_density,
        density_x_label=density_x_label,
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {save_path}/conf_space.png")


# ===========================================================================
# Stage 3 — Boltzmann probability (mirrors run_stage3_probability.py)
# ===========================================================================
def calculate_boltzmann_probs(energies, kde_model, T):
    """
    Calculates normalized Pi = [rho(E) * exp(-dE/kbT)] / Z

    Then scales to 0-1 (peak = 1) for plotting.
    """
    kb = 8.6173e-5  # eV/K

    # Adding epsilon to avoid zero
    rho_i = kde_model.evaluate(energies) + 1e-15

    # Calculate Boltzmann Weights
    relative_e = energies - np.min(energies)
    exponent = -relative_e / (kb * T)
    weights = np.exp(exponent)

    # Partition Function Z = sum(rho * weights)
    numerator = rho_i * weights
    Z = np.sum(numerator)

    # Normalized probabilities, then scale to 0-1 range
    probs = numerator / Z
    return probs / probs.max()


def step3_probability(idx, e_max=None):
    """Boltzmann probability analysis for index `idx`."""
    print(f"[STEP 3] Probability analysis for index {idx}")

    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    traj_path = os.path.join(dir_out, XSF_TRAJ_DIR, f'traj_{idx}.traj')

    if not os.path.exists(traj_path):
        print(f"  -> WARNING: {traj_path} missing, skipping probability")
        return

    print(f"  reading : {traj_path}")

    structures = read(traj_path, index=':')

    raw_energies = [atoms.get_potential_energy() for atoms in structures]
    num_atoms = len(structures[0])

    # Defining U = E_i - E_glob (normalized per atom)
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
    kde = gaussian_kde(energies)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)

    # Plot Boltzmann Probabilities for each Temp
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(energies, kde, T)

        peak_idx = np.argmax(probs)
        peak_energy = energies[peak_idx]

        note_label = f'{T} K'
        ax.scatter(energies, probs, color=color, s=15, alpha=0.5,
                   edgecolors='none', label=note_label)

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E)')
    ax.legend(frameon=False, loc='upper right')
    ax.set_ylim(0, 1 + 0.05)

    if e_max is not None:
        ax.set_xlim(0, e_max)
    else:
        ax.set_xlim(0, energies.max() + 0.05)

    plt.tight_layout()

    out_path = os.path.join(dir_out, IM_DIR,
                            'binding_probability_vs_temperature.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


# ===========================================================================
# Main — parse args, resolve indices, run stages
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Unified AGOX Analysis Pipeline for selected indices")
    parser.add_argument('--indices', type=str, default=None,
                        help="Comma-separated indices or group names "
                             "(novel_lcb_femgo). Default: all.")
    parser.add_argument('--idx', type=int, default=None,
                        help="Single index (shorthand for --indices).")
    parser.add_argument('--skip-probability', action='store_true',
                        help="Skip Stage 3 (Boltzmann probability).")
    parser.add_argument('--e-max', type=float, default=None,
                        help="Custom upper energy limit (eV/atom) for the "
                             "Stage 2 landscape and Stage 3 probability plots. "
                             "If omitted, each stage uses its own default.")
    parser.add_argument('--normalize-density', action='store_true',
                        help="Normalize the state-density panel (Stage 2) so "
                             "the peak of each KDE curve is scaled to 1 "
                             "(0-1 range on the density x-axis).")
    args = parser.parse_args()

    # Resolve indices
    if args.idx is not None:
        indices = [args.idx]
    elif args.indices:
        toks = [t.strip() for t in args.indices.split(',')]
        indices = []
        for t in toks:
            if t in GROUPS:
                indices.extend(GROUPS[t])
            else:
                indices.append(int(t))
    else:
        indices = ALL_INDICES

    print("=" * 70)
    print("AGOX ANALYSIS PIPELINE")
    print("Indices:", indices)
    if args.e_max is not None:
        print(f"e-max: {args.e_max} eV/atom")
    if args.normalize_density:
        print("normalize-density: True")
    if args.skip_probability:
        print("skip-probability: True (Stage 3 skipped)")
    print("=" * 70)

    for idx in indices:
        print(f"\n########## INDEX {idx} ##########")
        step1_database_processing(idx)
        step2_landscape(idx,
                        e_max=args.e_max,
                        normalize_density=args.normalize_density)
        if not args.skip_probability:
            step3_probability(idx, e_max=args.e_max)

    print(f"\nDONE. All outputs under: {OUT_DIR}")


if __name__ == '__main__':
    main()
