# TUTORIAL — Reproduce run c1_parallel_w500 (Mode A parallel walkers)

This reproduces the Wang–Landau run in
`1_runs/c1_parallel_w500/`: **plain Fe/MgO** (`dataset`, 13 seeds),
`--n-bins 100 --e-max 0.40`, `--relax-steps 100`, and **500 shared-histogram
walkers** (`--n-walkers 500`, Mode A).

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- **Ray** (>= 2.x) installed in that env — required for Mode A.
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local, fewer walkers to test)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/1_runs/c1_parallel_w500
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --dataset dataset --n-bins 100 --e-max 0.40 \
    --mc-steps 3000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe --relax-steps 100 \
    --temperatures 100,200,300,500,1000 \
    --n-walkers 8 --output ./wl_output_c1_parallel_w500 --rng 42
```

(`--mc-steps 3000 --n-walkers 8` for a quick smoke test; the HPC run below uses
`--mc-steps 30000 --n-walkers 500`.)

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/c_landausampling/1_runs/c1_parallel_w500
pjsub j_c1_parallel_w500.sh
```

## What each flag does

- `--dataset dataset` — plain Fe/MgO (13 seeds, 1297 structures).
- `--n-bins 100` — 100 energy bins for g(E) (fine resolution).
- `--e-max 0.40` — upper bin edge (eV/atom rel), spans island(0)→barrier/flat.
- `--relax-steps 100` — GPR BFGS relaxation per trial (c1's most converged).
- `--mc-steps 30000` — MC steps **per walker** (aggregated into the shared histogram).
- `--n-walkers 500` — **Mode A**: 500 Ray-actor walkers, each seeded `--rng + i`,
  sharing one `H`/`ln_g` via `WangLandauSharedState`; flatness + `ln_f` refinement
  act on the **aggregated** histogram.
- `--small-step 0.05` / `--large-step 0.20` — small/large Gaussian rattle scales.
- `--perturb-symbols Fe` — rattle the mobile Fe atoms only.
- `--temperatures 100,200,300,500,1000` — thermodynamics post-processing.

## Verification

- All `--n-walkers` actor processes start (live log shows per-walker seeds).
- Shared-histogram flatness drives `ln_f` halving on the **combined** H.
- `g_of_E.csv` + `g_of_E.png` + `thermodynamics.csv` + `heat_capacity.csv` produced
  (aggregate over all walkers).
- Memory: 500 walkers ≈ 68 GB ≈ 73% of the 92.7 GB genkai limit — watch `pjstat`
  / node RSS so it stays under the genkai cap.