#!/usr/bin/env python
"""
PDOS analysis for the Fe/MgO (Fe25/Mg25/O25) run in
_run/0_pdos/_results/37_dos.

Mirrors cell 52 ("# dos") of _archive/2_analysist/main_analyst.ipynb exactly:
same config block (seed_map / color_map / line_styles / plot_type / fig_dims
/ dpi / labels), same subplot branch (Total DOS black line + filled Fe-3d
channel, spin-down mirrored below zero) and same overlay branch (Fe-3d up/down
only), on an E-Ef axis.

Input: per-seed CSV files 37_dos/dos_seed_{seed}.csv (the notebook's exact
filename convention) with columns energy, total_dos_up, total_dos_down,
total_Fe_d_up, total_Fe_d_down (real orbital-projected Fe-3d PDOS, Fermi
shifted to 0).

Usage:
    /home/think/miniconda3/envs/agox_v2/bin/python analyze_dos.py
"""

import os

import pandas as pd
import matplotlib
matplotlib.use('Agg')          # headless-safe
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DOS_DIR = os.path.join(HERE, '37_dos')

# --- 07 / notebook cell 7 style: boxed serif ---
custom_rc_params = {
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
}
plt.rcParams.update(custom_rc_params)

# --- notebook cell 52 config ---
seed_map = {3: 'Island (Ground State)', 4: 'Flat'}
use_multi_color = True
main_color = 'black'
color_map = {'Island': '#1f77b4', 'Flat': '#d62728'}
line_styles = {'Island': '-', 'Flat': '-'}
energy_range = (-5.1, 5.1)

plot_type = 'overlay'                  # Options: 'subplot' or 'overlay'
fig_dims = (4, 4)
dpi_val = 300
x_label = '$E$ - $E_f$ (eV)'
y_label = 'Fe-3d PDOS (states/eV)'
plot_title = 'Fe-3d Comparison: Island vs Flat Growth'
legend_loc = 'lower right'


def load_seed_dfs(dos_dir, seed_map):
    """Build {name: df} by reading each seed's dos_seed_{seed}.csv directly.

    The files already carry the notebook's exact column names
    (energy, total_dos_up, total_dos_down, total_Fe_d_up, total_Fe_d_down).
    """
    out = {}
    for seed, name in seed_map.items():
        path = os.path.join(dos_dir, f'dos_seed_{seed}.csv')
        df = pd.read_csv(path)
        out[name] = df
    return out


def main():
    data = load_seed_dfs(DOS_DIR, seed_map)
    n = len(next(iter(data.values())))
    print(f'Loaded from {DOS_DIR} | seeds: {list(seed_map)} | points/seed: {n}')

    if plot_type == 'subplot':
        fig, axes = plt.subplots(2, 1, figsize=(fig_dims[0], fig_dims[1] * 1.8),
                                 sharex=True, dpi=dpi_val)
        for ax, name in zip(axes, data.keys()):
            df = data[name]
            c = color_map.get(name, main_color) if use_multi_color else main_color
            # Total DOS + filled projected channel
            ax.plot(df['energy'], df['total_dos_up'], color='black', lw=1,
                    label='Total DOS')
            ax.fill_between(df['energy'], df['total_Fe_d_up'], color=c,
                            alpha=0.4, label=f'{name}')
            # Spin down mirrored
            ax.plot(df['energy'], -df['total_dos_down'], color='black', lw=1)
            ax.fill_between(df['energy'], -df['total_Fe_d_down'], color=c,
                            alpha=0.6)
            ax.axvline(x=0, color='gray', linestyle=':', lw=1, alpha=0.7)
            ax.axhline(y=0, color='black', lw=0.8)
            ax.set_xlim(energy_range)
            ax.set_ylabel('DOS (states/eV)')
            ax.set_title(f'Electronic Structure: {name}', fontweight='bold')
            ax.legend(frameon=False, loc=legend_loc)
        plt.xlabel(x_label)

    elif plot_type == 'overlay':
        plt.figure(figsize=fig_dims, dpi=dpi_val)
        for name in data.keys():
            df = data[name]
            ls = line_styles.get(name, '-')
            c = color_map.get(name, main_color) if use_multi_color else main_color
            # Projected manifold
            plt.plot(df['energy'], df['total_Fe_d_up'],
                     color=c, ls=ls, lw=2, label=f'{name}')
            # Spin down mirrored
            plt.plot(df['energy'], -df['total_Fe_d_down'],
                     color=c, ls=ls, lw=2, alpha=0.7)
        plt.axvline(x=0, color='black', linestyle=':', alpha=0.5)
        plt.axhline(y=0, color='black', lw=0.8)
        plt.xlim(energy_range)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        # plt.title(plot_title)
        plt.legend(frameon=False, loc=legend_loc)

    # --- SAVE & DISPLAY ---
    plt.tight_layout()
    output_name = f"dos_comparison_{plot_type}.png"
    out_path = os.path.join(HERE, output_name)
    plt.savefig(out_path, bbox_inches='tight')
    print(f'Plotting complete. File saved: {out_path}')


if __name__ == '__main__':
    main()
