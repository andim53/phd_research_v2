"""
draw_landscape.py — Fig_ConDen: state density g(E) + PCA landscape with Δz coloring.

Reads the emitted dataset (analysis/Fig_ConDen.json) and plots:
  (a) left:  KDE state density g(E) vs E_i-E_glob (eV/atom)
  (b) right: PCA psi_1d vs E_i-E_glob, points colored by Fe-layer Δz (Å)

Run emit_datasets.py first. Output: analysis/figures/Fig_ConDen.png
"""
__version__ = "1.1.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as patheffects

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, ANALYSIS_DIR, ensure_fig_dir,
                    E_LABEL, DENSITY_LABEL, SCATTER_LABEL)

E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)
Z_LIMIT = (5.85, 0, 5)


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_ConDen.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    d = json.load(open(json_path))['data']
    rel = np.array(d['rel_energy'])
    dz = np.array(d['delta_z_A'])
    psi = np.array(d['psi_1d'])
    grid = np.array(d['kde_grid'])
    density = np.array(d['kde_density'])
    peaks = d['peaks_eV_per_atom']

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    eticks = np.round(np.linspace(min_e, max_e, E_LIMIT[2]), 1)

    fig, (ax_dens, ax_scat) = plt.subplots(
        1, 2, figsize=(6, 3), sharey=True,
        gridspec_kw={'width_ratios': [1, 2.5]})
    fig.subplots_adjust(wspace=0.1)

    ax_dens.plot(density, grid, color='black', lw=1.5, zorder=4)
    ax_dens.fill_betweenx(grid, 0, density, color='black', alpha=0.12, zorder=3)
    ax_dens.set_xlabel(DENSITY_LABEL, fontsize=10)
    ax_dens.set_ylabel(E_LABEL, fontsize=10)

    norm = mcolors.Normalize(vmin=Z_LIMIT[1], vmax=Z_LIMIT[0])
    sc = ax_scat.scatter(psi, rel, c=dz, s=5, cmap='PuBu', norm=norm,
                         edgecolors='black', linewidth=0.5, alpha=0.8, zorder=2)
    cbar = plt.colorbar(sc, ax=ax_scat, pad=0.02)
    cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
    cbar.set_ticks(list(np.linspace(Z_LIMIT[1], Z_LIMIT[0], Z_LIMIT[2])))
    ax_scat.set_xlabel(SCATTER_LABEL, fontsize=10)
    ax_scat.set_xlim(np.min(psi) - 0.1, np.max(psi) + 0.1)

    labels = ['Island', 'Flat']
    for i, peak_energy in enumerate(peaks):
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
    print(f"  ensemble: {len(rel)} configs, peaks at {peaks} eV/atom")


if __name__ == '__main__':
    main()
