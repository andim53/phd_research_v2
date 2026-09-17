"""Performance of the biased exploration in finding the global minimum (Fe/MgO).

SI study, Fe/MgO only, using ALL iterations of the 13 independent searches (not just the
iteration >= 10 window used for the PES analysis), because the question here is precisely
*how the search gets there over time* - including the pre-relaxation phase.

What is measured
----------------
For each search (seed) and each iteration i:
  - per-iteration minimum    min E over the candidates evaluated in that iteration
  - running best             min E over all candidates up to and including i

All energies are reported as dE/atom = (E - E_globalmin)/N_atoms [eV/atom], where the global
minimum is the lowest energy found anywhere in the 13 searches, so the best-known energy
descends to 0.

Metrics reported
----------------
  - the step change at the relaxation onset (i = 10 -> 10, the first relaxed iteration)
  - the pooled best-known energy curve (min over all searches, at each iteration)
  - the iteration at which the best-known energy first crosses each threshold
  - the per-search success rate: fraction of the 13 searches whose own running best is within
    a given tolerance of the global minimum, as a function of iteration

Outputs
-------
  figures/exploration_performance_femgo.png
  analysis/exploration_performance.json   (self-describing; see "description")

Usage
-----
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/exploration_performance.py
"""
VERSION = "1.0.0"

import json
import glob
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import FULL_ITERATIONS, completed_dbs  # noqa: E402
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

from agox.databases import Database

ROOT = 'data/femgo'
LABEL = 'Fe/MgO'
RELAX_ONSET = 10            # relaxation starts at iteration 10
THRESHOLDS = (0.20, 0.10, 0.05, 0.02, 0.005)
TOL_SUCCESS = (0.05, 0.02)  # tolerances for the per-search success-rate curve

COL = plt.get_cmap('tab10').colors


# ------------------------------------------------------------------------------- loading
def load(root=ROOT):
    """(seed, iteration, E_total, n_atoms) for every candidate with iteration metadata."""
    recs = []
    dbs, rejected = completed_dbs(f'{root}/*/1_db/db_*.db', verbose=True)
    if rejected:
        print(f'    {len(rejected)} unfinished run(s) excluded from {root} '
              f'(completion rule: {FULL_ITERATIONS} iterations)')
    for dbp in dbs:
        seed = dbp.split('/')[2]
        db = Database(filename=dbp)
        db.restore_to_memory()
        for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
            it = d.get('iteration')
            if it is None:
                continue
            recs.append((seed, int(it), float(c.get_potential_energy()), len(c)))
    return recs


def analyse(recs):
    gmin = min(r[2] for r in recs)
    nat = recs[0][3]
    per_seed = defaultdict(dict)                   # seed -> {iteration: [dE/atom, ...]}
    for s, i, e, n in recs:
        per_seed[s].setdefault(i, []).append((e - gmin) / nat)
    iterations = sorted(set(r[1] for r in recs))

    # per-search running best
    running = {}
    for s, d in per_seed.items():
        iis = sorted(d)
        es = np.array([min(d[i]) for i in iis])    # per-iteration minimum
        running[s] = (np.array(iis), np.minimum.accumulate(es), es)

    # pooled best-known curve over all searches
    pooled = []
    best = np.inf
    for i in iterations:
        best = min(best, min(min(v) for v in [per_seed[s].get(i, []) for s in per_seed] if v))
        pooled.append((i, best))
    pooled = (np.array([p[0] for p in pooled]), np.array([p[1] for p in pooled]))

    # first crossing of each threshold by the pooled best-known energy
    crossings = {}
    for thr in THRESHOLDS:
        hit = pooled[0][pooled[1] <= thr]
        crossings[f'{thr:.3f}'] = int(hit[0]) if len(hit) else None

    # step change at the relaxation onset (per search and pooled)
    step = {}
    for s, (iis, run, _) in running.items():
        pre = run[iis <= RELAX_ONSET - 1]
        first_relaxed = run[iis >= RELAX_ONSET]
        if len(pre) and len(first_relaxed):
            step[s] = float(pre[-1] - first_relaxed[0])
    pre_pool = pooled[1][pooled[0] <= RELAX_ONSET - 1][-1]
    post_pool = pooled[1][pooled[0] >= RELAX_ONSET][0]

    # fraction of searches within tol of the global minimum, as a function of iteration
    success = {}
    for tol in TOL_SUCCESS:
        frac = []
        for i in iterations:
            n_ok = 0
            for s, (iis, run, _) in running.items():
                m = iis <= i
                if m.any() and run[m][-1] <= tol:
                    n_ok += 1
            frac.append(n_ok / len(running))
        success[f'{tol:.2f}'] = frac

    per_seed_final = {s: float(run[-1]) for s, (iis, run, _) in running.items()}
    per_seed_reached_at = {}
    for s, (iis, run, _) in running.items():
        final = run[-1]
        per_seed_reached_at[s] = int(iis[np.argmax(run <= final + 1e-9)])

    return dict(
        gmin_eV=gmin, n_atoms=nat, n_searches=len(running), n_candidates=len(recs),
        iteration_min=int(min(iterations)), iteration_max=int(max(iterations)),
        per_search_final_best=per_seed_final,
        per_search_best_reached_at=per_seed_reached_at,
        pooled_best=[[int(i), float(v)] for i, v in zip(*pooled)],
        threshold_crossings=crossings,
        relax_onset=RELAX_ONSET,
        step_at_relax_onset={s: float(v) for s, v in step.items()},
        pooled_pre_relax_best=float(pre_pool),
        pooled_first_relaxed_best=float(post_pool),
        n_within_005=sum(1 for v in per_seed_final.values() if v <= 0.05),
        n_within_002=sum(1 for v in per_seed_final.values() if v <= 0.02),
        success_fraction={'tol': list(TOL_SUCCESS), 'iterations': [int(i) for i in iterations],
                          'fraction': {k: [float(x) for x in v] for k, v in success.items()}},
        running={s: [[int(i) for i in run[0]], [float(x) for x in run[1]]]
                 for s, run in running.items()},
        per_iteration_minima={s: [[int(i), float(x)] for i, x in zip(v[0], v[2])]
                              for s, v in running.items()},
    )


