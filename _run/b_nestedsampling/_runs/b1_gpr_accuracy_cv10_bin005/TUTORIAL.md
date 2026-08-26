# TUTORIAL — Reproduce run b1_gpr_accuracy_cv10_bin005

Step-by-step guide to reproduce this run (GPR accuracy, 10-fold CV, uncertainty,
bin 0.05) in isolation. Level: intermediate.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0) for local runs:
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- HPC pjsub (PJM) for the batch run (`gpaw_env`, set in `j_*.sh`).
- Dataset present in this dir: `dataset/seed_*/1_db/db_*.db` (13 DBs).

## Step 0 — What this run does

Two invocations of `gpr_accuracy.py` in **10-fold CV + uncertainty** mode with a
**0.05 eV/atom** bin (scaling up the reference `--cv-folds 3 --bin-width 0.1` runs):
1. Energy-range system → `out_energy_range/`
2. Fe_z (island-height) system → `out_fez/`

Higher CV (10 folds) → lower per-fold training-set size but more robust held-out
pooling; finer bin (0.05) → finer energy resolution per bin.

## Step 1 — Local run (validate on a small scale first if desired)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b1_gpr_accuracy_cv10_bin005
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 10 --uncertainty --bin-width 0.05 --output ./out_energy_range
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 10 --fez --uncertainty --bin-width 0.05 --output ./out_fez
```

Note: 10-fold CV trains 10 GPRs (one per fold) — this is slower than the 3-fold
reference (~10× the GPR trainings). Expect several minutes to tens of minutes.

## Step 2 — HPC launch

```bash
pjsub j_gpr_accuracy_cv10_bin005.sh
```

- Header: 24 cores, `gpaw_env`, 120 h.
- The job runs both invocations (energy-range then fez) sequentially, each with
  `OMP_NUM_THREADS=1` (the script is single-process via `use_ray=False`).

## Step 3 — Outputs & verification

Per output dir:
- `gpr_accuracy_by_energy_range_cv10folds.csv` — per-bin MAE/RMSE/R² (+ mean model
  std). More bins than the reference (0.05 eV/atom over ~0.675 range → ~14 bins).
- `uncertainty_by_energy_range.csv` — per-bin mean model std.
- `cv_fold_summary_10folds.csv` — per-fold MAE + mean/std.
- `*.png` plots; `DISCUSSION.md` in each dir.

Sanity checks:
- `cv_fold_summary_10folds.csv` fold-averaged MAE should be comparable to the
  reference 3-fold runs (~0.004 eV/atom overall); more folds → less variance across
  folds.
- Fe_z dir should show MAE varying with island height (least reliable at extremes).

## Pitfalls

- **Env:** job uses `gpaw_env`; if AGOX imports fail, edit the `.sh` to
  `conda activate agox_v2`.
- **Runtime:** 10-fold CV is ~10 GPR trainings — do not expect it to be as quick as
  the 3-fold reference.
- **Physical filter:** rattled/off-manifold predictions with |E|>1e4 eV are excluded
  and counted (`n_unphysical`).

## Verification checklist

- [ ] Both output dirs contain the CV CSVs + plots + DISCUSSION.md
- [ ] `cv_fold_summary_10folds.csv` has 10 fold rows + mean/std
- [ ] Fe_z CSV shows MAE varying across island-height bins
- [ ] Run via the env python (or HPC job)
