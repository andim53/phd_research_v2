# TUTORIAL — Reproduce run c2_boron3_N40_Emax04

This reproduces the Wang–Landau run in
`1_runs/c2_boron3_N40_Emax04/`: **B3-doped** (`dataset_boron3`, 7 seeds),
`--n-bins 100 --e-max 0.40`, `--mc-steps 20000000`, mobile Fe+B with the
**swap (permutation) move enabled** (`--swap-prob 0.2 --max-swaps 2`).

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/1_runs/c2_boron3_N40_Emax04
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --dataset dataset_boron3 --n-bins 100 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe,B \
    --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 \
    --temperatures 100,200,300,500,1000 \
    --output ./wl_output_c2 --rng 42
```

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/1_runs/c2_boron3_N40_Emax04
pjsub j_c2_boron3_N40_Emax04.sh
```

## What each flag does

- `--dataset dataset_boron3` — B3-doped (7 seeds, B3Fe25Mg25O25, 78 atoms).
- `--n-bins 100` / `--e-max 0.40` — 100 bins over `[0, 0.40]` eV/atom rel (fine).
- `--mc-steps 20000000` — WL MC steps.
- `--small-step 0.05` / `--large-step 0.20` — small/large Gaussian rattle scales.
- `--perturb-symbols Fe,B` — rattle both mobile species.
- `--swap-prob 0.2` — 20% of MC steps use a swap move instead of a rattle.
- `--max-swaps 2` — each swap move performs a random `1..2` position exchanges
  between a B and an Fe atom.
- `--swap-rattle 0.05` — Gaussian displacement applied to the two swapped atoms.
- `--temperatures 100,200,300,500,1000` — thermodynamics post-processing.

## Verification

- Live log shows `[WangLandau] Swap move ENABLED: prob=0.200 ... swapping among ['B','Fe']`.
- Move line at the end prints a non-zero swap count (~20% of `--mc-steps`).
- `g_of_E.csv` + `g_of_E.png` + `thermodynamics.csv` + `heat_capacity.csv` produced.
- Live log reaches the 1/t switch (or consciously accept the standard scheme).
