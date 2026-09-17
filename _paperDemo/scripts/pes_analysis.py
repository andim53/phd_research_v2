"""PES / wetting analysis across four systems:
    femgo    = Fe/MgO
    febmgo   = Fe-B/MgO
    fecomgo  = Fe-Co/MgO
    fecobmgo = Fe-Co-B/MgO

Flat-vs-island picture of the metal film on MgO:
  - AGOX/GOFEE (GPR surrogate + LCB) is a BIASED exploration starting from a reference
    FLAT metal layer, so the database samples a mixture of a flat (wetting) basin and an
    island (dewetting) basin.
  - Relaxation starts at iteration 10 -> only iteration >= 10 structures are used.

Flatness metric:
  dZ = z(metal_max) - z(metal_min)   [Angstrom], metal = Fe + Co (the film).
  dZ ~ 0  => flat film (good wetting);  dZ >> 0 => island / 3D clustering.

PES coordinate:
  dE/N = (E_i - E_globalmin) / N_atoms   [eV/atom], global min = 0, computed per system
  over the iteration>=10 set.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/pes_analysis.py \
      --min-iteration 10 --flat-dZ 1.0
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, csv, argparse, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import FULL_ITERATIONS, completed_dbs  # noqa: E402

METAL = ('Fe', 'Co')     # film species for the dZ flatness metric
D_CUT = 2.6              # Angstrom; B-O bonding cutoff

SYSTEMS = ['femgo', 'febmgo', 'fecomgo', 'fecobmgo']
LABELS = {'femgo': 'Fe/MgO', 'febmgo': 'Fe-B/MgO',
          'fecomgo': 'Fe-Co/MgO', 'fecobmgo': 'Fe-Co-B/MgO'}


def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))


def delta_z(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    m = np.isin(sym, METAL)
    z = atoms.get_positions()[m, 2]
    return float(z.max() - z.min()) if len(z) else np.nan


def b_contact_frac(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    if 'B' not in sym:
        return np.nan
    pos = atoms.get_positions()
    bpos = pos[sym == 'B']; opos = pos[sym == 'O']
    d = np.linalg.norm(bpos[:, None, :] - opos[None, :, :], axis=2).min(axis=1)
    return float((d < D_CUT).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-iteration', type=int, default=10)
    ap.add_argument('--flat-dZ', type=float, default=1.0)
    ap.add_argument('--out', default='analysis/pes_structures.csv')
    args = ap.parse_args()

    os.makedirs('analysis', exist_ok=True)
    rows, summary = [], {}
    for system in SYSTEMS:
        # only searches that ran the full iteration budget (see run_selection)
        dbs, rejected = completed_dbs(f'data/{system}/*/1_db/db_*.db', verbose=True)
        if rejected:
            print(f'    ({len(rejected)} unfinished run(s) excluded for {system})')
        recs = []
        for dbp in dbs:
            for c, d in load_rows(dbp):
                it = d.get('iteration')
                if it is None or it < args.min_iteration:
                    continue
                recs.append({
                    'system': system,
                    'seed': os.path.basename(os.path.dirname(os.path.dirname(dbp))),
                    'iteration': int(it),
                    'E_total': float(c.get_potential_energy()),
                    'n_atoms': len(c),
                    'dZ': delta_z(c),
                    'B_contact_frac': b_contact_frac(c),
                })
        gmin = min(r['E_total'] for r in recs)
        for r in recs:
            r['dE_per_atom'] = (r['E_total'] - gmin) / r['n_atoms']
        rows.extend(recs)

        dZ = np.array([r['dZ'] for r in recs])
        dE = np.array([r['dE_per_atom'] for r in recs])
        flat = dZ <= args.flat_dZ
        i_flat = None
        if flat.any():
            i_flat = int(np.where(flat)[0][np.argmin(dE[flat])])
            flat_min = dE[i_flat]
        else:
            flat_min = np.nan
        i_glob = int(np.argmin(dE))
        summary[system] = {
            'n': len(recs), 'n_seeds': len(dbs), 'gmin_eV': gmin,
            'dZ_mean': float(dZ.mean()), 'dZ_flat_frac': float(flat.mean()),
            'global_min_dZ': float(dZ[i_glob]),
            'flat_basin_min_dE': float(flat_min),
            'flat_basin_min_dZ': float(dZ[i_flat]) if i_flat is not None else np.nan,
        }

    cols = ['system','seed','iteration','E_total','n_atoms','dE_per_atom','dZ','B_contact_frac']
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"=== Basin summary (iteration >= {args.min_iteration}; flat = dZ <= {args.flat_dZ} A; "
          f"dZ over {'+'.join(METAL)}) ===")
    for system in SYSTEMS:
        s = summary[system]
        print(f"\n{LABELS[system]:14s} n={s['n']:5d} seeds={s['n_seeds']}")
        print(f"   global-min dZ = {s['global_min_dZ']:5.2f} A | mean dZ = {s['dZ_mean']:4.2f} A | "
              f"flat frac = {s['dZ_flat_frac']:.3f}")
        print(f"   FLAT-basin min dE/N = {s['flat_basin_min_dE']:.4f} eV/atom (at dZ={s['flat_basin_min_dZ']:.2f} A)")
    print(f"\nWrote {len(rows)} rows to {args.out}")


if __name__ == '__main__':
    main()
