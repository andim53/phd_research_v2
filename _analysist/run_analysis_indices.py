#!/usr/bin/env python3
"""
Unified AGOX Analysis Pipeline for selected simulation indices.

Applies, in order:
  1. Plotting style from codes/07_plotting_style_and_label_configuration.py
  2. Database processing loop (scripts/process_database.py -> process_database)
  3. Landscape analysis & evaluation (codes/14_landscape_analysis_and_evaluation_script.py),
     using scripts/plot_structure_landscape.py
  4. Plot-probability statistical-mechanics analysis (codes/76_plot_probability.py style)

Targets (grouped):
  Lattice sweep group 1 : 22, 23, 24, 25, 26
  Fe-concentration group: 27, 28, 29, 30, 31
  Lattice-on-MgO group  : 32, 33, 34, 35, 36   (32_dos has no seed dirs -> flat-mode)
  2ML / rattle group    : 67, 68, 69

Run from /home/think/Desktop/research/_analysist with the agox_v2 conda env:
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Make local scripts importable (process_database, plot_structure_landscape, ...)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'scripts'))

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from scripts.process_database import process_database
from scripts.plot_structure_landscape import plot_structure_landscape
from scripts.calculate_relative_energy import calculate_relative_energy

# --------------------------------------------------------------------------
# (1) Plotting style from codes/07_plotting_style_and_label_configuration.py
# --------------------------------------------------------------------------
COLORS = ['#FF0000', '#00FF00']
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1.5,
    'axes.edgecolor': 'black',
    'axes.spines.top': True,
    'axes.spines.right': True,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'xtick.top': True,
    'ytick.right': True,
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.minor.size': 2,
    'ytick.minor.size': 2,
    'xtick.minor.width': 1.0,
    'ytick.minor.width': 1.0,
    'axes.grid': False,
    'legend.frameon': True,
})
E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
RESULT_DIR = os.path.join(SCRIPT_DIR, '1_result')
OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')
XSF_TRAJ_DIR = '1_xsf_traj'
XSF_DIR = '1_xsf'
IM_DIR = '2_im'

# Groups of target indices
GROUPS = {
    'latt_sweep_1':  [22, 23, 24, 25, 26],
    'fe_concentration': [27, 28, 29, 30, 31],
    'latt_on_mgo': [32, 33, 34, 35, 36],
    'ml_rattle':    [67, 68, 69],
}
ALL_INDICES = [i for g in GROUPS.values() for i in g]

# Landscape analysis tuning (from codes/14)
# LANDSCAPE_TRAJ_FRAME = 65   # read traj_<idx>.traj, frame ':'
E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)
Z_ATOM_TYPE = 'Fe'


def db_paths_for(idx):
    """Return list of (dir_path, file_idx) tuples for a given top-level index."""
    folder_map = {
        22: '22_latt_0', 23: '23_latt_025', 24: '24_latt_50',
        25: '25_latt_075', 26: '26_latt_100',
        27: '27_fe_con0', 28: '28_fe_con5', 29: '29_fe_con10',
        30: '30_fe_con15', 31: '31_fe_con20',
        32: '32_dos', 33: '33_latt_25_mgo', 34: '34_latt_50_mgo',
        35: '35_latt_75_mgo', 36: '36_latt_100_mgo',
        67: '67_2ml', 68: '68_ratt_min1', 69: '69_ratt_min05',
    }
    return [(os.path.join(RESULT_DIR, folder_map[idx]), idx)]


def step1_database_processing(idx):
    """(2) Database processing loop - per codes/12_database_processing_loop.py."""
    print(f"\n[STEP 1] Database processing for index {idx}")
    db_paths = db_paths_for(idx)
    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    for dir_path, file_idx in db_paths:
        process_database(
            dir_path=dir_path,
            file_idx=file_idx,
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
    print(f"  -> outputs under {dir_out}")


def step2_landscape(idx):
    """(3) Landscape analysis & evaluation - per codes/14 + plot_structure_landscape."""
    print(f"[STEP 2] Landscape analysis for index {idx}")
    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')
    traj_path = os.path.join(dir_out, XSF_TRAJ_DIR, f'traj_{idx}.traj')
    if not os.path.exists(traj_path):
        print(f"  -> WARNING: {traj_path} missing, skipping landscape")
        return
    from ase.io import read
    structures = read(traj_path, index=':')

    raw_energies, valid = [], []
    for atoms in structures:
        try:
            raw_energies.append(atoms.get_potential_energy())
            valid.append(atoms)
        except Exception:
            continue
    if not valid:
        print("  -> no valid structures")
        return

    num_atoms = len(valid[0])
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms

    fp = Fingerprint.from_atoms(valid[0])
    data = np.array([fp.create_features(s).flatten() for s in valid])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    save_path = os.path.join(dir_out, IM_DIR)
    os.makedirs(save_path, exist_ok=True)
    fig = plot_structure_landscape(
        X_eigen, energies, z_data=None,
        save_path=save_path,
        animate_scatter=False,
        figsize=(5, 3), wspace=0.1, fontsize=10,
        e_limit=E_LIMIT, fill_density=True, dens_line_weight=0.9,
        show_limits=False, custom_peak_labels=None,
        cmap='PuBu', show_colorbar=False, cbar_pad=0.02,
        z_limit=(5.85, 0, 5), black_seed_zero=True,
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {save_path}/conf_space.png")


def step3_probability(idx):
    """(4) Plot probability (statistical mechanics) - per codes/76_plot_probability.py."""
    print(f"[STEP 3] Probability analysis for index {idx}")
    dir_path, _ = db_paths_for(idx)[0]
    # Find a database to sample binding energies from (first seed db found)
    # Gather EVERY seed .db under the index folder (mirrors process_database).
    db_files = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith('.db'):
                db_files.append(os.path.join(root, f))
    if not db_files:
        print(f"  -> no .db found for index {idx}, skipping probability")
        return

    all_atoms = []
    for db_file in db_files:
        db = Database(filename=db_file)
        db.restore_to_memory()
        all_atoms.extend(db.restore_to_trajectory())
    traj = all_atoms
    n_fe = 9
    E_slab = -92.946489
    mu_fe = -8.553673

    binding = np.array([a.get_potential_energy() for a in traj
                        if hasattr(a, 'get_potential_energy')])
    rel_eb = binding - np.min(binding)

    if len(rel_eb) < 2:
        print(f"  -> only {len(rel_eb)} frame(s) found; not enough for KDE, skipping probability")
        return
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(rel_eb)
    num_points = 1000
    grid = np.linspace(rel_eb.min(), rel_eb.max(), num_points)
    density = kde(grid)
    density = density / density.min()

    kB = 8.617333262e-5
    temperatures = [298.15, 348.60, 447.875, 547.15, 646.425]
    results = []
    for T in temperatures:
        beta = 1.0 / (kB * T)
        G_levels = grid - kB * T * np.log(density + 1e-20)
        delta_G = G_levels - np.min(G_levels)
        bf = np.exp(-beta * (delta_G * n_fe))
        Z = np.sum(bf)
        P = bf / Z
        results.append({'T': T, 'P': P})

    fig, ax = plt.subplots(figsize=(7, 6))
    for res in results:
        ax.plot(grid, res['P'], label=f"{res['T']} K", lw=1.5)
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E)')
    ax.legend(frameon=False, loc='upper right')
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, f'idx_{idx}', IM_DIR, 'binding_probability_vs_temperature.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run analysis for selected indices")
    parser.add_argument('--indices', type=str, default=None,
                        help="Comma-separated indices or group names "
                             "(latt_sweep_1, fe_concentration, latt_on_mgo, ml_rattle). "
                             "Default: all.")
    parser.add_argument('--skip-probability', action='store_true')
    args = parser.parse_args()

    if args.indices:
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
    print("=" * 70)

    for idx in indices:
        print(f"\n########## INDEX {idx} ##########")
        step1_database_processing(idx)
        step2_landscape(idx)
        if not args.skip_probability:
            step3_probability(idx)

    print("\nDONE. All outputs under:", OUT_DIR)


if __name__ == '__main__':
    main()
