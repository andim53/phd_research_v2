"""Select low-force, structurally-distinct structures for DFT re-relaxation.

For each system:
  1. Load all candidates with iteration >= 10 (relax starts at iteration 10).
  2. Keep those with max|F| < --max-force  (already fairly well relaxed).
  3. Greedily de-duplicate by descriptor distance using the AGOX Fingerprint
     (the same descriptor family used in the search): scan structures lowest-energy
     first, keep a structure only if its feature vector is > --desc-tol away from every
     already-kept structure.
  4. Write the kept structures to XSF/XYZ + a manifest CSV (with template_indices so the
     relaxation can freeze the substrate).

Usage (from _paperDemo root):
  /home/think/miniconda3/envs/agox_v2/bin/python relaxation/select_structures.py \
      --min-iteration 10 --max-force 0.5 --desc-tol 0.2
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, csv, argparse
from collections import Counter
from ase.io import write
from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from scope import (SYSTEMS_IN_SCOPE,  # noqa: E402
                   add_scope_arguments, db_glob, systems_from_args)

METAL = ('Fe', 'Co')
# The paper's scope (v9): Fe/MgO and Fe-B/MgO — see scripts/scope.py.
SYSTEMS = list(SYSTEMS_IN_SCOPE)


def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))


def film_formula(c, template_indices):
    fsym = Counter(c[i].symbol for i in range(len(c)) if i not in template_indices)
    return ''.join(f"{s}{n}" for s, n in fsym.items())


def delta_z(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    m = np.isin(sym, METAL)
    z = atoms.get_positions()[m, 2]
    return float(z.max() - z.min()) if len(z) else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-iteration', type=int, default=10)
    ap.add_argument('--force-percentile', type=float, default=5.0,
                    help='keep the lowest-force N%% of each system (per-system percentile)')
    ap.add_argument('--max-force', type=float, default=None,
                    help='optional absolute max|F| cutoff (eV/A); overrides percentile if set')
    ap.add_argument('--desc-tol', type=float, default=0.2,
                    help='min fingerprint-feature distance between kept structures')
    ap.add_argument('--outdir', default='relaxation/selected')
    add_scope_arguments(ap)
    args = ap.parse_args()
    SYSTEMS = systems_from_args(args)

    manifest_rows = []
    for system in SYSTEMS:
        dbs = sorted(glob.glob(db_glob(system, 'seed_*/1_db/db_*.db')))
        recs = []
        for dbp in dbs:
            seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            for c, d in load_rows(dbp):
                it = d.get('iteration')
                if it is None or it < args.min_iteration:
                    continue
                fmax = float(np.linalg.norm(c.get_forces(), axis=1).max())
                recs.append({'E': float(c.get_potential_energy()), 'seed': seed,
                             'iter': int(it), 'fmax': fmax, 'atoms': c.copy()})
        if not recs:
            print(f"{system}: no structures")
            continue

        # ---- force filter ----
        all_fmax = np.array([r['fmax'] for r in recs])
        if args.max_force is not None:
            cutoff = args.max_force
            rule = f"max|F| < {cutoff} (absolute)"
        else:
            cutoff = float(np.percentile(all_fmax, args.force_percentile))
            rule = f"lowest {args.force_percentile}% by max|F| (cutoff = {cutoff:.3f})"
        recs = [r for r in recs if r['fmax'] < cutoff]
        if not recs:
            print(f"{system}: no structures pass [{rule}]")
            continue

        # descriptor for dedup (built from the substrate template of a representative)
        tmpl = recs[0]['atoms'].get_template()
        tinds = set(recs[0]['atoms'].get_template_indices().tolist())
        env = Environment(template=tmpl, symbols=film_formula(recs[0]['atoms'], tinds),
                          print_report=False, use_box_constraint=False)
        fp = Fingerprint(environment=env)

        # sort lowest-E first; greedy distinct selection
        recs.sort(key=lambda r: r['E'])
        gmin = recs[0]['E']
        kept = []
        for r in recs:
            f = fp.create_features(r['atoms']).ravel()
            if all(np.linalg.norm(f - k['feat']) > args.desc_tol for k in kept):
                r['feat'] = f
                kept.append(r)

        os.makedirs(f"{args.outdir}/{system}", exist_ok=True)
        for i, r in enumerate(kept):
            a = r['atoms']
            tinds = a.get_template_indices().tolist()
            fname = f"{system}/{system}_{i:03d}.xyz"
            write(f"{args.outdir}/{fname}", a)
            manifest_rows.append({
                'system': system, 'file': fname, 'seed': r['seed'], 'iteration': r['iter'],
                'E_total': f"{r['E']:.6f}", 'dE_per_atom': f"{(r['E']-gmin)/len(a):.6f}",
                'max_force': f"{r['fmax']:.4f}", 'dZ': f"{delta_z(a):.4f}",
                'n_atoms': len(a), 'n_template': len(tinds),
                'template_indices': ';'.join(map(str, tinds)),
            })
        print(f"{system}: {len(recs)} pass [{rule}] -> {len(kept)} distinct kept "
              f"(desc-tol={args.desc_tol})")

    os.makedirs(args.outdir, exist_ok=True)
    cols = ['system','file','seed','iteration','E_total','dE_per_atom','max_force','dZ',
            'n_atoms','n_template','template_indices']
    with open(f"{args.outdir}/manifest.csv", 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in manifest_rows:
            w.writerow(r)
    print(f"\nWrote {len(manifest_rows)} structures + manifest.csv to {args.outdir}")


if __name__ == '__main__':
    main()
