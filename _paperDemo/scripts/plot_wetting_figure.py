"""Figure: wetting-metric comparison, Fe/MgO vs Fe-B/MgO.

Multi-panel boxplot of the per-structure wetting metrics from
analysis/wetting_metrics.csv. High-contrast, projection-legible:
tab10 solid fills, no pale/viridis washes.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/plot_wetting_figure.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, csv, os

def main():
    rows = list(csv.DictReader(open('analysis/wetting_metrics.csv')))
    fe = [r for r in rows if r['system'] == 'femgo']
    fb = [r for r in rows if r['system'] == 'febmgo']

    panels = [
        ('Fe_roughness',    'Fe film roughness (A)',        r'Fe / MgO', r'Fe-B / MgO'),
        ('Fe_height_mean',  'Mean Fe height above MgO (A)', r'Fe / MgO', r'Fe-B / MgO'),
        ('fe_coverage',     'Lateral Fe coverage (frac)',   r'Fe / MgO', r'Fe-B / MgO'),
        ('Fe_contact_frac', 'Fe-O contact fraction',        r'Fe / MgO', r'Fe-B / MgO'),
    ]

    os.makedirs('figures', exist_ok=True)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.6))
    tab10 = plt.get_cmap('tab10').colors
    colors = [tab10[0], tab10[1]]          # blue = Fe/MgO, orange = Fe-B/MgO
    labels = ['Fe / MgO', 'Fe-B / MgO']

    for ax, (key, ylab, *_rest) in zip(axes, panels):
        data = [np.array([r[key] for r in fe], float),
                np.array([r[key] for r in fb], float)]
        bp = ax.boxplot(data, widths=0.5, patch_artist=True,
                        medianprops=dict(color='black', lw=1.8),
                        showfliers=True, flierprops=dict(marker='o', ms=3,
                                                         markerfacecolor='black',
                                                         markeredgecolor='none', alpha=0.5))
        for patch, c in zip(bp['boxes'], colors):
            patch.set_facecolor(c); patch.set_edgecolor('black'); patch.set_linewidth(1.4)
        ax.set_xticks([1, 2]); ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylabel(ylab.replace(' (A)', ' (Å)'), fontsize=12)
        ax.tick_params(axis='y', labelsize=10)
        # mean markers
        for i, d in enumerate(data, 1):
            ax.plot(i, np.mean(d), 'k*', ms=13)
        ax.grid(axis='y', alpha=0.3, lw=0.6)

    fig.suptitle('Wetting of Fe on MgO: effect of Boron insertion\n'
                 '(AGOX structure search, low-energy window \u22643 eV)',
                 fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out = 'figures/wetting_metrics.png'
    fig.savefig(out, dpi=300, bbox_inches='tight')
    print('wrote', out)

    # numeric summary printed for the record
    for key, ylab, *_ in panels:
        a = np.mean(np.array([r[key] for r in fe], float)); b = np.mean(np.array([r[key] for r in fb], float))
        print(f"{key:18s} Fe/MgO={a:.3f}  Fe-B/MgO={b:.3f}")

if __name__ == '__main__':
    main()
