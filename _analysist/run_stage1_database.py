#!/usr/bin/env python3
"""
Stage 1 (standalone): Database processing for a single index.

Equivalent to step1_database_processing() in run_analysis_indices.py.

Reads AGOX .db files from 1_result/<folder>/seed_*/1_db/ (or flat 1_db/db_0.db),
filters iteration >= 10, and writes:
  0_analy/idx_N/1_xsf_traj/traj_N.traj, traj_N.xsf
  0_analy/idx_N/1_xsf_traj/seeds/N_seed_*.traj/.xsf
  0_analy/idx_N/1_xsf/N/struct_*.xsf
  0_analy/idx_N/data_N.csv
  0_analy/idx_N/progression_plots/progression_seed_split_N.png

Usage:
  /home/miniconda3/envs/agox_v2/bin/python run_stage1_database.py --idx 22

Environment: agox_v2 (ASE 3.25.0, AGOX 3.10.2, pandas, matplotlib)
"""
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'scripts'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.process_database import process_database

# ---------------------------------------------------------------------------
# Paths — resolved relative to this script's location (same convention as the
# main runner). 1_result/ and 0_analy/ live next to _analysist/.
# ---------------------------------------------------------------------------
RESULT_DIR = os.path.join(SCRIPT_DIR, '1_result')
OUT_DIR = os.path.join(SCRIPT_DIR, '0_analy')

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


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 1: database processing for a single AGOX index")
    parser.add_argument('--idx', type=int, required=True,
                        help="Simulation index (e.g. 22)")
    args = parser.parse_args()
    idx = args.idx

    if idx not in FOLDER_MAP:
        print(f"Index {idx} not in folder_map.")
        print(f"Known indices: {sorted(FOLDER_MAP.keys())}")
        sys.exit(1)

    folder = FOLDER_MAP[idx]
    dir_path = os.path.join(RESULT_DIR, folder)
    dir_out = os.path.join(OUT_DIR, f'idx_{idx}')

    if not os.path.isdir(dir_path):
        print(f"Input directory not found: {dir_path}")
        sys.exit(1)

    print(f"Stage 1 — index {idx}")
    print(f"  input : {dir_path}")
    print(f"  output: {dir_out}")

    process_database(
        dir_path=dir_path,
        file_idx=idx,
        dir_out=dir_out,
        dir_xsf_traj='1_xsf_traj',
        dir_xsf='1_xsf',
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


if __name__ == '__main__':
    main()
