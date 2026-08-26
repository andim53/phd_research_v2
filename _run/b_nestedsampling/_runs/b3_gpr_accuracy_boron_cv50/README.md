# Run b3_gpr_accuracy_boron_cv50 — GPR accuracy, 50-fold CV, bin 0.1 (B-doped Fe/MgO)

Run directory: `_runs/b3_gpr_accuracy_boron_cv50/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`gpr_accuracy.py` v1.4.0) + the B-doped
dataset (`dataset_boron/`, copied as `dataset/`).

## What this run does

Runs `gpr_accuracy.py` in **cross-validation + uncertainty** mode on the **B-doped
Fe/MgO** dataset (Fe25Mg25O25B7, 5 seeds, 496 structures), on the **Fe_z
(island-height) system**, with the **same parameters as `_runs/b1_gpr_accuracy_cv10_bin005`**:

```
gpr_accuracy.py --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 --output ./out_fez
```

Same as `b1_gpr_accuracy_cv10_bin005` (50-fold CV, bin 0.1, fez-only) but on the
**B-doped** dataset instead of the plain Fe/MgO set.

## Dataset (boron)

- Copied from `dataset_boron/` into this run as `dataset/` (gpr_accuracy.py reads
  `./dataset`).
- Composition: **Fe25Mg25O25B7** (7 B atoms doped into the Fe layer), 5 seeds (0-4),
  100 structures each (seed_4 has 96) = **496 structures** total.
- Uniform composition across all seeds → single Fingerprint descriptor valid.

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
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 --output ./out_fez
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

- `gpr_accuracy.py` — latest project-root version (v1.4.0), self-contained
- `dataset/` — B-doped seed DBs (5 DBs, Fe25Mg25O25B7; gitignored)
- `j_b3_gpr_accuracy_boron_cv50.sh` — PJM batch script (24 cores, gpaw_env)
- `README.md` / `TUTORIAL.md` — this run's docs
