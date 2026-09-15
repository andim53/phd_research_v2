"""PES / wetting analysis for Fe/MgO vs Fe-B/MgO AGOX/GOFEE structure-search DBs.

Reframed around the flat-vs-island picture of the Fe layer on MgO:
  - AGOX/GOFEE (GPR surrogate + LCB) is a BIASED exploration that starts from a
    reference FLAT Fe layer. The database therefore samples a mixture of basins:
    a flat (wetting) basin and an island (dewetting) basin.
  - Relaxation starts at iteration 10, so only structures with iteration >= 10 are used.

Flatness metric:
  dZ = z(Fe_max) - z(Fe_min)   [Angstrom]      dZ ~ 0  =>  flat Fe interface (good wetting)
                                               dZ >> 0 =>  island / 3D Fe clustering

Reference energy:
  dE/N = (E_i - E_globalmin) / N_atoms   [eV/atom],  global min = 0 (per system,
  computed over the iteration>=10 set). This is the PES map coordinate.

Basin analysis:
  Structures are binned by dZ. Within each basin the minimum dE/N is the basin ground
  state. The FLAT basin ground state vs the global minimum is reported per system, so
  we can ask: does B lower the flat-Fe relative energy (bring flat Fe closer to the
  ground state)?

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/pes_analysis.py \
      --min-iteration 10 --flat-dZ 1.0
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, csv, argparse
from agox.databases import Database

D_CUT = 2.6          # Angstrom; Fe-O / B-O bonding cutoff for interfacial contact


def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    cands = db.get_all_candidates()
    data = db.get_all_structures_data()
    return list(zip(cands, data))


def delta_z(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[sym == 'Fe', 2]
    return float(z.max() - z.min()) if len(z) else np.nan


def b_contact_frac(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    if 'B' not in sym:
        return np.nan
    pos = atoms.get_positions()
    bpos = pos[sym == 'B']
    opos = pos[sym == 'O']
    d = np.linalg.norm(bpos[:, None, :] - opos[None, :, :], axis=2).min(axis=1)
    return float((d < D_CUT).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-iteration', type=int, default=10,
                    help='keep structures with iteration >= this (relax starts at 10)')
    ap.add_argument('--flat-dZ', type=float, default=1.0,
                    help='dZ cutoff (Angstrom) below which a structure is "flat"')
    ap.add_argument('--out', default='analysis/pes_structures.csv')
    args = ap.parse_args()

    os.makedirs('analysis', exist_ok=True)
    rows = []
    summary = {}
    for system in ['femgo', 'febmgo']:
        dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
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
        # global min over the filtered set, per system
        gmin = min(r['E_total'] for r in recs)
        for r in recs:
            r['dE_per_atom'] = (r['E_total'] - gmin) / r['n_atoms']
        rows.extend(recs)

        dZ = np.array([r['dZ'] for r in recs])
        dE = np.array([r['dE_per_atom'] for r in recs])
        flat = dZ <= args.flat_dZ
        # basin ground states
        i_flat = None
        if flat.any():
            i_flat = int(np.where(flat)[0][np.argmin(dE[flat])])
            flat_min = dE[i_flat]
        else:
            flat_min = np.nan
        i_glob = int(np.argmin(dE))
        summary[system] = {
            'n': len(recs), 'gmin_eV': gmin,
            'dZ_mean': float(dZ.mean()), 'dZ_flat_frac': float(flat.mean()),
            'global_min_dZ': float(dZ[i_glob]),
            'flat_basin_min_dE': float(flat_min),
            'flat_basin_min_dZ': float(dZ[i_flat]) if i_flat is not None else np.nan,
        }

    cols = ['system','seed','iteration','E_total','n_atoms','dE_per_atom','dZ','B_contact_frac']
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"=== Basin summary (iteration >= {args.min_iteration}; flat = dZ <= {args.flat_dZ} A) ===")
    for system, s in summary.items():
        print(f"\n{system} (n={s['n']})")
        print(f"  global min energy      : {s['gmin_eV']:.2f} eV  (dZ of global min = {s['global_min_dZ']:.2f} A)")
        print(f"  mean dZ                : {s['dZ_mean']:.2f} A")
        print(f"  flat fraction (dZ<={args.flat_dZ}) : {s['dZ_flat_frac']:.3f}")
        print(f"  FLAT-basin min dE/N    : {s['flat_basin_min_dE']:.4f} eV/atom  (at dZ={s['flat_basin_min_dZ']:.2f} A)")
    print(f"\nWrote {len(rows)} rows to {args.out}")


if __name__ == '__main__':
    main()
