import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

roots = ['data/femgo','data/param_ratt05','data/param_ratt1','data/femgo_dip',
         'data/femgo_kappa/1_k1','data/femgo_kappa/0_k3','data/femgo_kappa/2_k4']
for root in roots:
    dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
    trash = [d for d in dbs if 'trash' in d]
    comps = Counter(); n=0
    for dbp in dbs:
        for c,d in load_rows(dbp):
            it = d.get('iteration')
            if it is None or it < 10: continue
            comps[c.get_chemical_formula()] += 1; n += 1
    print(f"{root:28s} dbs={len(dbs):3d} trash={len(trash)} n={n:5d} comps={dict(comps)}")
