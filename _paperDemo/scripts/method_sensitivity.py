"""Method-parameter sensitivity (Supplementary Material).

One SI study covering three parameter families of the biased-exploration scheme:
  - rattle strength   (HeteroStruct / RattleGenerator amplitude)
  - kappa             (LCB acquisition exploration parameter)
  - dipole correction (poissonsolver dipolelayer)

All runs are the same Fe25Mg25O25 (Fe/MgO) system. Baseline for every family is the
plain `femgo` run (rattle 1.5/2.3, kappa=2, no dipole correction).

Establishes BOTH:
  (1) robustness - does the method's conclusion survive across parameter choices?
  (2) optimality - which setting performs best (per-seed best energy)?

Metrics per setting: per-seed best dE/atom, running-best convergence, dZ/basin sampling
(flat fraction), structural diversity (mean pairwise AGOX-Fingerprint distance).

RUN SELECTION: only searches that ran the full iteration budget (run_selection.FULL_ITERATIONS)
are used.  Runs that stopped early have had less search time, so their per-seed best is
systematically worse, and because unfinished runs are not distributed evenly across settings they
bias the comparison between settings.  This applies to every data directory read here; the
excluded runs are printed.

NOTE ON DIPOLE: the two dipole runs are SEPARATE searches, so their E_min difference mixes
the dipole correction with sampling differences. This comparison is outcome-level only; a
clean isolation of the dipole energy shift would need the same structures recomputed
both ways (not done here).

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/method_sensitivity.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv, sys
from collections import Counter
from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import FULL_ITERATIONS, select_completed  # noqa: E402

METAL = ('Fe', 'Co')
DIV_N = 200
BASELINE = 'data/femgo'
FAMILIES = {
    'rattle': [
        ('baseline (1.5/2.3)', BASELINE, '#1f6fd0'),
        ('reduced-0.5 (1.0/1.8)', 'data/param_ratt05', '#2ca02c'),
        ('reduced-1.0 (0.5/1.3)', 'data/param_ratt1', '#d62728'),
    ],
    'kappa': [
        ('kappa=2 (baseline)', BASELINE, '#1f6fd0'),
        ('kappa=1', 'data/femgo_kappa/1_k1', '#2ca02c'),
        ('kappa=3', 'data/femgo_kappa/0_k3', '#ff7f0e'),
        ('kappa=4', 'data/femgo_kappa/2_k4', '#d62728'),
    ],
    'dipole': [
        ('no dipole (baseline)', BASELINE, '#1f6fd0'),
        ('dipole xy', 'data/femgo_dip', '#9467bd'),
    ],
}


def load_setting(root, formula='Fe25Mg25O25'):
    """Load iteration>=10 structures of the target composition, skipping scratch 'trash' dbs."""
    dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
    dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
    dbs, rejected = select_completed(dbs)          # completed runs only (run_selection)
    if rejected:
        detail = ', '.join(f"{os.path.basename(os.path.dirname(os.path.dirname(d)))}"
                           f"@{'no data' if hi is None else hi}" for d, hi in rejected)
        print(f'  {root}: excluded {len(rejected)} unfinished run(s): {detail}')
    recs = []
    for dbp in dbs:
        seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        db = Database(filename=dbp); db.restore_to_memory()
        for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
            it = d.get('iteration')
            if it is None or it < 10:
                continue
            if formula and c.get_chemical_formula() != formula:
                continue
            sym = np.array(c.get_chemical_symbols())
            z = c.get_positions()[np.isin(sym, METAL), 2]
            recs.append(dict(seed=seed, iteration=int(it), E=float(c.get_potential_energy()),
                             n_atoms=len(c), dZ=float(z.max() - z.min()), atoms=c.copy()))
    return recs


def fingerprint(recs):
    tmpl = recs[0]['atoms'].get_template()
    tinds = set(recs[0]['atoms'].get_template_indices().tolist())
    fsym = Counter(recs[0]['atoms'][i].symbol for i in range(len(recs[0]['atoms'])) if i not in tinds)
    env = Environment(template=tmpl, symbols=''.join(f'{s}{n}' for s, n in fsym.items()),
                      print_report=False, use_box_constraint=False)
    return Fingerprint(environment=env)


def metrics(recs, gmin):
    n_atoms = recs[0]['n_atoms']
    by_seed = {}
    for r in recs:
        by_seed.setdefault(r['seed'], []).append(r)
    seedbest = np.array([min(x['E'] for x in rows) for rows in by_seed.values()])
    seedbest_dE = (seedbest - gmin) / n_atoms
    dZ = np.array([r['dZ'] for r in recs]); flat = float((dZ <= 1.0).mean())
    fp = fingerprint(recs)
    rng = np.random.default_rng(0)
    idx = rng.choice(len(recs), size=min(DIV_N, len(recs)), replace=False)
    F = np.array([fp.create_features(recs[i]['atoms']).ravel() for i in idx])
    from scipy.spatial.distance import pdist
    div = float(pdist(F).mean())
    maxit = max(r['iteration'] for r in recs)
    grid = np.arange(10, maxit + 1)
    curves = []
    for rows in by_seed.values():
        rows.sort(key=lambda r: r['iteration'])
        its = np.array([r['iteration'] for r in rows]); es = np.array([r['E'] for r in rows])
        curves.append(np.interp(grid, its, np.minimum.accumulate(es), left=np.nan))
    return dict(n=len(recs), n_seeds=len(by_seed), seedbest=seedbest_dE,
                flat=flat, div=div, dZ=dZ, grid=grid,
                conv=np.nanmean(np.vstack(curves), axis=0), n_atoms=n_atoms)


def main():
    os.makedirs('analysis', exist_ok=True)
    # load everything once, keyed by path
    cache, gmin = {}, np.inf
    for fam, settings in FAMILIES.items():
        for name, root, col in settings:
            if root not in cache:
                cache[root] = load_setting(root)
                gmin = min(gmin, min(r['E'] for r in cache[root]))
    print(f"overall gmin = {gmin:.3f} eV\n")

    all_rows = []
    print(f'completed runs only: iteration max >= {FULL_ITERATIONS}\n')
    for fam, settings in FAMILIES.items():
        print(f"=== {fam} ===")
        M = {}
        for name, root, col in settings:
            m = metrics(cache[root], gmin); M[name] = m
            all_rows.append([fam, name, m['n'], m['n_seeds'], f"{m['seedbest'].mean():.5f}",
                             f"{m['seedbest'].std():.5f}", f"{m['flat']:.3f}", f"{m['div']:.3f}"])
            print(f"  {name:24s} n={m['n']:5d} seeds={m['n_seeds']:2d} "
                  f"per-seed best={m['seedbest'].mean():.5f}+-{m['seedbest'].std():.5f} eV/at  "
                  f"flat={m['flat']:.3f}  div={m['div']:.2f}")

        # figure 1x4
        fig, axes = plt.subplots(1, 4, figsize=(22, 4.8))
        for name, root, col in settings:
            m = M[name]
            axes[0].plot(m['grid'], (m['conv'] - gmin) / m['n_atoms'], color=col, lw=2, label=name)
        axes[0].set_xlabel('iteration'); axes[0].set_ylabel('running-best ΔE/atom (eV)')
        axes[0].set_title('(a) Convergence', fontweight='bold'); axes[0].set_yscale('log')
        axes[0].legend(fontsize=8); axes[0].grid(alpha=0.25, lw=0.5)

        bp = axes[1].boxplot([M[n]['seedbest'] for n, _, _ in settings], widths=0.5,
                             patch_artist=True, medianprops=dict(color='black', lw=1.8))
        for p, (_, _, c) in zip(bp['boxes'], settings):
            p.set_facecolor(c); p.set_edgecolor('black')
        axes[1].set_xticklabels([n for n, _, _ in settings], fontsize=7, rotation=12)
        axes[1].set_ylabel('per-seed best ΔE/atom (eV)')
        axes[1].set_title('(b) Robustness / optimality', fontweight='bold')
        axes[1].grid(axis='y', alpha=0.25, lw=0.5)

        for name, root, col in settings:
            axes[2].hist(M[name]['dZ'], bins=30, alpha=0.45, color=col, label=name, density=True)
        axes[2].axvspan(0, 1.0, color='0.85', alpha=0.5, zorder=0)
        axes[2].set_xlabel(r'$\Delta Z$ (Å)'); axes[2].set_ylabel('density')
        axes[2].set_title(r'(c) Basin sampling', fontweight='bold')
        axes[2].legend(fontsize=8); axes[2].grid(alpha=0.25, lw=0.5)

        x = np.arange(len(settings))
        cols = [c for _, _, c in settings]
        axes[3].bar(x - 0.2, [M[n]['div'] for n, _, _ in settings], 0.4, color=cols,
                    edgecolor='black', label='diversity')
        axes[3].bar(x + 0.2, [M[n]['flat'] for n, _, _ in settings], 0.4, color=cols,
                    edgecolor='black', hatch='//', label='flat fraction')
        axes[3].set_xticks(x); axes[3].set_xticklabels([n for n, _, _ in settings], fontsize=7, rotation=12)
        axes[3].set_title('(d) Diversity & flat sampling', fontweight='bold')
        axes[3].legend(fontsize=8); axes[3].grid(axis='y', alpha=0.25, lw=0.5)

        fig.tight_layout(rect=[0, 0, 1, 1])
        fig.savefig(f'figures/method_sensitivity_{fam}.png', dpi=300, bbox_inches='tight')
        print(f"  -> figures/method_sensitivity_{fam}.png\n")

    with open('analysis/method_sensitivity.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['family','setting','n_structures','n_seeds',
                    'per_seed_best_dE_at_mean','per_seed_best_dE_at_sd','flat_fraction',
                    'fingerprint_diversity'])
        w.writerows(all_rows)
    print('wrote analysis/method_sensitivity.csv')


if __name__ == '__main__':
    main()
