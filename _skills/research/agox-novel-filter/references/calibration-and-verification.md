# Calibration & verification for novel-filter (Fe/MgO, 1297 structures)

## The row-normalisation trap (why raw features are mandatory)

First attempt row-normalised the 720-dim fingerprint vectors to unit length.
The resulting feature space is on a hypersphere, compressing all pair distances:

| metric | raw Euclidean | after row-normalisation |
|---|---|---|
| min NN distance | 0.010 | 0.0009 |
| median NN distance | 0.40 | 0.037 |
| max NN distance | 1.80 | 0.167 |

With normalised features, ANY threshold over ~0.17 collapses the whole dataset:
`threshold=0.35` kept only **7** of 1297 structures. This is useless.

**Lesson:** use RAW Euclidean fingerprint distances. Distinct local minima in
the Fe/MgO system are ~1–6 apart in raw units (matching the `novelty_lcb`
reference distances); near-duplicate relaxations of the same basin are far
closer. The raw scaling is the one the acquisitor was calibrated against, so
thresholds compose with `_run/6_lcbnovel_benchmark/novelty_lcb/`.

## Raw NN-distance distribution (guidance for threshold choice)

```
min=0.0100  p5=0.1569  median=0.4029  p95=0.9407  max=1.7957
frac NN < 0.50 : 0.678
frac NN < 1.00 : 0.957
frac NN < 1.50 : 0.994
frac NN < 2.00 : 1.000
```

95.7% of structures have a near-twin within distance 1.0 — the dataset is dense
with near-duplicates (100 structures per seed, 13 seeds, many re-discoveries of
the same basins). Threshold 1.0 cleanly separates genuine distinct minima.

## Kept count vs threshold (energy-ordered greedy filter)

| threshold | kept / 1297 | kept E range (eV) |
|---|---|---|
| 0.10 | 1282 | -436.909 .. -386.292 |
| 0.25 | 1161 | -436.909 .. -386.292 |
| 0.50 | 655 | -436.909 .. -388.934 |
| 0.75 | 291 | -436.909 .. -386.600 |
| 1.00 | 164 | -436.909 .. -386.905 |
| 1.25 | 99 | -436.909 .. -392.888 |
| 1.50 | 61 | -436.909 .. -390.466 |
| 2.00 | 32 | -436.909 .. -390.466 |

The lowest-energy structure (-436.909 eV) is always kept first; `E_ref` and the
ground-state basin survive at every threshold.

## Verified run (defaults: threshold=1.0, temp=300 K, rng=42)

- kept 164 novel / 1297 total (removed 1133 duplicates)
- partition function Z(300 K) = 1.063335  (log Z = 0.0614)
- ground state dominates: Boltzmann weight 0.9404; next 0.0596; all others <1e-43
- outputs: 164 XSF in `novel_structures/`, `novel_structures_summary.csv`,
  `partition_function.csv`, `filter_summary.txt`

## Code quirks fixed during development

1. **Mixed-type CSV** — `np.savetxt` cannot write a `%s` column when the array is
   `dtype=float`; it raised `ValueError: could not convert string to float:
   'seed_7/1_db/db_7.db'`. Fix: write the summary CSV manually via
   `open(path,"w")` + f-string rows.
2. **Partition function underflow** — taking `np.log(weights)` on already-
   exponentiated weights triggers `RuntimeWarning: divide by zero` for hot-tail
   structures whose weight underflows to exactly 0.0. Fix: keep everything in log
   space — `log_weights = log_w - log_Z` with stable log-sum-exp, and write the
   log weights directly (not `np.log(weights)`). `partition_function` returns
   `(Z, log_Z, weights, log_weights)`.

## Verified API facts (AGOX 3.10.2)

- `descriptor.get_features(atoms).ravel()` == `descriptor.create_features(atoms).ravel()`,
  both shape `(1, 720)` for Fe/MgO, dtype float64.
- `Database(filename=p) → restore_to_memory() → restore_to_trajectory()` returns a
  list of ASE Atoms; energies via `a.get_potential_energy()`.
- `Fingerprint.from_atoms(structures[0])` is the correct constructor (the
  `Fingerprint(environment=Environment(...))` form can fail to parse symbols).
