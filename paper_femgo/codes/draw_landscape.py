"""
draw_landscape.py — Fig_ConDen: state density g(E) + PCA landscape with Δz coloring.

Two-panel figure matching _analysist plot_structure_landscape:
  (a) left:  KDE state density g(E) vs E_i-E_glob (eV/atom)
  (b) right: PCA psi_1d vs E_i-E_glob, points colored by Fe-layer Δz (Å)

Uses the paper's minimum-ensemble definition (iteration >= 10) over all
Fe-on-MgO seeds (3-15).

Output: analysis/figures/Fig_ConDen.png
"""
__version__ = "1.0.0"

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as patheffects
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, femgo_db_paths, load_agox_ensemble,
                    rel_energy_per_atom, delta_z, pca_psi1d,
                    ensure_fig_dir, E_LABEL, DENSITY_LABEL, SCATTER_LABEL)

E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)
Z_LIMIT = (5.85, 0, 5)


def main():
    apply_style()
    db_paths = femgo_db_paths()
    energies, atoms, _ = load_agox_ensemble(db_paths, start_iter=10)
    if len(energies) == 0:
        print("No ensemble data"); return

    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    dz = delta_z(atoms)
    psi = pca_psi1d(atoms)

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    eticks = np.round(np.linspace(min_e, max_e, E_LIMIT[2]), 1)

    fig, (ax_dens, ax_scat) = plt.subplots(
        1, 2, figsize=(6, 3), sharey=True,
        gridspec_kw={'width_ratios': [1, 2.5]})
    fig.subplots_adjust(wspace=0.1)

    # --- (a) state density ---
    energy_grid = np.linspace(min_e, max_e, 200)
    kde = gaussian_kde(rel)
    density = kde.evaluate(energy_grid)
    ax_dens.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
    ax_dens.fill_betweenx(energy_grid, 0, density, color='black', alpha=0.12, zorder=3)
    ax_dens.set_xlabel(DENSITY_LABEL, fontsize=10)
    ax_dens.set_ylabel(E_LABEL, fontsize=10)

    # --- (b) PCA scatter colored by Δz ---
    norm = mcolors.Normalize(vmin=Z_LIMIT[1], vmax=Z_LIMIT[0])
    sc = ax_scat.scatter(psi, rel, c=dz, s=5, cmap='PuBu', norm=norm,
                         edgecolors='black', linewidth=0.5, alpha=0.8, zorder=2)
    cbar = plt.colorbar(sc, ax=ax_scat, pad=0.02)
    cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
    tick_locs = np.linspace(Z_LIMIT[1], Z_LIMIT[0], Z_LIMIT[2])
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
    ax_scat.set_xlabel(SCATTER_LABEL, fontsize=10)
    ax_scat.set_xlim(np.min(psi) - 0.1, np.max(psi) + 0.1)

    # --- peak detection + dashed lines on both panels ---
    peaks, _ = find_peaks(density, prominence=np.max(density) * 0.05)
    peaks = sorted(peaks, key=lambda idx: energy_grid[idx])
    labels = ['Island', 'Flat']
    for i, peak_idx in enumerate(peaks):
        peak_energy = energy_grid[peak_idx]
        for ax in (ax_dens, ax_scat):
            ax.axhline(y=peak_energy, color='black', linestyle='--',
                       linewidth=1, alpha=0.5, zorder=1)
        txt = labels[i] if i < len(labels) else f'Peak {i+1}'
        t = ax_dens.text(0.05, peak_energy + 0.005, f'{txt}: {peak_energy:.3f} eV',
                         fontsize=8, color='black', verticalalignment='bottom', zorder=11)
        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(eticks)

    out = os.path.join(ensure_fig_dir(), 'Fig_ConDen.png')
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")
    print(f"  ensemble: {len(rel)} configs, peaks at {[round(energy_grid[p],3) for p in peaks]} eV/atom")


if __name__ == '__main__':
    main()
