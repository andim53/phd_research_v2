import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

for root in ['data/femgo_kappa/1_k1','data/femgo_kappa/0_k3','data/femgo_kappa/2_k4']:
    print(f"=== {root} ===")
    for dbp in sorted(glob.glob(f'{root}/**/*.db', recursive=True)):
        comps = Counter()
        n = 0
        for c,d in load_rows(dbp):
            it = d.get('iteration')
            if it is None or it < 10: continue
            comps[c.get_chemical_formula()] += 1; n += 1
        flag = ' <-- MIXED/ODD' if len(comps) > 1 or 'Fe25Mg25O25' not in comps else ''
        print(f"  {os.path.relpath(dbp, root):40s} n={n:4d} {dict(comps)}{flag}")
