"""Ensemble / motif analysis of the flat-vs-island PES across the four systems.

WHY THIS EXISTS
---------------
`scripts/pes_analysis.py` describes each system by two hand-picked structures: the single
flat-basin minimum and the single island global minimum (see figures/pes_four_systems.png).
Both branches of the PES are in fact *ensembles* of many near-degenerate configurations -
the island branch contains islands of many different heights, and the flat branch contains
many lateral arrangements that differ only in where B / Co sits. A claim built on one
structure per branch is therefore only as robust as that pick.

This script answers, from the existing AGOX/GOFEE databases:

  1. DATA INTEGRITY - inventory of independent replicas (AGOX seeds) per system, including
     empty / truncated / partial runs that the `seed_*` glob in pes_analysis.py silently
     drops or silently accepts. Rebuilds analysis/pes_structures.csv and reports the effect
     of the partial `stop_16` run on the Fe numbers.
  2. DISTRIBUTION - describes the flat branch as a distribution (per-replica minimum,
     median, IQR) rather than a single point, and contrasts it with the island branch.
  3. MOTIF TEST - the decisive question: are the low-energy structures of a branch the
     *same* structural motif recurring across replicas, or many distinct motifs? Uses the
     AGOX global `Fingerprint` (radial+angular distribution functions: invariant under
     permutation, translation and rotation) as a structural distance, and calibrates the
     "same motif" scale against the distance distribution of random pairs in the branch.

A branch whose low-energy structures sit far below the random-pair distance scale is one
recurring motif (the hand-picked structure is representative -> point claims are defensible).
A branch whose low-energy structures span the random-pair scale is a degenerate manifold
(-> claims must be stated as distribution properties).

Outputs
-------
  analysis/pes_structures.csv               (canonical: seed_* replicas, unchanged schema)
  analysis/pes_structures_with_partial.csv  (adds data/<system>/stop_* partial runs)
  analysis/ensemble_stats.json              (self-describing; see "description" block)

Usage
-----
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/ensemble_analysis.py
"""
VERSION = "1.0.0"

import json
import glob
import os
import csv
import argparse
import numpy as np
from collections import Counter, defaultdict
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

from agox.databases import Database
from agox.models.descriptors import Fingerprint
from agox.environments import Environment

METAL = ('Fe', 'Co')          # film species for the dZ flatness metric
D_CUT = 2.6                   # Angstrom; B-O bonding cutoff (matches pes_analysis.py)
FLAT_DZ = 1.0                 # Angstrom; flat/island split (matches pes_analysis.py)
MIN_ITER = 10                 # relaxation starts at iteration 10
RNG = np.random.default_rng(0)
RAND_PAIRS = 300              # random pairs sampled per (system, branch) for calibration

SYSTEMS = ['femgo', 'febmgo', 'fecomgo', 'fecobmgo']
LABELS = {'femgo': 'Fe/MgO', 'febmgo': 'Fe-B/MgO',
          'fecomgo': 'Fe-Co/MgO', 'fecobmgo': 'Fe-Co-B/MgO'}
CSV_COLS = ['system', 'seed', 'iteration', 'E_total', 'n_atoms',
            'dE_per_atom', 'dZ', 'B_contact_frac']


