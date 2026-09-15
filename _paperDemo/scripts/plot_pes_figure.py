"""Figures for the four-system PES analysis:
  (1) pes_four_systems.png  — 2x2 PES maps (dE/N vs dZ)
  (2) flat_state_summary.png — flat-basin ground-state comparison (2x2 design: B x Co)
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, csv, os

FLAT_DZ = 1.0
SYSTEMS = [('femgo','Fe/MgO'), ('febmgo','Fe-B/MgO'),
           ('fecomgo','Fe-Co/MgO'), ('fecobmgo','Fe-Co-B/MgO')]
rows = list(csv.DictReader(open('analysis/pes_structures.csv')))
tab10 = plt.get_cmap('tab10').colors
# color by host: Fe host = blue family, Fe-Co host = green family; B = solid/darker
COL = {'femgo': tab10[0], 'febmgo': tab10[3], 'fecomgo': tab10[2], 'fecobmgo': tab10[4]}

def get(system):
    r = [x for x in rows if x['system'] == system]
    return (np.array([float(x['dZ']) for x in r]),
            np.array([float(x['dE_per_atom']) for x in r]))

# ---- Figure 1: 2x2 PES maps ----
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
flat_stats = {}
for ax, (system, lab) in zip(axes.ravel(), SYSTEMS):
    dZ, dE = get(system)
    ax.scatter(dZ, dE, s=12, alpha=0.5, color=COL[system], edgecolors='none')
    ig = int(np.argmin(dE))
    ax.plot(dZ[ig], dE[ig], 'k*', ms=16, label=f'global min (ΔZ={dZ[ig]:.1f} Å)')
    m = dZ <= FLAT_DZ
    if m.any():
        i_f = np.where(m)[0][np.argmin(dE[m])]
        ax.plot(dZ[i_f], dE[i_f], 'D', color='black', ms=8,
                label=f'flat-basin min ({dE[i_f]:.3f} eV/atom)')
        flat_stats[system] = dE[i_f]
    ax.axvspan(0, FLAT_DZ, color='0.85', alpha=0.5, zorder=0)
    ax.set_xlabel(r'$\Delta Z$ = z(metal$_{max}$) - z(metal$_{min}$)  (Å)', fontsize=11)
    ax.set_ylabel(r'$\Delta E/N$  (eV/atom)', fontsize=11)
    ax.set_title(f'{lab}  (n={len(dZ)})', fontsize=12, fontweight='bold')
    ax.set_ylim(-0.01, 0.5); ax.legend(fontsize=8, loc='upper right')
    ax.grid(alpha=0.25, lw=0.5)
fig.suptitle('PES map of metal-film wetting on MgO: flat vs island states\n'
             '(AGOX/GOFEE, iterations \u2265 10, global min = 0 eV/atom, ΔZ over Fe+Co)',
             fontsize=13, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig('figures/pes_four_systems.png', dpi=300, bbox_inches='tight')
print('wrote figures/pes_four_systems.png')

# ---- Figure 2: flat-basin ground-state 2x2 summary ----
fig, ax = plt.subplots(figsize=(7.5, 5.5))
systems = [s for s, _ in SYSTEMS]
vals = [flat_stats.get(s, np.nan) for s in systems]
labels = [l for _, l in SYSTEMS]
colors = [COL[s] for s in systems]
bars = ax.bar(range(4), vals, color=colors, edgecolor='black', width=0.62)
ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=11, rotation=12)
ax.set_ylabel('Flat-basin ground-state\nrelative energy (eV/atom)', fontsize=12)
ax.set_title('Flat-Fe state vs ground state: effect of B and Co', fontsize=13, fontweight='bold')
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.003, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
# bracket annotations for the B effect
def hbar(x0, x1, y, txt):
    ax.plot([x0, x0, x1, x1], [y, y+0.006, y+0.006, y], lw=1.2, color='0.3')
    ax.text((x0+x1)/2, y+0.009, txt, ha='center', fontsize=9, color='0.3')
hbar(0, 1, max(vals)+0.012, f'B effect: {vals[1]-vals[0]:+.3f}')
hbar(2, 3, max(vals)+0.012, f'B effect: {vals[3]-vals[2]:+.3f}')
ax.set_ylim(0, max(vals)+0.05)
ax.grid(axis='y', alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig('figures/flat_state_summary.png', dpi=300, bbox_inches='tight')
print('wrote figures/flat_state_summary.png')
for s, v in zip(systems, vals):
    print(f"  {s}: {v:.4f} eV/atom")
