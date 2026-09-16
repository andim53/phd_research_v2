import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

for system in ['param_ratt05','param_ratt1','femgo']:
    dbs = sorted(glob.glob(f'data/{system}/**/*.db', recursive=True))
    comps = Counter(); n=0; iters=set()
    print(f"\n=== {system} ({len(dbs)} dbs) ===")
    for dbp in dbs:
        c0 = None
        try:
            for c,d in load_rows(dbp):
                comps[c.get_chemical_formula()] += 1; n += 1
                iters.add(d.get('iteration'))
                n_at = len(c)
        except Exception as e:
            print(f"  ERR {dbp}: {e}"); continue
        print(f"  {os.path.relpath(dbp)}")
    print(f"  total cands: {n}")
    for comp,cn in comps.most_common(4): print(f"    {comp}: {cn}")
