"""Quick side-view render of the exported flat structures (sanity check)."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

fig, axes = plt.subplots(2, 1, figsize=(9, 7))
for ax, path, lab in zip(axes,
        ['analysis/flat_structures/femgo_flat_min.xsf',
         'analysis/flat_structures/febmgo_flat_min.xsf'],
        ['Fe / MgO  (flat-basin min)', 'Fe-B / MgO  (flat-basin min)']):
    a = read(path)
    sym = np.array(a.get_chemical_symbols())
    pos = a.get_positions()
    colors = {'Mg':'#1f9e4f','O':'#d33','Fe':'#1f6fd0','B':'#e08a1e'}
    for s in ['Mg','O','Fe','B']:
        m = sym==s
        if m.any():
            ax.scatter(pos[m,0], pos[m,2], s=(180 if s in ('Fe','B') else 60),
                       c=colors[s], label=s, edgecolors='black', linewidths=0.4)
    fez = pos[sym=='Fe',2]
    ax.axhline(fez.min(), ls='--', c='0.5', lw=0.8)
    ax.axhline(fez.max(), ls='--', c='0.5', lw=0.8)
    ax.annotate(f'ΔZ = {fez.max()-fez.min():.2f} Å', xy=(0.02, 0.85), xycoords='axes fraction', fontsize=11)
    ax.set_title(lab, fontweight='bold'); ax.set_xlabel('x (Å)'); ax.set_ylabel('z (Å)')
    ax.legend(fontsize=8, ncol=4); ax.set_aspect('equal')
fig.suptitle('Flat-basin minimum structures (side view)', fontweight='bold')
fig.tight_layout()
fig.savefig('figures/flat_structures_preview.png', dpi=200, bbox_inches='tight')
print('wrote figures/flat_structures_preview.png')
