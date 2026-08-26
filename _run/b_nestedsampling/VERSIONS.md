# VERSIONS — Project b_nestedsampling source code version manifest

Every in-scope source file carries a module-level `__version__ = "X.Y.Z"` (semver).
This table is the single-source manifest of current versions. **Update this table
whenever a file's `__version__` is bumped** (and record the old→new in `LOG.md`).

Versioning rules:
- **Initial baseline:** all files start at `1.0.0`.
- **Patch bump (`X.Y.Z` → `X.Y.Z+1`):** on every code edit to a file.
- **Minor bump (`X.Y.Z` → `X.Y+1.0`):** on API/behavior changes.
- The version param lives at module level, after the shebang/docstring and any
  `from __future__` import. Pre-existing function-local `__version__` values in
  `scripts/*.py` (0.0.1) are left untouched.

## Source code (tracked, in scope)

| File | Version |
|---|---|
| `main.py` | 1.1.0 |
| `nested_sampling/__init__.py` | 1.0.0 |
| `nested_sampling/__main__.py` | 1.0.0 |
| `nested_sampling/nested_sampler.py` | 1.1.0 |
| `nested_sampling/gpr_training.py` | 1.0.0 |
| `nested_sampling/state_density.py` | 1.0.0 |
| `nested_sampling/utils.py` | 1.0.0 |
| `smoke_test_temperature_free.py` | 1.0.0 |
| `scripts/build_mgo_stack.py` | 1.0.0 |
| `scripts/build_fe_stack.py` | 1.0.0 |
| `scripts/build_heteroStruct.py` | 1.0.0 |
| `scripts/hetero_struct_randomize.py` | 1.0.0 |
| `scripts/plot_structure.py` | 1.0.0 |

## Not individually versioned (duplicated snapshots / data)

- `dataset/` — original AGOX search code + seed DBs (data; DBs gitignored).
- `_runs/`, `_analysist/`, `_archives/`, `_tmp/` — run/analysis outputs and
  per-run copies (regenerable or snapshots).
