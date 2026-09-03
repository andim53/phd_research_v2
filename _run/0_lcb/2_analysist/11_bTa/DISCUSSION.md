# DISCUSSION — family `11_bTa` (Ta–B interstitial alloy)

Analysis of the `fxg` leaves 7–10 under a 3×3×3 BCC Ta host with interstitial B.

## Running command (Stage-1 progression replot, used for all four leaves)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
for L in 7_fxg_0b 8_fxg_1b 9_fxg_3b 10_fxg_5b; do
  $PY run_analysis_indices.py --from-json 11_bTa/$L/analysis_indices \
      --outdir 11_bTa/$L/analysis_indices --seeds 0-4 \
      --xlabel "Sampled Structure" --x-max 140 --no-bullets
done
```

Runner: `run_analysis_indices.py` (v2.7.0). Flags: seeds 0–4, custom x-axis
label, x-axis capped at 140, Seed-0 window bullets suppressed (global GS star kept).

## Host supercell

- Lattice: **3×3×3 BCC Ta**, cubic, cell length ≈ 9.99 Å (implied primitive
  a₀ ≈ 3.33 Å, matching BCC Ta).
- Host atom count: **54 Ta** (3³ BCC conventional cells × 2 Ta per cell).
- Interstitials added as B.

## Leaf composition (grounded in the DB data)

| Leaf       | Total atoms | Ta | B  | B % (B/(Ta+B)) |
|------------|-------------|----|----|----------------|
| `7_fxg_0b` | 54          | 54 | 0  | 0.00 %         |
| `8_fxg_1b` | 55          | 54 | 1  | 1.82 %         |
| `9_fxg_3b` | 57          | 54 | 3  | 5.26 %         |
| `10_fxg_5b`| 59          | 54 | 5  | 8.47 %         |

B percentages are reported as B atoms over total atoms (Ta+B). The leaf suffix
(`0b`/`1b`/`3b`/`5b`) corresponds to the number of interstitial B atoms (0, 1, 3, 5).

## Notes

- All four leaves share the same 54-Ta host; only the interstitial B count differs,
  giving a clean concentration scan 0 % → 8.47 % B.
- Structure/atom counts are read from `seed_*/1_db/db_*.db` (identical across seeds
  for a given leaf; count taken from Seed 0).