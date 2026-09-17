"""Top-view registry figure: interface Fe sitting atop O (or Mg) on the MgO lattice."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

CASES = [('data/dos_femgo_flatngs/4.xsf', 'FLAT  (all 25 Fe atop O)'),
         ('data/dos_femgo_flatngs/3.xsf', 'ISLAND  (9 interface Fe atop O)')]
CONTACT_CUT = 2.8

fig, axes = plt.subplots(1, 2, figsize=(13, 6.4))
for ax, (xsf, title) in zip(axes, CASES):
    a = read(xsf); sym = np.array(a.get_chemical_symbols()); pos = a.get_positions()
    oxy = pos[sym == 'O'][:, :2]; mxy = pos[sym == 'Mg'][:, :2]
    ax.scatter(mxy[:, 0], mxy[:, 1], s=55, c='#1f9e4f', marker='s',
               edgecolors='black', linewidths=0.4, label='Mg', zorder=2)
    ax.scatter(oxy[:, 0], oxy[:, 1], s=75, c='#d33', marker='o',
               edgecolors='black', linewidths=0.4, label='O', zorder=3)
    fe_idx = np.where(sym == 'Fe')[0]
    opos3 = pos[sym == 'O']
    for i in fe_idx:
        p = pos[i]
        dO = np.linalg.norm(opos3 - p, axis=1).min()
        contact = dO < CONTACT_CUT
        ax.scatter(p[0], p[1], s=230 if contact else 90,
                   facecolors='none', edgecolors='#1f6fd0' if contact else '0.55',
                   linewidths=1.8 if contact else 1.0,
                   zorder=4 if contact else 1)
    ax.set_aspect('equal'); ax.set_title(title, fontweight='bold', fontsize=12)
    ax.set_xlabel('x (Å)'); ax.set_ylabel('y (Å)')
    ax.grid(alpha=0.2, lw=0.5)
    ax.legend(fontsize=9, loc='upper right')
    ax.annotate('blue rings = Fe in O-contact (d$_{Fe-O}$ < 2.8 Å)\n'
                'note: each in-contact Fe is centred on an O',
                xy=(0.02, 0.02), xycoords='axes fraction', fontsize=8.5, color='0.3')
fig.tight_layout(rect=[0, 0, 1, 1])
fig.savefig('figures/interface_registry_topview.png', dpi=300, bbox_inches='tight')
print('wrote figures/interface_registry_topview.png')
