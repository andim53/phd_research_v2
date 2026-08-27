# GPR robustness to positional rattling (kernel tolerance)

How to measure how much positional displacement a trained GPR surrogate can
tolerate before its energy predictions degrade — "how much rattling the kernel
can handle". Implemented as `--rattle` in `_run/b_nestedsampling/gpr_accuracy.py`.

## What it answers

Given DB structures, rattle (Gaussian-displace) selected atoms by increasing
amplitudes, predict with the trained GPR, and report accuracy (MAE/RMSE/R²) and
uncertainty vs rattling distance. This bounds the safe perturbation scale — e.g.
for the nested-sampling prior `--perturb` amplitude.

## Pattern

1. Sample N DB structures (default 200; keep bounded — runtime scales as
   N × copies × n_amplitudes × predict-cost).
2. Choose which atoms to rattle via a configurable symbol flag (e.g.
   `--rattle-symbols Fe`), mirroring the `--perturb-symbols` convention in the
   nested sampler. Do NOT hardcode the species.
3. Amplitudes as a comma list (e.g. `0.05,0.1,0.2,0.5,1.0` Å).
4. For each amplitude, rattle each sample `copies` times, predict, pool the
   per-atom errors `(E_pred - E_base)/n_atoms`.
5. Report per-amplitude MAE/RMSE/R² (+ mean model std with `--uncertainty`),
   CSV + plot + DISCUSSION.md.

## CRITICAL pitfall — the |E|>1e4 physical filter

Rattled structures leave the training manifold. The AGOX GPR (Fingerprint
descriptor + RBF kernel) then extrapolates catastrophically: at amplitudes of
~0.5–1.0 Å it returns absurd energies (MAE ~10³⁰–10³⁹ eV/atom, i.e. total garbage).
This is the SAME failure the nested sampler guards against with `|E| < 1e4`.

**You MUST filter rattled predictions with `abs(E_pred) > 1e4` → exclude and
count them** (an `n_unphysical` column), otherwise the MAE/RMSE columns are
meaningless and the plot axis explodes. Without the filter the "results" look like
a numeric overflow bug.

Verified Fe/MgO (100 structs × 3 copies, Fe rattled):
| amplitude | MAE (eV/atom) | n_unphysical |
|---|---|---|
| 0.05 Å | 0.008 | 0/300 |
| 0.10 Å | 0.034 | 0/300 |
| 0.20 Å | 0.30 | 1/300 |
| 0.50 Å | 20.2 | 214/300 |
| 1.00 Å | 94.0 | 296/300 |

Model std grows in step: 0.002 → 0.005 → 0.016 → 0.077 → 0.125 eV/atom.

## Interpretable finding

- The kernel tolerates small rattling (~0.05–0.1 Å) with mild degradation.
- It degrades **catastrophically beyond ~0.2 Å** as structures leave the training
  manifold (large MAE AND a large fraction of unphysical predictions).
- This directly bounds the safe `--perturb`/rattling scale for the surrogate —
  report it as such, not just as a curve.

## Worth noting

- The `predict_energy_and_uncertainty` return must be flattened:
  `float(np.asarray(e_pred).ravel()[0])` — the AGOX API sometimes wraps scalars in
  arrays, and comparing an unflattened array to `1e4` or subtracting can silently
  broadcast or error.
- In-sample mode only is a reasonable default for a perturbation-robustness test
  (you are probing the trained kernel's extrapolation, not re-estimating
  generalization); combining with `--cv` changes the question.
