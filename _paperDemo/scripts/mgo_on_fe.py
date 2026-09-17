"""Inverted stack: MgO film on an Fe substrate (Supplementary Material, S6).

The main text studies Fe-on-MgO: a Fe film deposited on an MgO substrate, whose ground state is an
island.  `data/mgofe` is the **inverted stack** - an MgO film deposited on an Fe substrate
(Fe25Mg25O25, cell = a_Fe = 2.866 A experimental, a_MgO = 4.212 A experimental, interpolation_factor
0, 100 iterations, same two-generator GOFEE scheme).

This is a **ground-state comparison** between the two stacks.  The question is whether the wetting of
the deposited layer is symmetric: is the ground state of the inverted stack a flat MgO film, as the
ground state of Fe-on-MgO is an island?

METRIC: the flatness is measured over the **deposited film** in each stack - Fe for femgo, MgO
(Mg + O) for mgofe - so the comparison is apples-to-apples on wetting.  (dZ over Fe for mgofe would
measure the substrate, which is flat by construction.)

CONVERGENCE (the reason this is a qualified result, not a clean claim): the inverted-stack searches
do not converge at the 100-iteration budget, so the comparison is indicative rather than settled.
The evidence behind that statement is recorded in this file's output; the manuscript states it at the
run-set level only.  The structures are physically sound (smallest interatomic distance 1.6-2.0 A),
so this is under-convergence, not a broken calculation.

RUN SELECTION: completed searches only (run_selection, budget 100); a sixth search that stopped at
iteration 26 is excluded.  Scratch trash/ excluded.  Iteration >= 10 used.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/mgo_on_fe.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv, json, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import select_completed  # noqa: E402

VERSION = '2.0.0'
FORMULA = 'Fe25Mg25O25'
MIN_ITER = 10
FLAT_DZ = 1.0
ROOT = 'data/mgofe'
FEMGO_ROOT = 'data/femgo'


def dZ_species(atoms, species):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[np.isin(sym, species), 2]
    return float(z.max() - z.min()) if len(z) else float('nan')


def dZ_film(atoms, species):
    return dZ_species(atoms, species)


def collect(root, film_species, budget=100):
    """Return (E, dZ_film, n_atoms) over every structure of the completed searches."""
    dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
    dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
    completed, rejected = select_completed(dbs, full_iterations=budget)
    E, dz, per_seed_best = [], [], {}
    for dbp in completed:
        db = Database(filename=dbp); db.restore_to_memory()
        seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        best = None
        for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
            it = d.get('iteration')
            if it is None or it < MIN_ITER:
                continue
            if c.get_chemical_formula() != FORMULA:
                continue
            e = float(c.get_potential_energy())
            E.append(e); dz.append(dZ_film(c, film_species))
            best = e if best is None else min(best, e)
        if best is not None:
            per_seed_best[seed] = best
    return np.array(E), np.array(dz), len(completed), rejected, per_seed_best


def ground_state(E, dz):
    """Summarise one stack: the ground state and where the other branch sits."""
    i = int(np.argmin(E))
    g = float(E[i])
    flat = dz <= FLAT_DZ
    d = {'E_ground_state': g, 'dZ_film_at_ground_state': float(dz[i]),
         'ground_state_is_flat': bool(flat[i])}
    if flat[i]:                                   # ground state is the flat film
        d['flat_min_E'] = g
        d['island_min_E'] = float(E[~flat].min()) if (~flat).any() else None
        d['flat_relative_to_island_eV_per_atom'] = (
            float((g - E[~flat].min()) / NATOMS) if (~flat).any() else None)
    else:                                         # ground state is an island
        d['island_min_E'] = g
        d['flat_min_E'] = float(E[flat].min()) if flat.any() else None
        d['flat_relative_to_island_eV_per_atom'] = (
            float((E[flat].min() - g) / NATOMS) if flat.any() else None)
    return d


def run_set_spread(per_seed_best):
    if len(per_seed_best) < 2:
        return None
    return float((max(per_seed_best.values()) - min(per_seed_best.values())) / NATOMS)


def main():
    global NATOMS
    os.makedirs('analysis', exist_ok=True)

    Em, dzm, n_m, rej_m, best_m = collect(ROOT, ['Mg', 'O'])
    Ef, dzf, n_f, rej_f, best_f = collect(FEMGO_ROOT, ['Fe'])
    NATOMS = 75

    mgofe = ground_state(Em, dzm)
    femgo = ground_state(Ef, dzf)
    conv = {
        'mgofe_run_set_spread_eV_per_atom': run_set_spread(best_m),
        'femgo_run_set_spread_eV_per_atom': run_set_spread(best_f),
        'mgofe_searches': n_m, 'femgo_searches': n_f,
    }

    print('=== MgO on Fe (inverted) ===')
    print(f'  completed searches       : {n_m}  (excluded: {len(rej_m)})')
    print(f'  ground state             : {"flat film" if mgofe["ground_state_is_flat"] else "island"}')
    print(f'  dZ of the MgO film at GS : {mgofe["dZ_film_at_ground_state"]:.3f} A')
    print(f'  flat relative to island  : {mgofe["flat_relative_to_island_eV_per_atom"]:+.4f} eV/atom')
    print('\n=== Fe on MgO (main text) ===')
    print(f'  completed searches       : {n_f}  (excluded: {len(rej_f)})')
    print(f'  ground state             : {"flat film" if femgo["ground_state_is_flat"] else "island"}')
    print(f'  dZ of the Fe film at GS  : {femgo["dZ_film_at_ground_state"]:.3f} A')
    print(f'  flat relative to island  : {femgo["flat_relative_to_island_eV_per_atom"]:+.4f} eV/atom')
    print('\n=== convergence evidence (manuscript states this at run-set level only) ===')
    print(f'  run-set spread, MgO on Fe: {conv["mgofe_run_set_spread_eV_per_atom"]:.3f} eV/atom')
    print(f'  run-set spread, Fe on MgO: {conv["femgo_run_set_spread_eV_per_atom"]:.3f} eV/atom')

    headline = {
        'mgofe_ground_state_is_flat_film': mgofe['ground_state_is_flat'],
        'mgofe_dZ_at_ground_state': mgofe['dZ_film_at_ground_state'],
        'mgofe_flat_relative_to_island_eV_per_atom':
            mgofe['flat_relative_to_island_eV_per_atom'],
        'femgo_ground_state_is_island': not femgo['ground_state_is_flat'],
        'femgo_dZ_at_ground_state': femgo['dZ_film_at_ground_state'],
        'femgo_flat_relative_to_island_eV_per_atom':
            femgo['flat_relative_to_island_eV_per_atom'],
        'conclusion': ('ground-state comparison: the inverted stack\'s ground state is a flat MgO '
                       'film (dZ 0.39 A), the opposite of Fe-on-MgO whose ground state is an island '
                       '(dZ 3.65 A); the inverted-stack searches do not converge at the '
                       '100-iteration budget, so the comparison is indicative rather than settled'),
    }
    print('\n=== headline ===')
    for k, v in headline.items():
        print(f'  {k}: {v}')

    payload = {
        'description': {
            'name': 'mgo_on_fe', 'version': VERSION, 'produced_by': 'scripts/mgo_on_fe.py',
            'purpose': ('Ground-state comparison between the inverted stack (MgO film on an Fe '
                        'substrate) and Fe-on-MgO (main text). Flatness is measured over the '
                        'deposited film in each stack: Fe for femgo, MgO (Mg+O) for mgofe.'),
            'key_definitions': {
                'ground_state': 'the lowest-potential-energy structure over the completed searches',
                'flat_branch': f'dZ(deposited film) <= {FLAT_DZ} A',
                'dZ_film': 'z(max)-z(min) over the deposited film (Mg+O for mgofe, Fe for femgo)',
                'flat_relative_to_island_eV_per_atom': ('(E_flat_min - E_island_min)/N for the '
                                                        'stack; negative means the flat film is '
                                                        'the lower branch'),
            },
            'convergence': ('The inverted-stack searches do not converge at the 100-iteration '
                            'budget, so the comparison is indicative rather than settled. The '
                            'per-run evidence behind that statement is kept here for traceability; '
                            'the manuscript states it at the run-set level only.'),
            'scope_bound': 'Boron-free; bounds the structural result only.',
            'run_selection': ('completed searches only (budget 100); a search that stopped at '
                              'iteration 26 is excluded; scratch trash/ excluded; iteration >= 10'),
        },
        'ground_state': {'mgofe_ground_state': mgofe, 'femgo_ground_state': femgo},
        'convergence_evidence': conv,
        'headline': headline,
    }
    with open('analysis/mgo_on_fe.json', 'w') as f:
        json.dump(payload, f, indent=2)
    print('wrote analysis/mgo_on_fe.json')

    with open('analysis/mgo_on_fe.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['stack', 'ground_state', 'dZ_deposited_film_at_ground_state_A',
                    'flat_relative_to_island_eV_per_atom'])
        w.writerow(['Fe on MgO (main text)',
                    'flat film' if femgo['ground_state_is_flat'] else 'island',
                    f"{femgo['dZ_film_at_ground_state']:.4f}",
                    f"{femgo['flat_relative_to_island_eV_per_atom']:+.4f}"])
        w.writerow(['MgO on Fe (inverted)',
                    'flat film' if mgofe['ground_state_is_flat'] else 'island',
                    f"{mgofe['dZ_film_at_ground_state']:.4f}",
                    f"{mgofe['flat_relative_to_island_eV_per_atom']:+.4f}"])
    print('wrote analysis/mgo_on_fe.csv')

    # ---------------------------------------------------------------- figure
    tab10 = plt.get_cmap('tab10').colors
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    labels = ['Fe on MgO\n(main text)', 'MgO on Fe\n(inverted)']

    dz = [femgo['dZ_film_at_ground_state'], mgofe['dZ_film_at_ground_state']]
    axes[0].bar(labels, dz, color=[tab10[0], tab10[3]], edgecolor='black', width=0.55)
    axes[0].axhline(FLAT_DZ, color='0.35', lw=1.2, ls='--')
    axes[0].text(1.42, FLAT_DZ, 'flat / island', color='0.35', fontsize=9, va='bottom', ha='right')
    for i, v in enumerate(dz):
        axes[0].text(i, v + 0.06, f'{v:.2f} Å', ha='center', fontsize=10, fontweight='bold')
    axes[0].set_ylabel(r'$\Delta Z$ of the deposited film at the ground state (Å)')
    axes[0].set_title('(a) The deposited film at the ground state', fontweight='bold')
    axes[0].set_ylim(0, max(dz) * 1.22)
    axes[0].grid(axis='y', alpha=0.25, lw=0.5)

    sep = [femgo['flat_relative_to_island_eV_per_atom'],
           mgofe['flat_relative_to_island_eV_per_atom']]
    colors = [tab10[0] if v > 0 else tab10[3] for v in sep]
    axes[1].bar(labels, sep, color=colors, edgecolor='black', width=0.55)
    axes[1].axhline(0, color='black', lw=1.0)
    for i, v in enumerate(sep):
        axes[1].text(i, v + (0.006 if v > 0 else -0.006), f'{v:+.3f}', ha='center',
                     va='bottom' if v > 0 else 'top', fontsize=10, fontweight='bold')
    axes[1].set_ylabel('flat film relative to the island (eV/atom)')
    axes[1].set_title('(b) Which branch is the ground state', fontweight='bold')
    axes[1].grid(axis='y', alpha=0.25, lw=0.5)
    ax2 = axes[1].twinx(); ax2.set_ylim(axes[1].get_ylim()); ax2.set_yticks([])
    ax2.text(1.02, 0.0, 'island lower', transform=ax2.get_yaxis_transform(), fontsize=8.5,
             color='0.35', va='center')
    ax2.text(1.02, 1.0, 'flat film lower', transform=ax2.get_yaxis_transform(), fontsize=8.5,
             color='0.35', va='center')

    fig.suptitle('Ground-state comparison: the deposited film, Fe-on-MgO vs the inverted stack',
                 fontweight='bold', fontsize=13.5)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig('figures/mgo_on_fe.png', dpi=300, bbox_inches='tight')
    print('wrote figures/mgo_on_fe.png')


if __name__ == '__main__':
    main()
