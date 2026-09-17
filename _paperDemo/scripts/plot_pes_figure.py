"""Figures for the PES analysis: one panel per analysed system.

  (1) figures/pes_<n>_systems.png    — PES maps (dE/N vs dZ), one panel per system
  (2) figures/flat_state_summary.png — flat-basin ground-state comparison, one bar per system,
                                       with the B effect bracketed between successive pairs

Scope (v9): the paper studies the Fe host only, Fe/MgO and Fe-B/MgO, so this writes
`pes_2_systems.png` (1x2 panels) and a two-bar summary.  Run `scripts/scope.py` for why; if
`analysis/pes_structures.csv` holds all four systems (`ensemble_analysis.py --all-systems`) the
grid, the summary and the file name grow accordingly.

NOTE — figure design is the scientist's call.  The mechanical scope changes made here (panel
count, output file name, the shared energy range anchored to the boron-free reference) are recorded
with the open styling questions in `figures/INSTRUCTION.md`; do not restyle this script without
reading it.
"""
__version__ = '1.2.1'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scope import SYSTEMS_IN_SCOPE, label  # noqa: E402

FLAT_DZ = 1.0

rows = list(csv.DictReader(open('analysis/pes_structures.csv')))
present = sorted({r['system'] for r in rows}, key=lambda s: list(SYSTEMS_IN_SCOPE).index(s)
                 if s in SYSTEMS_IN_SCOPE else 99)
if '--all-systems' not in sys.argv:                  # paper scope unless asked otherwise
    present = [s for s in present if s in SYSTEMS_IN_SCOPE]
if not present:
    raise SystemExit('no systems in analysis/pes_structures.csv for the current scope — '
                     'run scripts/pes_analysis.py first')
SYSTEMS = [(s, label(s)) for s in present]

tab10 = plt.get_cmap('tab10').colors
# color by host: Fe host = blue family; B = the warmer member of the pair
COL = {'femgo': tab10[0], 'febmgo': tab10[3], 'fecomgo': tab10[2], 'fecobmgo': tab10[4]}


def get(system):
    r = [x for x in rows if x['system'] == system]
    return (np.array([float(x['dZ']) for x in r]),
            np.array([float(x['dE_per_atom']) for x in r]))


# ---- Figure 1: one PES map per system ----
# One energy range for every panel, anchored to the BORON-FREE Fe/MgO model (the reference), so the
# two systems are read on a single scale.  This is a deliberate ceiling, not a data-driven union:
# the Fe-B/MgO searches reach much higher dE/N (up to 2.15 eV/atom), and drawing the reference on
# that union range would compress the flat-island region that the figure is about.  Structures above
# the ceiling are therefore NOT shown in the Fe-B panel; their number is printed below so it stays
# on the record.  (Scientist's decision, 2026-09-18.)
REFERENCE = SYSTEMS[0][0]
Y_LIM = (-0.01, max(0.5, 1.05 * float(get(REFERENCE)[1].max())))
n = len(SYSTEMS)
ncols = min(2, n)
nrows = int(np.ceil(n / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(6.2 * ncols, 5.2 * nrows), squeeze=False)
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
    ax.set_ylim(*Y_LIM)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(alpha=0.25, lw=0.5)
for ax in axes.ravel()[n:]:                            # hide any unused panel
    ax.axis('off')
for system, lab in SYSTEMS:                            # what the shared ceiling hides
    dE = get(system)[1]
    k = int((dE > Y_LIM[1]).sum())
    if k:
        print(f'  {lab}: {k} of {len(dE)} points ({100 * k / len(dE):.1f} %) above the shared '
              f'{Y_LIM[1]:.3f} eV/atom ceiling — not shown in the panel')
fig.tight_layout(rect=[0, 0, 1, 1])
out1 = f'figures/pes_{n}_systems.png'
fig.savefig(out1, dpi=300, bbox_inches='tight')
print(f'wrote {out1}')

# ---- Figure 2: flat-basin ground-state comparison, one bar per system ----
fig, ax = plt.subplots(figsize=(2.6 + 2.4 * n, 5.5))
systems = [s for s, _ in SYSTEMS]
vals = [flat_stats.get(s, np.nan) for s in systems]
labels = [str(l) for _, l in SYSTEMS]
colors = [COL[s] for s in systems]
bars = ax.bar(range(n), vals, color=colors, edgecolor='black', width=0.62)
ax.set_xticks(range(n)); ax.set_xticklabels(labels, fontsize=11, rotation=12)
ax.set_ylabel('Flat-basin ground-state\nrelative energy (eV/atom)', fontsize=12)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.003, f'{v:.3f}', ha='center',
            fontsize=10, fontweight='bold')


# bracket annotations for the B effect, successive pairs
def hbar(x0, x1, y, txt):
    ax.plot([x0, x0, x1, x1], [y, y + 0.006, y + 0.006, y], lw=1.2, color='0.3')
    ax.text((x0 + x1) / 2, y + 0.009, txt, ha='center', fontsize=9, color='0.3')


ytop = float(np.nanmax(vals))
for k in range(0, n - 1, 2):
    hbar(k, k + 1, ytop + 0.012, f'B effect: {vals[k + 1] - vals[k]:+.3f}')
ax.set_ylim(0, ytop + 0.05)
ax.grid(axis='y', alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig('figures/flat_state_summary.png', dpi=300, bbox_inches='tight')
print('wrote figures/flat_state_summary.png')
for s, v in zip(systems, vals):
    print(f"  {s}: {v:.4f} eV/atom")