# ------------------------------------------------------------------------------- figure
def figure(r):
    it_max = r['iteration_max']
    fig, axes = plt.subplots(1, 3, figsize=(20, 5.6))

    # (a) per-search running best
    ax = axes[0]
    for k, s in enumerate(sorted(r['running'])):
        iis, run = r['running'][s]
        ax.plot(iis, run, color=COL[k % 10], lw=1.8, alpha=0.85)
    med_i = np.arange(1, it_max + 1)
    med = []
    for i in med_i:
        vals = []
        for s in r['running']:
            iis = np.asarray(r['running'][s][0])
            run = np.asarray(r['running'][s][1])
            m = np.asarray(iis) <= i
            if m.any():
                vals.append(run[m][-1])
        med.append(np.median(vals))
    ax.plot(med_i, med, color='black', lw=2.6, label='median over searches')
    ax.axvline(r['relax_onset'], color='0.35', lw=2.0)
    ax.annotate('relaxation\nbegins', xy=(r['relax_onset'], 0.52), xytext=(14, 0.50),
                fontsize=10, color='0.25',
                arrowprops=dict(arrowstyle='->', color='0.35', lw=1.4))
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'best $\Delta E/N$ so far  (eV/atom)')
    ax.set_title('(a) Convergence of each independent search', fontweight='bold')
    ax.legend(fontsize=9, frameon=False)
    ax.grid(alpha=0.25, lw=0.5)

    # (b) pooled best-known + per-iteration minima
    ax = axes[1]
    for k, s in enumerate(sorted(r['per_iteration_minima'])):
        arr = np.array(r['per_iteration_minima'][s])
        ax.scatter(arr[:, 0], arr[:, 1], s=9, color=COL[k % 10], alpha=0.45,
                   edgecolors='none')
    pb = np.array(r['pooled_best'])
    ax.plot(pb[:, 0], pb[:, 1], color='black', lw=2.6, label='best known (all searches)')
    for thr, it in r['threshold_crossings'].items():
        if it is None:
            continue
        ax.plot([it], [float(thr)], marker='o', ms=6, color='black')
        ax.annotate(f'{float(thr):.3f} at i={it}', xy=(it, float(thr)),
                    xytext=(it + 4, float(thr) + 0.035), fontsize=9)
    ax.axvline(r['relax_onset'], color='0.35', lw=2.0)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$\Delta E/N$  (eV/atom)')
    ax.set_title('(b) Lowest energy found, and best known so far', fontweight='bold')
    ax.set_ylim(-0.01, 0.65)
    ax.legend(fontsize=9, frameon=False, loc='upper right')
    ax.grid(alpha=0.25, lw=0.5)

    # (c) per-search success rate
    ax = axes[2]
    its = r['success_fraction']['iterations']
    for k, tol in enumerate(r['success_fraction']['tol']):
        lab = f'{tol:.2f}'
        ax.plot(its, r['success_fraction']['fraction'][lab], color=COL[k], lw=2.4,
                label=f"within {tol:.2f} eV/atom")
    ax.axvline(r['relax_onset'], color='0.35', lw=2.0)
    ax.set_xlabel('iteration')
    ax.set_ylabel('fraction of the 13 searches')
    ax.set_title('(c) Searches that have reached the global-minimum region',
                 fontweight='bold')
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=9, frameon=False, loc='upper left')
    ax.grid(alpha=0.25, lw=0.5)

    fig.tight_layout(rect=[0, 0, 1, 1])
    os.makedirs('figures', exist_ok=True)
    out = 'figures/exploration_performance_femgo.png'
    fig.savefig(out, dpi=300, bbox_inches='tight')
    print(f'wrote {out}')


