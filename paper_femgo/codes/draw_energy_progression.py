"""
draw_energy_progression.py — Fig_Prog: GPR optimization energy progression.

Plots best-so-far relative energy (E_i - E_glob)/N vs evaluated-candidate count
for each independent Fe-on-MgO seed, in the _analysist plot_energy_progression
style. Uses the paper's minimum-ensemble definition (iteration >= 10).

Output: analysis/figures/Fig_Prog.png
"""
__version__ = "1.0.0"

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, femgo_db_paths, load_agox_ensemble,
                    rel_energy_per_atom, ensure_fig_dir, E_LABEL)


def best_so_far(rel):
    """Cumulative minimum of the relative-energy series."""
    return np.minimum.accumulate(rel)


def main():
    apply_style()
    db_paths = femgo_db_paths()
    if not db_paths:
        print("No femgo dbs found")
        return

    fig, ax = plt.subplots(figsize=(5, 4), dpi=300)

    colors = ['#1B70FC', '#E31A1C', '#33A02C', '#FF7F00']
    line_styles = [':', '--', '-', '-.']

    for i, p in enumerate(db_paths):
        energies, atoms, meta = load_agox_ensemble([p], start_iter=10)
        if len(energies) == 0:
            continue
        n_atoms = len(atoms[0])
        rel = rel_energy_per_atom(energies, n_atoms)
        # order by iteration (candidate count) so the x-axis is monotonic
        order = np.argsort([m.get('iteration', 0) for m in meta])
        rel = rel[order]
        best = best_so_far(rel)
        x = np.arange(1, len(best) + 1)
        ax.plot(x, best, linewidth=1.8,
                linestyle=line_styles[i % len(line_styles)],
                color=colors[i % len(colors)],
                label=f'Seed {os.path.basename(os.path.dirname(os.path.dirname(p))).replace("seed_", "")}',
                zorder=3)

    ax.set_xlabel('Evaluated Candidate Count ($N_i$)')
    ax.set_ylabel(E_LABEL)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.legend(loc='best', fontsize=8, frameon=False, ncol=2)

    out = os.path.join(ensure_fig_dir(), 'Fig_Prog.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
