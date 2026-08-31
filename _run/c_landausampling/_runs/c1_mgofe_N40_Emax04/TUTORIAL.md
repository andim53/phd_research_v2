# TUTORIAL — Reproduce run c1_mgofe_N40_Emax04

This reproduces the Wang–Landau run in
`_runs/c1_mgofe_N40_Emax04/`: **plain Fe/MgO** (`dataset`, 13 seeds),
`--n-bins 40 --e-max 0.40`, `--mc-steps 20000000`, rattle-only on Fe (no swap).

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/_runs/c1_mgofe_N40_Emax04
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe \
    --temperatures 100,200,300,500,1000 \
    --output ./wl_output_c1 --rng 42
```

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/_runs/c1_mgofe_N40_Emax04
pjsub j_c1_mgofe_N40_Emax04.sh
```

## MC-steps sweep (HPC, PJM)

```bash
pjsub j_c1_mgofe_N40_Emax04_sweep.sh
```

Runs the SAME parameters at `--mc-steps 10000 / 30000 / 50000` sequentially in one
job, each to its own output dir: `./wl_output_c1_sweep_10000`,
`./wl_output_c1_sweep_30000`, `./wl_output_c1_sweep_50000`. For a
convergence-over-mc-steps comparison of g(E) and thermodynamics.

## What each flag does

- `--dataset dataset` — plain Fe/MgO (13 seeds, 1297 structures).
- `--n-bins 40` — 40 energy bins for g(E).
- `--e-max 0.40` — upper bin edge (eV/atom rel), spans island(0)→barrier/flat.
- `--mc-steps 20000000` — WL MC steps.
- `--small-step 0.05` / `--large-step 0.40` — small/large Gaussian rattle scales.
- `--perturb-symbols Fe` — rattle the mobile Fe atoms only (single species, so
  no swap move is possible/needed).
- `--temperatures 100,200,300,500,1000` — thermodynamics post-processing.

## Verification

- Live log reaches the 1/t switch (or consciously accept the standard scheme).
- `g_of_E.csv` + `g_of_E.png` + `thermodynamics.csv` + `heat_capacity.csv` produced.
- Move line prints `0 swap` (single-species).
