"""
Energy statistics of the LCB-only Fe/MgO dataset (calibration utility).

Reads every AGOX database in ./dataset (seeds 3-15) and prints the DFT energy
distribution. This is the source used to calibrate the Novelty-LCB energy window
(NOVELTY_TARGET_ENERGY / NOVELTY_DELTA_E in main.py).

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python energy_stats.py

Output (as of 2026-08-22): 1297 structures, Mg25O25Fe25 (75 atoms),
E in [-436.91, -386.29] eV, band centre = -411.6 eV, p1..p99 = [-436.8, -391.6].
"""
import glob
import numpy as np
from collections import Counter
from agox.databases import Database

paths = sorted(glob.glob('dataset/seed_*/1_db/db_*.db'))
print("seeds found:", [p.split('/')[1] for p in paths], "count:", len(paths))

all_E = []
comps = Counter()
n_atoms = set()
for p in paths:
    db = Database(filename=p); db.restore_to_memory()
    traj = db.restore_to_trajectory()
    for a in traj:
        e = a.get_potential_energy()
        all_E.append(e)
        comps[tuple(a.get_chemical_symbols())] += 1
        n_atoms.add(len(a))

all_E = np.array(all_E)
print("n structures:", len(all_E))
print("composition distinct:", len(comps), dict(comps.most_common(3)))
print("n_atoms set:", n_atoms)
print("E min: %.4f" % all_E.min())
print("E max: %.4f" % all_E.max())
print("E mean: %.4f" % all_E.mean())
print("E median: %.4f" % np.median(all_E))
for q in [1, 5, 25, 50, 75, 95, 99]:
    print("p%02d: %.4f" % (q, np.percentile(all_E, q)))
