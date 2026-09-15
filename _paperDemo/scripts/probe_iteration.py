import matplotlib; matplotlib.use('Agg')
import numpy as np, glob
from collections import Counter
from agox.databases import Database

dbp = 'data/femgo/seed_13/1_db/db_13.db'
db = Database(filename=dbp)
db.restore_to_memory()
cands = db.get_all_candidates()
iters = [c.get_iteration() if hasattr(c, 'get_iteration') else None for c in cands]
print("has get_iteration:", hasattr(cands[0], 'get_iteration'))
# direct from db rows
import sqlite3
con = sqlite3.connect(dbp)
rows = con.execute("SELECT iteration, energy FROM structures ORDER BY iteration").fetchall()
print("n rows:", len(rows))
itc = Counter(r[0] for r in rows)
print("iteration -> count:", dict(sorted(itc.items())))
print("first 5:", rows[:5])
print("last 5:", rows[-5:])
