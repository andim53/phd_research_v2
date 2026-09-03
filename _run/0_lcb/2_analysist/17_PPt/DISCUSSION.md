# DISCUSSION — family `17_PPt` (Pt–P interstitial alloy, XRD crystallinity)

XRD-crystallinity analysis of the Pt–P concentration leaves in supercell families
`0_plus5cell`, `1_plus0cell`, `2_plus3cell` (the `3_plus10cell` family was excluded
by scope). Produced by the two-stage XRD pipeline (`xrd_extract_structures.py` v1.0.0
in `agox_v2`; `xrd_simulate_crystallinity.py` v1.3.0 in `pymat_xrd`).

## Method (grounded in code + data)

- Reference relative energy per atom: `rel = (E - E_glob)/n_atoms`, `E_glob` = the
  leaf's global minimum (shown per leaf below). All DB structures (iteration ≥ 10)
  are binned into 0.1 eV/atom windows over [0, 0.5]; a deterministic sample of each
  window (cap 150) is written as CIF.
- Per window, powder XRD is simulated for every sampled structure (pymatgen
  `XRDCalculator`, Cu Kα, 2θ 10–90°, 0.02° grid, Gaussian broaden σ=0.15°), averaged
  → one pattern per window.
- Two crystallinity indices are evaluated on the window-averaged pattern:
  - **peak-fraction CI** = area in resolved-peak neighbourhoods (±0.6° 2θ, peaks via
    `find_peaks`, prominence >2% of max) / total area.
  - **integrated CI** = (total − amorphous background)/total, background = wide 5°
    running mean (amorphous halo).
- Plots (`crystallinity_vs_energy.png`) use the shared energy x-label
  `$E_{i}-E_{glob}$ (eV/atom)` and are drawn with only the windows ≤ 0.25 eV/atom,
  x-axis to 0.3, y-axis to 1.

## Cells & compositions

All 3×3×3 leaves = Pt₁₀₈ host + P interstitials. Exception: `0_PPt_4x4_20P` is a
4×4 cell = Pt₂₅₆ P₆₄ (n=320).

| Family | leaf | n_atoms | composition | E_glob (eV) |
|---|---|---|---|---|
| 0_plus5cell | 0_PPt_4x4_20P | 320 | Pt256 P64 | −1832.406 |
| 0_plus5cell | 1_3x3_20P | 135 | Pt108 P27 | −780.933 |
| 0_plus5cell | 2_3x3_30P | 154 | Pt108 P46 | −820.570 |
| 0_plus5cell | 3_3x3_0P | 108 | Pt108 | −628.218 |
| 0_plus5cell | 4_3x3_10p | 120 | Pt108 P12 | −704.212 |
| 1_plus0cell | 0_0P | 108 | Pt108 | −653.806 |
| 1_plus0cell | 1_10P | 120 | Pt108 P12 | −687.708 |
| 1_plus0cell | 2_20P | 135 | Pt108 P27 | −704.237 |
| 1_plus0cell | 3_30P | 154 | Pt108 P46 | −644.285 |
| 2_plus3cell | 0_0P | 108 | Pt108 | −642.900 |
| 2_plus3cell | 1_10P | 120 | Pt108 P12 | −703.658 |
| 2_plus3cell | 2_20P | 135 | Pt108 P27 | −762.430 |
| 2_plus3cell | 3_30P | 154 | Pt108 P46 | −766.247 |

## CI results (per window centre; peak-fraction / integrated)

| Leaf | 0.05 | 0.15 | 0.25 |
|---|---|---|---|
| 0_plus5cell/0_PPt_4x4_20P | 0.953 / 0.229 | 0.968 / 0.223 | 0.955 / 0.220 |
| 0_plus5cell/1_3x3_20P | 0.976 / 0.354 | 0.981 / 0.350 | 0.988 / 0.348 |
| 0_plus5cell/2_3x3_30P | 0.980 / 0.349 | 0.981 / 0.350 | 0.991 / 0.350 |
| 0_plus5cell/3_3x3_0P | 0.956 / 0.807 | 0.864 / 0.464 | 0.972 / 0.359 |
| 0_plus5cell/4_3x3_10p | 0.867 / 0.466 | 0.915 / 0.390 | 0.980 / 0.354 |
| 1_plus0cell/0_0P | 0.980 / 0.825 | 0.834 / 0.664 | 0.834 / 0.545 |
| 1_plus0cell/1_10P | 0.865 / 0.528 | 0.861 / 0.496 | 0.917 / 0.425 |
| 1_plus0cell/2_20P | 0.973 / 0.378 | 0.972 / 0.376 | 0.988 / 0.376 |
| 1_plus0cell/3_30P | 0.980 / 0.378 | 0.982 / 0.375 | 0.990 / 0.374 |
| 2_plus3cell/0_0P | 0.983 / 0.828 | 0.832 / 0.593 | 0.876 / 0.416 |
| 2_plus3cell/1_10P | 0.859 / 0.522 | 0.908 / 0.405 | 0.909 / 0.401 |
| 2_plus3cell/2_20P | 0.969 / 0.352 | 0.975 / 0.353 | 0.979 / 0.356 |
| 2_plus3cell/3_30P | 0.977 / 0.357 | 0.978 / 0.359 | 0.986 / 0.360 |

## Observations (grounded in the numbers)

- **Pt-only hosts (0P leaves)** have the highest integrated CI at 0.05 eV/atom
  (0.81–0.83 across families) — the most crystalline/least amorphous patterns.
  Their integrated CI falls steeply with energy (e.g. 1_plus0cell/0_0P 0.825 → 0.427
  by 0.45), i.e. higher-energy Pt-only structures become progressively more
  disordered/amorphous.
- **P-doped leaves** (10P/20P/30P) show high peak-fraction CI (~0.86–0.99) but low
  and nearly energy-flat integrated CI (~0.35–0.53). The P interstitials suppress
  the sharp Pt-only crystallinity, and the integrated CI stays roughly constant
  across energy (weak energy dependence).
- **20P & 30P leaves** are internally consistent across all three supercell families:
  peak-fraction CI ~0.97–0.99, integrated CI flat ~0.35–0.38. Concentration (20P vs
  30P) has little effect.
- **0_plus5cell/0_PPt_4x4_20P (the 4×4 cell)** is an outlier: integrated CI is low
  and flat (~0.22) despite peak-fraction CI ~0.95–0.98 — the larger cell's averaged
  pattern has a large diffuse component not captured by resolved peaks.
- **Caveat on statistics:** high-energy windows often have few structures (e.g.
  0_plus5cell/4_3x3_10p 0.45 n=2; 0_plus5cell/3_3x3_0P 0.45 n=3). Their CI values
  are the least reliable. The `--ci-x-data-max 0.25` plots exclude these.

## Rebplot / reproduce

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
PY_X scripts/xrd_simulate_crystallinity.py --from-json <leaf>/xrd_out \
    --outdir <leaf>/xrd_out --ci-x-data-max 0.25 --ci-x-max 0.3 --ci-y-max 1.0
```