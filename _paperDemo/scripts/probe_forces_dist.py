import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scope import db_glob, systems_from_argv  # noqa: E402

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

for system in systems_from_argv():          # paper scope by default; --all-systems for all four
    fm = []
    for dbp in sorted(glob.glob(db_glob(system, 'seed_*/1_db/db_*.db'))):
        for c,d in load_rows(dbp):
            it = d.get('iteration')
            if it is None or it < 10: continue
            fm.append(float(np.linalg.norm(c.get_forces(), axis=1).max()))
    fm = np.array(fm)
    qs = np.percentile(fm, [1,5,10,25,50,75,90])
    print(f"{system}: n={len(fm)} max|F| min={fm.min():.2f} p1={qs[0]:.2f} p5={qs[1]:.2f} "
          f"p10={qs[2]:.2f} p25={qs[3]:.2f} med={qs[4]:.2f} p75={qs[5]:.2f} p90={qs[6]:.2f} max={fm.max():.2f}")
