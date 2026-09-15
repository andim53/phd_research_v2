"""Export FLAT-basin minimum AND lowest-energy (island) structures to XSF.

Reproduces the selection in pes_analysis.py (iteration >= 10, global min = 0 eV/atom,
flat = dZ <= flat-dZ cutoff) and writes, per system:
  - {system}_flat_min.xsf   : lowest-energy FLAT structure (dZ <= flat-dZ)
  - {system}_ground_min.xsf : lowest-energy structure found overall (island-like)

NOTE: these structures are NOT DFT-converged (residual forces ~1-2 eV/A); see the
relaxation caveat in experiment_log.md and the `relaxation/` pipeline.

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

        # --- ground state (global minimum) ---
        E_g, dZ_g, seed_g, it_g, atoms_g = min(recs, key=lambda r: r[0])
        out_g = f"{args.outdir}/{system}_ground_min.xsf"
        write(out_g, atoms_g)
        print(f"{system}: GROUND  {out_g}")
        print(f"   seed={seed_g} iter={it_g}  dZ={dZ_g:.3f} A  dE/N=0.0000 eV/atom  "
              f"n={len(atoms_g)}  E={E_g:.2f} eV  ({atoms_g.get_chemical_formula()})")

        # --- flat-basin minimum ---
        flat = [r for r in recs if r[1] <= args.flat_dZ]
        if not flat:
            print(f"   (no flat structures at dZ <= {args.flat_dZ})")
            continue
        E_f, dZ_f, seed_f, it_f, atoms_f = min(flat, key=lambda r: r[0])
        dE_f = (E_f - gmin) / len(atoms_f)
        out_f = f"{args.outdir}/{system}_flat_min.xsf"
        write(out_f, atoms_f)
        print(f"{system}: FLAT    {out_f}")
        print(f"   seed={seed_f} iter={it_f}  dZ={dZ_f:.3f} A  dE/N={dE_f:.4f} eV/atom  "
              f"n={len(atoms_f)}  E={E_f:.2f} eV  ({atoms_f.get_chemical_formula()})")


if __name__ == '__main__':
    main()
