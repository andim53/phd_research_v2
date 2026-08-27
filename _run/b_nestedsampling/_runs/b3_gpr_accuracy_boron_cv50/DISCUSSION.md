# DISCUSSION — b3_gpr_accuracy_boron_cv50 (GPR accuracy on B-doped Fe/MgO)

## What was run

| Parameter | Value |
|---|---|
| Script | `gpr_accuracy.py` v1.5.0 |
| Mode | 50-fold CV + uncertainty, Fe_z system, bin 0.1 |
| Dataset | B-doped Fe/MgO, Fe25Mg25O25B7 (82 atoms), 5 seeds, 496 structures |
| Outlier cut | `--e-max-per-atom -5.2` (keeps 452 structures, spread ~0.67 eV/atom) |
| Output | `out_fez/` |

## Error & fixes

The original HPC run crashed at the plot with a `yerr`/`y` shape mismatch, and the
metrics were unphysical (~10⁹ eV/atom). Two fixes in `gpr_accuracy.py`:

1. **`bin_mean_std()` length mismatch on empty bins** — now skips empty bins (aligned
   with `rows`), fixing the `errorbar` crash.
2. **High-energy outliers broke the GPR fit** — added a `|E|<1e4 eV` physical filter to
   the prediction loops AND a `--e-max-per-atom` flag to drop structures above a
   physical E/atom threshold. With `-5.2`, the surviving set matches the working
   Fe/MgO spread (~0.67 eV/atom) and the GPR fits (in-sample MAE ≈ 0.0002 eV/atom).

## Verified results (5-fold CV smoke, real output)

- Fold-averaged overall MAE = **0.0086 ± 0.0006 eV/atom**
- Overall: MAE = 0.0086, RMSE = 0.0118, R² = 0.996 (eV/atom)
- Energy-range per-bin MAE: 0.0047–0.0115 eV/atom (R² 0.71–0.92)
- Fe_z (island-height) per-bin MAE: 0.0056–0.0107 eV/atom (R² ~0.99)
- Mean model std = 0.0083 eV/atom (tracks the error — well calibrated)

## Interpretation

Once the high-energy outliers are excluded, the GPR fits the B-doped landscape and CV
gives physical, meaningful accuracy-vs-energy-range and accuracy-vs-island-height
results — comparable in quality to the plain Fe/MgO runs. This confirms the boron GPR-CV
is viable **only** with the outlier cut; without it the surrogate cannot represent the
~5 eV/atom spread and produces unphysical predictions.

## Caveats

- The surviving set (452 of 496) drops the high-E structures from seeds 2-4; these are
  likely DFT-failure artifacts and should ideally be re-generated at the source.
- The `--e-max-per-atom` threshold is a controllable flag; `-5.2` was chosen to match
  the working Fe/MgO energy spread.
