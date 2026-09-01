# TUTORIAL — Reproduce run b6_tfree_walk_emax04

This reproduces the nested-sampling run in `_runs/b6_tfree_walk_emax04/`: plain
Fe/MgO (no B), temperature-free, `--e-max-per-atom 0.4`, windowed initial-live
seeding `[0.3, 0.35]`, and the dual-scale MC walk enabled.

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b6_tfree_walk_emax04
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
    --e-max-per-atom 0.4 \
    --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
    --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
    --output ./ns_output_tfree_walk_emax04 --rng 42
```

## Reproduce (HPC, PJM)

Submit the self-contained job script:

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b6_tfree_walk_emax04
pjsub j_b6_tfree_walk_emax04.sh
```

The job script runs `main.py` with the same command line and `OMP_NUM_THREADS=1`.

## What each flag does

- `--temperature-free` — beta kept out of the likelihood; post-processes Z/F/posterior
  at `--temperatures`.
- `--e-max-per-atom 0.4` — drop DB structures above 0.4 eV/atom relative to the min
  (before GPR training + sampling).
- `--e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000` — windowed
  initial-live seeding: one anchor live point found by bounded-attempt search in
  [0.30, 0.35] eV/atom; remaining live points capped at 0.35; RuntimeError if the
  band is empty after 1000 draws.
- `--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both` —
  dual-scale constrained MC walk in `sample_constrained` (clone a random live point,
  50 Gaussian trials, small 0.05 / large 0.40, 50/50 both; accept steps below the
  energy boundary; fall back to rejection draws).

## Verification

- Live log shows the windowed-start anchor rel energy in `[0.30, 0.35]` and all
  initial live points ≤ 0.35.
- `unphys: 0`; live-energy range converges toward `E_ref` over iterations.
- `samples.csv`, `final_live_energies.csv`, `thermodynamics.csv`, `posterior_T*/` and
  `analysis/` PNGs are produced.
- The final state-density/landscape analysis runs without the `plot_structure_landscape
  's'` TypeError (the correct `plot_structure_landscape.py` is bundled).

## Note on dataset

The `dataset/` copy holds the plain Fe/MgO seed DBs (seed_3..15, no Boron). The
`--e-max-per-atom 0.4` filter keeps the low-energy band (Fe/MgO spans ~0.67 eV/atom).
