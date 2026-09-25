"""draw_wet_landscape.py — Fig_wetLandscape: PCA landscape (Fe/MgO vs Fe-B/MgO).

Reads analysis/Fig_wetLandscape.json (from emit_wetting_modes.py) and plots two
side-by-side panels: psi_1d (per-system PC1 of the AGOX Fingerprint) vs relative
energy, colored by dZ (flat = low dZ, island = high dZ), with a shared colorbar in
its own axes (not overlapping either panel).

The two PC1 axes are fit independently (feature spaces are species-locked: femgo
720-d, febmgo 1500-d), so only the energy positions and the flat/island separation —
not absolute psi values — are compared across panels. The psi sign is aligned so
flat sits on the left in both.

Output: analysis/figures/Fig_wetLandscape.png
"""
__version__ = "1.4.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as patheffects
from mpl_toolkits.axes_grid1 import make_axes_locatable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir, E_LABEL, SCATTER_LABEL

Z_LIMIT = (5.85, 0, 5)          # dZ color range (matches Fig_ConDen)
E_MAX = 0.7                     # relative-energy cap (matches Fig_ConDen)


def main():
    apply_style()
    jp = os.path.join(ANALYSIS_DIR, 'Fig_wetLandscape.json')
    if not os.path.exists(jp):
        print(f'  MISSING {jp} — run emit_wetting_modes.py first')
        return
    d = json.load(open(jp))['data']

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4), sharey=True)
    norm = mcolors.Normalize(vmin=Z_LIMIT[1], vmax=Z_LIMIT[0])

    sc = None
    for ax, (system, label) in zip(axes, (('femgo', 'Fe/MgO'), ('febmgo', 'Fe-B/MgO'))):
        s = d[system]
        sc = ax.scatter(s['psi_1d'], s['rel_energy'], c=s['delta_z_A'], s=24,
                        cmap='YlGnBu_r', norm=norm, edgecolors='none', alpha=0.8, zorder=2)
        ax.set_title(label, fontsize=12)
        ax.set_xlabel(SCATTER_LABEL)
        ax.set_ylim(0, E_MAX)

        # flat + island mode lines (horizontal dashed, white shadow — matches Fig_ConDen)
        for mode, name in ((s['island_mode'], 'Island'), (s['flat_mode'], 'Flat')):
            line = ax.axhline(y=mode, color='black', linestyle='--', linewidth=1.2,
                              alpha=1.0, zorder=20)
            line.set_path_effects([patheffects.withStroke(linewidth=3.5, foreground='white')])
            ax.text(0.03, mode + 0.008, f'{name}: {mode:.3f}',
                    transform=ax.get_yaxis_transform(), fontsize=8,
                    color='black', verticalalignment='bottom', zorder=21,
                    path_effects=[patheffects.withStroke(linewidth=2, foreground='white')])

    axes[0].set_ylabel(E_LABEL)

    # dedicated colorbar axes, separated from the right (Fe-B) panel
    divider = make_axes_locatable(axes[1])
    cax = divider.append_axes('right', size='5%', pad=0.18)
    cbar = fig.colorbar(sc, cax=cax)
    cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
    cbar.set_ticks(list(np.linspace(Z_LIMIT[1], Z_LIMIT[0], Z_LIMIT[2])))

    fig.subplots_adjust(wspace=0.3)
    out = os.path.join(ensure_fig_dir(), 'Fig_wetLandscape.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {out}')


if __name__ == '__main__':
    main()
