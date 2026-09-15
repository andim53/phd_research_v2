"""PES-map figure: relative energy per atom vs Delta-Z (Fe layer flatness).

Left: energy-landscape (PES) projection, dE/N vs dZ, one panel per system, showing the
flat basin (dZ~0) and island basin (dZ~3-4 A). Marks the global minimum and the
flat-basin minimum. Right: combined overlay + flat-basin ground-state comparison bar.

High contrast, projectable (tab10 solid colors, no pale washes).
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, csv, os

FLAT_DZ = 1.0

rows = list(csv.DictReader(open('analysis/pes_structures.csv')))
def get(system):
    r = [x for x in rows if x['system'] == system]
    dZ = np.array([float(x['dZ']) for x in r])
    dE = np.array([float(x['dE_per_atom']) for x in r])
    return dZ, dE

tab10 = plt.get_cmap('tab10').colors
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
specs = [('femgo', tab10[0], 'Fe / MgO'), ('febmgo', tab10[1], 'Fe-B / MgO')]

# panels 1 & 2: PES maps
flat_stats = {}
for ax, (system, color, lab) in zip(axes[:2], specs):
    dZ, dE = get(system)
    ax.scatter(dZ, dE, s=14, alpha=0.55, color=color, edgecolors='none')
    # global min
    ig = int(np.argmin(dE))
    ax.plot(dZ[ig], dE[ig], 'k*', ms=18, label=f'global min (dZ={dZ[ig]:.1f} Å)')
    # flat basin min
    m = dZ <= FLAT_DZ
    if m.any():
        i_f = np.where(m)[0][np.argmin(dE[m])]
        ax.plot(dZ[i_f], dE[i_f], marker='D', color='black', ms=9,
                label=f'flat-basin min ({dE[i_f]:.3f} eV/atom)')
        flat_stats[system] = dE[i_f]
    ax.axvspan(0, FLAT_DZ, color='0.85', alpha=0.5, zorder=0)
    ax.set_xlabel(r'$\Delta Z$ = z(Fe$_{max}$) - z(Fe$_{min}$)  (Å)', fontsize=12)
    ax.set_ylabel(r'$\Delta E/N$  (eV/atom)', fontsize=12)
    ax.set_title(f'{lab}  (n={len(dZ)})', fontsize=13, fontweight='bold')
    ax.set_ylim(-0.01, 0.5)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(alpha=0.25, lw=0.5)
    ax.annotate('flat\n(wetting)', xy=(0.5, 0.45), ha='center', fontsize=9, color='0.35')
    ax.annotate('island\n(dewetting)', xy=(4.0, 0.45), ha='center', fontsize=9, color='0.35')

# panel 3: flat-basin ground-state comparison
ax = axes[2]
systems = ['femgo', 'febmgo']
vals = [flat_stats.get(s, np.nan) for s in systems]
bars = ax.bar([0, 1], vals, color=[tab10[0], tab10[1]], edgecolor='black', width=0.6)
ax.set_xticks([0, 1]); ax.set_xticklabels(['Fe / MgO', 'Fe-B / MgO'], fontsize=12)
ax.set_ylabel('Flat-basin ground-state\nrelative energy (eV/atom)', fontsize=12)
ax.set_title('Flat-Fe state vs ground state', fontsize=13, fontweight='bold')
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.003, f'{v:.3f}', ha='center', fontsize=11, fontweight='bold')
ax.grid(axis='y', alpha=0.25, lw=0.5)

fig.suptitle('Potential-energy-surface map of Fe wetting on MgO: flat vs island states\n'
             '(AGOX/GOFEE, iterations \u2265 10, global min = 0 eV/atom)',
             fontsize=14, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.90])
os.makedirs('figures', exist_ok=True)
out = 'figures/pes_flat_island.png'
fig.savefig(out, dpi=300, bbox_inches='tight')
print('wrote', out)
for s, v in flat_stats.items():
    print(f"  {s} flat-basin min dE/N = {v:.4f} eV/atom")
