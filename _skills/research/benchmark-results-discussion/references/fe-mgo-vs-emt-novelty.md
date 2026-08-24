# Worked example — replicating a benchmark's novelty analysis onto another project

Scenario (session 2026-08-24): user pointed at a results project
`_analysist/1_result/73_novel_benchEMT` (Ni8/Au EMT toy benchmark) and asked to
"perform the same novelty analysis, only the analysis" on a *different* project's
real databases — `_analysist/1_result/72_novel_AutoGlob_1eVperAtomAboveGlob`
(Fe25Mg25O25 on MgO(001), GPAW, seed 3). No AGOX search was re-run; only the analysis
functions were reused.

## The two databases analysed (seed 3, 100 evals each)

- Regular LCB: `dataset/seed_3/1_db/db_3.db`  (best −435.315 eV)
- Novelty-LCB: `output/seed_3/1_db/db_3.db`    (best −432.015 eV)

Both Fe25Mg25O25 (75 atoms), composition uniform, 100 finite-energy candidates.

## Key numbers (DUP_THRESHOLD = 1.5, Fe/MgO Fingerprint descriptor)

| Metric | Regular LCB | Novelty-LCB |
|---|---|---|
| Distinct configurations | 48 | 75 |
| Duplicate evaluations | 52 (52%) | 25 (25%) |
| Best energy (eV) | −435.315 | −432.015 |
| Energy range (eV) | 44.85 | 44.30 |
| Distinct below −430 eV | 8 | 6 |

Discovery curves: Regular saturates ~47 distinct by eval ~90; Novelty is still climbing
to 74 at eval 100 (71→74 between evals 91–100) — never flattens.

## The critical techniques that made this correct

1. **Use the target project's OWN descriptor.** Built the Fe/MgO environment via
   `main.build_environment(slab_substrate, slab_deposition)` + `Fingerprint` (720-dim),
   NOT the EMT benchmark's descriptor. Reusing the toy descriptor would compute distances
   in the wrong feature space.
2. **Verify the DBs before trusting metrics** — load with
   `Database(filename, initialize=False)` + `restore_to_memory()` + `get_all_candidates()`,
   check `Counter(symbols)` and finite-energy counts.
3. **Run under `agox_v2`** (`/home/think/miniconda3/envs/agox_v2/bin/python`). The
   base/sandbox python has no AGOX — `execute_code` cannot import `agox`. Write a `.py`
   and run it via terminal with the env python (or use execute_code only for numpy
   aggregation over the results JSON).

## The DUP_THRESHOLD default gotcha

User asked to "compare based on the code's default DUP_THRESHOLD." Reading the source:
- `73_novel_benchEMT/main_benchmark.py` → `DUP_THRESHOLD = 1.5` (the benchmark-analysis
  value used by `get_distinct_configurations`).
- `novelty_lcb/acquisitor.py` → `is_distinct(..., threshold=0.1)` (a different helper
  default).

Use the benchmark-analysis default (1.5) for cross-project comparability and state it.
Absolute distinct counts scale with the threshold; the relative Novelty-vs-Regular
comparison is robust to it. Lesson: read the actual source, don't assume the threshold
transfers.

## Cross-system lesson (toy vs real landscape)

The same method gave opposite-looking results on the two systems:
- **EMT toy (73):** novelty marginal — both acquisitors ~1–2 basins, ~97% duplicates.
- **Fe/MgO real (72):** novelty strong — +27 distinct basins, duplicates 52%→25%,
  but 3.3 eV shallower best minimum.

Interpretation: the smooth few-basin EMT surface gives the novelty term nothing to find;
the rough, many-basin Fe/MgO landscape is where novelty's diversity pressure pays off.
When a discussion spans systems, call out that a toy-landscape null/marginal result is a
property of the landscape, not of the method. For the parent project's goal (build a
diverse basin database for downstream novel-filter/nested-sampling), Novelty-LCB is the
better acquisitor; Regular LCB is better only if the sole goal is the single deepest
minimum.
