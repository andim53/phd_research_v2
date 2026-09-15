"""Quick statistical check on wetting metrics (Mann-Whitney U, effect size).

Reads the per-atom relative-energy windowed CSV from wetting_metrics.py.
"""
import numpy as np, csv

rows = list(csv.DictReader(open('analysis/wetting_metrics.csv')))
fe = [r for r in rows if r['system'] == 'femgo']
fb = [r for r in rows if r['system'] == 'febmgo']


def mw_u(a, b):
    from scipy.stats import mannwhitneyu
    return mannwhitneyu(np.array(a, float), np.array(b, float), alternative='two-sided').pvalue


def cohens_d(a, b):
    a = np.array(a, float); b = np.array(b, float)
    s = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / s if s > 0 else float('nan')


for k in ['Fe_contact_frac', 'Fe_roughness', 'Fe_height_mean', 'fe_coverage']:
    a = [r[k] for r in fe]; b = [r[k] for r in fb]
    print(f"{k:16s} femgo={np.mean(np.array(a,float)):.3f} febmgo={np.mean(np.array(b,float)):.3f}  "
          f"MW-U p={mw_u(a,b):.4f}  Cohen's d={cohens_d(a,b):+.2f}")
