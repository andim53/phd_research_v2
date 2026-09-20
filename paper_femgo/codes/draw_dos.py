"""
draw_dos.py — Fig_dos: spin-polarized Fe-3d projected DOS, island vs flat.

Reads the emitted dataset (analysis/Fig_dos.json) and plots the summed Fe-dz2
PDOS for the island (black) and flat (red) configurations. Positive = spin-up,
negative = spin-down (mirrored). Fermi level at E-Ef=0.

Run emit_datasets.py first. Output: analysis/figures/Fig_dos.png
"""
__version__ = "1.1.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir

ENERGY_RANGE = (-5.1, 5.1)
STYLE = {'island': ('Island (Ground State)', 'black'),
         'flat': ('Flat', '#d62728')}


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_dos.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    data = json.load(open(json_path))['data']

    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
    for key, (name, color) in STYLE.items():
        if key not in data:
            continue
        d = data[key]
        ax.plot(d['energy'], d['fe_dz2_up'], color=color, lw=2, label=name)
        ax.plot(d['energy'], [-x for x in d['fe_dz2_down']], color=color, lw=2, alpha=0.7)

    ax.axvline(x=0, color='black', linestyle=':', alpha=0.5)
    ax.axhline(y=0, color='black', lw=0.8)
    ax.set_xlim(ENERGY_RANGE)
    ax.set_xlabel(r'$E - E_f$ (eV)')
    ax.set_ylabel('Fe-3d PDOS (states/eV)')
    ax.legend(frameon=False, loc='lower right')

    out = os.path.join(ensure_fig_dir(), 'Fig_dos.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
