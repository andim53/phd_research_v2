"""draw_wetting_modes.py — Fig_wetModes: collective flat/island density (Fe/MgO vs Fe-B/MgO).

Reads analysis/Fig_wetModes.json (from emit_wetting_modes.py) and plots the four
branch-conditional KDE densities (flat/island x Fe/MgO solid, Fe-B dashed), normalized
to peak = 1, with each branch's mode marked at its peak. The mode gap (flat mode -
island mode) is annotated per system; the boron effect is the shrinkage of that gap.
Multi-seed runs are pooled (no error bars).

Output: analysis/figures/Fig_wetModes.png
"""
__version__ = "1.2.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir, E_LABEL

FLAT_COLOR = '#c0392b'      # crimson
ISLAND_COLOR = '#1f618d'    # steel blue
X_MAX = 0.6


def main():
    apply_style()
    jp = os.path.join(ANALYSIS_DIR, 'Fig_wetModes.json')
    if not os.path.exists(jp):
        print(f'  MISSING {jp} — run emit_wetting_modes.py first')
        return
    d = json.load(open(jp))['data']

    fig, ax = plt.subplots(figsize=(6.2, 4.2))

    # four branch densities: flat (red) / island (blue) x Fe/MgO (solid) / Fe-B (dashed)
    for system, ls in (('femgo', '-'), ('febmgo', '--')):
        s = d[system]
        grid = np.array(s['kde_grid'])
        ax.plot(grid, s['flat_density'], color=FLAT_COLOR, ls=ls, lw=1.6, zorder=3)
        ax.plot(grid, s['island_density'], color=ISLAND_COLOR, ls=ls, lw=1.6, zorder=3)

    # mode markers at each branch peak (all peak-normalized, so y = 1.0)
    for system, ls in (('femgo', 'o'), ('febmgo', 's')):
        s = d[system]
        ax.plot(s['flat_mode'], 1.0, marker=ls, color=FLAT_COLOR, ms=7, zorder=5)
        ax.plot(s['island_mode'], 1.0, marker=ls, color=ISLAND_COLOR, ms=7, zorder=5)

    # annotate the mode gap per system: a double-arrow just above the peaks (island -> flat),
    # with a vertical stub dropping from each end to its peak marker, so the span is unambiguous.
    for system, y in (('femgo', 1.06), ('febmgo', 1.14)):
        s = d[system]
        for x in (s['island_mode'], s['flat_mode']):
            ax.plot([x, x], [1.0, y], color='0.55', ls=':', lw=0.9, zorder=4)
        ax.annotate('', xy=(s['flat_mode'], y), xytext=(s['island_mode'], y),
                    arrowprops=dict(arrowstyle='<->', color='0.3', lw=1.2), zorder=6)
        ax.text((s['island_mode'] + s['flat_mode']) / 2, y + 0.015,
                f"{s['mode_gap']:.3f}", ha='center', va='bottom',
                fontsize=9, color='0.25')

    handles = [
        mlines.Line2D([], [], color=FLAT_COLOR, ls='-', lw=1.6, label='Fe/MgO flat'),
        mlines.Line2D([], [], color=FLAT_COLOR, ls='--', lw=1.6, label='Fe-B/MgO flat'),
        mlines.Line2D([], [], color=ISLAND_COLOR, ls='-', lw=1.6, label='Fe/MgO island'),
        mlines.Line2D([], [], color=ISLAND_COLOR, ls='--', lw=1.6, label='Fe-B/MgO island'),
    ]
    ax.legend(handles=handles, fontsize=9, loc='upper right', frameon=True)

    ax.set_xlim(0, X_MAX)
    ax.set_ylim(0, 1.24)
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Normalized density (peak = 1)')

    out = os.path.join(ensure_fig_dir(), 'Fig_wetModes.png')
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {out}')


if __name__ == '__main__':
    main()
