"""Export the FLAT-basin minimum structure(s) to XSF for inspection.

Reproduces the selection in pes_analysis.py (iteration >= 10, global min = 0 eV/atom,
flat = dZ <= flat-dZ cutoff) and writes the lowest-energy FLAT structure per system.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/export_flat_xsf.py \
      --min-iteration 10 --flat-dZ 1.0
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, argparse
from ase.io import write
from agox.databases import Database

METAL = ('Fe', 'Co')
SYSTEMS = ['femgo', 'febmgo', 'fecomgo', 'fecobmgo']


def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))


def delta_z(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    m = np.isin(sym, METAL)
    z = atoms.get_positions()[m, 2]
    return float(z.max() - z.min()) if len(z) else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-iteration', type=int, default=10)
    ap.add_argument('--flat-dZ', type=float, default=1.0)
    ap.add_argument('--outdir', default='analysis/flat_structures')
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    for system in SYSTEMS:
        dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
        recs = []
        for dbp in dbs:
            seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            for c, d in load_rows(dbp):
                it = d.get('iteration')
                if it is None or it < args.min_iteration:
                    continue
                recs.append((float(c.get_potential_energy()), delta_z(c), seed, int(it), c))
        gmin = min(r[0] for r in recs)
        # flat structures, pick lowest relative energy
        flat = [r for r in recs if r[1] <= args.flat_dZ]
        if not flat:
            print(f"{system}: no flat structures at dZ <= {args.flat_dZ}")
            continue
        flat.sort(key=lambda r: r[0])
        E, dZ, seed, it, atoms = flat[0]
        dE = (E - gmin) / len(atoms)
        out = f"{args.outdir}/{system}_flat_min.xsf"
        write(out, atoms)
        print(f"{system}: wrote {out}")
        print(f"   seed={seed} iteration={it}  dZ={dZ:.3f} A  dE/N={dE:.4f} eV/atom  "
              f"n_atoms={len(atoms)}  E={E:.2f} eV")
        print(f"   composition: {atoms.get_chemical_formula()}")


if __name__ == '__main__':
    main()
