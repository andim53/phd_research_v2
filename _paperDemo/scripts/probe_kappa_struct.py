import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

for name, root in [('baseline','data/femgo'), ('kappa=1','data/femgo_kappa/1_k1'),
                   ('kappa=3','data/femgo_kappa/0_k3')]:
    dbp = sorted(glob.glob(f'{root}/**/*.db', recursive=True))[0]
    recs = load_rows(dbp)
    c, d = recs[0]
    sym = np.array(c.get_chemical_symbols())
    ti = c.get_template_indices()
    tmpl = c.get_template()
    print(f"{name}: {dbp}")
    print(f"  n={len(c)} symbols[:8]={list(sym[:8])} symbols[-6:]={list(sym[-6:])}")
    print(f"  template formula={tmpl.get_chemical_formula()} n_template={len(ti)}")
    print(f"  template symbols[:6]={list(np.array(tmpl.get_chemical_symbols())[:6])}")
    # check a few structures in this db have same ordering
    for k in [1, 50, len(recs)-1]:
        s = np.array(recs[k][0].get_chemical_symbols())
        print(f"    rec[{k}] formula={recs[k][0].get_chemical_formula()} first={s[0]} n_tmpl={len(recs[k][0].get_template_indices())}")
