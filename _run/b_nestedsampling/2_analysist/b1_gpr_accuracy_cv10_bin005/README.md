# Run b1_gpr_accuracy_cv10_bin005 — GPR accuracy, 50-fold CV, bin 0.1 (Fe_z)

Run directory: `1_runs/b1_gpr_accuracy_cv10_bin005/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`gpr_accuracy.py` v1.4.0) + full dataset.

> Note: dir name retains the original `cv10_bin005`; the current run spec is
> **50-fold CV** (`--cv-folds 50`) at **bin-width 0.1** on the **Fe_z system only**.

## What this run does

Runs `gpr_accuracy.py` in **cross-validation + uncertainty** mode on the combined
Fe/MgO dataset, on the **Fe_z (island-height) system only** (mirrors
`_tmp/gpr_acc_fez_cv3_out` but at much higher CV):

- `--cv --cv-folds 50 --fez --uncertainty --bin-width 0.1` → `out_fez/`

Reference run being scaled up: `_tmp/gpr_acc_fez_cv3_out` (was `--cv-folds 3`).

## Environment

- HPC batch (`j_b1.sh`) activates `gpaw_env` (standing HPC convention). The script
  needs AGOX/ASE (agox_v2 locally); on HPC `gpaw_env` has it. If it fails on AGOX
  imports, switch `conda activate gpaw_env` → `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/1_runs/b1_gpr_accuracy_cv10_bin005
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 --output ./out_fez
```

## Usage (HPC)

```bash
pjsub j_b1.sh
```

## Outputs (`out_fez/`)

- `gpr_accuracy_by_fe_z.csv` (+ `mean_model_std_eV_per_atom` column)
- `uncertainty_by_fe_z.csv`
- `gpr_accuracy_by_energy_range_cv50folds.csv` (energy-range metrics from the same run)
- `uncertainty_by_energy_range.csv`, `cv_fold_summary_50folds.csv`
- `gpr_accuracy_by_fe_z.png`, `gpr_accuracy_by_energy_range_cv50folds.png`
- `DISCUSSION.md`

## Contents

- `gpr_accuracy.py` — latest project-root version (v1.4.0), self-contained
- `dataset/` — full seed DBs (13 DBs, Fe25Mg25O25, ~23 MB; gitignored)
- `j_b1.sh` — PJM batch script (24 cores, gpaw_env), runs the Fe_z CV-50 run
- `README.md` / `TUTORIAL.md` — this run's docs
