import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os
from collections import Counter
from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

def load_rows(dbp):
    db = Database(filename=dbp); db.restore_to_memory()
    return list(zip(db.get_all_candidates(), db.get_all_structures_data()))

root = 'data/femgo_kappa/1_k1'
recs = []
for dbp in sorted(glob.glob(f'{root}/**/*.db', recursive=True)):
    for c,d in load_rows(dbp):
        it = d.get('iteration')
        if it is None or it < 10: continue
        recs.append(c)

# check for anomalies
lens = Counter(len(c) for c in recs)
print("atom counts:", dict(lens))
comps = Counter(c.get_chemical_formula() for c in recs)
print("compositions:", dict(comps))

# build fingerprint from first, test each
c0 = recs[0]
tmpl = c0.get_template(); ti = set(c0.get_template_indices().tolist())
fsym = Counter(c0[i].symbol for i in range(len(c0)) if i not in ti)
env = Environment(template=tmpl, symbols=''.join(f'{s}{n}' for s,n in fsym.items()),
                  print_report=False, use_box_constraint=False)
fp = Fingerprint(environment=env)
bad = []
for j, c in enumerate(recs):
    try:
        fp.create_features(c)
    except Exception as e:
        bad.append((j, len(c), c.get_chemical_formula(), str(e)[:60]))
print(f"failed: {len(bad)} / {len(recs)}")
for b in bad[:5]:
    print("  ", b)
# any with NaN positions?
nan = [j for j,c in enumerate(recs) if np.isnan(c.get_positions()).any()]
print("NaN positions:", len(nan))
