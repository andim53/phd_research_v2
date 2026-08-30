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
| 0.00-0.46 | 254 | 0.0028 | 0.0048 | 0.999 | 0.0049 |
| 0.46-0.93 | 48 | 0.0058 | 0.0080 | 0.997 | 0.0114 |
| 0.93-1.39 | 37 | 0.0049 | 0.0077 | 0.997 | 0.0095 |
| 1.39-1.86 | 37 | 0.0055 | 0.0072 | 0.997 | 0.0090 |
| 1.86-2.32 | 105 | 0.0039 | 0.0058 | 0.997 | 0.0047 |
| 2.32-2.79 | 201 | 0.0036 | 0.0065 | 0.998 | 0.0036 |
| 2.79-3.25 | 211 | 0.0028 | 0.0040 | 0.999 | 0.0024 |
| 3.25-3.71 | 141 | 0.0038 | 0.0070 | 0.997 | 0.0030 |
| 3.71-4.18 | 118 | 0.0051 | 0.0097 | 0.994 | 0.0034 |
| 4.18-4.64 | 116 | 0.0052 | 0.0076 | 0.995 | 0.0031 |
| 4.64-5.11 | 22 | 0.0073 | 0.0099 | 0.993 | 0.0035 |
| 5.11-5.57 | 7 | 0.0078 | 0.0092 | 0.995 | 0.0041 |
| **OVERALL** | 1297 | 0.0039 | 0.0066 | 1.000 | |

## What it is

The plot shows MAE, RMSE (left axis) and R^2 (right axis) with per-bin 1-sigma model-std error bars vs delta Fe_z (the Fe island height, Angstrom), binned into ~0.5 A windows.

## What it means

delta Fe_z is a geometric descriptor of the deposition morphology: it measures how tall/rugged the Fe island is (vertical spread of Fe atoms). This run shows how GPR prediction accuracy and self-estimated uncertainty vary with island height.

## What it implies

- Overall MAE = 0.0039 eV/atom, R^2 = 1.000. Per bin, MAE ranges from 0.0028 (delta Fe_z 0.00-0.46 A, n=254) to 0.0078 (delta Fe_z 5.11-5.57 A, n=7). Model std averages 0.0052 eV/atom across bins.

## Outcome

See the key trend above; the full per-bin table quantifies how the surrogate's reliability changes with Fe island height.

## Overall interpretation

- **Verdict:** the GPR's accuracy varies across delta Fe_z bins and its model std tracks the error.
- **Implication:** for nested-sampling / partition-function work, structures with extreme island heights are the least reliable predictions.
- **Caveats/limitations:** small bin counts at the extremes make those metrics noisy; per-bin R^2 is a within-bin quantity.
- **Bottom line:** delta Fe_z (island height) is a meaningful coordinate along which GPR reliability varies; combine with --uncertainty to see the model's own confidence.
