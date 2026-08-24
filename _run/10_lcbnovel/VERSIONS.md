# VERSIONS — Project 10_lcbnovel source code version manifest

Every in-scope source file carries a module-level `__version__ = "X.Y.Z"` (semver).
This table is the single-source manifest of current versions. **Update this table
whenever a file's `__version__` is bumped** (and record the old→new in `LOG.md`).

Versioning rules:
- **Initial baseline:** all files start at `1.0.0`.
- **Patch bump (`X.Y.Z` → `X.Y.Z+1`):** on every code edit to a file.
- **Minor bump (`X.Y.Z` → `X.Y+1.0`):** on API/behavior changes.
- The version param lives at module level, after the shebang/docstring and any
  `from __future__` import.

## Source code (tracked, in scope)

| File | Version |
|---|---|
| `main.py` | 1.0.0 |
| `main_benchmark.py` | 1.0.0 |
| `main_benchmark_sweep.py` | 1.0.0 |
| `energy_stats.py` | 1.0.0 |
| `smoke_test_serialization.py` | 1.0.0 |
| `test_window_logic.py` | 1.0.0 |
| `novelty_lcb/__init__.py` | 1.0.0 |
| `novelty_lcb/acquisitor.py` | 1.0.0 |
| `novelty_lcb/benchmark_helpers.py` | 1.0.0 |
| `novelty_lcb/common.py` | 1.0.0 |
| `novelty_lcb/utils.py` | 1.0.0 |
| `scripts/build_fe_stack.py` | 1.0.0 |
| `scripts/build_heteroStruct.py` | 1.0.0 |
| `scripts/build_mgo_stack.py` | 1.0.0 |
| `scripts/hetero_struct_randomize.py` | 1.0.0 |
| `scripts/plot_structure.py` | 1.0.0 |
| `_analysist/run_analysis_indices.py` | 1.0.0 |
| `_analysist/scripts/calculate_relative_energy.py` | 1.0.0 |
| `_analysist/scripts/plot_structure_landscape.py` | 1.0.0 |
| `_analysist/scripts/process_database.py` | 1.0.0 |

## Out of scope (not versioned)

Duplicated snapshot copies under `_runs/1|2|3|73` and `dataset/` (and
`dataset/trash/`) are self-contained per-run snapshots of the source above and are
**not** individually versioned; bump the source file and sync the copy if a run
needs the updated code.
