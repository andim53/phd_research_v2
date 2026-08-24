---
name: agox-novel-filter
description: "Use when deduplicating AGOX DB structures."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agox, novelty, dedup, fingerprint, partition-function, materials-science, database]
    related_skills: [agox, agox-nested-sampling, agox-gpr-analysis, simulation-analysis]
---

# AGOX Novel-Structure Filtering (dedup for partition-function representation)

## Overview

Deduplicates every structure across all AGOX seed databases down to a **distinct
(novel) subset** where no two structures are "alike", measured by the minimum
Euclidean distance in fingerprint descriptor space. This gives a
partition-function representation with **no double counting** — each structural
basin / local minimum appears exactly once (its lowest-energy representative).
Reusable pieces live in `/home/think/Desktop/research/_run/9_novelFilter/`:

- `run_filter.py` — run script: globs all `seed_*/1_db/db_*.db`, builds one
  Fingerprint descriptor, filters, evaluates `Z(T)` over the distinct set.
- `novel_filter/` — importable package (`filter_novel`, `build_features`,
  `nearest_neighbour_distances`, `partition_function`, `save_novel_subset`).

The novelty measure is the SAME one used by `NoveltyLCBAcquisitor` /
`is_distinct` in `_run/6_lcbnovel_benchmark/novelty_lcb/`, so thresholds compose.

## When to Use

- Removing duplicate / near-identical structures before computing a partition
  function, DOS, or any per-structure sum over a multi-seed AGOX dataset.
- Building a diverse representative set from many seeds (each basin once).
- Any "filter structures that are not alike" task on AGOX `.db` files.

## Environment

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0).
- `matplotlib.use('Agg')` before any plotting import in headless runs.
- Same dataset convention as `agox-nested-sampling`: `dataset/seed_*/1_db/db_*.db`,
  all seeds must share one composition/atom count for a single global Fingerprint.
  Verify with `Counter(tuple(a.get_chemical_symbols()))` before combining.

## Core technique (verified on Fe/MgO, 1297 structures, Mg25O25Fe25)

1. **Load all seeds**: `Database(filename=p) → restore_to_memory() →
   restore_to_trajectory()`; energies via `a.get_potential_energy()`.
2. **Descriptor**: `Fingerprint.from_atoms(structures[0])` (720-dim for Fe/MgO).
   `descriptor.get_features(a).ravel()` == `create_features(a)`; shape `(1,720)`.
3. **Greedy filter**: process structures lowest-energy first; keep a structure
   only if its min Euclidean distance to every already-kept structure **exceeds**
   the threshold. Lowest-energy-first ⇒ the lowest-energy member of each basin is
   kept as its representative (energy-ascending `order = np.argsort(energies)`).
   First structure is always kept (`min_dist = inf`).
4. **Partition function in log space** over the kept set:
   `log_w = -beta*(E - E_ref)`, `log_Z = m + log(sum(exp(log_w - m)))` (stable
   log-sum-exp), normalised `log_weights = log_w - log_Z`. Energies ~ -400 eV and
   beta ~ 40 mean raw `exp(beta*E)` over/underflows.

## Run

```bash
cd /home/think/Desktop/research/_run/9_novelFilter
/home/think/miniconda3/envs/agox_v2/bin/python run_filter.py \
    --threshold 1.0 --temp 300 --output ./novel_output --rng 42
```

Outputs: `novel_structures/novel_<rank>_E<e>.xsf`, `novel_structures_summary.csv`
(rank, dataset index, energy, source DB, min-dist-to-kept),
`partition_function.csv` (energy + Boltzmann weights), `filter_summary.txt`.

## Common Pitfalls

1. **DO NOT row-normalise the feature vectors.** This was the single biggest trap.
   After normalisation the Fe/MgO NN distances compress to min 0.0009 / median 0.037
   / max 0.167, so ANY threshold over ~0.17 collapses the set (0.35 → only 7 kept).
   Use **raw** Euclidean fingerprint distances (matching novelty_lcb), where
   distinct minima are ~1-6 apart and near-duplicates are much closer.
2. **Calibrate the threshold from the NN-distance distribution first**, don't guess.
   Compute `nearest_neighbour_distances(features)` and read `fract < threshold`
   before filtering. Fe/MgO raw NN: min 0.010, median 0.40, p95 0.94, max 1.80.
   Threshold 1.0 keeps 164; rough kept counts: 0.5→655, 1.0→164, 1.5→61, 2.0→32.
3. **`np.savetxt` cannot write mixed string/float rows** — the summary CSV carries a
   source-DB string. Writing it with `np.savetxt(..., fmt=["%d","%d","%.6f","%s",...])`
   over a `np.asarray(rows, dtype=float)` fails with `could not convert string to
   float`. Write mixed-type CSVs manually with `open(...)` + f-string rows.
4. **Do the whole partition-function sum in log space** (see step 4) so hot-tail
   weights underflow to exactly 0.0 without a divide-by-zero warning — compute
   `log_weights` from the stable logsumexp and write those, not `np.log(weights)`.
5. **Uniform composition required** — one global Fingerprint only supports one
   stoichiometry. Same pre-check as nested sampling.

## Reference files

- `references/calibration-and-verification.md` — NN-distance distribution, kept-count
  vs threshold table, verified run outputs, and the row-normalisation trap in detail.

## Verification Checklist

- [ ] `Counter` over `get_chemical_symbols()` confirms one composition / atom count
- [ ] Features are RAW (not row-normalised); NN distances span ~0.01 to ~1.8 for Fe/MgO
- [ ] Threshold chosen from the NN distribution, not guessed
- [ ] Mixed-type CSV written manually, not via `np.savetxt`
- [ ] `partition_function` returns `(Z, log_Z, weights, log_weights)` computed in log space
- [ ] Run via `/home/think/miniconda3/envs/agox_v2/bin/python`
