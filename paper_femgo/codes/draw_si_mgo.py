"""
draw_si_mgo.py — SI Fig_mgo: reverse deposition (MgO-on-Fe).

Reads the emitted dataset (analysis/Fig_mgo.json) and plots (a) state density
g(E) and (b) PCA landscape psi_1d vs E_i-E_glob colored by Δz.

Run emit_datasets.py first. Output: analysis/figures/Fig_mgo.png
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, ANALYSIS_DIR, ensure_fig_dir,
                    E_LABEL, DENSITY_LABEL, SCATTER_LABEL)

E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)
Z_LIMIT = (5.85, 0, 5)


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_mgo.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    d = json.load(open(json_path))['data']
    rel = np.array(d['rel_energy'])
    dz = np.array(d['delta_z_A'])
    psi = np.array(d['psi_1d'])
    grid = np.array(d['kde_grid'])
    density = np.array(d['kde_density'])

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    fig, (ax_dens, ax_scat) = plt.subplots(
        1, 2, figsize=(6, 3), sharey=True,
        gridspec_kw={'width_ratios': [1, 2.5]})
    fig.subplots_adjust(wspace=0.1)

    ax_dens.plot(density, grid, color='black', lw=1.5)
    ax_dens.fill_betweenx(grid, 0, density, color='black', alpha=0.12)
    ax_dens.set_xlabel(DENSITY_LABEL, fontsize=10)
    ax_dens.set_ylabel(E_LABEL, fontsize=10)

    norm = mcolors.Normalize(vmin=Z_LIMIT[1], vmax=Z_LIMIT[0])
    sc = ax_scat.scatter(psi, rel, c=dz, s=5, cmap='PuBu', norm=norm,
                         edgecolors='black', linewidth=0.5, alpha=0.8)
    cbar = plt.colorbar(sc, ax=ax_scat, pad=0.02)
    cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
    cbar.set_ticks(list(np.linspace(Z_LIMIT[1], Z_LIMIT[0], Z_LIMIT[2])))
    ax_scat.set_xlabel(SCATTER_LABEL, fontsize=10)
    ax_scat.set_xlim(np.min(psi) - 0.1, np.max(psi) + 0.1)

    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(np.round(np.linspace(min_e, max_e, E_LIMIT[2]), 1))

    out = os.path.join(ensure_fig_dir(), 'Fig_mgo.png')
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")
    print(f"  mgofe ensemble: {len(rel)} configs")


if __name__ == '__main__':
    main()