# ----------------------------------------------------------------------------- loading
def delta_z(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.get_positions()[np.isin(sym, METAL), 2]
    return float(z.max() - z.min()) if len(z) else np.nan


def b_contact_frac(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    if 'B' not in sym:
        return np.nan
    pos = atoms.get_positions()
    b, o = pos[sym == 'B'], pos[sym == 'O']
    d = np.linalg.norm(b[:, None, :] - o[None, :, :], axis=2).min(axis=1)
    return float((d < D_CUT).mean())


def load_system(system, include_partial):
    """Return records for one system: iteration>=MIN_ITER structures, all replicas.

    Mirrors pes_analysis.py exactly for the `seed_*` replicas; optionally also picks up
    `stop_*` (partial) runs, which the original `seed_*` glob drops.
    """
    pats = [f'data/{system}/seed_*/1_db/db_*.db']
    if include_partial:
        pats.append(f'data/{system}/stop_*/1_db/db_*.db')
    dbs = sorted(d for p in pats for d in glob.glob(p))
    recs = []
    for dbp in dbs:
        replica = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
        partial = not replica.startswith('seed_')
        db = Database(filename=dbp)
        db.restore_to_memory()
        cands, data = db.get_all_candidates(), db.get_all_structures_data()
        for c, d in zip(cands, data):
            it = d.get('iteration')
            if it is None or it < MIN_ITER:
                continue
            recs.append(dict(system=system, replica=replica, partial=partial,
                             iteration=int(it), E=float(c.get_potential_energy()),
                             n_atoms=len(c), dZ=delta_z(c), B_contact_frac=b_contact_frac(c),
                             atoms=c.copy()))
    return recs, dbs


def _n_candidates(dbp):
    """Number of candidates stored in a database (0 for an aborted/empty run)."""
    db = Database(filename=dbp)
    db.restore_to_memory()
    return len(db.get_all_candidates())


def normalise(recs):
    """dE_per_atom = (E - E_globalmin)/N, global min computed over the given set."""
    gmin = min(r['E'] for r in recs)
    for r in recs:
        r['dE_per_atom'] = (r['E'] - gmin) / r['n_atoms']
    return gmin


def write_csv(path, recs):
    """Same schema and numeric formatting as scripts/pes_analysis.py (full float repr)."""
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(CSV_COLS)
        for r in sorted(recs, key=lambda r: (r['system'], r['replica'], r['iteration'])):
            w.writerow([r['system'], r['replica'], r['iteration'], r['E'], r['n_atoms'],
                        r['dE_per_atom'], r['dZ'], r['B_contact_frac']])


# ----------------------------------------------------------------------------- stats
def branch_stats(data):
    """Per-replica and pooled statistics for the flat and island branches."""
    dZ = np.array([r['dZ'] for r in data])
    dE = np.array([r['dE_per_atom'] for r in data])
    flat, island = dZ <= FLAT_DZ, dZ > FLAT_DZ
    by_flat, by_isl = defaultdict(list), defaultdict(list)
    for r in data:
        (by_flat if r['dZ'] <= FLAT_DZ else by_isl)[r['replica']].append(r['dE_per_atom'])
    out = {
        'n_structures': len(data),
        'n_replicas': len(set(r['replica'] for r in data)),
        'global_min_dZ': float(dZ[int(np.argmin(dE))]),
        'island': {
            'n': int(island.sum()),
            'min': float(dE[island].min()) if island.any() else None,
            'median': float(np.median(dE[island])) if island.any() else None,
            'p10': float(np.percentile(dE[island], 10)) if island.any() else None,
            'dZ_median': float(np.median(dZ[island])) if island.any() else None,
            'n_within_0.02_of_island_min': int((dE <= dE[island].min() + 0.02).sum())
                                            if island.any() else 0,
        },
        'flat': {
            'n': int(flat.sum()),
            'fraction': float(flat.mean()),
            'min': float(dE[flat].min()) if flat.any() else None,
            'median': float(np.median(dE[flat])) if flat.any() else None,
            'p10': float(np.percentile(dE[flat], 10)) if flat.any() else None,
            'max': float(dE[flat].max()) if flat.any() else None,
            'n_within_0.01_of_flat_min': int((dE[flat] <= dE[flat].min() + 0.01).sum())
                                          if flat.any() else 0,
            'n_within_0.02_of_flat_min': int((dE[flat] <= dE[flat].min() + 0.02).sum())
                                          if flat.any() else 0,
            'n_within_0.04_of_flat_min': int((dE[flat] <= dE[flat].min() + 0.04).sum())
                                          if flat.any() else 0,
        },
    }
    # per-replica minima - the ensemble-level view of the branch
    for key, by in (('flat', by_flat), ('island', by_isl)):
        vals = np.array(sorted(min(v) for v in by.values()))
        out[key]['per_replica_min'] = [float(v) for v in vals]
        out[key]['per_replica_min_median'] = float(np.median(vals)) if len(vals) else None
        out[key]['per_replica_min_sd'] = float(vals.std(ddof=1)) if len(vals) > 1 else None
        out[key]['n_replicas_with_branch'] = int(len(vals))
    return out


def clustered_bootstrap_effect(recs_a, recs_b, n_boot=2000):
    """Distribution shift between the flat branches of two systems, resampling *replicas*
    (the independent unit) rather than structures.

    Reports both statistics the manuscript uses:
      - shift of the per-replica MINIMUM (this is the frozen MT-3/MT-4 statistic)
      - shift of the per-replica MEDIAN (ensemble-level, less sensitive to one lucky replica)
    plus a two-sided permutation p-value on the per-replica minima.
    """
    def per_replica(sample):
        by = defaultdict(list)
        for r in sample:
            if r['dZ'] <= FLAT_DZ:
                by[r['replica']].append(r['dE_per_atom'])
        return {k: min(v) for k, v in by.items()}

    a, b = per_replica(recs_a), per_replica(recs_b)
    ak, bk = list(a), list(b)
    va = np.array([a[k] for k in ak]); vb = np.array([b[k] for k in bk])

    out = {'n_replicas_a': len(ak), 'n_replicas_b': len(bk),
           'per_replica_min_a': float(va.mean()), 'per_replica_min_b': float(vb.mean()),
           'min_shift_eV_per_atom': float(va.min() - vb.min()),
           'median_shift_eV_per_atom': float(np.median(va) - np.median(vb)),
           'mean_shift_eV_per_atom': float(va.mean() - vb.mean())}

    for stat, fn in (('median', np.median), ('mean', np.mean)):
        boots = []
        for _ in range(n_boot):
            sa = [a[k] for k in RNG.choice(ak, len(ak), replace=True)]
            sb = [b[k] for k in RNG.choice(bk, len(bk), replace=True)]
            boots.append(fn(sa) - fn(sb))
        boots = np.array(boots)
        out[f'{stat}_ci95'] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
        out[f'{stat}_same_sign_fraction'] = float((np.sign(boots) == np.sign(out[f'{stat}_shift_eV_per_atom'])).mean())

    # two-sided permutation test on the per-replica minima
    obs = abs(va.mean() - vb.mean())
    pool = np.concatenate([va, vb]); na = len(va)
    perm = np.array([abs(pool[RNG.permutation(len(pool))][:na].mean()
                         - pool[RNG.permutation(len(pool))][na:].mean()) for _ in range(5000)])
    out['perm_p_mean_min'] = float((perm >= obs).mean())
    return out


# ----------------------------------------------------------------------------- motif test
def fingerprint_all(data):
    """AGOX global Fingerprint (radial + angular distribution functions) per structure.

    The descriptor is a distribution function of the whole (template + film) structure, so it
    is invariant under atom permutation, translation and rotation - no alignment needed.
    """
    c0 = data[0]['atoms']
    tmpl = c0.get_template()
    ti = set(c0.get_template_indices().tolist())
    film_syms = Counter(c0[i].symbol for i in range(len(c0)) if i not in ti)
    env = Environment(template=tmpl,
                      symbols=''.join(f'{s}{n}' for s, n in film_syms.items()),
                      print_report=False, use_box_constraint=False)
    fp = Fingerprint(environment=env)
    F = np.array([fp.create_features(r['atoms']).ravel() for r in data])
    return F


def motif_test(data, F, branch, window):
    """Compare the low-energy structures of a branch against the branch's random-pair scale.

    Returns the mean within-set distance, the random-pair distribution summary, their ratio,
    and a single-linkage cluster count at a data-driven cut (5th pct of random-pair distance).
    """
    dZ = np.array([r['dZ'] for r in data])
    dE = np.array([r['dE_per_atom'] for r in data])
    m = dZ <= FLAT_DZ if branch == 'flat' else dZ > FLAT_DZ
    if m.sum() < 2:
        return None
    idx_branch = np.where(m)[0]
    lo = dE[idx_branch].min()
    sel = idx_branch[dE[idx_branch] <= lo + window]
    if len(sel) < 2:
        return {'window': window, 'n_low': int(len(sel)), 'note': 'too few structures'}

    D_low = squareform(pdist(F[sel]))
    iu = np.triu_indices(len(sel), 1)
    within = D_low[iu]

    # random-pair scale of the same branch (calibration)
    rc = RNG.choice(idx_branch, size=(RAND_PAIRS, 2))
    rc = rc[rc[:, 0] != rc[:, 1]]
    rand = np.linalg.norm(F[rc[:, 0]] - F[rc[:, 1]], axis=1)
    cut = float(np.percentile(rand, 5))

    Z = linkage(F[sel], method='single')
    labels = fcluster(Z, t=cut, criterion='distance')
    clusters = {}
    for lab, i in zip(labels, sel):
        clusters.setdefault(int(lab), []).append(data[i]['replica'])

    return {
        'window_eV_per_atom': window,
        'n_low': int(len(sel)),
        'low_set_gmin': float(lo),
        'within_low_mean': float(within.mean()),
        'within_low_max': float(within.max()),
        'random_pair_scale_mean': float(rand.mean()),
        'random_pair_scale_p05': cut,
        'ratio_within_over_random': float(within.mean() / rand.mean()),
        'n_clusters_at_p05_cut': int(len(clusters)),
        'cluster_replicas': {str(k): sorted(set(v)) for k, v in sorted(clusters.items())},
        'cluster_sizes': {str(k): len(v) for k, v in sorted(clusters.items())},
        'replicas_in_low_set': sorted(set(data[i]['replica'] for i in sel)),
        'mean_dZ_low_set': float(dZ[sel].mean()),
        'sd_dZ_low_set': float(dZ[sel].std()),
    }


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-json', default='analysis/ensemble_stats.json')
    args = ap.parse_args()

    canonical, inventory, empty = [], {}, {}
    for system in SYSTEMS:
        all_dbs = sorted(d for d in glob.glob(f'data/{system}/*/1_db/db_*.db')
                         if 'trash' not in d.lower())
        empty[system] = [os.path.basename(os.path.dirname(os.path.dirname(d)))
                         for d in all_dbs if _n_candidates(d) == 0]
        recs, dbs = load_system(system, include_partial=False)
        normalise(recs)
        canonical.extend(recs)
        with_partial, _ = load_system(system, include_partial=True)
        inventory[system] = {
            'n_replica_dirs_on_disk': len(all_dbs),
            'n_seed_dbs_loaded': len(dbs),
            'replicas': sorted(set(r['replica'] for r in recs)),
            'n_replicas_with_data': len(set(r['replica'] for r in recs)),
            'n_structures': len(recs),
            'empty_replica_dirs': empty[system],
            'partial_replicas_on_disk': [os.path.basename(os.path.dirname(os.path.dirname(d)))
                                         for d in all_dbs
                                         if not os.path.basename(os.path.dirname(
                                             os.path.dirname(d))).startswith('seed_')],
            'replicas_used_with_partial': sorted(set(r['replica'] for r in with_partial)),
            'n_structures_with_partial': len(with_partial),
        }
    write_csv('analysis/pes_structures.csv', canonical)
    print(f'wrote analysis/pes_structures.csv ({len(canonical)} rows)')

    # ---- effect of including the partial stop_* runs (Fe host only has one) ----
    partial_effect = {}
    for system in SYSTEMS:
        base, _ = load_system(system, include_partial=False)
        normalise(base)
        full, _ = load_system(system, include_partial=True)
        if len(full) == len(base):
            continue
        recs_all = full
        normalise(recs_all)
        # canonical normalisation applied to the same superset for a like-for-like view
        g_all = min(r['E'] for r in recs_all)
        for r in base:
            r['dE_renorm'] = (r['E'] - g_all) / r['n_atoms']
        for r in recs_all:
            r['dE_renorm'] = r['dE_per_atom']
        partial_effect[system] = {
            'n_structures_without': len(base),
            'n_structures_with': len(recs_all),
            'extra_replicas': sorted(set(r['replica'] for r in recs_all)
                                     - set(r['replica'] for r in base)),
            'global_min_eV_without': min(r['E'] for r in base),
            'global_min_eV_with': g_all,
            'flat_min_without': branch_stats(base)['flat']['min'],
            'flat_min_with_renorm': branch_stats(recs_all)['flat']['min'],
            'flat_fraction_without': branch_stats(base)['flat']['fraction'],
            'flat_fraction_with': branch_stats(recs_all)['flat']['fraction'],
        }
    # variant CSV: all systems with their partial runs included (renormalised per system)
    if partial_effect:
        sup = []
        for system in SYSTEMS:
            recs, _ = load_system(system, include_partial=True)
            normalise(recs)
            sup.extend(recs)
        write_csv('analysis/pes_structures_with_partial.csv', sup)
        print(f'wrote analysis/pes_structures_with_partial.csv ({len(sup)} rows)')

    # ---- per-system statistics + motif tests ----
    stats = {}
    for system in SYSTEMS:
        data = [r for r in canonical if r['system'] == system]
        b = branch_stats(data)
        print(f"\n=== {LABELS[system]} ({system}) ===")
        print(f"  replicas={b['n_replicas']} n={b['n_structures']} "
              f"island={b['island']['n']} flat={b['flat']['n']} ({b['flat']['fraction']:.3f})")
        print(f"  FLAT  min={b['flat']['min']:.4f} median={b['flat']['median']:.4f} "
              f"| per-replica min median={b['flat']['per_replica_min_median']:.4f} "
              f"sd={b['flat']['per_replica_min_sd']:.4f} "
              f"({b['flat']['n_replicas_with_branch']} replicas)")
        print(f"        within +0.01 of min: {b['flat']['n_within_0.01_of_flat_min']}   "
              f"+0.02: {b['flat']['n_within_0.02_of_flat_min']}   "
              f"+0.04: {b['flat']['n_within_0.04_of_flat_min']}")
        print(f"  ISLAND min={b['island']['min']:.4f} median={b['island']['median']:.4f} "
              f"dZ_med={b['island']['dZ_median']:.2f}  within +0.02 of island min: "
              f"{b['island']['n_within_0.02_of_island_min']}")
        F = fingerprint_all(data)
        b['motif'] = {
            'flat': motif_test(data, F, 'flat', 0.02),
            'flat_0.04': motif_test(data, F, 'flat', 0.04),
            'island': motif_test(data, F, 'island', 0.02),
            'island_0.05': motif_test(data, F, 'island', 0.05),
        }
        for k, v in b['motif'].items():
            if v and 'ratio_within_over_random' in v:
                print(f"  MOTIF [{k:10s}] n_low={v['n_low']:3d} "
                      f"within/random={v['ratio_within_over_random']:.3f} "
                      f"clusters@p05={v['n_clusters_at_p05_cut']:3d} "
                      f"replicas={len(v['replicas_in_low_set'])}")
        stats[system] = b

    # ---- B / Co effects as distribution shifts (replica-resampled) ----
    def recs_of(s):
        return [r for r in canonical if r['system'] == s]
    effects = {
        'B_in_Fe_host': clustered_bootstrap_effect(recs_of('femgo'), recs_of('febmgo')),
        'B_in_FeCo_host': clustered_bootstrap_effect(recs_of('fecomgo'), recs_of('fecobmgo')),
        'Co_alone': clustered_bootstrap_effect(recs_of('femgo'), recs_of('fecomgo')),
    }
    print('\n=== effects as a shift of the flat branch (replica-resampled, eV/atom) ===')
    for k, v in effects.items():
        print(f"  {k:14s} per-replica min: {v['per_replica_min_a']:.4f} vs "
              f"{v['per_replica_min_b']:.4f}  shift(min-of-min) {v['min_shift_eV_per_atom']:+.4f}")
        print(f"                 median shift {v['median_shift_eV_per_atom']:+.4f} "
              f"CI95 [{v['median_ci95'][0]:+.4f}, {v['median_ci95'][1]:+.4f}]  "
              f"same-sign {v['median_same_sign_fraction']:.3f}  "
              f"perm-p(mean-min) {v['perm_p_mean_min']:.3f}  "
              f"(n={v['n_replicas_a']} vs {v['n_replicas_b']})")

    # ---- main-text vs SI baseline: same system defined with two different replica sets ----
    si_check = None
    si_csv = 'analysis/method_sensitivity.csv'
    if os.path.exists(si_csv):
        si = [r for r in csv.DictReader(open(si_csv)) if r['setting'].startswith('baseline')]
        if si:
            base = branch_stats([r for r in canonical if r['system'] == 'femgo'])
            femgo_partial, _ = load_system('femgo', include_partial=True)
            normalise(femgo_partial)
            bp = branch_stats(femgo_partial)
            si_check = {
                'si_baseline_row': {k: si[0][k] for k in ('setting', 'n_structures', 'n_seeds',
                                                          'flat_fraction')},
                'main_text_definition': {'n_structures': base['n_structures'],
                                         'n_replicas': base['n_replicas'],
                                         'flat_fraction': base['flat']['fraction']},
                'with_partial_definition': {'n_structures': bp['n_structures'],
                                            'n_replicas': bp['n_replicas'],
                                            'flat_fraction': bp['flat']['fraction']},
                'consistent': (int(si[0]['n_structures']) == bp['n_structures']
                               and int(si[0]['n_seeds']) == bp['n_replicas']),
                'note': ('method_sensitivity.py loads data/<system>/**/*.db (recursive), which '
                         'includes stop_* partial runs; pes_analysis.py loads only seed_*/. '
                         'The same "femgo baseline" is therefore reported with different '
                         'replica counts and a different flat fraction.'),
            }
            print(f"\n=== dataset-definition check (femgo) ===\n"
                  f"  main text (seed_* only): {base['n_structures']} structures / "
                  f"{base['n_replicas']} replicas, flat fraction {base['flat']['fraction']:.3f}\n"
                  f"  SI baseline (recursive): {si[0]['n_structures']} structures / "
                  f"{si[0]['n_seeds']} replicas, flat fraction {float(si[0]['flat_fraction']):.3f}\n"
                  f"  with partial runs:       {bp['n_structures']} structures / "
                  f"{bp['n_replicas']} replicas, flat fraction {bp['flat']['fraction']:.3f}")

    payload = {
        'description': {
            'name': 'ensemble_stats',
            'version': VERSION,
            'produced_by': 'scripts/ensemble_analysis.py',
            'purpose': ('Describe the flat/island PES as ensembles rather than two hand-picked '
                        'structures: replica inventory, branch distributions, and a motif test '
                        'asking whether a branch\'s low-energy structures are one recurring '
                        'structural motif or a degenerate manifold.'),
            'key_definitions': {
                'dZ': 'z(max)-z(min) over Fe+Co film atoms [Angstrom]',
                'dE_per_atom': '(E - E_globalmin)/n_atoms [eV/atom]; global min per system over replicas',
                'flat_branch': f'dZ <= {FLAT_DZ} A',
                'island_branch': f'dZ > {FLAT_DZ} A',
                'replica': 'independent AGOX seed (data/<system>/seed_*/1_db/db_*.db)',
                'motif_distance': ('AGOX global Fingerprint (radial+angular distribution '
                                   'functions, 720-d) Euclidean distance; invariant under '
                                   'permutation/translation/rotation, so no alignment needed'),
                'ratio_within_over_random': ('mean pairwise fingerprint distance among the '
                                             'low-energy structures of a branch, divided by the '
                                             'same quantity for random pairs in that branch. '
                                             '<<1 => one recurring motif; ~1 => degenerate manifold'),
                'n_clusters_at_p05_cut': ('single-linkage clusters of the low-energy set, cut at '
                                          'the 5th percentile of the branch random-pair distance'),
                'statistics_note': ('structures within one replica are correlated, so the replica '
                                    '(seed) is the independent unit; effects are resampled over '
                                    'replicas, not structures'),
            },
            'caveats': [
                'The search is BIASED (LCB exploration seeded from a flat layer), so structure '
                'counts in an energy window are exploration densities, not a density of states. '
                'They support qualitative statements, not thermodynamic entropies.',
                'Structures are not DFT-converged (surrogate relaxation + 1 GPAW step).',
                f'flat/island split at dZ <= {FLAT_DZ} A is a chosen threshold.',
                'Replica counts differ across systems and some replicas are truncated.',
            ],
            'inputs': {'dbs_glob': 'data/{system}/seed_*/1_db/db_*.db (+ stop_* for the partial variant)',
                       'n_structures_canonical': len(canonical)},
            'schema': {
                'systems': 'per-system branch distributions + motif tests',
                'replica_inventory': 'db/replica accounting per system',
                'partial_run_effect': 'effect of including data/<system>/stop_* partial runs',
                'dataset_definition_check': ('same system described with two different replica '
                                             'sets (main text seed_* only vs SI recursive glob)'),
                'effects': 'flat-branch shifts, resampled over replicas (median CI + perm p)',
            },
        },
        'version': VERSION,
        'constants': {'flat_dZ': FLAT_DZ, 'min_iteration': MIN_ITER, 'b_o_cutoff': D_CUT,
                      'random_pairs_per_branch': RAND_PAIRS},
        'replica_inventory': inventory,
        'partial_run_effect': partial_effect,
        'dataset_definition_check': si_check,
        'systems': stats,
        'effects': effects,
    }
    with open(args.out_json, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f'\nwrote {args.out_json}')


if __name__ == '__main__':
    main()
