# Run c1_parallel_w500 — Wang–Landau on plain Fe/MgO (dataset), Mode A parallel walkers

Run directory: `1_runs/c1_parallel_w500/` (self-contained, launchable on HPC).
Copied from the latest project-root code (**main.py v1.5.0** with `--n-walkers` +
`wang_landau/` including `parallel_wl.py`) + the **plain Fe/MgO** dataset
(`dataset/`, 13 seeds, 1297 structures, Fe25Mg25O25 / 75 atoms).

This is the **baseline Wang–Landau run driven by ~500 shared-histogram walkers**
(Mode A): all walkers feed one `H`/`ln_g` Ray actor so the combined walk reaches
flatness faster, instead of the serial single-walker budget in `c1`.

## What this run does

```bash
main.py --dataset dataset --n-bins 100 --e-max 0.40 \
    --mc-steps 30000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe --relax-steps 100 \
    --temperatures 100,200,300,500,1000 \
    --n-walkers 500 --output ./wl_output_c1_parallel_w500 --rng 42
```

Treatment (same physics as `c1_mgofe_N40_Emax04`):
- **`--dataset dataset`** — plain Fe/MgO (13 seeds, 1297 structures).
- **`--n-bins 100` / `--e-max 0.40`** — g(E) over `[0, 0.40]` eV/atom relative.
- **`--relax-steps 100`** — GPR BFGS relaxation per trial (matches c1's most
  converged relax setting); single setting, not the 10/30/50/100 sweep.
- **`--n-walkers 500`** — **Mode A**: 500 Ray-actor walkers, each seeded
  `--rng + i` (42..541), sharing one `H`/`ln_g` with periodic sync; flatness and
  `ln_f` refinement act on the **aggregated** histogram. Total visits ≈
  500 × 30000 = 15M.
- **`--small-step 0.05` / `--large-step 0.20`** — dual-scale rattle; **Fe only**,
  no swap.

## Memory note

Each walker costs ≈ 135 MB (GPR copy + Ray process). 500 walkers ≈ 68 GB ≈
**73% of the 92.7 GB (92760 MB) genkai node limit** — fits, but with ~25 GB
headroom after Ray's object store. Note 500 walkers on a 64-core node over-
subscribes (~8×), so wall-time speedup saturates near ~64; the win here is
statistical (independent chains aggregate to flatness in fewer total MC steps).

## Launch

```bash
pjsub j_c1_parallel_w500.sh     # edit seed via SEED=... if needed (see AGENTS)
```

## Outputs

Written to `./wl_output_c1_parallel_w500/`: `g_of_E.csv`, `g_of_E.png`,
`thermodynamics.csv`, `heat_capacity.csv` (aggregate over all 500 walkers).