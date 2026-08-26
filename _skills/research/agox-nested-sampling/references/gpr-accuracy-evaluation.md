# GPR surrogate accuracy & uncertainty evaluation (AGOX)

How to measure how well the AGOX GPR predicts energies, as a function of a
structural descriptor (energy range, delta Fe_z / Fe island height, rattling
distance). Used in project `_run/b_nestedsampling/gpr_accuracy.py` (gpr_accuracy.py).

## The AGOX GPR exposes predictive uncertainty

Do NOT assume the GPR only has `predict_energy`. It also has:
- `predict_energy_and_uncertainty(atoms)` -> `(energy, uncertainty)`
- `predict_uncertainty(atoms)`

`uncertainty` is the posterior predictive std (the model's self-estimated
uncertainty). Confirm via `gpr.predict_energy_and_uncertainty(structures[i])`.
`np.asarray(unc).ravel()[0]` gives the scalar.

## Metrics — use eV/atom to match the energy-range axis

Report MAE, RMSE, R² in **eV/atom** (per-atom: `(E_pred - E_DFT) / n_atoms`), so
they are comparable to the per-atom energy-range axis. R² is per-bin
(within-bin variance) — low per-bin R² reflects low within-bin variance as much as
error; do not over-read it.

## Two evaluation modes — this is the key distinction

1. **In-sample** (train one GPR on all N, predict the same N): gives near-zero
   errors (MAE ~0.001 eV/atom, R² ≈ 1.0) because these are interpolation points.
   It measures **training-set fit**, NOT generalization. A flat near-zero curve
   here is expected, not a finding.
2. **K-fold CV** (opt-in `--cv`, default 5 folds): train on K-1/K, predict held-out
   1/K, pool held-out errors across folds. Gives the honest out-of-sample picture.
   Stratify by the descriptor bin so every fold sees a spread of the axis.
   Observed: 5-fold CV overall MAE ~0.004 eV/atom vs in-sample 0.0007 (~5-6x).

## Uncertainty tracks error only in CV mode

- In-sample: model std is small and flat (~0.001 eV/atom) — it is interpolation
  confidence and **understates** true error.
- CV: the pooled held-out model std (~0.0046) matches the held-out MAE (~0.0044)
  and rises at the same bins where R² drops — well-calibrated. Use `--cv
  --uncertainty` together for a meaningful error bar.

## Pitfalls

- **Bin width must match the actual energy scale.** The Fe/MgO 1297-structure set
  spans only ~0–0.675 eV/atom (E/atom -5.83 to -5.15). A "1 eV/atom" bin width
  collapses everything into one bin. Default ~0.1 eV/atom (≈7 bins). Always
  check the range first:
  `dE_above_min = (E_DFT - E_DFT.min()) / n_atoms; dE_above_min.max()`.
- **Small top bins (n=20-32) give noisy metrics.** Call that out; don't over-read
  their R².
- **Error grows toward high energy / sparse regions** — the GPR both generalizes
  worse AND is more uncertain at the energy extremes (fewer training points, more
  extrapolation). This is a real, physically meaningful trend to report.

## Cross-validation fold stratification

Assign structures to folds round-robin within each descriptor bin (shuffled), so
each fold sees all energy ranges. Simple and effective for the descriptor-binned
accuracy question.
