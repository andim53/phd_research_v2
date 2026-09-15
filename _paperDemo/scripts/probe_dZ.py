import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from agox.databases import Database

def load_rows(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    cands = db.get_all_candidates()
    data = db.get_all_structures_data()
    return list(zip(cands, data))

# probe: Delta-Z distribution and lowest-energy structures with iteration>=10
for system in ['femgo','febmgo']:
    dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
    dZ_all = []
    for dbp in dbs:
        rows = load_rows(dbp)
        for c, d in rows:
            it = d.get('iteration')
            if it is None or it < 10:
                continue
            sym = np.array(c.get_chemical_symbols())
            z = c.get_positions()[sym=='Fe', 2]
            dZ = z.max() - z.min()
            dZ_all.append(dZ)
    dZ_all = np.array(dZ_all)
    print(f"=== {system} (iteration>=10): n={len(dZ_all)} ===")
    print(f"  dZ min={dZ_all.min():.2f} max={dZ_all.max():.2f} mean={dZ_all.mean():.2f}")
    hist, edges = np.histogram(dZ_all, bins=20)
    for h, e0, e1 in zip(hist, edges[:-1], edges[1:]):
        print(f"    {e0:5.2f}-{e1:5.2f}: {'#'*h} {h}")
