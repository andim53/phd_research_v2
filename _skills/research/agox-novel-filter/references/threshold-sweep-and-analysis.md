# Threshold sweep + per-threshold landscape/probability analysis

Session-specific detail for the later stages of the novel-filter workflow
(`_run/9_novelFilter`), beyond the core filter in SKILL.md.

## Threshold sweep

`run_filter.py --thresholds <csv>` runs the greedy filter once per threshold
value. Each threshold writes its own folder with ALL kept structures:

```
novel_output/
├── threshold_comparison.csv     # threshold, n_kept, n_removed, kept E range, log_Z, Z
├── thr_0.25/  novel_structures/*.xsf  + novel_structures_summary.csv + partition_function.csv + filter_summary.txt
├── thr_0.5/   ...
└── thr_2/     ...
```

`--threshold` (single float) is used only when `--thresholds` is omitted.
Folder names are `thr_<v:g>` (so `1.0` → `thr_1`, `0.25` → `thr_0.25`).

Verified kept-count vs threshold (Fe/MgO, 1297 in):
| threshold | kept | removed |
|---|---|---|
| 0.25 | 1161 | 136 |
| 0.50 | 655 | 642 |
| 0.75 | 291 | 1006 |
| 1.00 | 164 | 1133 |
| 1.25 | 99 | 1198 |
| 1.50 | 61 | 1236 |
| 2.00 | 32 | 1265 |

## Per-threshold landscape + probability

`run_analysis_thresholds.py` reuses the `_analysist` Stage-2
(`run_stage2_landscape.py`) and Stage-3 (`run_stage3_probability.py`) logic,
looped over every `thr_<v>/`. It imports
`_analysist/scripts/plot_structure_landscape.py` via sys.path.

For each threshold it writes `analysis/thr_<v>/`:
- `conf_space.png` — PCA on fingerprints (top eigenvector of covariance) vs
  per-atom relative energy `(E_i−E_glob)/N` + KDE state-density panel.
- `binding_probability_vs_temperature.png` — Boltzmann
  `P(E)=ρ(E)·exp(−ΔE/kT)/Z` at the reference temperatures
  [298.15, 348.60, 447.875, 547.15, 646.425] K, per-atom relative axis.

Flags: `--thresholds` (folder-name suffixes to analyse, default all),
`--e-max <eV/atom>` (common energy axis across thresholds so panels are
directly comparable), `--normalize-density`.

Verified per-threshold rel-E max (eV/atom): 0.25→0.675, 0.5→0.640, 0.75→0.671,
1.0→0.667, 1.25→0.587, 1.5→0.619, 2.0→0.619. All 14 figures produced.

## Side-by-side structure comparison

`compare_xsf.py --outdir ./novel_output --n 5 --dest ./side_by_side` copies
the top-N (by rank) XSF from every threshold into
`side_by_side/rank<r>/thr_<v>_novel_<rank>_E<e>.xsf`. Pure filesystem copy (no
AGOX needed). Rank 0 is identical across thresholds (global min always kept);
higher ranks diverge — that divergence shows the threshold effect.

## Key data-flow detail

The XSF files carry no energy (see SKILL.md pitfall #2). The analysis scripts
recover energies from each threshold's `novel_structures_summary.csv`
(columns: rank, dataset_index, energy_eV, source, min_dist_to_kept), pairing by
rank parsed from the filename (`novel_<rank>_E<e>.xsf`).
