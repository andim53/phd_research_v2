"""Probe: how the truncated runs affect each method-sensitivity family.

Each family root contains a few searches that stopped early (iteration max < 100).  Those
truncated searches always have the *worst* per-seed best (0.23-0.35 eV/atom, vs ~0.03-0.09
for full searches), so they inflate both the mean and the standard deviation of whatever
family they sit in — and the contamination is NOT uniform across settings.

Three variants are computed for every setting:
  (a) as-reported    : every db found (the numbers in analysis/method_sensitivity.csv)
  (b) full-only      : truncated searches dropped
  (c) common window  : per-seed best restricted to iterations <= WINDOW for all seeds
                       (the same search budget for every setting — the fair comparison)

Usage: /home/think/miniconda3/envs/agox_v2/bin/python scripts/probe_truncation_effect.py
"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from method_sensitivity import load_setting, FAMILIES

WINDOW = 37          # max iteration of the shortest common window (the baseline's truncated run)

gmin = np.inf
cache = {}
for fam, settings in FAMILIES.items():
    for name, root, col in settings:
        if root not in cache:
            cache[root] = load_setting(root)
            gmin = min(gmin, min(r['E'] for r in cache[root]))
print(f'overall gmin = {gmin:.3f} eV   common window = iterations 10-{WINDOW}\n')


def variant(recs, mode):
    if mode == 'as-reported':
        rows = recs
    elif mode == 'full-only':
        rows = [r for r in recs if r['iteration'] <= 100 and _maxit(recs, r['seed']) >= 100]
    else:
        rows = [r for r in recs if r['iteration'] <= WINDOW]
    n_atoms = recs[0]['n_atoms']
    by_seed = {}
    for r in rows:
        by_seed.setdefault(r['seed'], []).append(r)
    v = np.array([(min(x['E'] for x in rr) - gmin) / n_atoms for rr in by_seed.values()])
    return v


_MAX = {}


def _maxit(recs, seed):
    key = (id(recs), seed)
    if key not in _MAX:
        _MAX[key] = max(r['iteration'] for r in recs if r['seed'] == seed)
    return _MAX[key]


for mode in ('as-reported', 'full-only', f'common window (<= {WINDOW})'):
    print(f'=== {mode} ===')
    for fam, settings in FAMILIES.items():
        parts = []
        for name, root, col in settings:
            v = variant(cache[root], mode)
            parts.append(f'{name}: {v.mean():.5f}+-{v.std():.5f} (n={len(v)})')
        print(f'  {fam:7s} ' + ' | '.join(parts))
    print()
