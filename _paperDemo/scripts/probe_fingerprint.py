import matplotlib; matplotlib.use('Agg')
import numpy as np
from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

db = Database(filename='data/femgo/seed_13/1_db/db_13.db'); db.restore_to_memory()
cands = db.get_all_candidates()
c0 = cands[0]
tmpl = c0.get_template()
print("template:", tmpl.get_chemical_formula(), len(tmpl))
# film = non-template atoms
ti = set(c0.get_template_indices().tolist())
film = [a.index for a in c0 if a.index not in ti]
from collections import Counter
fsym = Counter(c0[i].symbol for i in film)
film_formula = ''.join(f"{s}{n}" for s,n in fsym.items())
print("film:", film_formula, len(film))

env = Environment(template=tmpl, symbols=film_formula, print_report=False, use_box_constraint=False)
fp = Fingerprint(environment=env)
feats = np.array([fp.create_features(c).ravel() for c in cands])
print("features shape:", feats.shape)
# pairwise distance stats
from scipy.spatial.distance import pdist
d = pdist(feats)
print(f"pairwise feat distance: min={d.min():.4f} mean={d.mean():.4f} max={d.max():.4f}")
