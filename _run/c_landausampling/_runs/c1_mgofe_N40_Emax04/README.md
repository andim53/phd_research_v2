# Run c1_mgofe_N40_Emax04 — Wang–Landau on plain Fe/MgO (dataset)

Run directory: `_runs/c1_mgofe_N40_Emax04/` (self-contained, launchable on HPC).
Copied from the latest project-root code (**main.py v1.1.0** + `wang_landau/`
package) + the **plain Fe/MgO** dataset (`dataset/`, 13 seeds, 1297 structures,
Fe25Mg25O25 / 75 atoms).

This is the **baseline** Wang–Landau run: single mobile species (Fe), no swap
move.

## What this run does

```bash
main.py --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe \
    --temperatures 100,200,300,500,1000 \
    --output ./wl_output_c1 --rng 42
```

Treatment:
- **`--dataset dataset`** — plain Fe/MgO (13 seeds, 1297 structures).
- **`--n-bins 40` / `--e-max 0.40`** — g(E) over `[0, 0.40]` eV/atom relative.
- **`--mc-steps 20000000`** — HPC-scale WL walk budget.
- **`--small-step 0.05` / `--large-step 0.40`** — dual-scale rattle.
- **`--perturb-symbols Fe`** — rattle only the mobile Fe atoms. **No swap** (the
  plain Fe/MgO system has a single mobile species, so swaps are a no-op anyway).

## Outputs

Written to `./wl_output_c1/`: `g_of_E.csv`, `g_of_E.png`,
`thermodynamics.csv`, `heat_capacity.csv`.

## MC-steps sweep job (`j_c1_mgofe_N40_Emax04_sweep.sh`)

A companion PJM job runs the **same** parameters at three smaller MC-step budgets
in ONE job, writing each to its own output dir (all params identical to the
baseline except `--mc-steps` and `--output`):

| Run | `--mc-steps` | `--output` |
|---|---|---|
| sweep 10k | `10000` | `./wl_output_c1_sweep_10000` |
| sweep 30k | `30000` | `./wl_output_c1_sweep_30000` |
| sweep 50k | `50000` | `./wl_output_c1_sweep_50000` |

Launch: `pjsub j_c1_mgofe_N40_Emax04_sweep.sh` (three sequential `main.py` calls,
each to its own output dir). Useful for a convergence-over-mc-steps study.
