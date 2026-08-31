# VERSIONS — Project c_landausampling source code version manifest

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

| File | Version | Description |
|---|---|---|
| `main.py` | 1.3.0 | Root runner: load dataset → train GPR → WangLandauSampler → thermodynamics; added `--start-from-min` flag; default init starts from the global minimum (start_from_top=False); added `--e-reject` extrapolation guard; reduced `--large-step` default 0.40→0.20 |
| `wang_landau/__init__.py` | 1.0.0 | Package re-exports |
| `wang_landau/wang_landau_sampler.py` | 1.3.0 | WangLandauSampler (flat-histogram density of states, standard→1/t); added swap move; init fix: default start_from_top=False (start from global minimum); start_from_top=True requires rel E strictly inside [e_min,e_max); added `e_reject` extrapolation guard (reject trials > e_reject, default 5*e_max); reduced default large_step 0.40→0.20 |
| `wang_landau/gpr_training.py` | 1.0.0 | load_all_seeds, build_gpr, validate_gpr |
| `wang_landau/thermodynamics.py` | 1.0.0 | g_of_E_to_thermodynamics, heat_capacity_from_thermo |
| `wang_landau/utils.py` | 1.0.0 | K_B constant, shift_energies, _logsumexp |
| `smoke_test_wang_landau.py` | 1.2.0 | Cheap local validation (fake 1-atom double-well GPR) + 2-species swap-move test + extrapolation-guard test |
| `_analysist/analyze_wl_outputs.py` | 1.0.0 | Extract per-output g(E)/thermo/convergence metrics from c1/c2 wl_output_* dirs + .out logs; plot state density per system |

## Not individually versioned (duplicated snapshots / data)

- `dataset/`, `dataset_boron3/`, `dataset_boron/` — AGOX seed DBs + original
  search code (data; DBs/xsf gitignored).
- `_runs/`, `_analysist/`, `_archives/`, `_tmp/` — run/analysis outputs and
  per-run copies (regenerable or snapshots).
- `j_wanglandau.sh` — batch launcher (not versioned as source).
