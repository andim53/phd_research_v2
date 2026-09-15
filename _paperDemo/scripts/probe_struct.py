import matplotlib; matplotlib.use('Agg')
import numpy as np, glob
from agox.databases import Database

def load_cands(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return db.get_all_candidates()

for system, dbp in [('femgo','data/femgo/seed_13/1_db/db_13.db'),
                    ('febmgo','data/febmgo/seed_4/1_db/db_4.db')]:
    cands = load_cands(dbp)
    ebest = min(cands, key=lambda c: c.get_potential_energy())
    atoms = ebest
    sym = np.array(atoms.get_chemical_symbols())
    pos = atoms.get_positions()
    z = pos[:,2]
    print(f"=== {system} (E={ebest.get_potential_energy():.2f}) ===")
    print(f"  symbols: {dict(zip(*np.unique(sym, return_counts=True)))}")
    print(f"  cell: {atoms.get_cell_lengths_and_angles()}")
    for s in ['Mg','O','Fe','B']:
        if s in sym:
            zs = z[sym==s]
            print(f"  {s}: n={len(zs)} z[min,max]={zs.min():.2f},{zs.max():.2f} span={zs.max()-zs.min():.2f}")
