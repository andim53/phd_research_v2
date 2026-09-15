import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

for system in ['fecomgo','fecobmgo']:
    dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
    comps = Counter(); n=0; iters=set(); energies=[]
    cellz=None
    for dbp in dbs:
        for c,d in load_rows(dbp):
            comps[c.get_chemical_formula()]+=1; n+=1
            iters.add(d.get('iteration')); energies.append(c.get_potential_energy())
            if cellz is None: cellz=c.cell[2,2]
    print(f"=== {system}: {len(dbs)} dbs, {n} cands ===")
    for comp,cn in comps.most_common(5): print(f"    {comp}: {cn}")
    e=np.array(energies)
    print(f"  E: min={e.min():.2f} max={e.max():.2f} range={e.max()-e.min():.2f} eV")
    print(f"  iterations present: {sorted([i for i in iters if i is not None])[:5]}...{sorted([i for i in iters if i is not None])[-3:]}")
    print(f"  cell z: {cellz}")
