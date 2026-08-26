# Run b1_gpr_accuracy_cv10_bin005 — GPR accuracy, 10-fold CV, bin 0.05

Run directory: `_runs/b1_gpr_accuracy_cv10_bin005/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`gpr_accuracy.py` v1.4.0) + full dataset.

## What this run does

Runs `gpr_accuracy.py` in **cross-validation mode with uncertainty** on the combined
Fe/MgO dataset, at **bigger parameters than the reference runs**: **10-fold CV**
(`--cv-folds 10`) and a **finer energy bin** (`--bin-width 0.05` eV/atom vs the
reference 0.1). It covers **both** reference systems in one job:

1. **Energy-range system** (mirrors `_tmp/gpr_acc_cv_uncert_out`):
   `--cv --cv-folds 10 --uncertainty --bin-width 0.05` → `out_energy_range/`
2. **Fe_z (island-height) system** (mirrors `_tmp/gpr_acc_fez_cv3_out`):
   `--cv --cv-folds 10 --fez --uncertainty --bin-width 0.05` → `out_fez/`

Reference runs being scaled up:
- `_tmp/gpr_acc_cv_uncert_out` (was `--cv-folds 3 --bin-width 0.1`)
- `_tmp/gpr_acc_fez_cv3_out` (was `--cv-folds 3 --bin-width 0.1`)

## Environment

- HPC batch (`j_gpr_accuracy_cv10_bin005.sh`) activates `gpaw_env` (standing HPC
  convention). The script needs AGOX/ASE (agox_v2 locally); on HPC `gpaw_env` has it.
  If it fails on AGOX imports, switch `conda activate gpaw_env` → `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b1_gpr_accuracy_cv10_bin005
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 10 --uncertainty --bin-width 0.05 --output ./out_energy_range
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 10 --fez --uncertainty --bin-width 0.05 --output ./out_fez
```

## Usage (HPC)

```bash
pjsub j_gpr_accuracy_cv10_bin005.sh
```

## Outputs

Per output dir (`out_energy_range/`, `out_fez/`):
- `gpr_accuracy_by_energy_range_cv10folds.csv` (+ `mean_model_std_eV_per_atom` column)
- `uncertainty_by_energy_range.csv`
- `cv_fold_summary_10folds.csv` (fold-averaged MAE)
- `gpr_accuracy_by_energy_range_cv10folds.png`
- (fez dir additionally) `gpr_accuracy_by_fe_z.csv`, `uncertainty_by_fe_z.csv`,
  `gpr_accuracy_by_fe_z.png`
- `DISCUSSION.md` in each output dir

## Contents

- `gpr_accuracy.py` — latest project-root version (v1.4.0), self-contained
- `dataset/` — full seed DBs (13 DBs, Fe25Mg25O25, ~23 MB; gitignored)
- `j_gpr_accuracy_cv10_bin005.sh` — PJM batch script (24 cores, gpaw_env)
- `README.md` / `TUTORIAL.md` — this run's docs
