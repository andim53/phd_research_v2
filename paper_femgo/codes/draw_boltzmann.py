"""
draw_boltzmann.py — Fig_Boltz: temperature-dependent Boltzmann probability.

Reads the emitted dataset (analysis/Fig_Boltz.json) and plots P(E) for
temperatures 300-10000 K, color gradient dark blue -> light yellow.

Run emit_datasets.py first. Output: analysis/figures/Fig_Boltz.png
"""
__version__ = "1.4.0"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir, E_LABEL

COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_Boltz.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    data = json.load(open(json_path))['data']

    fig, ax = plt.subplots(figsize=(5, 4), dpi=300)
    for i, (T, d) in enumerate(data.items()):
        ax.plot(d['energy'], d['prob'], color=COLORS_PLASMA[i % len(COLORS_PLASMA)],
                lw=1.0, label=f'{T} K')

    for e, lab in [(0.075, 'Islands'), (0.255, 'Flat')]:
        vline = ax.axvline(x=e, color='black', linestyle='--',
                           linewidth=1.2, alpha=1.0, zorder=20)
        vline.set_path_effects(
            [patheffects.withStroke(linewidth=3.5, foreground='white')]
        )
        t = ax.text(e, 0.02, lab, fontsize=8, rotation=90,
                    verticalalignment='bottom', horizontalalignment='right')
        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E) (peak-normalized)')
    ax.set_xlim(0.0, 0.7)  # relative-energy (x) axis capped at 0.7 eV/atom (owner)
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, loc='upper right', fontsize=8)

    out = os.path.join(ensure_fig_dir(), 'Fig_Boltz.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
