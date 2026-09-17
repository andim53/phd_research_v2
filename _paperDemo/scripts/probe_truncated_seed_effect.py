"""Probe: effect of excluding truncated `seed_*` runs from the main-text (2x2) systems.

The paper's loaders glob `seed_*/1_db/db_*.db`, which drops runs named `stop_*` but silently
ACCEPTS truncated `seed_*` runs.  Two of the four systems have one:

  data/fecomgo/seed_4   iterations 1-10   (10 candidates, iteration 10 only)
  data/fecobmgo/seed_3  iterations 1-73   (66 candidates)
  (femgo/stop_16 and febmgo/seed_6 are already excluded: the former by name, the latter empty)

This recomputes the headline quantities with and without those replicas:
  global minimum, flat-basin minimum, flat fraction, per-replica minima.

Usage: /home/think/miniconda3/envs/agox_v2/bin/python scripts/probe_truncated_seed_effect.py
"""
import sys, json, numpy as np
sys.path.insert(0, 'scripts')
from ensemble_analysis import load_system, FLAT_DZ, MIN_ITER
from scope import ALL_SYSTEMS

# This probe is the v8 audit record of the truncation finding, so it deliberately covers all four
# systems including the two the paper has since archived (v9). load_system resolves the archived
# data root, so re-running it after the data move still reproduces the audit.
SYSTEMS = list(ALL_SYSTEMS)
TRUNCATED = {'fecomgo': ['seed_4'], 'fecobmgo': ['seed_3']}


def maxit(recs, rep):
    return max(r['iteration'] for r in recs if r['replica'] == rep)


def stats(recs):
    E = np.array([r['E'] for r in recs])
    dZ = np.array([r['dZ'] for r in recs])
    n = len(recs)
    reps = {}
    for r in recs:
        reps.setdefault(r['replica'], []).append(r['E'])
    repmin = np.array([min(v) for v in reps.values()])
    flat = dZ <= FLAT_DZ
    return dict(n=n, n_rep=len(reps), Emin=E.min(), flat_min=E[flat].min() if flat.any() else np.nan,
                flat_frac=float(flat.mean()), repmin=repmin)


allrecs = {s: load_system(s, include_partial=False)[0] for s in SYSTEMS}

print('=== replica inventory (iteration range) ===')
for s in SYSTEMS:
    recs = allrecs[s]
    reps = sorted({r['replica'] for r in recs})
    print(f'\n  {s}: {len(reps)} replicas carrying data')
    for rep in reps:
        hi = maxit(recs, rep)
        t = '  <== TRUNCATED' if hi < 100 else ''
        print(f'      {rep:10s} iteration max {hi:3d}{t}')

print('\n\n=== effect of dropping the truncated replicas ===')
summary = {}
for s in SYSTEMS:
    recs = allrecs[s]
    keep = [r for r in recs if r['replica'] not in TRUNCATED.get(s, [])]
    a, b = stats(recs), stats(keep)
    # energies are per-system; report eV/atom against each variant's own global minimum
    summary[s] = dict(
        all_n=a['n'], all_rep=a['n_rep'], all_frac=a['flat_frac'],
        keep_n=b['n'], keep_rep=b['n_rep'], keep_frac=b['flat_frac'],
        all_globmin_dZ=min((r['dZ'] for r in recs if r['E'] == a['Emin']), default=np.nan),
        keep_globmin_dZ=min((r['dZ'] for r in keep if r['E'] == b['Emin']), default=np.nan),
        globmin_shift_eV_per_atom=(b['Emin'] - a['Emin']) / recs[0]['n_atoms'],
        flatmin_rel_eV_per_atom=(a['flat_min'] - a['Emin']) / recs[0]['n_atoms'],
        flatmin_rel_keep_eV_per_atom=(b['flat_min'] - b['Emin']) / recs[0]['n_atoms'],
        repmin_all=a['repmin'], repmin_keep=b['repmin'],
    )

print(f"\n{'system':10s} {'reps':>10s} {'structs':>12s} {'flat frac':>16s} {'flat-vs-globmin (eV/atom)':>28s}")
print(f"{'':10s} {'all->keep':>10s} {'all->keep':>12s} {'all->keep':>16s} {'all->keep':>28s}")
for s in SYSTEMS:
    d = summary[s]
    print(f"{s:10s} {d['all_rep']:>4d}->{d['keep_rep']:<4d} {d['all_n']:>6d}->{d['keep_n']:<5d} "
          f"{d['all_frac']:>7.3f}->{d['keep_frac']:<7.3f} "
          f"{d['flatmin_rel_eV_per_atom']:>13.4f}->{d['flatmin_rel_keep_eV_per_atom']:<13.4f}")

print('\n=== global-minimum location (does the excluded replica own it?) ===')
for s in SYSTEMS:
    d = summary[s]
    rep = min(d['repmin_all'])
    print(f"  {s:10s} global min dZ = {d['all_globmin_dZ']:.3f} A "
          f"(after exclusion {d['keep_globmin_dZ']:.3f} A); "
          f"shift = {d['globmin_shift_eV_per_atom']:+.5f} eV/atom")
    if s in TRUNCATED:
        ids = TRUNCATED[s]
        for i, rep in enumerate(sorted(allrecs[s] and {r['replica'] for r in allrecs[s]})):
            pass
        for rid in ids:
            rows = [r for r in allrecs[s] if r['replica'] == rid]
            print(f"      {rid} best dE/N = "
                  f"{(min(r['E'] for r in rows) - d['repmin_keep'].min()) / rows[0]['n_atoms']:+.5f} eV/atom "
                  f"relative to the kept global minimum")

print('\n=== per-replica minima (eV/atom vs each variant\'s global min) ===')
for s in SYSTEMS:
    d = summary[s]
    am = (d['repmin_all'] - d['repmin_all'].min()) / allrecs[s][0]['n_atoms']
    km = (d['repmin_keep'] - d['repmin_keep'].min()) / allrecs[s][0]['n_atoms']
    print(f"  {s:10s} all : {np.round(np.sort(am), 4)}")
    print(f"  {'':10s} keep: {np.round(np.sort(km), 4)}")

json.dump({s: {k: (v.tolist() if isinstance(v, np.ndarray) else v)
               for k, v in summary[s].items()} for s in SYSTEMS},
          open('/tmp/trunc_seed_effect.json', 'w'), indent=1, default=str)
print('\nwrote /tmp/trunc_seed_effect.json')
