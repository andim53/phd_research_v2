"""Probe: seed inventory of every method-sensitivity family.

Checks each root in method_sensitivity.FAMILIES for (a) how many dbs are counted,
(b) the iteration range of each, so truncated runs are visible.

Usage: /home/think/miniconda3/envs/agox_v2/bin/python scripts/probe_family_seeds.py
"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from method_sensitivity import load_setting, FAMILIES

gmin = np.inf
cache = {}
for fam, settings in FAMILIES.items():
    for name, root, col in settings:
        if root not in cache:
            cache[root] = load_setting(root)
            gmin = min(gmin, min(r['E'] for r in cache[root]))

print(f'overall gmin = {gmin:.3f} eV\n')
for fam, settings in FAMILIES.items():
    print(f'=== {fam} ===')
    for name, root, col in settings:
        recs = cache[root]
        n_atoms = recs[0]['n_atoms']
        by_seed = {}
        for r in recs:
            by_seed.setdefault(r['seed'], []).append(r)
        bests = {}
        trunc = []
        for s, rows in by_seed.items():
            its = [x['iteration'] for x in rows]
            bests[s] = (min(x['E'] for x in rows) - gmin) / n_atoms
            if max(its) < 100:
                trunc.append((s, min(its), max(its)))
        v = np.array(list(bests.values()))
        print(f'  {name:24s} root={root:28s} seeds={len(bests):2d} '
              f'best={v.mean():.5f}+-{v.std():.5f}')
        if trunc:
            for s, lo, hi in trunc:
                print(f'      TRUNCATED: {s}  iterations {lo}-{hi}  best={bests[s]:.5f}')
        else:
            print('      all seeds run to iteration 100')
    print()
