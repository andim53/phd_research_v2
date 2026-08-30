# DISCUSSION — GPR accuracy & uncertainty vs delta Fe_z (Fe island height)

Run directory: `out_fez`
Evaluation mode: 50-fold CV

## What was run

| Parameter | Value |
|---|---|
| Dataset | combined multi-seed Fe/MgO, 1297 structures (75 atoms each) |
| delta Fe_z | Fe island height = max(Fe z) - min(Fe z) (Angstrom), binned 0.5 A |
| Metrics | MAE, RMSE, R^2 (eV/atom) per delta Fe_z bin + mean model std (eV/atom) |

## Per-bin results (from the CSV)

| delta Fe_z (A) | n | MAE (eV/atom) | RMSE (eV/atom) | R^2 | mean model std (eV/atom) |
|---|---|---|---|---|---|
| 0.00-0.48 | 73 | 0.0048 | 0.0069 | 0.997 | 0.0059 |
| 0.48-0.96 | 33 | 0.0054 | 0.0069 | 0.997 | 0.0058 |
| 0.96-1.44 | 47 | 0.0064 | 0.0101 | 0.995 | 0.0067 |
| 1.44-1.92 | 56 | 0.0079 | 0.0098 | 0.994 | 0.0086 |
| 1.92-2.39 | 78 | 0.0080 | 0.0110 | 0.994 | 0.0087 |
| 2.39-2.87 | 70 | 0.0087 | 0.0119 | 0.993 | 0.0091 |
| 2.87-3.35 | 38 | 0.0071 | 0.0092 | 0.994 | 0.0089 |
| 3.35-3.83 | 35 | 0.0081 | 0.0108 | 0.994 | 0.0088 |
| 3.83-4.31 | 15 | 0.0072 | 0.0094 | 0.992 | 0.0069 |
| 4.31-4.79 | 7 | 0.0111 | 0.0137 | 0.994 | 0.0070 |
| **OVERALL** | 452 | 0.0072 | 0.0099 | 1.000 | |

## What it is

The plot shows MAE, RMSE (left axis) and R^2 (right axis) with per-bin 1-sigma model-std error bars vs delta Fe_z (the Fe island height, Angstrom), binned into ~0.5 A windows.

## What it means

delta Fe_z is a geometric descriptor of the deposition morphology: it measures how tall/rugged the Fe island is (vertical spread of Fe atoms). This run shows how GPR prediction accuracy and self-estimated uncertainty vary with island height.

## What it implies

- Overall MAE = 0.0072 eV/atom, R^2 = 1.000. Per bin, MAE ranges from 0.0048 (delta Fe_z 0.00-0.48 A, n=73) to 0.0111 (delta Fe_z 4.31-4.79 A, n=7). Model std averages 0.0076 eV/atom across bins.

## Outcome

See the key trend above; the full per-bin table quantifies how the surrogate's reliability changes with Fe island height.

## Overall interpretation

- **Verdict:** the GPR's accuracy varies across delta Fe_z bins and its model std tracks the error.
- **Implication:** for nested-sampling / partition-function work, structures with extreme island heights are the least reliable predictions.
- **Caveats/limitations:** small bin counts at the extremes make those metrics noisy; per-bin R^2 is a within-bin quantity.
- **Bottom line:** delta Fe_z (island height) is a meaningful coordinate along which GPR reliability varies; combine with --uncertainty to see the model's own confidence.
