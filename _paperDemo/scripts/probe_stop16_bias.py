"""Probe: does the truncated `stop_16` run bias the method-sensitivity baseline?

`method_sensitivity.load_setting('data/femgo')` picks up every non-trash db under the tree,
so the "baseline" family counts 14 dbs — seeds 3-15 (13 full searches, iterations 1-100)
plus `stop_16` (a truncated search, iterations 1-37).  The main text and SI S1 use 13.

This recomputes the baseline per-seed best with and without the truncated run, using the
same loader and the same per-seed-best definition as `method_sensitivity.py`.

Usage: /home/think/miniconda3/envs/agox_v2/bin/python scripts/probe_stop16_bias.py
"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from method_sensitivity import load_setting, BASELINE


def per_seed_best(recs, gmin):
    n_atoms = recs[0]['n_atoms']
    by_seed = {}
    for r in recs:
        by_seed.setdefault(r['seed'], []).append(r)
    out = {}
    for s, rows in by_seed.items():
        out[s] = (min(x['E'] for x in rows) - gmin) / n_atoms
    return out


recs = load_setting(BASELINE)
gmin = min(r['E'] for r in recs)
print(f'baseline root      : {BASELINE}')
print(f'n db records       : {len(recs)}')
seeds = sorted({r['seed'] for r in recs})
print(f'seeds              : {seeds}')
for s in seeds:
    its = [r['iteration'] for r in recs if r['seed'] == s]
    print(f'  {s:10s} iterations {min(its):3d}-{max(its):3d}')

best = per_seed_best(recs, gmin)
full = {s: v for s, v in best.items() if s != 'stop_16'}
allv = np.array(list(best.values()))
fullv = np.array(list(full.values()))
print()
print(f'WITH stop_16    (n={len(allv):2d}): {allv.mean():.5f} +- {allv.std():.5f} eV/atom'
      f'   stop_16 best = {best["stop_16"]:.5f}')
print(f'WITHOUT stop_16 (n={len(fullv):2d}): {fullv.mean():.5f} +- {fullv.std():.5f} eV/atom')
print(f'delta mean      : {fullv.mean() - allv.mean():+.5f} eV/atom '
      f'({100 * (fullv.mean() - allv.mean()) / allv.mean():+.1f} %)')
print(f'CLAIMS/reported baseline value: 0.05030')
