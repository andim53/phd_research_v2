import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

sets = {
  'femgo (kappa=2, baseline)': ['data/femgo'],
  'kappa=1': ['data/femgo_kappa/1_k1'],
  'kappa=3': ['data/femgo_kappa/0_k3'],
  'kappa=4': ['data/femgo_kappa/2_k4'],
  'femgo_dip (dipole xy)': ['data/femgo_dip'],
}
for name, roots in sets.items():
    dbs = [d for r in roots for d in sorted(glob.glob(f'{r}/**/*.db', recursive=True))]
    comps=Counter(); n=0; seeds=set(); emin=np.inf
    for dbp in dbs:
        seed=os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        try:
            for c,d in load_rows(dbp):
                comps[c.get_chemical_formula()]+=1; n+=1; seeds.add(seed)
                emin=min(emin,c.get_potential_energy())
        except Exception as e:
            print(f"  ERR {dbp}: {e}")
    top = comps.most_common(1)[0] if comps else ('?',0)
    print(f"{name:26s} dbs={len(dbs):3d} seeds={len(seeds):2d} cands={n:5d} "
          f"comp={top[0]} Emin={emin:.2f}")