def main():
    recs = load()
    r = analyse(recs)
    os.makedirs('analysis', exist_ok=True)

    print(f'{LABEL}: {r["n_searches"]} searches, {r["n_candidates"]} candidates, '
          f'iterations {r["iteration_min"]}–{r["iteration_max"]}')
    print(f'  global minimum E = {r["gmin_eV"]:.6f} eV ({r["n_atoms"]} atoms)')
    print(f'\n  step at the relaxation onset (i={r["relax_onset"] - 1} -> '
          f'{r["relax_onset"]}): pooled best {r["pooled_pre_relax_best"]:.3f} -> '
          f'{r["pooled_first_relaxed_best"]:.3f} eV/atom')
    st = np.array(list(r['step_at_relax_onset'].values()))
    print(f'    per-search drop: median {np.median(st):.3f}, range {st.min():.3f} '
          f'to {st.max():.3f} eV/atom')
    print('\n  iteration at which the best-known energy first crosses:')
    for thr, it in r['threshold_crossings'].items():
        print(f'    {thr} eV/atom -> i = {it}')
    print(f'\n  per-search final best (eV/atom): '
          f'{ {s: round(v, 3) for s, v in sorted(r["per_search_final_best"].items())} }')
    print(f'  searches within 0.05 eV/atom of the global minimum: {r["n_within_005"]}'
          f' / {r["n_searches"]}')
    print(f'  searches within 0.02 eV/atom of the global minimum: {r["n_within_002"]}'
          f' / {r["n_searches"]}')

    payload = {
        'description': {
            'name': 'exploration_performance',
            'version': VERSION,
            'produced_by': 'scripts/exploration_performance.py',
            'purpose': ('Measure how the biased GOFEE search approaches the global minimum '
                        'over iteration, for Fe/MgO, using all iterations (including the '
                        'pre-relaxation phase that the PES analysis discards).'),
            'definitions': {
                'dE_per_atom': '(E - E_globalmin)/n_atoms [eV/atom]; global min = lowest '
                               'energy found in any of the 13 searches, so the best-known '
                               'curve reaches 0',
                'per_iteration_min': 'lowest energy among the candidates evaluated in that '
                                     'iteration',
                'running_best': 'lowest energy over all iterations up to and including i',
                'pooled_best': 'running best minimised over all 13 searches',
                'relax_onset': 'iteration 10 - the first iteration at which candidates are '
                               'surrogate-relaxed (PES analysis keeps i >= 10 only)',
                'success_fraction': ('fraction of the 13 searches whose own running best is '
                                     'within a tolerance of the global minimum, vs iteration'),
            },
            'caveats': [
                'Energies are single GPAW steps on surrogate-relaxed structures, not '
                'converged minima (residual forces ~1-2 eV/A); the curve measures the search, '
                'not the physical convergence of any structure.',
                'Iteration index is the AGOX iteration, not a computational cost; each '
                'iteration evaluates a fixed number of candidates (20 generated, M selected).',
                'The search is biased (seeded from a flat reference layer), so this measures '
                'exploration performance, not an unbiased global-optimisation benchmark.',
                'Fe/MgO only (the system with the most searches, 13).',
            ],
            'main_quantities': {
                'pooled_pre_relax_best': 'best-known dE/atom just before relaxation begins',
                'pooled_first_relaxed_best': 'best-known dE/atom at the first relaxed iteration',
                'step_at_relax_onset': 'per-search drop in running best across the onset',
                'threshold_crossings': 'first iteration at which the pooled best crosses a '
                                       'given dE/atom',
                'per_search_final_best': 'final running best of each search',
                'n_within_005': 'searches ending within 0.05 eV/atom of the global minimum',
            },
            'figure': 'figures/exploration_performance_femgo.png',
        },
        'version': VERSION,
        'system': 'femgo',
        'label': LABEL,
        'data': r,
    }
    out = 'analysis/exploration_performance.json'
    with open(out, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f'\nwrote {out}')
    figure(r)


if __name__ == '__main__':
    main()
