# DISCUSSION — b13_gpr_accuracy_boron3_cv50 (GPR accuracy on B3-doped Fe/MgO)

## What was run

| Parameter | Value |
|---|---|
| Script | `gpr_accuracy.py` v1.5.1 |
| Mode | 50-fold CV + uncertainty, Fe_z system, bin 0.1 |
| Dataset | B3-doped Fe/MgO, B3Fe25Mg25O25 (78 atoms), 6 non-empty seeds, 597 structures |
| Outlier cut | `--e-max-per-atom 0.67` (keeps 568 structures) |
| Output | `out_fez/` |

## Status

This run dir was created to reproduce the b3 GPR-accuracy analysis on the **boron3** dataset
(B3Fe25Mg25O25, 78 atoms, 6 seeds) with exactly b3's parameters. The actual 50-fold-CV results
are produced by the HPC job (`j_b13_gpr_accuracy_boron3_cv50.sh`) or a local run of
`gpr_accuracy.py` — this DISCUSSION will be filled in from the real output once the run
completes.

For reference, b3's (B7, 82-atom) verified results were: overall MAE 0.0086 / RMSE 0.0118 /
R² 0.996 eV/atom (5-fold CV smoke), with physical per-bin errors once the outlier cut was applied.
b13's numbers will differ because the boron3 composition (3 B, 78 atoms) and energy spread differ.

## Caveats

- The `--e-max-per-atom 0.67` threshold is a controllable flag; it keeps 568 of 597 boron3
  structures.
- High-energy outlier structures (likely DFT-failure artifacts) are excluded; the surviving set
  should ideally be re-generated at the source if those matter.
