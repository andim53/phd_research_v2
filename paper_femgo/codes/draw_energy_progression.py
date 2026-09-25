"""
draw_energy_progression.py — Fig_Prog: GPR optimization energy progression.

Reads the emitted dataset (analysis/Fig_Prog.json) and plots best-so-far
relative energy vs evaluated-candidate count for each independent Fe-on-MgO
run, in the _analysist plot_energy_progression style. Runs are labeled
Run 1..13 (on-disk seeds 3..15 renumbered).

Run emit_datasets.py first. Output: analysis/figures/Fig_Prog.png
"""
__version__ = "1.3.1"

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import apply_style, ANALYSIS_DIR, ensure_fig_dir, E_LABEL


def main():
    apply_style()
    json_path = os.path.join(ANALYSIS_DIR, 'Fig_Prog.json')
    if not os.path.exists(json_path):
        print(f"  MISSING {json_path} — run emit_datasets.py first")
        return
    data = json.load(open(json_path))['data']

    fig, ax = plt.subplots(figsize=(5, 4), dpi=300)
    # 13 distinct colors from viridis, single solid linestyle per run
    viridis = plt.cm.viridis(np.linspace(0.0, 0.9, len(data)))

    for i, (run, d) in enumerate(data.items()):
        x = d['candidate_count']
        y = d['best_rel_energy']
        ax.plot(x, y, linewidth=1.4, linestyle='-',
                color=viridis[i], label=run, zorder=3)

    ax.set_xlabel('Evaluated Candidate Count ($N_i$)')
    ax.set_ylabel(E_LABEL)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.legend(loc='best', fontsize=8, frameon=True, ncol=2)

    out = os.path.join(ensure_fig_dir(), 'Fig_Prog.png')
    plt.tight_layout()
    plt.savefig(out, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
