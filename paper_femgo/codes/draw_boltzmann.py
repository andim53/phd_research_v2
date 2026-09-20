"""
draw_boltzmann.py — Fig_Boltz: temperature-dependent Boltzmann probability.

P(E) = g(E) * exp(-(E-E_glob)/k_B T) / Z, weighted by the KDE state density,
over the minimum-ensemble (iteration >= 10). Temperatures 300-10000 K,
color gradient dark blue -> light yellow (plasma-like), matching the draft.

Output: analysis/figures/Fig_Boltz.png
"""
__version__ = "1.0.0"

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, femgo_db_paths, load_agox_ensemble,
                    rel_energy_per_atom, ensure_fig_dir, E_LABEL)

KB = 8.617333262e-5  # eV/K
TEMPS = np.linspace(300, 10000, 10)
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


def main():
    apply_style()
    db_paths = femgo_db_paths()
    energies, atoms, _ = load_agox_ensemble(db_paths, start_iter=10)
    if len(energies) == 0:
        print("No ensemble data"); return

    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    kde = gaussian_kde(rel)

    # energy grid for smooth curves
    grid = np.linspace(rel.min(), rel.max(), 1000)
    rho = kde.evaluate(grid) + 1e-15

    fig, ax = plt.subplots(figsize=(5, 4), dpi=300)

    for T, color in zip(TEMPS, COLORS_PLASMA):
        weights = rho * np.exp(-grid / (KB * T))
        Z = np.sum(weights)
        probs = weights / Z
        probs = probs / probs.max()          # peak-normalize (visualization)
        ax.plot(grid, probs, color=color, lw=1.5, label=f'{int(T)} K')

    # mark the two high-degeneracy peaks
    for e, lab in [(0.075, 'Islands'), (0.255, 'Flat')]:
        ax.axvline(x=e, color='black', linestyle='--', linewidth=1, alpha=0.5)
        t = ax.text(e, 0.02, lab, fontsize=8, rotation=90,
                    verticalalignment='bottom', horizontalalignment='right')
        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('Probability P(E) (peak-normalized)')
    ax.set_xlim(0, rel.max() + 0.05)
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, loc='upper right', fontsize=8)

    out = os.path.join(ensure_fig_dir(), 'Fig_Boltz.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
