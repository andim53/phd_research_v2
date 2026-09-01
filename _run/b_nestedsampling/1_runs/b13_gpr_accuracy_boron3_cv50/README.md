# Run b13_gpr_accuracy_boron3_cv50 — GPR accuracy, 50-fold CV, bin 0.1 (B3-doped Fe/MgO)

Run directory: `1_runs/b13_gpr_accuracy_boron3_cv50/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`gpr_accuracy.py` v1.5.1) + the **boron3** dataset
(`dataset_boron3/`, copied as `dataset/`, **6 non-empty seeds**; seed_6 is empty and excluded).

## What this run does

Runs `gpr_accuracy.py` in **cross-validation + uncertainty** mode on the **boron3** dataset
(B3Fe25Mg25O25, 6 seeds, 597 structures), on the **Fe_z (island-height) system**, with the **same
parameters as `1_runs/b3_gpr_accuracy_boron_cv50`**:

```bash
gpr_accuracy.py --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
                --e-max-per-atom 0.67 --output ./out_fez
```

Same as b3 (50-fold CV, bin 0.1, fez-only) but on the **boron3** dataset (B3Fe25Mg25O25, 78
atoms) instead of b3's boron (Fe25Mg25O25B7, 82 atoms). `--e-max-per-atom 0.67` keeps structures
within 0.67 eV/atom of the dataset minimum (568 of 597 remain), dropping the high-energy
outliers that otherwise break the GPR fit.

## Dataset (boron3)

- Copied from `dataset_boron3/` into this run as `dataset/` (gpr_accuracy.py reads `./dataset`).
- Composition: **B3Fe25Mg25O25** (3 B atoms doped into the Fe layer), 78 atoms, 6 non-empty
  seeds (0-5; seed_6 is empty and excluded), 100 structures each (seed_3 has 97) = **597
  structures** total.
- Uniform composition across all seeds → single Fingerprint descriptor valid.
- `--e-max-per-atom 0.67` (relative to the dataset minimum) keeps **568 / 597** structures.

## Environment

- HPC batch (`j_b13_gpr_accuracy_boron3_cv50.sh`) activates `gpaw_env` (standing HPC
  convention). The script needs AGOX/ASE (agox_v2 locally). If it fails on AGOX
  imports, switch `conda activate gpaw_env` → `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/1_runs/b13_gpr_accuracy_boron3_cv50
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
    --e-max-per-atom 0.67 --output ./out_fez
```

## Usage (HPC)

```bash
pjsub j_b13_gpr_accuracy_boron3_cv50.sh
```

## Outputs (`out_fez/`)

- `gpr_accuracy_by_fe_z.csv` (+ `mean_model_std_eV_per_atom` column)
- `uncertainty_by_fe_z.csv`
- `gpr_accuracy_by_energy_range_cv50folds.csv` + `uncertainty_by_energy_range.csv`
- `cv_fold_summary_50folds.csv` (per-fold MAE + mean/std, 50 rows)
- `gpr_accuracy_by_fe_z.png`, `gpr_accuracy_by_energy_range_cv50folds.png`
- `DISCUSSION.md`

## Contents

- `gpr_accuracy.py` — latest project-root version (v1.5.1), self-contained
- `dataset/` — boron3 seed DBs (6 DBs, B3Fe25Mg25O25; gitignored)
- `j_b13_gpr_accuracy_boron3_cv50.sh` — PJM batch script (24 cores, gpaw_env),
  runs with `--e-max-per-atom 0.67`
- `README.md` / `TUTORIAL.md` — this run's docs
