# Novel structure filter — distinct (non-repeating) set for a partition function

Run script: `run_filter.py`
Package: `novel_filter/`

## What it does
1. Loads **every** structure from **every** seed database in
   `dataset/seed_*/1_db/db_*.db` (seeds 3–15, 1297 structures, Mg25O25Fe25 /
   75 atoms).
2. Builds one `Fingerprint` descriptor (720-dim) and computes the feature
   vector of every structure (raw Euclidean distances).
3. **Greedily filters** the combined set down to a **distinct (novel) subset**:
   structures are processed lowest-energy first, and a structure is kept only if
   its minimum Euclidean distance in descriptor space to every already-kept
   structure exceeds `--threshold`. This removes near-duplicate structures
   (same basin / local minimum found multiple times across seeds) so each
   structural basin is represented exactly once — **no double counting**.
4. Evaluates the canonical partition function over the distinct subset,
   `Z(T) = sum_i exp(-beta*E_i)`, in log space.

The novelty measure (minimum Euclidean distance in fingerprint space) is the
same one used by `NoveltyLCBAcquisitor` / `is_distinct` in
`_run/6_lcbnovel_benchmark/novelty_lcb/`.

## Environment
Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```

## Usage
```
/home/think/miniconda3/envs/agox_v2/bin/python run_filter.py \
    --thresholds 0.5,1.0,1.5,2.0 --temp 300 --output ./novel_output --rng 42
```

Options:
- `--thresholds` comma-separated list of thresholds to sweep; **each threshold
                 writes its own `thr_<v>/` output folder containing ALL kept
                 `.xsf` files**, so you can compare how the distinct set changes
                 as the filter parameter varies. If omitted, only `--threshold`
                 is used. Default none.
- `--threshold`  single threshold used when `--thresholds` is not given (min
                 **raw Euclidean fingerprint distance** from all kept structures
                 to be novel; same measure as novelty_lcb). Default 1.0.
- `--temp`       temperature (K) for the partition function, default 300
- `--output`     output directory, default `./novel_output`
- `--rng`        RNG seed, default 42

## Outputs (written to `--output`)
For each threshold `--thresholds` entry:
- `thr_<v>/novel_structures/novel_<rank>_E<e>.xsf` — ALL distinct structures for that threshold
- `thr_<v>/novel_structures_summary.csv` — rank, dataset index, energy, source DB,
  min distance to the kept set
- `thr_<v>/partition_function.csv` — rank, energy, Boltzmann weight, log weight over
  the distinct set
- `thr_<v>/filter_summary.txt` — counts and final Z

Plus, across all thresholds:
- `threshold_comparison.csv` — threshold, n_kept, n_removed, kept E range,
  log_Z, Z for every swept threshold (quick side-by-side comparison).

## Comparing structures across thresholds
`compare_xsf.py` copies the top-N structures (by rank) from every threshold
folder into one `side_by_side/` tree for easy eyeballing:
```
python3 compare_xsf.py --outdir ./novel_output --n 5 --dest ./side_by_side
```
This produces `side_by_side/rank<r>/thr_<v>_novel_<rank>_E<e>.xsf` — open the
same-rank folder and cycle the files to see how the structure at that rank
changes as the threshold varies.

## Landscape & probability analysis per threshold
`run_analysis_thresholds.py` runs the same Stage-2 landscape + Stage-3
Boltzmann-probability analyses as `_analysist/run_stage2_landscape.py` and
`_analysist/run_stage3_probability.py`, but once per threshold's filtered set:
```
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py \
    --outdir ./novel_output
```
For each `thr_<v>/` it writes to `novel_output/analysis/thr_<v>/`:
- `conf_space.png` — PCA landscape (top-eigenvector fingerprint projection vs
  per-atom relative energy + KDE state-density panel)
- `binding_probability_vs_temperature.png` — Boltzmann P(E) at 5 temperatures

Structures come from `thr_<v>/novel_structures/*.xsf` (rank-ordered);
energies from `thr_<v>/novel_structures_summary.csv` (xsf carries no energy).
Options: `--thresholds` to select a subset, `--e-max` for a common energy axis,
`--normalize-density`. Run all 7 thresholds to see how the landscape and
probability evolve as the filter goes 0.25 → 2.0.
