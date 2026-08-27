# Run b3_gpr_accuracy_boron_cv50 — GPR accuracy, 50-fold CV, bin 0.1 (B-doped Fe/MgO)

Run directory: `_runs/b3_gpr_accuracy_boron_cv50/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`gpr_accuracy.py` v1.5.0) + the B-doped
dataset (`dataset_boron/`, copied as `dataset/`).

## What this run does

Runs `gpr_accuracy.py` in **cross-validation + uncertainty** mode on the **B-doped
Fe/MgO** dataset (Fe25Mg25O25B7, 5 seeds, 496 structures), on the **Fe_z
(island-height) system**, with the **same parameters as `_runs/b1_gpr_accuracy_cv10_bin005`**
plus a **high-energy outlier cut**:

```
gpr_accuracy.py --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
                --e-max-per-atom -5.2 --output ./out_fez
```

Same as `b1_gpr_accuracy_cv10_bin005` (50-fold CV, bin 0.1, fez-only) but on the
**B-doped** dataset, with `--e-max-per-atom -5.2` to drop the high-energy outlier
structures (see "Error explanation" below).

## Error explanation & fix (this run)

**Original failure** (`j_b3_gpr_accuracy_boron_cv50.sh.6602525.out`): the run crashed
at the plot step with
`ValueError: 'yerr' (shape: (57,)) ... shape matches 'y' (shape: (22,))`, and the
printed MAE/RMSE/R² were astronomically large (~10⁹ eV/atom, R² ~ −10²⁰).

**Two root causes** (fixed in `gpr_accuracy.py` v1.4.2 → v1.5.0):

1. **Length-mismatch bug when there are empty bins.** `bin_mean_std()` returned one
   value per grid bin (including empty bins → `NaN`), but the plot arrays (`centers`,
   `mae`, …) came from `bin_metrics()` which **skips empty bins**. When a dataset has
   empty energy bins (the boron data, with bins spanning 0–5.6 eV/atom, does), the
   lengths disagree and `matplotlib.errorbar` crashes.
   → **Fix:** `bin_mean_std()` now skips empty bins, aligned with `rows`.

2. **The boron dataset's high-energy outliers break the GPR fit.** The B-doped seeds
   contain a few structures with E/atom up to −0.23 eV (dE above min ≈ 5.6 eV/atom,
   vs ~0.67 for the plain Fe/MgO set). The GPR cannot fit such a wide landscape:
   even in-sample predictions were −7140..+6296 eV, and CV held-out predictions were
   almost all unphysical (|E|>1e4 eV) → empty pooled errors → the crash above.
   → **Fix (two parts):**
   - Added a **`|E|<1e4 eV` physical filter** to the CV and in-sample prediction loops
     (exclude/count unphysical predictions, like the sampler does).
   - Added a **`--e-max-per-atom <eV/atom>` flag** to exclude structures above a
     physical E/atom threshold before training AND evaluation (controllable; default
     = keep all). The b3 run uses **`--e-max-per-atom -5.2`**, which keeps 452
     structures with a spread of ~0.67 eV/atom — matching the working plain Fe/MgO set.

**Verification (real output, 5-fold CV smoke with `-5.2`):** the pipeline now completes
with physical results — fold-averaged MAE = **0.0086 ± 0.0006 eV/atom**, overall
MAE=0.0086 / RMSE=0.0118 / R²=0.996, per-bin MAE 0.0047–0.0115 eV/atom, model std
0.0083 eV/atom, Fe_z + energy-range CSVs/plots written. In-sample MAE ≈ 0.0002 eV/atom.

## Dataset (boron)

- Copied from `dataset_boron/` into this run as `dataset/` (gpr_accuracy.py reads
  `./dataset`).
- Composition: **Fe25Mg25O25B7** (7 B atoms doped into the Fe layer), 5 seeds (0-4),
  100 structures each (seed_4 has 96) = **496 structures** total.
- Uniform composition across all seeds → single Fingerprint descriptor valid.
- **Note:** seeds 2-4 contain high-energy outlier structures (E/atom up to −0.23 eV)
  that are likely DFT failures; they must be excluded for the GPR to fit. The run uses
  `--e-max-per-atom -5.2` to drop them (452 structures remain).

## Environment

- HPC batch (`j_b3_gpr_accuracy_boron_cv50.sh`) activates `gpaw_env` (standing HPC
  convention). The script needs AGOX/ASE (agox_v2 locally). If it fails on AGOX
  imports, switch `conda activate gpaw_env` → `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b3_gpr_accuracy_boron_cv50
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
    --e-max-per-atom -5.2 --output ./out_fez
```

## Usage (HPC)

```bash
pjsub j_b3_gpr_accuracy_boron_cv50.sh
```

## Outputs (`out_fez/`)

- `gpr_accuracy_by_fe_z.csv` (+ `mean_model_std_eV_per_atom` column)
- `uncertainty_by_fe_z.csv`
- `gpr_accuracy_by_energy_range_cv50folds.csv` + `uncertainty_by_energy_range.csv`
- `cv_fold_summary_50folds.csv` (per-fold MAE + mean/std, 50 rows)
- `gpr_accuracy_by_fe_z.png`, `gpr_accuracy_by_energy_range_cv50folds.png`
- `DISCUSSION.md`

## Contents

- `gpr_accuracy.py` — latest project-root version (v1.5.0), self-contained
- `dataset/` — B-doped seed DBs (5 DBs, Fe25Mg25O25B7; gitignored)
- `j_b3_gpr_accuracy_boron_cv50.sh` — PJM batch script (24 cores, gpaw_env),
  runs with `--e-max-per-atom -5.2`
- `README.md` / `TUTORIAL.md` — this run's docs
