# Novel (distinct) structure filter — dedup AGOX DBs for a partition function

The sibling of nested sampling: instead of sampling a GPR surrogate, this *directly
dedups* the already-relaxed structures in a multi-seed AGOX database so each
structural basin is counted exactly once. Needed because across seeds the search
re-finds the same minima many times as slightly different relaxations; summing
`Z = sum_i exp(-beta*E_i)` over ALL stored structures double-counts each basin.

Reusable code: `/home/think/Desktop/research/_run/9_novelFilter/`
(`run_filter.py` + `novel_filter/` package, README + NOVEL_FILTER_RUN.md).
Env python `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Technique

1. Load all `seed_*/1_db/db_*.db` (glob + `Database`/`restore_to_trajectory`), keep
   structures + energies + per-structure source DB.
2. `Fingerprint.from_atoms(structures[0])` → feature matrix (n, 720) via
   `descriptor.get_features(a).ravel()`.
3. **Greedy energy-ordered selection**: `order = argsort(energies, stable)`; keep a
   structure iff its minimum Euclidean distance to every already-kept feature vector
   is `> threshold`. Lowest-energy member of each basin is kept (the right
   representative for Boltzmann weighting). Chunk the pairwise distance computation
   (128-block) so you never materialise an n×n matrix.
4. Partition function over the kept set in log space: `log w = -beta*(E - E_ref)`,
   log-sum-exp normalisation, return weights AND log-weights.
5. **Threshold sweep**: pass a comma-separated `--thresholds` list; each value writes
   its own `thr_<v>/novel_structures/*.xsf` folder so the distinct sets can be
   compared side by side across filter parameters. `threshold_comparison.csv` at the
   top collates n_kept / n_removed / E range / log_Z / Z per threshold.

## CRITICAL pitfall: raw vs row-normalised features

The AGOX `Fingerprint` raw vectors have norm ≈ 10 (Fe/MgO: min 9.7, med 10.8,
max 12.3). **If you row-normalise to unit length before computing distance, all
inter-structure distances collapse to < ~0.17** (max nearest-neighbour), so a
sensible-looking threshold (e.g. 0.35) over-filters to a handful of structures
(7/1297 in the first attempt). Use **raw Euclidean distances** — matching the
novelty measure in `_run/6_lcbnovel_benchmark/novelty_lcb` — and a threshold in
raw units.

## Threshold calibration is data-driven

Print the nearest-neighbour-distance distribution first (chunked). Fe/MgO verified:
min 0.010, median 0.403, p95 0.941, max 1.796; 95.7% of structures have a near-twin
within 1.0. The "knee" separating near-duplicate relaxations from genuinely distinct
minima is ≈ 1.0 here. Kept counts vs raw threshold (energy-ordered greedy):
0.25→1161, 0.5→655, 0.75→291, **1.0→164**, 1.25→99, 1.5→61, 2.0→32.

## Implementation gotchas

- `np.savetxt` **cannot write mixed string/float rows** — a `fmt=["%d","%f","%s",...]`
  on a float-typed array raises `ValueError: could not convert string to float`.
  Write the summary CSV manually with a `for` loop when it carries a source-DB
  string column.
- Return log-weights, not just `np.exp(weights)` — normalised weights underflow to
  0 on hot tails and `np.log(0)` fires a `RuntimeWarning: divide by zero`.
- `verify_uniform_composition` (one formula + one atom count) is a hard prerequisite
  for a single global descriptor; raise rather than silently producing a broken one.

## Scope note

This is a **dedup of already-relaxed structures — no GPR is trained.** If you want a
*surrogate-sampled* partition function (new structures, not just DB ones), that is the
nested-sampling path in the parent SKILL.md, not this filter.
