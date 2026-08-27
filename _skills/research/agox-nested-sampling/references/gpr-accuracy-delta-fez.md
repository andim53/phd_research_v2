# GPR accuracy & uncertainty vs delta Fe_z (Fe island height) — `--fez`

Session-specific addition to `gpr_accuracy.py` (project
`/home/think/Desktop/research/_run/b_nestedsampling/`), v1.3.0, on top of the
in-sample / CV / uncertainty modes in `gpr-accuracy-analysis.md` and
`gpr-accuracy-cv-uncertainty.md`. Prompt origin: PROMPTS.md flag `20260827_0041`.

## What it answers

How the GPR's prediction accuracy (MAE/RMSE/R²) and self-estimated uncertainty
change as a function of the **Fe island height** — a geometric descriptor of the
deposition morphology, not an energy axis.

**delta Fe_z = max(Fe z) − min(Fe z)** (Å), i.e. the vertical spread of the Fe
atoms. Bin it in Å (~0.5 Å default; the full range is ~0.001–5.57 Å).

## Pattern

1. Compute per-structure island height with a helper that selects only the
   `Fe` atoms:
   ```python
   def fe_z_height(atoms, symbols=("Fe",)):
       import numpy as np
       sym = np.array(atoms.get_chemical_symbols())
       z = atoms.positions[np.isin(sym, symbols), 2]
       return float(z.max() - z.min()) if len(z) else float("nan")
   ```
2. **Align the binning axis with the SAME prediction errors used for the
   energy-range analysis.** In in-sample mode that is `err_per_atom`; in CV mode
   it is `pooled_err` — and the Fe_z values must be the held-out test structures'
   heights in the SAME order the pooled errors were collected (reconstruct the
   per-fold `test_idx` list, don't use the full-set order). This is the main
   footgun: an out-of-order binning axis silently mangles the per-bin metrics.
3. Bin on the Å axis with a generic per-bin MAE/RMSE/R² helper (reuse the same
   metric logic as `bin_metrics`, but parameterise the binning coordinate — do not
   hardcode the eV/atom energy axis).
4. With `--uncertainty`, add per-bin mean model std (via `bin_mean_std`) as 1σ
   error bars on the MAE curve.
5. Outputs: `gpr_accuracy_by_fe_z.csv` (+ `uncertainty_by_fe_z.csv`),
   `gpr_accuracy_by_fe_z.png`, and a `DISCUSSION.md` in the output dir.

## Verified result (Fe/MgO, 3-fold CV, `--cv 3 --fez --uncertainty`)

| delta Fe_z (Å) | n | MAE (eV/atom) | R² | model std (eV/atom) |
|---|---|---|---|---|
| 0.00–0.46 | 254 | 0.0036 | 0.998 | 0.0057 |
| 0.46–0.93 | 48 | 0.0065 | 0.995 | 0.0117 |
| 0.93–1.39 | 37 | 0.0083 | 0.986 | 0.0103 |
| 2.79–3.25 | 211 | 0.0030 | 0.999 | 0.0026 |
| 5.11–5.57 | 7 | 0.0059 | 0.996 | 0.0045 |

Interpretation: the GPR is **most accurate for mid island heights (~2.3–3.7 Å,
MAE ~0.003–0.004)** and **least accurate for very flat islands (~0.5–1.4 Å, MAE up
to 0.008, model std up to 0.012)**. The model's self-reported std tracks the actual
held-out error — well-calibrated.

## Key caveats

- **In-sample `--fez` errors are near-zero** (MAE ~0.0002–0.001 eV/atom, R²≈1.0,
  model std ~0.001) because the points are interpolation. Use `--cv` for the honest
  held-out picture, exactly like the energy-range analysis.
- Small bin counts at the extremes (n=7–37) make those per-bin R²/std noisy —
  state it in the DISCUSSION.md.
- The `--fez` analysis is orthogonal to `--cv`/`--uncertainty` — combine freely
  (e.g. `--cv --uncertainty --fez`).
