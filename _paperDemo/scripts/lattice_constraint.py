"""Lattice-constraint sensitivity (Supplementary Material, §S5).

The main-text Fe/MgO model takes the Fe lattice constant for the simulation cell, so the **substrate**
carries the in-plane mismatch (MgO compressed against its bulk value) and the film is unstrained -
the inverse of the experimental stack.  This study moves that constraint: the cell is set to

    a_custom = a_Fe + f * (a_MgO/sqrt(2) - a_Fe)

with f = 0.25, 0.75 and 1.0, and both the Fe film and the MgO stack are built on a_custom.  At
f -> 0 the film is at its own lattice constant and the substrate is compressed; at f = 1 the
substrate is at the MgO lattice constant and the film is stretched in-plane.  The mismatch is thus
transferred from one phase to the other along the sweep, and at the endpoints one phase is at its
own equilibrium value.

REFERENCE POINT: the paper's own Fe/MgO model (13 completed searches at 100 iterations, cell = a_Fe)
is reported as the f -> 0 limit.  It is not the same run set as the sweep, and it uses
a_Fe = 2.87019 A against 2.866 A in the sweep, so the comparison is stated with that caveat.
The f = 0 and f = 0.5 arms of this sweep are deliberately outside the paper's scope
(scientist's decision, 2026-09-17).

SCOPE BOUND: all runs here are Fe25Mg25O25 (boron-free).  This study therefore bounds the structural
result - the island ground state and the flat basin being distinct and higher (MT-1, MT-2) - and the
strain-convention limitation.  It does not test the boron effect (MT-3).

RUN SELECTION: each arm is tested against its own 100-iteration budget (run_selection), scratch
`trash/` databases are excluded, and only iteration >= 10 structures are used (relaxation starts at
10).  The a_MgO used to define the far end of the sweep is the experimental MgO lattice constant
(4.212 A as used in the inputs; 4.2112 A nominal).

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/lattice_constraint.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv, json, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import select_completed  # noqa: E402

VERSION = '1.0.0'
METAL = ('Fe', 'Co')
FORMULA = 'Fe25Mg25O25'
MIN_ITER = 10
FLAT_DZ = 1.0
BUDGET = 100                     # every arm in this study is a 100-iteration run

A_FE = 2.866                     # Fe lattice constant used in the sweep inputs
A_MGO = 4.212                    # experimental MgO lattice constant, as used in the inputs

# (label, root, interpolation factor, colour)
ARMS = [
    ('f = 0.25', 'data/latt_conc/3_latt_025', 0.25, '#1f6fd0'),
    ('f = 0.75', 'data/latt_conc/2_latt_075', 0.75, '#2ca02c'),
    ('f = 1.00', 'data/latt_conc/4_latt_100', 1.00, '#d62728'),
]
MAIN_TEXT_ROOT = 'data/femgo'    # the paper's Fe/MgO model, reported as the f -> 0 reference


def dZ_of(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[np.isin(sym, METAL), 2]
    return float(z.max() - z.min()) if len(z) else float('nan')


def load_run(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    rows = []
    for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
        it = d.get('iteration')
        if it is None or it < MIN_ITER:
            continue
        if c.get_chemical_formula() != FORMULA:
            continue
        rows.append((int(it), float(c.get_potential_energy()), len(c), dZ_of(c),
                     float(c.cell[0][0])))
    rows.sort()
    return rows


def run_metrics(rows):
    E = np.array([r[1] for r in rows]); dZ = np.array([r[3] for r in rows]); n_at = rows[0][2]
    g = E.min(); flat = dZ <= FLAT_DZ
    i_glob = int(np.argmin(E))
    out = {'n': len(rows), 'E_gmin': float(g), 'n_atoms': n_at,
           'in_plane_A': float(rows[0][4]),
           'island_ground_state': bool(dZ[i_glob] > FLAT_DZ),
           'dZ_glob': float(dZ[i_glob]),
           'island_dZ_median': float(np.median(dZ[~flat])) if (~flat).any() else None,
           'flat_min_rel': float((E[flat].min() - g) / n_at) if flat.any() else None,
           'flat_fraction': float(flat.mean()), 'n_flat': int(flat.sum())}
    if flat.any() and (~flat).any():
        out['gap'] = float((E[flat].min() - E[~flat].min()) / n_at)
    else:
        out['gap'] = None
    return out


def pooled_metrics(runs):
    allr = [r for rows in runs for r in rows]
    return run_metrics(allr) | {'n_runs': len(runs)}


def main():
    os.makedirs('analysis', exist_ok=True)
    per_run, pooled, rejected_report, rows_by_label = [], {}, [], {}
    for label, root, f, col in ARMS:
        dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
        dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
        completed, rejected = select_completed(dbs, full_iterations=BUDGET)
        for d, hi in rejected:
            rejected_report.append((root, os.path.basename(os.path.dirname(os.path.dirname(d))), hi))
        print(f'=== {label} ({root}): {len(completed)} completed, {len(rejected)} excluded ===')
        loaded = []
        for dbp in completed:
            seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            rows = load_run(dbp)
            if not rows:
                print(f'  {seed}: no usable structures'); continue
            loaded.append(rows)
            m = run_metrics(rows); m.update(arm=label, factor=f, seed=seed, root=root)
            per_run.append(m)
            print(f'  {seed:8s} n={m["n"]:4d} cell={m["in_plane_A"]/5:.5f} A  '
                  f'island-GS={m["island_ground_state"]}  flat_min_rel={m["flat_min_rel"]:.4f}  '
                  f'flat_frac={m["flat_fraction"]:.3f}')
        rows_by_label[label] = loaded
        if loaded:
            p = pooled_metrics(loaded); p.update(arm=label, factor=f, root=root)
            pooled[label] = p
            print(f'  POOLED: n_runs={p["n_runs"]} flat_min_rel={p["flat_min_rel"]:.4f} '
                  f'gap={p["gap"]:.4f} flat_frac={p["flat_fraction"]:.3f} '
                  f'island-GS={p["island_ground_state"]}')

    # the paper's own model at the Fe-matched end of the axis
    ref = {}
    ref_dbs = sorted(glob.glob(f'{MAIN_TEXT_ROOT}/**/*.db', recursive=True))
    ref_dbs = [d for d in ref_dbs if 'trash' not in d.lower().replace('\\', '/')]
    ref_completed, _ = select_completed(ref_dbs, full_iterations=100)
    ref_rows = [load_run(d) for d in ref_completed]
    if ref_rows:
        ref = pooled_metrics(ref_rows)
        ref.update(arm='main text (Fe-matched)', factor=0.0, root=MAIN_TEXT_ROOT)
        rows_by_label[ref['arm']] = ref_rows
        print(f"\n=== reference: main-text Fe/MgO model, {ref['n_runs']} completed searches ===")
        print(f"  cell={ref['in_plane_A']/5:.5f} A  flat_min_rel={ref['flat_min_rel']:.4f}  "
              f"gap={ref['gap']:.4f}  flat_frac={ref['flat_fraction']:.3f}  "
              f"island-GS={ref['island_ground_state']}")

    # ---- strains implied by each constraint ----
    a_mgo_matched = A_MGO / np.sqrt(2)
    strains = {}
    for label, root, f, col in ARMS:
        a_custom = A_FE + f * (a_mgo_matched - A_FE)
        strains[label] = {
            'interpolation_factor': f, 'a_custom': a_custom,
            'film_strain_pct': (a_custom - A_FE) / A_FE * 100,
            'substrate_strain_pct': (a_custom - a_mgo_matched) / a_mgo_matched * 100,
        }
    strains['main text (Fe-matched)'] = {
        'interpolation_factor': 0.0, 'a_custom': 2.87019,
        'film_strain_pct': 0.0,
        'substrate_strain_pct': (2.87019 - a_mgo_matched) / a_mgo_matched * 100,
        'note': 'a_Fe = 2.87019 A here against 2.866 A in the sweep'}

    head = {
        'arms_with_island_ground_state': int(sum(1 for p in pooled.values()
                                                 if p['island_ground_state'])) + int(bool(ref) and ref['island_ground_state']),
        'n_arms_and_reference': len(pooled) + (1 if ref else 0),
        'flat_min_rel_by_factor': {str(p['factor']): p['flat_min_rel']
                                   for p in list(pooled.values()) + ([ref] if ref else [])},
        'gap_by_factor': {str(p['factor']): p['gap']
                          for p in list(pooled.values()) + ([ref] if ref else [])},
        'flat_min_rel_spread_across_arms': float(np.ptp([p['flat_min_rel']
                                                         for p in list(pooled.values()) + ([ref] if ref else [])])),
        'n_runs_total': int(sum(p['n_runs'] for p in pooled.values())),
        'all_runs_island_ground_state': bool(all(m['island_ground_state'] for m in per_run)
                                             and (not ref or ref['island_ground_state'])),
    }
    print('\n=== headline ===')
    for k, v in head.items():
        print(f'  {k}: {v}')

    payload = {
        'description': {
            'name': 'lattice_constraint', 'version': VERSION,
            'produced_by': 'scripts/lattice_constraint.py',
            'purpose': ('Does the paper\'s structural result survive changing which phase sets the '
                        'in-plane lattice? The cell is swept from Fe-matched toward MgO-matched, so '
                        'the mismatch moves off the substrate and onto the film.'),
            'key_definitions': {
                'interpolation_factor f': 'a_custom = a_Fe + f*(a_MgO/sqrt(2) - a_Fe); f = 1 puts the '
                                          'substrate at the experimental MgO lattice constant',
                'a_Fe': A_FE, 'a_MgO_experimental': A_MGO, 'a_MgO_matched': a_mgo_matched,
                'flat_branch': f'ΔZ <= {FLAT_DZ} A', 'min_iteration': MIN_ITER,
                'flat_min_rel': '(E_flat_min - E_global_min)/N within the arm [eV/atom]; the '
                                'main-text definition, normalised per arm',
                'gap': '(E_flat_min - E_island_min)/N within the arm [eV/atom]; identical to '
                       'flat_min_rel whenever the island is the ground state',
            },
            'reference_point': ('the paper\'s Fe/MgO model (13 completed searches, cell = a_Fe) is the '
                                'f -> 0 end of the axis; it uses a_Fe = 2.87019 A against 2.866 A in '
                                'the sweep, and the f = 0 and f = 0.5 arms of the sweep are out of '
                                'scope by decision'),
            'scope_bound': ('All arms are Fe25Mg25O25 (boron-free), so this bounds the structural '
                            'claims (MT-1, MT-2) and the strain-convention limitation, not the boron '
                            'effect (MT-3).'),
            'caveats': [
                'Structures are not DFT-converged (surrogate relaxation + 1 GPAW step).',
                'Absolute energies are not comparable across arms (different cells); only the '
                'separation between the flat and island branches within an arm is meaningful.',
                'Unequal run counts per arm (see n_runs).',
                'The flat fraction is a sampling weight of a biased exploration, not a population.',
            ],
        },
        'arms': {label: {'root': root, 'factor': f, 'budget': BUDGET}
                 for label, root, f, _ in ARMS},
        'strains': strains,
        'excluded_runs': [{'root': r, 'replica': s, 'max_iteration': h} for r, s, h in rejected_report],
        'per_run': per_run, 'pooled_by_arm': pooled, 'main_text_reference': ref, 'headline': head,
    }
    with open('analysis/lattice_constraint.json', 'w') as fh:
        json.dump(payload, fh, indent=2)
    print('wrote analysis/lattice_constraint.json')

    with open('analysis/lattice_constraint.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['arm', 'factor', 'in_plane_A', 'n', 'n_flat', 'flat_fraction',
                    'island_ground_state', 'dZ_glob', 'island_dZ_median',
                    'flat_min_rel_eV_per_atom', 'gap_eV_per_atom'])
        for m in sorted(per_run, key=lambda m: (m['factor'], m['seed'])):
            w.writerow([m['arm'], m['factor'], f"{m['in_plane_A']:.5f}", m['n'], m['n_flat'],
                        f"{m['flat_fraction']:.4f}", int(m['island_ground_state']),
                        f"{m['dZ_glob']:.4f}",
                        '' if m['island_dZ_median'] is None else f"{m['island_dZ_median']:.4f}",
                        '' if m['flat_min_rel'] is None else f"{m['flat_min_rel']:.5f}",
                        '' if m['gap'] is None else f"{m['gap']:.5f}"])
        for p in list(pooled.values()) + ([ref] if ref else []):
            w.writerow([p['arm'] + ' [pooled]', p['factor'], f"{p['in_plane_A']:.5f}", p['n'],
                        p['n_flat'], f"{p['flat_fraction']:.4f}", int(p['island_ground_state']),
                        f"{p['dZ_glob']:.4f}",
                        '' if p['island_dZ_median'] is None else f"{p['island_dZ_median']:.4f}",
                        '' if p['flat_min_rel'] is None else f"{p['flat_min_rel']:.5f}",
                        '' if p['gap'] is None else f"{p['gap']:.5f}"])
    print('wrote analysis/lattice_constraint.csv')

    # ------------------------------------------------------------------ figure
    tab10 = plt.get_cmap('tab10').colors
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))

    # (a) flat-basin separation vs constraint, pooled per arm + per-run scatter
    xs, ys, xs_all, ys_all = [], [], [], []
    for p in sorted(list(pooled.values()) + ([ref] if ref else []), key=lambda p: p['factor']):
        xs.append(p['factor'] * 100); ys.append(p['flat_min_rel'])
        for m in per_run:
            if m['arm'] == p['arm']:
                xs_all.append(p['factor'] * 100); ys_all.append(m['flat_min_rel'])
    axes[0].plot(xs, ys, color='black', lw=1.8, marker='o', ms=8, zorder=4, label='pooled per arm')
    axes[0].scatter(xs_all, ys_all, color=tab10[0], s=45, alpha=0.7, edgecolors='none',
                    label='individual searches', zorder=3)
    axes[0].set_xlabel('constraint: 0 = Fe-matched, 100 = MgO-matched  (%)')
    axes[0].set_ylabel('flat-basin min ΔE/N (eV/atom)')
    axes[0].set_title('(a) Flat–island separation vs the constraint', fontweight='bold')
    axes[0].legend(fontsize=9); axes[0].grid(alpha=0.25, lw=0.5)

    # (b) ΔZ distributions
    arms_order = sorted(list(pooled.values()) + ([ref] if ref else []), key=lambda p: p['factor'])
    for p in arms_order:
        dZ = np.array([r[3] for rows in rows_by_label[p['arm']] for r in rows])
        axes[1].hist(dZ, bins=40, histtype='step', lw=1.8, density=True,
                     color=tab10[arms_order.index(p)], label=f"{p['arm']} (n={len(dZ)})")
    axes[1].axvspan(0, FLAT_DZ, color='0.85', alpha=0.5, zorder=0)
    axes[1].set_xlabel(r'$\Delta Z$ (Å)'); axes[1].set_ylabel('density')
    axes[1].set_title('(b) Basin sampling in each arm', fontweight='bold')
    axes[1].legend(fontsize=9); axes[1].grid(alpha=0.25, lw=0.5)

    # (c) per-run flat-basin minimum, spread within each arm
    for i, p in enumerate(arms_order):
        vals = [m['flat_min_rel'] for m in per_run if m['arm'] == p['arm'] and m['flat_min_rel']]
        if vals:
            axes[2].scatter([i] * len(vals), vals, s=55, edgecolors='black',
                            color=tab10[i], zorder=3)
            axes[2].plot([i - 0.22, i + 0.22], [float(np.median(vals))] * 2, color='black', lw=1.8,
                         zorder=4)
    axes[2].set_xticks(range(len(arms_order)))
    axes[2].set_xticklabels([p['arm'] for p in arms_order], fontsize=9, rotation=10)
    axes[2].set_ylabel('flat-basin min ΔE/N per search (eV/atom)')
    axes[2].set_title('(c) Search-to-search spread within each arm', fontweight='bold')
    axes[2].grid(axis='y', alpha=0.25, lw=0.5)

    fig.suptitle('Lattice-constraint sensitivity — Fe/MgO, no boron (cell swept from Fe-matched '
                 'to MgO-matched)', fontweight='bold', fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig('figures/lattice_constraint.png', dpi=300, bbox_inches='tight')
    print('wrote figures/lattice_constraint.png')


if __name__ == '__main__':
    main()
