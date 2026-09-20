"""
draw_dos.py — Fig_dos: spin-polarized Fe-3d projected DOS, island vs flat.

Sums the per-atom Fe dz2 columns from the two DOS CSVs:
  dos_seed_3.csv -> island ground state (black)
  dos_seed_4.csv -> flat reference (red)
Positive = spin-up, negative = spin-down (mirrored). Fermi level at E-Ef=0.

Output: analysis/figures/Fig_dos.png
"""
__version__ = "1.0.0"

import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, DATA_DIR, ensure_fig_dir

SEED_MAP = {3: ('Island (Ground State)', 'black'),
            4: ('Flat', '#d62728')}
ENERGY_RANGE = (-5.1, 5.1)


def sum_fe_dz2(df):
    """Sum all Fe*_dz2_up / Fe*_dz2_down columns into total up/down."""
    up_cols = [c for c in df.columns if re.match(r'Fe\d+_dz2_up$', c)]
    down_cols = [c for c in df.columns if re.match(r'Fe\d+_dz2_down$', c)]
    return (df[up_cols].sum(axis=1).values,
            df[down_cols].sum(axis=1).values)


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)

    for seed, (name, color) in SEED_MAP.items():
        path = os.path.join(DATA_DIR, 'dos_femgo_flatngs', f'dos_seed_{seed}.csv')
        if not os.path.exists(path):
            print(f"  MISSING {path}"); continue
        df = pd.read_csv(path)
        up, down = sum_fe_dz2(df)
        ax.plot(df['energy'], up, color=color, lw=2, label=name)
        ax.plot(df['energy'], -down, color=color, lw=2, alpha=0.7)

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
