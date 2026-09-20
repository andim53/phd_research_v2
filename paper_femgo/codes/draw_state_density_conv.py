"""
draw_state_density_conv.py — Fig_convStateDens: state-density convergence.

Compares g(E) from a single seed (black) against cumulative distributions
formed by aggregating seeds sequentially (shades of blue), matching the draft.

Output: analysis/figures/Fig_convStateDens.png
"""
__version__ = "1.0.0"

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, femgo_db_paths, load_agox_ensemble,
                    rel_energy_per_atom, ensure_fig_dir, E_LABEL, DENSITY_LABEL)

E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)


def main():
    apply_style()
    db_paths = femgo_db_paths()
    if not db_paths:
        print("No femgo dbs"); return

    # per-seed relative energies
    per_seed = []
    for p in db_paths:
        energies, atoms, _ = load_agox_ensemble([p], start_iter=10)
        if len(energies) == 0:
            continue
        n_atoms = len(atoms[0])
        per_seed.append(rel_energy_per_atom(energies, n_atoms))

    min_e, max_e = E_LIMIT[0], E_LIMIT[1]
    grid = np.linspace(min_e, max_e, 200)

    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)

    # single seed (seed 0 of the paper = first on disk) in black
    kde0 = gaussian_kde(per_seed[0])
    ax.plot(kde0.evaluate(grid), grid, color='black', lw=1.5, label='Seed 0')

    # cumulative aggregation in shades of blue
    blues = plt.cm.Blues(np.linspace(0.85, 0.35, len(per_seed)))
    cum = np.concatenate(per_seed[:1])
    for i in range(1, len(per_seed)):
        cum = np.concatenate([cum, per_seed[i]])
        kde = gaussian_kde(cum)
        ax.plot(kde.evaluate(grid), grid, color=blues[i], lw=1.2,
                label=f'Seeds 0-{i}')

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
