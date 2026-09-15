"""Rattle-strength analysis for the biased-exploration (GOFEE + flat-Fe seed) search.

Compares three femgo-scheme runs differing only in rattle strength:
  baseline   rattle 1.5 / 2.3   data/femgo
  reduced-0.5  1.0 / 1.8        data/param_ratt05
  reduced-1.0  0.5 / 1.3        data/param_ratt1

Questions covered:
  (1) robustness     - does the search reach the same ground state / basin picture?
  (2) optimal rattle - lowest energy? fastest convergence?
  (3) exploration    - which basins (flat vs island), and how diversely?

Metrics (fair, per-seed where counts differ):
  - per-seed best energy ΔE/atom (each seed = one independent search) -> robustness/optimality
  - running-best convergence vs iteration (mean over seeds)
  - ΔZ distribution + flat fraction (ΔZ <= 1.0 A) -> basin sampling
  - structural diversity: mean pairwise AGOX-Fingerprint distance (subsampled)

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/rattle_analysis.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv
from collections import Counter
from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

METAL = ('Fe', 'Co')
DIV_N = 200        # subsample size for the pairwise-diversity estimate

SETTINGS = [
    ('baseline (1.5/2.3)', 'data/femgo', '#1f6fd0'),
    ('reduced-0.5 (1.0/1.8)', 'data/param_ratt05', '#2ca02c'),
    ('reduced-1.0 (0.5/1.3)', 'data/param_ratt1', '#d62728'),
]


def load_setting(root):
    dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
    recs = []
    for dbp in dbs:
        seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        db = Database(filename=dbp); db.restore_to_memory()
        for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
            it = d.get('iteration')
            if it is None or it < 10:
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


def main():
    os.makedirs('analysis', exist_ok=True)
    all_recs, gmin = {}, np.inf
    for name, root, col in SETTINGS:
        recs = load_setting(root)
        all_recs[name] = recs
        gmin = min(gmin, min(r['E'] for r in recs))
    print(f"{'setting':24s} {'n':>5s} {'seeds':>5s} {'per-seed best dE/at (mean±sd)':>32s} "
          f"{'flatfrac':>9s} {'diversity':>10s}")

    summary, per_seed, dz_all, conv = [], {}, {}, {}
    for name, root, col in SETTINGS:
        recs = all_recs[name]
        n_atoms = recs[0]['n_atoms']
        # per-seed best
        by_seed = {}
        for r in recs:
            by_seed.setdefault(r['seed'], []).append(r)
        seedbest = np.array([min(x['E'] for x in rows) for rows in by_seed.values()])
        seedbest_dE = (seedbest - gmin) / n_atoms
        # flat fraction + dZ
        dZ = np.array([r['dZ'] for r in recs]); dz_all[name] = dZ
        flat_frac = float((dZ <= 1.0).mean())
        # diversity: mean pairwise fingerprint distance on a RANDOM subsample of all structures
        fp = fingerprint(recs)
        rng = np.random.default_rng(0)
        idx = rng.choice(len(recs), size=min(DIV_N, len(recs)), replace=False)
        F = np.array([fp.create_features(recs[i]['atoms']).ravel() for i in idx])
        from scipy.spatial.distance import pdist
        div = float(pdist(F).mean())
        # convergence: mean running-best dE/atom vs iteration
        maxit = max(r['iteration'] for r in recs)
        grid = np.arange(10, maxit + 1)
        curves = []
        for rows in by_seed.values():
            rows.sort(key=lambda r: r['iteration'])
            its = np.array([r['iteration'] for r in rows]); es = np.array([r['E'] for r in rows])
            curves.append(np.interp(grid, its, np.minimum.accumulate(es), left=np.nan))
        conv[name] = (grid, np.nanmean(np.vstack(curves), axis=0), n_atoms)
        per_seed[name] = seedbest_dE
        summary.append([col, name, len(recs), len(by_seed), f"{seedbest_dE.mean():.5f}",
                        f"{seedbest_dE.std():.5f}", f"{flat_frac:.3f}", f"{div:.3f}"])
        print(f"{name:24s} {len(recs):5d} {len(by_seed):5d} "
              f"{seedbest_dE.mean():>18.5f} ± {seedbest_dE.std():<10.5f} "
              f"{flat_frac:9.3f} {div:10.3f}")

    with open('analysis/rattle_summary.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['color','setting','n_structures','n_seeds','per_seed_best_dE_at_mean',
                    'per_seed_best_dE_at_sd','flat_fraction','mean_pairwise_fingerprint_dist'])
        w.writerows(summary)
    print('\nwrote analysis/rattle_summary.csv')

    # ---- figure 2x2 ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for name, root, col in SETTINGS:
        g, run, na = conv[name]
        axes[0, 0].plot(g, (run - gmin) / na, color=col, lw=2, label=name)
    axes[0, 0].set_xlabel('iteration'); axes[0, 0].set_ylabel('running-best ΔE/atom (eV)')
    axes[0, 0].set_title('(a) Convergence vs rattle strength', fontweight='bold')
    axes[0, 0].set_yscale('log'); axes[0, 0].legend(fontsize=9); axes[0, 0].grid(alpha=0.25, lw=0.5)

    data = [per_seed[n] for n, _, _ in SETTINGS]
    bp = axes[0, 1].boxplot(data, widths=0.5, patch_artist=True,
                            medianprops=dict(color='black', lw=1.8))
    for p, (_, _, c) in zip(bp['boxes'], SETTINGS):
        p.set_facecolor(c); p.set_edgecolor('black')
    axes[0, 1].set_xticklabels([n.split(' ')[0] + '\n' + n.split(' ')[1] for n, _, _ in SETTINGS], fontsize=9)
    axes[0, 1].set_ylabel('per-seed best ΔE/atom (eV)')
    axes[0, 1].set_title('(b) Robustness: best energy per independent seed', fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.25, lw=0.5)

    for name, root, col in SETTINGS:
        axes[1, 0].hist(dz_all[name], bins=30, alpha=0.45, color=col, label=name, density=True)
    axes[1, 0].axvspan(0, 1.0, color='0.85', alpha=0.5, zorder=0)
    axes[1, 0].set_xlabel(r'$\Delta Z$ (Å)'); axes[1, 0].set_ylabel('density')
    axes[1, 0].set_title(r'(c) Basin sampling ($\Delta Z$)', fontweight='bold')
    axes[1, 0].legend(fontsize=9); axes[1, 0].grid(alpha=0.25, lw=0.5)

    divs = [float(s[7]) for s in summary]; flats = [float(s[6]) for s in summary]
    names = [n for n, _, _ in SETTINGS]; cols = [c for _, _, c in SETTINGS]
    x = np.arange(len(names))
    axes[1, 1].bar(x - 0.2, divs, 0.4, color=cols, edgecolor='black', label='fingerprint diversity')
    axes[1, 1].bar(x + 0.2, flats, 0.4, color=cols, edgecolor='black', hatch='//', label='flat fraction')
    axes[1, 1].set_xticks(x); axes[1, 1].set_xticklabels(names, fontsize=8, rotation=10)
    axes[1, 1].set_title('(d) Diversity & flat-basin sampling', fontweight='bold')
    axes[1, 1].legend(fontsize=9); axes[1, 1].grid(axis='y', alpha=0.25, lw=0.5)

    fig.suptitle('Impact of rattle strength on the biased-exploration search (Fe/MgO)',
                 fontweight='bold', fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig('figures/rattle_analysis.png', dpi=300, bbox_inches='tight')
    print('wrote figures/rattle_analysis.png')


if __name__ == '__main__':
    main()
