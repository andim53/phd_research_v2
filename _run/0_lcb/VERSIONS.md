# VERSIONS.md — Source version manifest

Every source file carries a module-level `__version__ = "X.Y.Z"` (semver, baseline
`1.0.0`). **Any code change bumps that version**; update this manifest and record
old→new in `LOG.md`.

- **Bump rule:** patch (`1.0.0 → 1.0.1`) on every edit; minor (`1.0.1 → 1.1.0`) on
  API/behavior changes.
- **Scope:** version **source only**. The per-run duplicated snapshots under
  `17_PPt/<cell>/<conc>/scripts/` and `generated_structures/` are **not**
  individually versioned — edit the canonical `17_PPt/scripts/` + family `main.py`.

## Current versions

| File | Version |
|---|---|
| `2_analysist/run_analysis_indices.py` | 2.3.0 |
| `2_analysist/scripts/plot_structure_landscape.py` | 1.1.0 |
| `2_analysist/scripts/xrd_simulate_crystallinity.py` | 1.1.0 |

> `17_PPt/` scripts and `main.py` files currently carry no module-level `__version__`
> (pre-dates this project). Adding/bumping versions for them is a pending task.

| `2_analysist/run_analysis_indices.py` | 2.4.0 | `--seeds` subset + legend-clip fix |

| `2_analysist/run_analysis_indices.py` | 2.5.0 | `--xlabel` custom Stage-1 x-axis title |

| `2_analysist/run_analysis_indices.py` | 2.6.0 | `--x-max` cap on Stage-1 x-axis |

| `2_analysist/run_analysis_indices.py` | 2.7.0 | `--no-bullets` flag on Stage-1 progression |

| `2_analysist/run_analysis_indices.py` | 2.8.0 | `--no-gs-star` flag on Stage-1 progression |

| `2_analysist/scripts/extract_rel_window_xsf.py` | 1.0.0 | new: .xsf export by rel-E/atom window |

| `2_analysist/scripts/xrd_simulate_crystallinity.py` | 1.2.0 | CI-plot x-axis uses shared energy label E_LABEL |

| `2_analysist/scripts/xrd_simulate_crystallinity.py` | 1.3.0 | `--ci-x-data-max`/`--ci-x-max`/`--ci-y-max` on CI plot |

| `2_analysist/scripts/xrd_extract_structures.py` | 1.1.0 | adaptive window-label precision for fine bins |
