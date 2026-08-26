# GPR accuracy: K-fold CV + uncertainty (additions to `gpr_accuracy.py`)

Session-specific additions to `gpr_accuracy.py` (project
`/home/think/Desktop/research/_run/b_nestedsampling/`), on top of the in-sample
accuracy-vs-energy-range described in `references/gpr-accuracy-analysis.md`.
Version history: v1.0.0 in-sample → v1.1.0 CV → v1.2.0 uncertainty.

## Cross-validation (`--cv`, v1.1.0) — the truthful generalization estimate

In-sample residuals are tiny (MAE ~0.0007 eV/atom) because test == training points.
To report a real out-of-sample accuracy, use K-fold CV:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 5 --bin-width 0.1 --output ./gpr_accuracy_cv_out
```

- `--cv` opt-in (in-sample stays default), `--cv-folds N` (default 5).
- **Stratified by energy bin** (`stratify_folds()`): each dE bin's indices are
  round-robin'd onto folds (after a shuffle), so every fold trains on a spread of
  energy ranges — fairer per-range accuracy than a random split.
- Each fold trains on K-1/K, predicts the held-out 1/K; held-out `(dE, err)` are
  **pooled across folds** and binned via the same `bin_metrics()`. A per-fold
  overall MAE is also recorded.
- Outputs: `gpr_accuracy_by_energy_range_cv{K}folds.csv` (pooled per-bin),
  `cv_fold_summary_{K}folds.csv` (fold MAE + mean/std), `..._cv{K}folds.png`.
- Note: CV trains K GPRs (~K × train time); use `--use-ray` on HPC for speed.
- Verified 5-fold: overall MAE=0.0040 RMSE=0.0067 R²=0.998 eV/atom; per-fold
  MAE 0.0039/0.0043/0.0038/0.0040/0.0040, mean 0.0040±0.0002. Error grows toward
  higher-energy bins (MAE~0.010, R²~0.58 at 0.39–0.48 eV/atom).

## Uncertainty (`--uncertainty`, v1.2.0)

Uses the AGOX GPR's OWN predictive uncertainty (posterior std), NOT residual
spread — the model's self-estimated error as a function of energy range:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --uncertainty --bin-width 0.1 --output ./gpr_accuracy_uncert_out
```

- API: `gpr.predict_energy_and_uncertainty(atoms)` returns `(energy, uncertainty)`.
  Take the first element of `np.asarray(unc).ravel()` and divide by n_atoms for
  eV/atom. (Also `predict_uncertainty`, `predict_forces_and_uncertainty` exist.)
- In-sample: per-structure std of the single trained model on the training set.
- CV: collect the std of each held-out prediction alongside its error, pool across
  folds (avg per bin).
- `bin_mean_std(dE, std, edges, n_bins)` — per-bin mean std aligned with
  `bin_metrics()` rows.
- Outputs: `uncertainty_by_energy_range.csv` (per-bin mean model std), plus a
  `mean_model_std_eV_per_atom` column rewritten into the main accuracy CSV, and
  per-bin 1σ model-std error bars on the plot (`ax1.errorbar(centers, mae,
  yerr=std_per_bin, ...)`).
- Verified: in-sample overall mean model std ~0.0011 eV/atom; 3-fold CV ~0.0046
  eV/atom. In CV the model's self-reported std tracks the actual error and rises at
  the energy extremes (std ~0.016–0.019 eV/atom where R² drops to ~0.5–0.2) — the
  GPR is both less accurate AND more uncertain at the energy extremes.

## Pitfalls / notes

- Both additions share one code path: after loading, `main()` branches on
  `--cv`; uncertainty data is collected during whichever branch, then unified
  (`pooled_dE, pooled_std` for CV vs `dE_per_atom, std_per_atom` for in-sample)
  before reporting. Guard `std_per_bin`/`overall_std` init to None so the plot and
  summary only add uncertainty artifacts when `--uncertainty` was passed.
- Pyright-under-base-python3 flags AGOX imports as unresolved — false positives;
  judge by `py_compile` under `agox_v2`.
- Energy axis is always eV/atom (the full dE range is only ~0.675 eV/atom, so keep
  `--bin-width` ~0.1, not the prompt's literal "1 eV/atom").
