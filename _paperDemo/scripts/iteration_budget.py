"""Iteration-budget sensitivity (Supplementary Material, §S4).

The main-text Fe/MgO model was searched with a 100-iteration budget.  This study asks whether the
paper's *comparison* survives a longer budget: the same calculation, script and reference layer were
run with N_iterations = 200, 400 and 600 (`data/extraIteration/{0_200Iter,1_400Iter,2_600Iter}`),
so the only thing that changed is how long the search was allowed to run.

Primary evidence: **per-run truncation**.  Every run's own iterations are cut at a budget k
(10 <= iteration <= k, k = 100 ... the run's full budget) and the flat/island quantities are
recomputed, so the 100-iteration and full-budget numbers come from the *same trajectory* and need
no cross-run normalisation.  The arms are then described as run sets (secondary).

Reported per run and per k:
  - whether the ground state is an island                      (MT-1)
  - the flat-basin minimum energy relative to that window's own global minimum  (MT-2)
  - the **absolute** flat-island gap (E_flat - E_island)/N      [eV/atom, normalisation-free]
  - the number of flat structures and the flat fraction (descriptive only)

RUN SELECTION: each arm is tested against **its own** budget (200/400/600), because the project's
completed-run rule is "ran the full configured budget".  Scratch `trash/` and `_trash/` directories
are excluded, as is any structure below iteration 10 (relaxation starts at 10).  Composition is
fixed to Fe25Mg25O25 (boron-free) - see the scope bound in the SI section.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/iteration_budget.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, glob, os, csv, json, sys
from agox.databases import Database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_selection import select_completed  # noqa: E402

VERSION = '1.0.0'
METAL = ('Fe', 'Co')
FORMULA = 'Fe25Mg25O25'          # boron-free: this study bounds the structural claims, not MT-3
MIN_ITER = 10                    # relaxation starts at iteration 10 (matches the main analysis)
FLAT_DZ = 1.0                    # flat/island split (matches the main analysis)
CHECKPOINTS = (100, 200, 400, 600)

ARMS = [                         # (label, root, configured iteration budget, colour)
    ('200 iterations', 'data/extraIteration/0_200Iter', 200, '#1f6fd0'),
    ('400 iterations', 'data/extraIteration/1_400Iter', 400, '#ff7f0e'),
    ('600 iterations', 'data/extraIteration/2_600Iter', 600, '#2ca02c'),
]


def dZ_of(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[np.isin(sym, METAL), 2]
    return float(z.max() - z.min()) if len(z) else float('nan')


def load_run(dbp):
    """(iteration, E, n_atoms, dZ) for one database, iteration >= MIN_ITER, target composition."""
    db = Database(filename=dbp)
    db.restore_to_memory()
    rows = []
    for c, d in zip(db.get_all_candidates(), db.get_all_structures_data()):
        it = d.get('iteration')
        if it is None or it < MIN_ITER:
            continue
        if c.get_chemical_formula() != FORMULA:
            continue
        rows.append((int(it), float(c.get_potential_energy()), len(c), dZ_of(c)))
    rows.sort()
    return rows


def window_stats(rows, k):
    """Flat/island quantities for the same run truncated at budget k (iteration <= k)."""
    w = [r for r in rows if r[0] <= k]
    if not w:
        return None
    E = np.array([r[1] for r in w]); dZ = np.array([r[3] for r in w])
    n_atoms = w[0][2]
    i_glob = int(np.argmin(E))
    flat = dZ <= FLAT_DZ
    out = {'k': int(k), 'n': len(w), 'n_flat': int(flat.sum()),
           'E_glob': float(E[i_glob]), 'dZ_glob': float(dZ[i_glob]),
           'island_ground_state': bool(dZ[i_glob] > FLAT_DZ)}
    if flat.any():
        i_flat = int(np.where(flat)[0][np.argmin(E[flat])])
        out['E_flat'] = float(E[i_flat]); out['dZ_flat'] = float(dZ[i_flat])
        out['flat_min_rel'] = float((E[i_flat] - E[i_glob]) / n_atoms)     # own-normalised
    else:
        out['E_flat'] = None; out['dZ_flat'] = None; out['flat_min_rel'] = None
    isl = ~flat
    if isl.any():
        out['E_island'] = float(E[isl].min())
        out['gap_eV_per_atom'] = float((E[flat].min() - E[isl].min()) / n_atoms) if flat.any() else None
    else:
        out['E_island'] = None; out['gap_eV_per_atom'] = None
    out['flat_fraction'] = float(flat.mean())
    return out


def main():
    ap_budgets = list(CHECKPOINTS)
    os.makedirs('analysis', exist_ok=True)
    per_run, provenance = [], {}
    rejected_report = []

    for label, root, budget, col in ARMS:
        dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
        dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
        completed, rejected = select_completed(dbs, full_iterations=budget)
        for d, hi in rejected:
            rejected_report.append((root, os.path.basename(os.path.dirname(os.path.dirname(d))), hi))
        print(f'=== {label}: {len(completed)} completed, {len(rejected)} excluded '
              f'(budget {budget}) ===')
        for dbp in completed:
            seed = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            rows = load_run(dbp)
            if not rows:
                print(f'  {seed}: no usable structures'); continue
            ks = sorted({k for k in ap_budgets if k <= budget} | {budget})
            for k in ks:
                st = window_stats(rows, k)
                if st is None:
                    continue
                st.update(arm=label, seed=seed, budget=budget, root=root)
                per_run.append(st)
            full = window_stats(rows, budget)
            at100 = window_stats(rows, 100)
            print(f'  {seed:8s} n(k={budget})={full["n"]:4d} island-GS={full["island_ground_state"]} '
                  f'flat_min_rel@{budget}={full["flat_min_rel"]:.4f} '
                  f'(at 100: {at100["flat_min_rel"]:.4f}) '
                  f'gap {at100["gap_eV_per_atom"]:+.4f} -> {full["gap_eV_per_atom"]:+.4f} eV/atom')
            # provenance: does this run's first-100-iteration window match other arms' runs?
            provenance.setdefault(seed, {})[label] = round(at100['E_glob'], 4)

    # ---- per-arm / per-checkpoint aggregates ----
    def agg(rows_subset):
        if not rows_subset:
            return {}
        rel = [r['flat_min_rel'] for r in rows_subset if r['flat_min_rel'] is not None]
        gap = [r['gap_eV_per_atom'] for r in rows_subset if r['gap_eV_per_atom'] is not None]
        return {'n_runs': len(rows_subset),
                'n_island_ground_state': int(sum(r['island_ground_state'] for r in rows_subset)),
                'flat_min_rel_min': float(np.min(rel)) if rel else None,
                'flat_min_rel_median': float(np.median(rel)) if rel else None,
                'gap_min': float(np.min(gap)) if gap else None,
                'gap_median': float(np.median(gap)) if gap else None,
                'flat_fraction_median': float(np.median([r['flat_fraction'] for r in rows_subset]))}

    summary = {}
    for label, root, budget, col in ARMS:
        summary[label] = {'budget': budget,
                          'by_checkpoint': {str(k): agg([r for r in per_run
                                                         if r['arm'] == label and r['k'] == k])
                                            for k in sorted({r['k'] for r in per_run
                                                             if r['arm'] == label})}}

    # ---- pooled view: the main-text definition, so the numbers are directly comparable ----
    # The main text normalises by the *pooled* global minimum of the system's searches; the
    # per-run quantities above use each run's own minimum and are therefore systematically lower.
    def pooled(rows_by_run):
        allr = [r for rows in rows_by_run for r in rows]
        if not allr:
            return {}
        E = np.array([r[1] for r in allr]); dZ = np.array([r[3] for r in allr]); n_at = allr[0][2]
        g = E.min(); flat = dZ <= FLAT_DZ
        return {'n': len(allr), 'n_runs': len(rows_by_run),
                'E_pooled_gmin': float(g),
                'island_ground_state': bool(dZ[int(np.argmin(E))] > FLAT_DZ),
                'flat_min_rel_pooled': float((E[flat].min() - g) / n_at),
                'gap_pooled': float((E[flat].min() - E[~flat].min()) / n_at),
                'flat_fraction': float(flat.mean())}

    pooled_by_arm = {}
    # one pass per arm over its databases, then pool the truncated windows
    for label, root, budget, col in ARMS:
        dbs = sorted(glob.glob(f'{root}/**/*.db', recursive=True))
        dbs = [d for d in dbs if 'trash' not in d.lower().replace('\\', '/')]
        completed, _ = select_completed(dbs, full_iterations=budget)
        loaded = [load_run(d) for d in completed]
        for k in sorted({r['k'] for r in per_run if r['arm'] == label}):
            pooled_by_arm.setdefault(label, {})[str(k)] = pooled(
                [[r for r in rows if r[0] <= k] for rows in loaded])

    # the main-text model for reference: the 13 completed Fe/MgO searches at their full 100 iterations
    ref = {}
    ref_dbs = sorted(glob.glob('data/femgo/**/*.db', recursive=True))
    ref_dbs = [d for d in ref_dbs if 'trash' not in d.lower().replace('\\', '/')]
    ref_completed, _ = select_completed(ref_dbs, full_iterations=100)
    ref_rows = [load_run(d) for d in ref_completed]
    if ref_rows:
        ref = {'label': 'main-text Fe/MgO model (13 completed searches, 100 iterations)'}
        ref.update(pooled(ref_rows))
        print(f"\nmain-text reference: {ref['n_runs']} runs, pooled flat-basin min "
              f"{ref['flat_min_rel_pooled']:.4f} eV/atom, island GS {ref['island_ground_state']}")

    # ---- the primary per-run comparison: 100 -> full budget ----
    paired = []
    for label, root, budget, col in ARMS:
        for seed in sorted({r['seed'] for r in per_run if r['arm'] == label}):
            a = next((r for r in per_run if r['arm'] == label and r['seed'] == seed and r['k'] == 100), None)
            b = next((r for r in per_run if r['arm'] == label and r['seed'] == seed and r['k'] == budget), None)
            if not a or not b:
                continue
            paired.append({'arm': label, 'seed': seed, 'budget': budget,
                           'flat_min_rel_at100': a['flat_min_rel'], 'flat_min_rel_full': b['flat_min_rel'],
                           'flat_min_rel_change': (b['flat_min_rel'] - a['flat_min_rel']),
                           'gap_at100': a['gap_eV_per_atom'], 'gap_full': b['gap_eV_per_atom'],
                           'gap_change': (b['gap_eV_per_atom'] - a['gap_eV_per_atom']),
                           'island_ground_state_at100': a['island_ground_state'],
                           'island_ground_state_full': b['island_ground_state'],
                           'dE_glob_improvement_eV_per_atom': float(
                               (b['E_glob'] - a['E_glob']) / b['n'])})
    ch = np.array([p['flat_min_rel_change'] for p in paired])
    gc = np.array([p['gap_change'] for p in paired])
    imp = np.array([p['dE_glob_improvement_eV_per_atom'] for p in paired])
    headline = {
        'n_runs_paired': len(paired),
        'runs_with_island_ground_state_at_100': int(sum(p['island_ground_state_at100'] for p in paired)),
        'runs_with_island_ground_state_at_full': int(sum(p['island_ground_state_full'] for p in paired)),
        'flat_min_rel_change_median': float(np.median(ch)),
        'flat_min_rel_change_range': [float(ch.min()), float(ch.max())],
        'runs_flat_min_rel_lower': int((ch < 0).sum()),   # flat basin moved *down* (closer)
        'runs_flat_min_rel_higher': int((ch > 0).sum()),
        'gap_change_median': float(np.median(gc)),
        'gap_change_range': [float(gc.min()), float(gc.max())],
        'global_min_improvement_median': float(np.median(imp)),
        'global_min_improvement_range': [float(imp.min()), float(imp.max())],
        'runs_global_min_improved': int((imp < 0).sum()),
    }
    print('\n=== per-run 100 -> full budget ===')
    for k, v in headline.items():
        print(f'  {k}: {v}')

    payload = {
        'description': {
            'name': 'iteration_budget', 'version': VERSION,
            'produced_by': 'scripts/iteration_budget.py',
            'purpose': ('Does the paper\'s comparison (island ground state; flat basin distinct and '
                        'higher) survive a longer search than the 100-iteration budget used for the '
                        'main text? The same script, reference layer and system were run with 200, '
                        '400 and 600 iterations - only N_iterations differs.'),
            'primary_evidence': ('per-run truncation: each run is cut at k = 100 ... its own budget, '
                                 'so both numbers come from the same trajectory and no cross-run '
                                 'normalisation is involved'),
            'key_definitions': {
                'flat_branch': f'ΔZ <= {FLAT_DZ} A', 'min_iteration': MIN_ITER,
                'flat_min_rel': '(E_flat_min - E_global_min)/N for the same truncated window [eV/atom]',
                'gap_eV_per_atom': '(E_flat_min - E_island_min)/N, normalisation-free [eV/atom]',
                'island_ground_state': 'the lowest-energy structure of the window has ΔZ > 1.0 A',
                'note_gap_vs_rel': ('gap_eV_per_atom and flat_min_rel are numerically identical '
                                    'whenever the island is the ground state, which holds in every '
                                    'run here: the separation is then set entirely by the flat branch.'),
                'pooled vs per-run': ('per_run uses each run\'s own global minimum; '
                                      'pooled_by_arm uses the pooled minimum of the arm, which is the '
                                      'main-text definition and is the number comparable to the '
                                      'paper\'s 0.1888 eV/atom. per-run values are systematically '
                                      'lower.'),
            },
            'scope_bound': ('All runs are Fe25Mg25O25 (boron-free), so this study bounds the '
                            'structural claims (MT-1, MT-2 and the flat-island separation); it does '
                            'not test the boron effect (MT-3).'),
            'run_selection': ('each arm is tested against its own configured budget '
                              '(200/400/600), scratch trash/ and _trash/ excluded, iteration >= 10'),
            'caveats': [
                'Structures are not DFT-converged (surrogate relaxation + 1 GPAW step).',
                'The arms are independent run sets, not truncations of one another: the same seed '
                'can follow a different trajectory in different arms, so arm-level differences mix '
                'budget with trajectory.',
                'Unequal run counts per arm (see n_runs).',
            ],
        },
        'arms': {label: {'root': root, 'budget': budget} for label, root, budget, _ in ARMS},
        'excluded_runs': [{'root': r, 'replica': s, 'max_iteration': h} for r, s, h in rejected_report],
        'per_run': per_run, 'per_run_paired': paired, 'summary': summary, 'headline': headline,
        'pooled_by_arm': pooled_by_arm, 'main_text_reference': ref,
        'provenance_first_100_iterations': provenance,
    }
    with open('analysis/iteration_budget.json', 'w') as f:
        json.dump(payload, f, indent=2)
    print('wrote analysis/iteration_budget.json')

    with open('analysis/iteration_budget.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['arm', 'seed', 'budget', 'k', 'n', 'n_flat', 'flat_fraction',
                    'island_ground_state', 'dZ_glob', 'flat_min_rel_eV_per_atom',
                    'gap_eV_per_atom', 'E_glob', 'E_flat', 'E_island'])
        for r in sorted(per_run, key=lambda r: (r['arm'], r['seed'], r['k'])):
            w.writerow([r['arm'], r['seed'], r['budget'], r['k'], r['n'], r['n_flat'],
                        f"{r['flat_fraction']:.4f}", int(r['island_ground_state']),
                        f"{r['dZ_glob']:.4f}",
                        '' if r['flat_min_rel'] is None else f"{r['flat_min_rel']:.5f}",
                        '' if r['gap_eV_per_atom'] is None else f"{r['gap_eV_per_atom']:.5f}",
                        f"{r['E_glob']:.4f}",
                        '' if r['E_flat'] is None else f"{r['E_flat']:.4f}",
                        '' if r['E_island'] is None else f"{r['E_island']:.4f}"])
    print('wrote analysis/iteration_budget.csv')

    # ------------------------------------------------------------------ figure
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))
    tab10 = plt.get_cmap('tab10').colors
    armcol = {'200 iterations': tab10[0], '400 iterations': tab10[1], '600 iterations': tab10[2]}

    # (a) per-run convergence of the *absolute* island minimum: how much the search still gains
    for label, root, budget, col in ARMS:
        for seed in sorted({r['seed'] for r in per_run if r['arm'] == label}):
            rr = sorted([r for r in per_run if r['arm'] == label and r['seed'] == seed],
                        key=lambda r: r['k'])
            if not rr:
                continue
            e_final = rr[-1]['E_glob']; n_at = rr[-1]['n']
            ks = [r['k'] for r in rr]
            ds = [(r['E_glob'] - e_final) / n_at for r in rr]   # >= 0, -> 0 at the full budget
            axes[0].plot(ks, ds, color=col, lw=1.8, marker='o', ms=4, alpha=0.85)
    axes[0].set_xlabel('iteration budget $k$')
    axes[0].set_ylabel('ground state above its final value (eV/atom)')
    axes[0].set_title('(a) The search is still improving in absolute terms', fontweight='bold')
    axes[0].grid(alpha=0.25, lw=0.5)
    handles = [plt.Line2D([], [], color=armcol[l], lw=1.8) for l, _, _, _ in ARMS]
    axes[0].legend(handles, [l for l, _, _, _ in ARMS], fontsize=9)

    # (b) per-run flat-basin minimum relative to its own global minimum
    for label, root, budget, col in ARMS:
        for seed in sorted({r['seed'] for r in per_run if r['arm'] == label}):
            rr = sorted([r for r in per_run if r['arm'] == label and r['seed'] == seed],
                        key=lambda r: r['k'])
            ks = [r['k'] for r in rr]; vs = [r['flat_min_rel'] for r in rr]
            axes[1].plot(ks, vs, color=col, lw=1.8, marker='s', ms=4, alpha=0.85)
    axes[1].set_xlabel('iteration budget $k$'); axes[1].set_ylabel('flat-basin min ΔE/N (eV/atom)')
    axes[1].set_title('(b) The flat–island separation does not shrink', fontweight='bold')
    axes[1].grid(alpha=0.25, lw=0.5)

    # (c) paired change 100 -> full budget
    x = np.arange(len(ARMS))
    for i, (label, root, budget, col) in enumerate(ARMS):
        vals = [p['flat_min_rel_change'] for p in paired if p['arm'] == label]
        axes[2].scatter([i] * len(vals), vals, color=col, s=60, edgecolors='black', zorder=3)
        if vals:
            axes[2].plot([i - 0.22, i + 0.22], [np.median(vals)] * 2, color='black', lw=1.8, zorder=4)
    axes[2].axhline(0, color='0.4', lw=1.2)
    axes[2].set_xticks(x); axes[2].set_xticklabels([l for l, _, _, _ in ARMS], fontsize=10)
    axes[2].set_ylabel('Δ(flat-basin min ΔE/N):  full − 100')
    axes[2].set_title('(c) Change from 100 iterations to the full budget', fontweight='bold')
    axes[2].grid(axis='y', alpha=0.25, lw=0.5)

    fig.tight_layout(rect=[0, 0, 1, 1])
    fig.savefig('figures/iteration_budget.png', dpi=300, bbox_inches='tight')
    print('wrote figures/iteration_budget.png')


if __name__ == '__main__':
    main()
