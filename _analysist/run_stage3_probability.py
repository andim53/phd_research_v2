#!/usr/bin/env python3
"""
Stage 3 (standalone): Probability (statistical mechanics) for a single index.

Equivalent to step3_probability() in run_analysis_indices.py.

Walks 1_result/<folder>/ for every *.db, loads all frames, computes binding
energies, builds a Gaussian KDE over relative binding energy, and runs a
Boltzmann / partition-function loop over five temperatures to produce:
  0_analy/idx_N/2_im/binding_probability_vs_temperature.png

Usage:
  /home/miniconda3/envs/agox_v2/bin/python run_stage3_probability.py --idx 22

Environment: agox_v2 (AGOX 3.10.2, scipy, matplotlib)
"""
import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from agox.databases import Database
from scipy.stats import gaussian_kde

# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

RESULT_DIR = os.path.join(SCRIPT_DIR, '1_result')
OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')
IM_DIR = '2_im'

# folder_map — single-source mirror of run_analysis_indices.db_paths_for()
FOLDER_MAP = {
    22: '22_latt_0', 23: '23_latt_025', 24: '24_latt_50',
    25: '25_latt_075', 26: '26_latt_100',
    27: '27_fe_con0', 28: '28_fe_con5', 29: '29_fe_con10',
    30: '30_fe_con15', 31: '31_fe_con20',
    32: '32_dos', 33: '33_latt_25_mgo', 34: '34_latt_50_mgo',
    35: '35_latt_75_mgo', 36: '36_latt_100_mgo',
    67: '67_2ml', 68: '68_ratt_min1', 69: '69_ratt_min05',
}

# Energy axis label — matches the researcher style used everywhere
E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'

# ---------------------------------------------------------------------------
# Researcher plotting style (mirrors codes/07 + the rcParams block in the
# main runner). Applied once at import time so every figure matches.
# ---------------------------------------------------------------------------
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
    'xtick.major.size': 5,
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


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 3: probability analysis for a single AGOX index")
    parser.add_argument('--idx', type=int, required=True,
                        help="Simulation index (e.g. 22)")
    args = parser.parse_args()
    idx = args.idx

    if idx not in FOLDER_MAP:
        print(f"Index {idx} not in folder_map.")
        print(f"Known indices: {sorted(FOLDER_MAP.keys())}")
        sys.exit(1)

    dir_path = os.path.join(RESULT_DIR, FOLDER_MAP[idx])

    if not os.path.isdir(dir_path):
        print(f"Input directory not found: {dir_path}")
        sys.exit(1)

    print(f"Stage 3 — index {idx}")
    print(f"  scanning: {dir_path}")

    # --- gather EVERY .db under the index folder (all seeds) ---
    db_files = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith('.db'):
                db_files.append(os.path.join(root, f))

    if not db_files:
        print(f"  -> no .db found for index {idx}, skipping probability")
        sys.exit(0)

    all_atoms = []
    for db_file in db_files:
        db = Database(filename=db_file)
        db.restore_to_memory()
        all_atoms.extend(db.restore_to_trajectory())

    # --- binding-energy constants (same as codes/76) ---
    n_fe = 9
    E_slab = -92.946489   # eV
    mu_fe = -8.553673     # eV/atom

    binding = np.array([
        a.get_potential_energy()
        for a in all_atoms
        if hasattr(a, 'get_potential_energy')
    ])
    rel_eb = binding - np.min(binding)

    if len(rel_eb) < 2:
        print(f"  -> only {len(rel_eb)} frame(s) found; "
              f"need >= 2 for KDE, skipping probability")
        sys.exit(0)

    # --- Gaussian KDE over relative binding energy ---
    kde = gaussian_kde(rel_eb)
    num_points = 1000
    grid = np.linspace(rel_eb.min(), rel_eb.max(), num_points)
    density = kde(grid)
    density = density / density.min()

    # --- Boltzmann / partition-function loop over 5 temperatures ---
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

    # --- plot ---
    fig, ax = plt.subplots(figsize=(7, 6))
    for res in results:
        ax.plot(grid, res['P'], label=f"{res['T']} K", lw=1.5)
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E)')
    ax.legend(frameon=False, loc='upper right')
    plt.tight_layout()

    out_path = os.path.join(OUT_DIR, f'idx_{idx}', IM_DIR,
                            'binding_probability_vs_temperature.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


if __name__ == '__main__':
    main()
