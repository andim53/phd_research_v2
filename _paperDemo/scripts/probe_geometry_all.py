import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scope import db_glob, systems_from_argv  # noqa: E402

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

# examine substrate z + metal(Fe/Co/B) z for one lowest-energy struct per system
for system in systems_from_argv():          # paper scope by default; --all-systems for all four
    dbp = sorted(glob.glob(db_glob(system, 'seed_*/1_db/db_*.db')))[0]
    recs = [(c.get_potential_energy(), c) for c,d in load_rows(dbp)]
    E, c = min(recs, key=lambda r: r[0])
    sym = np.array(c.get_chemical_symbols()); pos = c.get_positions()
    print(f"=== {system} (E={E:.1f}, n={len(c)}) cell_z={c.cell[2,2]:.2f} ===")
    for s in ['Mg','O','Fe','Co','B']:
        m = sym==s
        if m.any():
            z = pos[m,2]
            print(f"  {s:2s} n={m.sum():2d} z=[{z.min():.2f}, {z.max():.2f}] span={z.max()-z.min():.2f}")
