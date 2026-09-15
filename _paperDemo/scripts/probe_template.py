import matplotlib; matplotlib.use('Agg')
import numpy as np, glob
from agox.databases import Database

db = Database(filename='data/femgo/seed_13/1_db/db_13.db')
db.restore_to_memory()
c = db.get_all_candidates()[0]
print("type:", type(c))
attrs = [a for a in dir(c) if 'templ' in a.lower() or 'constraint' in a.lower() or 'index' in a.lower()]
print("template/index attrs:", attrs)
for a in ['get_template_indices','template_indices','template','prioritized_candidates']:
    if hasattr(c, a):
        try:
            v = getattr(c, a)
            v = v() if callable(v) else v
            print(f"  {a}: {type(v)} -> {str(v)[:120]}")
        except Exception as e:
            print(f"  {a}: ERR {e}")
# also check what the standard candidate exposes
print("n atoms:", len(c))
