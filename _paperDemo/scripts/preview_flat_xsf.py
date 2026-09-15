"""Side-view render of flat-basin min vs ground-state structures (sanity check)."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

SYSTEMS = [('femgo','Fe/MgO'), ('febmgo','Fe-B/MgO'),
           ('fecomgo','Fe-Co/MgO'), ('fecobmgo','Fe-Co-B/MgO')]
colors = {'Mg':'#1f9e4f','O':'#d33','Fe':'#1f6fd0','Co':'#7b3fbf','B':'#e08a1e'}

fig, axes = plt.subplots(4, 2, figsize=(13, 14))
for i, (system, lab) in enumerate(SYSTEMS):
    for j, (suffix, tag) in enumerate([('flat_min','flat (wet)'), ('ground_min','ground state (island)')]):
        ax = axes[i, j]
        a = read(f'analysis/flat_structures/{system}_{suffix}.xsf')
        sym = np.array(a.get_chemical_symbols()); pos = a.get_positions()
        for s in ['Mg','O','Fe','Co','B']:
            m = sym == s
            if m.any():
                ax.scatter(pos[m,0], pos[m,2], s=(150 if s in ('Fe','Co','B') else 40),
                           c=colors[s], label=s, edgecolors='black', linewidths=0.4)
        mz = np.isin(sym, ('Fe','Co')); z = pos[mz,2]
        ax.axhline(z.min(), ls='--', c='0.5', lw=0.8); ax.axhline(z.max(), ls='--', c='0.5', lw=0.8)
        ax.annotate(f'ΔZ={z.max()-z.min():.2f} Å', xy=(0.03, 0.82), xycoords='axes fraction', fontsize=10)
        ax.set_title(f'{lab} — {tag}', fontweight='bold', fontsize=10)
        ax.set_ylabel('z (Å)'); ax.set_aspect('equal')
        if i == 0 and j == 0:
            ax.legend(fontsize=8, ncol=5, loc='upper right')
fig.suptitle('Flat-basin minimum vs ground-state structures (side view)', fontweight='bold', fontsize=13)
fig.tight_layout()
fig.savefig('figures/flat_vs_ground_preview.png', dpi=200, bbox_inches='tight')
print('wrote figures/flat_vs_ground_preview.png')
