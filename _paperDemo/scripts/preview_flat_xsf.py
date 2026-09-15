"""Quick side-view render of the exported flat structures (sanity check), 4 systems."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

SYSTEMS = [('femgo','Fe/MgO'), ('febmgo','Fe-B/MgO'),
           ('fecomgo','Fe-Co/MgO'), ('fecobmgo','Fe-Co-B/MgO')]
fig, axes = plt.subplots(4, 1, figsize=(9, 13))
colors = {'Mg':'#1f9e4f','O':'#d33','Fe':'#1f6fd0','Co':'#7b3fbf','B':'#e08a1e'}
for ax, (system, lab) in zip(axes, SYSTEMS):
    a = read(f'analysis/flat_structures/{system}_flat_min.xsf')
    sym = np.array(a.get_chemical_symbols()); pos = a.get_positions()
    for s in ['Mg','O','Fe','Co','B']:
        m = sym == s
        if m.any():
            ax.scatter(pos[m,0], pos[m,2], s=(150 if s in ('Fe','Co','B') else 45),
                       c=colors[s], label=s, edgecolors='black', linewidths=0.4)
    mz = np.isin(sym, ('Fe','Co'))
    z = pos[mz,2]
    ax.axhline(z.min(), ls='--', c='0.5', lw=0.8); ax.axhline(z.max(), ls='--', c='0.5', lw=0.8)
    ax.annotate(f'ΔZ(metal) = {z.max()-z.min():.2f} Å', xy=(0.02, 0.82),
                xycoords='axes fraction', fontsize=11)
    ax.set_title(lab, fontweight='bold'); ax.set_ylabel('z (Å)')
    ax.legend(fontsize=8, ncol=5, loc='upper right'); ax.set_aspect('equal')
fig.suptitle('Flat-basin minimum structures (side view)', fontweight='bold')
fig.tight_layout()
fig.savefig('figures/flat_structures_preview.png', dpi=200, bbox_inches='tight')
print('wrote figures/flat_structures_preview.png')
