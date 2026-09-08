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

| `2_analysist/scripts/xrd_groundstate_extract.py` | 1.0.0 | new: extract rel-E=0 ground-state CIFs |
| `2_analysist/scripts/xrd_groundstate_compare.py` | 1.0.0 | new: ground-state XRD + CI comparison plots |

| `2_analysist/scripts/xrd_simulate_crystallinity.py` | 1.4.0 | XRD sim uses scaled=False (true intensity) |
| `2_analysist/scripts/xrd_groundstate_compare.py` | 1.1.0 | XRD sim uses scaled=False (true intensity) |

| `2_analysist/scripts/xrd_groundstate_extract.py` | 2.0.0 | element-agnostic host/interstitial detection |
| `2_analysist/scripts/xrd_groundstate_compare.py` | 2.0.0 | element-agnostic labels; works for any host/interstitial |

| `2_analysist/scripts/xrd_groundstate_compare.py` | 2.1.0 | subscripted-formula legend (e.g. Ta₅₄B₀ (0.0% B)) |

| `2_analysist/run_analysis_indices.py` | 2.9.0 | self-describing `description` block embedded in each stage JSON |
| `2_analysist/scripts/xrd_simulate_crystallinity.py` | 1.4.3 | self-describing `description` block embedded in xrd_plots.json |
| `2_analysist/scripts/xrd_groundstate_compare.py` | 2.1.2 | `--figsize 'W,H'` overlay size flag (INSTR#5) + self-describing `description` block in xrd_plots.json |

| `2_analysist/run_analysis_indices.py` | 2.10.0 | `--novelty-dist` structural-novelty filter for Stages 2/3 (INSTR #6) |
| `2_analysist/run_analysis_indices.py` | 2.11.0 | `--h` Gaussian-KDE bandwidth flag (kde_bw) for Stages 2/3 (INSTR #7) |
| `2_analysist/scripts/plot_structure_landscape.py` | 1.2.0 | `kde_bw` param threaded through Stage-2 landscape density KDE (INSTR #7) |
| `2_analysist/run_analysis_indices.py` | 2.12.0 | Stage-3 continuous probability density (∫P dE=1) as DEFAULT + `--peak-norm` legacy opt-out; `--h` now forwarded into Stage 3; Stage-3 JSON self-describing description upgraded to schema v2 (mode/norm/n_structures/method/dual-mode field legend) |
