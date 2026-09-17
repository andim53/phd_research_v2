"""Inverted stack: MgO film on an Fe substrate (Supplementary Material, S6).

The main text studies Fe-on-MgO: a Fe film deposited on an MgO substrate, whose ground state is an
island.  `data/mgofe` is the **inverted stack** - an MgO film deposited on an Fe substrate
(Fe25Mg25O25, cell = a_Fe = 2.866 A experimental, a_MgO = 4.212 A experimental, interpolation_factor
0, 100 iterations, same two-generator GOFEE scheme).  The question is whether the wetting of the
deposited layer is symmetric: does the MgO film on Fe wet (stay flat) or island, and how does that
compare with the Fe film on MgO?

METRIC: the flatness is measured over the **deposited film** in each stack - Fe for femgo, MgO
(Mg + O) for mgofe - so the comparison is apples-to-apples on wetting.  (dZ over Fe for mgofe would
measure the substrate, which is always flat.)

DATA-QUALITY FINDING (the reason this is a qualified result, not a clean claim): the 5 completed
mgofe searches are badly under-converged.  Per-seed best energies span ~59 eV (~0.8 eV/atom),
against ~0.09 eV/atom for the Fe-on-MgO searches, and the structures are physically intact (min
interatomic distance 1.6-2.0 A), so this is a failure to converge at 100 iterations, not a crash.
The lowest-energy structure found is a FLAT MgO film (dZ 0.39 A), ~0.33 eV/atom below the best
island found - the opposite of Fe-on-MgO - but only 1 of 5 completed searches reaches it.  The
flat-film-is-lowest observation therefore rests on essentially one search and is not robust.

RUN SELECTION: completed searches only (run_selection, budget 100); seed_5 stopped at iteration 26
and is excluded.  Scratch trash/ excluded.  Iteration >= 10 used.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/mgo_on_fe.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv, json, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import select_completed  # noqa: E402

VERSION = '1.0.0'
FORMULA = 'Fe25Mg25O25'
MIN_ITER = 10
FLAT_DZ = 1.0
BUDGET = 100
ROOT = 'data/mgofe'
FEMGO_ROOT = 'data/femgo'


def dZ_film(atoms):
    """dZ over the deposited film: Mg + O for mgofe (the MgO film)."""
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[(sym == 'Mg') | (sym == 'O'), 2]
    return float(z.max() - z.min()) if len(z) else float('nan')


def dZ_fe(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[sym == 'Fe', 2]
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
        rows.append((int(it), float(c.get_potential_energy()), len(c), dZ_film(c), dZ_fe(c)))
    rows.sort()
    return rows


def main():
    os.makedirs('analysis', exist_ok=True)
    dbs = sorted(glob.glob(f'{ROOT}/**/*.db', recursive=True))
    dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
    completed, rejected = select_completed(dbs, full_iterations=BUDGET)
    print(f'=== mgofe: {len(completed)} completed, {len(rejected)} excluded ===')
    for d, hi in rejected:
        print(f'  excluded: {os.path.basename(os.path.dirname(os.path.dirname(d)))} @ {hi}')

    per_run, all_rows = [], []
    for dbp in completed:
        seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        rows = load_run(dbp)
        if not rows:
            continue
        all_rows.extend(rows)
        E = np.array([r[1] for r in rows]); zf = np.array([r[3] for r in rows])
        i = int(np.argmin(E))
        flat = zf <= FLAT_DZ
        per_run.append({
            'seed': seed, 'n': len(rows), 'Emin': float(E[i]), 'dZ_film_at_Emin': float(zf[i]),
            'flat_fraction': float(flat.mean()),
            'flat_min_E': float(E[flat].min()) if flat.any() else None,
            'island_min_E': float(E[~flat].min()) if (~flat).any() else None,
        })
        print(f'  {seed:8s} n={len(rows):3d} Emin={E[i]:9.3f} dZ(MgO)@Emin={zf[i]:.2f} '
              f'flatfrac={flat.mean():.3f}')

    # pooled quantities
    E = np.array([r[1] for r in all_rows]); zf = np.array([r[3] for r in all_rows])
    n_at = all_rows[0][2]
    g = E.min(); i_glob = int(np.argmin(E))
    flat = zf <= FLAT_DZ
    best_island = E[~flat].min() if (~flat).any() else None
    pooled = {
        'n_structures': len(all_rows), 'n_seeds': len(per_run),
        'E_global_min': float(g), 'dZ_film_at_global_min': float(zf[i_glob]),
        'global_min_is_flat': bool(zf[i_glob] <= FLAT_DZ),
        'flat_fraction': float(flat.mean()),
        'best_island_E': float(best_island) if best_island is not None else None,
        'flat_island_gap_eV_per_atom': float((g - best_island) / n_at) if best_island is not None else None,
        'n_seeds_reaching_flat_film': int(sum(1 for r in per_run if r['flat_min_E'] is not None)),
        'per_seed_best_spread_eV_per_atom': float((max(r['Emin'] for r in per_run)
                                                    - min(r['Emin'] for r in per_run)) / n_at),
    }
    print('\n=== pooled ===')
    for k, v in pooled.items():
        print(f'  {k}: {v}')

    # femgo comparison (Fe film on MgO): island ground state, flat-basin min 0.1888
    femgo = {}
    fdbs = sorted(glob.glob(f'{FEMGO_ROOT}/**/*.db', recursive=True))
    fdbs = [d for d in fdbs if 'trash' not in d.lower().replace('\\', '/')]
    fcomp, _ = select_completed(fdbs, full_iterations=100)
    frows = []
    for dbp in fcomp:
        db = Database(filename=dbp); db.restore_to_memory()
        for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
            it = d.get('iteration')
            if it is None or it < MIN_ITER:
                continue
            sym = np.array(c.get_chemical_symbols()); z = c.get_positions()[sym == 'Fe', 2]
            frows.append((float(c.get_potential_energy()), float(z.max() - z.min()), len(c)))
    if frows:
        fE = np.array([r[0] for r in frows]); fz = np.array([r[1] for r in frows]); fn = frows[0][2]
        fg = fE.min(); fflat = fz <= FLAT_DZ
        femgo = {
            'n_seeds': len(fcomp), 'n_structures': len(frows),
            'global_min_is_island': bool(fz[int(np.argmin(fE))] > FLAT_DZ),
            'flat_basin_min_eV_per_atom': float((fE[fflat].min() - fg) / fn),
            'per_seed_best_spread_eV_per_atom': None,  # computed below
        }
        # per-seed spread for femgo
        by = {}
        for dbp in fcomp:
            db = Database(filename=dbp); db.restore_to_memory()
            es = [float(c.get_potential_energy()) for c in db.get_all_candidates()]
            by[os.path.basename(os.path.dirname(os.path.dirname(dbp)))] = min(es)
        femgo['per_seed_best_spread_eV_per_atom'] = float((max(by.values()) - min(by.values())) / fn)
        print('\n=== femgo (Fe film on MgO) comparison ===')
        for k, v in femgo.items():
            print(f'  {k}: {v}')

    headline = {
        'mgofe_global_min_is_flat': pooled['global_min_is_flat'],
        'mgofe_flat_film_dZ': pooled['dZ_film_at_global_min'],
        'mgofe_flat_island_gap_eV_per_atom': pooled['flat_island_gap_eV_per_atom'],
        'mgofe_n_seeds_reaching_flat_film': pooled['n_seeds_reaching_flat_film'],
        'mgofe_n_seeds_total': pooled['n_seeds'],
        'mgofe_per_seed_best_spread_eV_per_atom': pooled['per_seed_best_spread_eV_per_atom'],
        'femgo_global_min_is_island': femgo.get('global_min_is_island'),
        'femgo_flat_basin_min_eV_per_atom': femgo.get('flat_basin_min_eV_per_atom'),
        'femgo_per_seed_best_spread_eV_per_atom': femgo.get('per_seed_best_spread_eV_per_atom'),
        'conclusion': ('qualified: the lowest structure found for MgO-on-Fe is a flat MgO film '
                       '(opposite of Fe-on-MgO), but the search does not converge at 100 iterations '
                       '(per-seed best spans ~0.8 eV/atom; only 1 of 5 searches reaches the flat '
                       'film), so this is a weak/negative result, not a clean claim'),
    }
    print('\n=== headline ===')
    for k, v in headline.items():
        print(f'  {k}: {v}')

    payload = {
        'description': {
            'name': 'mgo_on_fe', 'version': VERSION,
            'produced_by': 'scripts/mgo_on_fe.py',
            'purpose': ('Compare the wetting of the deposited layer between Fe-on-MgO (main text) '
                        'and the inverted MgO-on-Fe stack. Flatness is measured over the deposited '
                        'film in each case: Fe for femgo, MgO (Mg+O) for mgofe.'),
            'key_definitions': {
                'flat_branch': f'dZ(film) <= {FLAT_DZ} A', 'min_iteration': MIN_ITER,
                'dZ_film': 'z(max)-z(min) over the deposited film (Mg+O for mgofe, Fe for femgo)',
                'flat_island_gap_eV_per_atom': '(E_flat_min - E_island_min)/N, pooled',
            },
            'data_quality': ('The 5 completed mgofe searches are badly under-converged: per-seed '
                             'best spans ~59 eV (~0.8 eV/atom) against ~0.09 eV/atom for femgo, and '
                             'the structures are physically intact, so this is a failure to '
                             'converge at 100 iterations, not a crash. The flat-film-is-lowest '
                             'observation rests on 1 of 5 searches.'),
            'scope_bound': ('Boron-free; bounds the structural result only.'),
            'run_selection': ('completed searches only (budget 100); seed_5 stopped at 26 and is '
                              'excluded; scratch trash/ excluded; iteration >= 10'),
        },
        'per_run': per_run, 'pooled': pooled, 'femgo_comparison': femgo, 'headline': headline,
    }
    with open('analysis/mgo_on_fe.json', 'w') as f:
        json.dump(payload, f, indent=2)
    print('wrote analysis/mgo_on_fe.json')

    with open('analysis/mgo_on_fe.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['seed', 'n', 'Emin', 'dZ_film_at_Emin', 'flat_fraction',
                    'flat_min_E', 'island_min_E'])
        for r in per_run:
            w.writerow([r['seed'], r['n'], f"{r['Emin']:.4f}", f"{r['dZ_film_at_Emin']:.4f}",
                        f"{r['flat_fraction']:.4f}",
                        '' if r['flat_min_E'] is None else f"{r['flat_min_E']:.4f}",
                        '' if r['island_min_E'] is None else f"{r['island_min_E']:.4f}"])
    print('wrote analysis/mgo_on_fe.csv')

    # ------------------------------------------------------------------ figure
    tab10 = plt.get_cmap('tab10').colors
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))
    # (a) per-seed best energy (shows the 59 eV spread)
    seeds = [r['seed'] for r in per_run]
    emin = [r['Emin'] for r in per_run]
    axes[0].bar(range(len(seeds)), emin, color=tab10[0], edgecolor='black', width=0.6)
    axes[0].set_xticks(range(len(seeds))); axes[0].set_xticklabels(seeds)
    axes[0].set_ylabel('per-seed best energy (eV)')
    axes[0].set_title('(a) Per-seed best — the search does not converge', fontweight='bold')
    axes[0].grid(axis='y', alpha=0.25, lw=0.5)
    # (b) dZ(MgO) at the per-seed best
    dz = [r['dZ_film_at_Emin'] for r in per_run]
    axes[1].bar(range(len(seeds)), dz, color=tab10[1], edgecolor='black', width=0.6)
    axes[1].axhline(FLAT_DZ, color='0.4', lw=1.2, ls='--')
    axes[1].set_xticks(range(len(seeds))); axes[1].set_xticklabels(seeds)
    axes[1].set_ylabel(r'$\Delta Z$ of the MgO film at the best (Å)')
    axes[1].set_title('(b) Only one search finds a flat film', fontweight='bold')
    axes[1].grid(axis='y', alpha=0.25, lw=0.5)
    # (c) flat fraction per seed
    ff = [r['flat_fraction'] for r in per_run]
    axes[2].bar(range(len(seeds)), ff, color=tab10[2], edgecolor='black', width=0.6)
    axes[2].set_xticks(range(len(seeds))); axes[2].set_xticklabels(seeds)
    axes[2].set_ylabel('flat fraction (dZ(MgO) <= 1.0 A)')
    axes[2].set_title('(c) Flat-basin sampling per search', fontweight='bold')
    axes[2].grid(axis='y', alpha=0.25, lw=0.5)
    fig.suptitle('Inverted stack: MgO film on Fe substrate (5 completed searches, 100 iterations)',
                 fontweight='bold', fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig('figures/mgo_on_fe.png', dpi=300, bbox_inches='tight')
    print('wrote figures/mgo_on_fe.png')


if __name__ == '__main__':
    main()
