"""
draw_state_density_conv.py — Fig_convStateDens: state-density convergence.

Reads the emitted dataset (analysis/Fig_convStateDens.json) and plots g(E)
from a single run (black) against cumulative distributions (shades of blue).
Runs are labeled Run 1..13 (on-disk seeds 3..15 renumbered).

Run emit_datasets.py first. Output: analysis/figures/Fig_convStateDens.png
"""
__version__ = "1.4.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir, E_LABEL, DENSITY_LABEL

E_LIMIT = (0.0 - 0.1, 0.7, 5)  # relative-energy axis capped at 0.7 eV/atom (owner)


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_convStateDens.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    d = json.load(open(json_path))['data']
    grid = np.array(d['grid'])
    curves = d['curves']

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)

    # single run in black
    ax.plot(curves['Run 1'], grid, color='black', lw=1.0, label='Run 1')

    # cumulative in shades of blue
    blues = plt.cm.Blues(np.linspace(0.85, 0.35, len(curves) - 1))
    for i, (name, dens) in enumerate(curves.items()):
        if name == 'Run 1':
            continue
        ax.plot(dens, grid, color=blues[i - 1], lw=0.9, label=name)

    ax.set_xlabel(DENSITY_LABEL)
    ax.set_ylabel(E_LABEL)
    ax.set_ylim(min_e, max_e)
    ax.legend(frameon=False, loc='upper right', fontsize=7)

    out = os.path.join(ensure_fig_dir(), 'Fig_convStateDens.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
