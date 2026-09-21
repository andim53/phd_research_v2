"""
draw_si_mgo.py — SI Fig_mgo: reverse deposition (MgO-on-Fe).

Reads the emitted dataset (analysis/Fig_mgo.json) and plots three panels:
  (a) state density g(E)
  (b) PCA landscape psi_1d vs E_i-E_glob colored by Δz
  (c) temperature-dependent Boltzmann probability P(E)

Run emit_datasets.py first. Output: analysis/figures/Fig_mgo.png
"""
__version__ = "1.3.0"

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

E_LIMIT = (0.0 - 0.1, 3.7, 5)  # relative-energy axis capped at 3.7 eV/atom (owner)
Z_LIMIT = (5.85, 0, 5)
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


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
    boltz = d.get('boltzmann', {})

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    fig, (ax_dens, ax_scat, ax_boltz) = plt.subplots(
        1, 3, figsize=(9, 3),
        gridspec_kw={'width_ratios': [1, 2.5, 2.5]})
    fig.subplots_adjust(wspace=0.35)

    # (a) state density
    ax_dens.plot(density, grid, color='black', lw=1.0)
    ax_dens.fill_betweenx(grid, 0, density, color='black', alpha=0.12)
    ax_dens.set_xlabel(DENSITY_LABEL, fontsize=10)
    ax_dens.set_ylabel(E_LABEL, fontsize=10)
    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(np.round(np.linspace(min_e, max_e, E_LIMIT[2]), 1))

    # (b) PCA landscape colored by Δz
    norm = mcolors.Normalize(vmin=Z_LIMIT[1], vmax=Z_LIMIT[0])
    sc = ax_scat.scatter(psi, rel, c=dz, s=10, cmap='PuBu', norm=norm,
                         edgecolors='none', alpha=0.8)
    cbar = plt.colorbar(sc, ax=ax_scat, pad=0.02)
    cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
    cbar.set_ticks(list(np.linspace(Z_LIMIT[1], Z_LIMIT[0], Z_LIMIT[2])))
    ax_scat.set_xlabel(SCATTER_LABEL, fontsize=10)
    ax_scat.set_ylim(min_e, max_e)
    ax_scat.set_xlim(np.min(psi) - 0.1, np.max(psi) + 0.1)

    # (c) temperature-dependent Boltzmann probability
    for i, (T, c) in enumerate(boltz.items()):
        ax_boltz.plot(c['energy'], c['prob'], color=COLORS_PLASMA[i % len(COLORS_PLASMA)],
                      lw=1.0, label=f'{T} K')
    ax_boltz.set_xlabel(E_LABEL, fontsize=10)
    ax_boltz.set_ylabel('Probability P(E)', fontsize=10)
    ax_boltz.set_xlim(min_e, max_e)
    ax_boltz.set_ylim(0, 1.05)
    ax_boltz.legend(frameon=False, loc='upper right', fontsize=7)

    out = os.path.join(ensure_fig_dir(), 'Fig_mgo.png')
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")
    print(f"  mgofe ensemble: {len(rel)} configs")


if __name__ == '__main__':
    main()