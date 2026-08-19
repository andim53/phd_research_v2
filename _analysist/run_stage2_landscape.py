#!/usr/bin/env python3
"""
Stage 2 (standalone): Landscape analysis for a single index.

Equivalent to step2_landscape() in run_analysis_indices.py.

Reads the combined trajectory written by Stage 1:
  0_analy/idx_N/1_xsf_traj/traj_N.traj
Computes a PCA on AGOX Fingerprint descriptors (top eigenvector of the
covariance matrix) and plots the conformation landscape:
  0_analy/idx_N/2_im/conf_space.png

Usage:
  /home/miniconda3/envs/agox_v2/bin/python run_stage2_landscape.py --idx 22

Environment: agox_v2 (ASE 3.25.0, AGOX 3.10.2, scipy, matplotlib)
"""
import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ase.io import read
from agox.models.descriptors.fingerprint import Fingerprint
from scripts.plot_structure_landscape import plot_structure_landscape

# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')
IM_DIR = '2_im'
XSF_TRAJ_DIR = '1_xsf_traj'

# Landscape tuning — same values used in the main runner (codes/14 path)
E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)

# ---------------------------------------------------------------------------
# Plotting style for Stage 2 figures — same rcParams used by the main
# runner (codes/07 + run_analysis_indices).  figsize is intentionally
# kept at the smaller (3, 3) used originally so every figure matches.
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
        description="Stage 2: landscape analysis for a single AGOX index")
    parser.add_argument('--idx', type=int, required=True,
                        help="Simulation index (e.g. 22)")
    parser.add_argument('--e-max', type=float, default=None,
                        help="Custom upper energy limit (eV/atom) for the landscape plot. "
                             "If omitted, uses the default e_limit max (1.5 + 0.1).")
    parser.add_argument('--normalize-density', action='store_true',
                        help="Normalize the state-density panel so the peak of each KDE "
                             "curve is scaled to 1 (0-1 range on the density x-axis).")
    args = parser.parse_args()
    idx = args.idx

    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    traj_path = os.path.join(dir_out, XSF_TRAJ_DIR, f'traj_{idx}.traj')

    if not os.path.exists(traj_path):
        print(f"WARNING: {traj_path} missing — run Stage 1 first.")
        sys.exit(0)

    print(f"Stage 2 — index {idx}")
    print(f"  reading : {traj_path}")

    structures = read(traj_path, index=':')

    raw_energies = []
    valid = []
    for atoms in structures:
        try:
            raw_energies.append(atoms.get_potential_energy())
            valid.append(atoms)
        except Exception:
            continue

    if not valid:
        print("  -> no valid structures with energies")
        sys.exit(0)

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

    if args.e_max is not None:
        e_limit = (0.0 - 0.1, args.e_max, 5)
    else:
        e_limit = E_LIMIT

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
        s=5,
        normalize_density=args.normalize_density,
        density_x_label='State Density\n(a.u.)' if args.normalize_density else 'State Density\n(config./eV)',
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {save_path}/conf_space.png")


if __name__ == '__main__':
    main()
