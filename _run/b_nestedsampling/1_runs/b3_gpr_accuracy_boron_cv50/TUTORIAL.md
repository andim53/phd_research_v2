# TUTORIAL — Reproduce run b3_gpr_accuracy_boron_cv50

Step-by-step guide to reproduce this run (GPR accuracy, 50-fold CV, uncertainty,
bin 0.1, Fe_z system, B-doped dataset) in isolation. Level: intermediate.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0) for local runs:
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- HPC pjsub (PJM) for the batch run (`gpaw_env`, set in `j_b3_gpr_accuracy_boron_cv50.sh`).
- Dataset present in this dir: `dataset/seed_*/1_db/db_*.db` (5 DBs, Fe25Mg25O25B7).

## Step 0 — What this run does

A single invocation of `gpr_accuracy.py` in **50-fold CV + uncertainty** mode at
**bin-width 0.1** on the **Fe_z (island-height) system** of the **B-doped** Fe/MgO
dataset — identical parameters to `1_runs/b1_gpr_accuracy_cv10_bin005`, but on
Fe25Mg25O25B7 (496 structures):

```
gpr_accuracy.py --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
                --e-max-per-atom 0.67 --output ./out_fez
```

50-fold CV trains 50 GPRs (one per fold); ~10 test structures per fold on this
smaller 452-structure (post-cut) set. Higher CV → robust held-out pooling but
**slower** (50 GPR trainings — expect several hours on HPC).

`--e-max-per-atom 0.67` drops structures with E/atom − min E/atom > 0.67 eV (the high-energy
outliers from seeds 2-4 that otherwise break the GPR fit). See README.md "Error
explanation & fix".

## Step 1 — Local run (validate on a small scale first if desired)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/1_runs/b3_gpr_accuracy_boron_cv50
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
    --e-max-per-atom 0.67 --output ./out_fez
```

For a quick local sanity check you can lower `--cv-folds` (e.g. 5) temporarily; the
HPC job uses 50.

## Step 2 — HPC launch

```bash
pjsub j_b3_gpr_accuracy_boron_cv50.sh
```

- Header: 24 cores, `gpaw_env`, 120 h.
- The job runs the single Fe_z invocation with `OMP_NUM_THREADS=1`.

## Step 3 — Outputs & verification (`out_fez/`)

- `gpr_accuracy_by_fe_z.csv` — per-bin (island-height) MAE/RMSE/R² (+ mean model std).
- `uncertainty_by_fe_z.csv` — per-bin mean model std.
- `gpr_accuracy_by_energy_range_cv50folds.csv` + `uncertainty_by_energy_range.csv`.
- `cv_fold_summary_50folds.csv` — per-fold MAE + mean/std (50 rows).
- `*.png` plots; `DISCUSSION.md`.

Sanity checks:
- `cv_fold_summary_50folds.csv` should have 50 fold rows.
- Fe_z CSV should show MAE varying with island height.

## Pitfalls

- **Env:** job uses `gpaw_env`; if AGOX imports fail, edit the `.sh` to
  `conda activate agox_v2`.
- **Runtime:** 50-fold CV = 50 GPR trainings — use the HPC job, not local at full folds.
- **Composition:** dataset must stay uniform Fe25Mg25O25B7 for the single descriptor.
- **Physical filter:** off-manifold predictions with |E|>1e4 eV are excluded/counted.

## Verification checklist

- [ ] `out_fez/` contains the fez + energy-range CV CSVs, plots, and DISCUSSION.md
- [ ] `cv_fold_summary_50folds.csv` has 50 fold rows + mean/std
- [ ] Fe_z CSV shows MAE varying across island-height bins
- [ ] Run via the env python (or HPC job)
