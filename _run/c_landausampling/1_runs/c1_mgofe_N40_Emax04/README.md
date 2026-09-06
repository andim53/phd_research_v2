# Run c1_mgofe_N40_Emax04 — Wang–Landau on plain Fe/MgO (dataset)

Run directory: `1_runs/c1_mgofe_N40_Emax04/` (self-contained, launchable on HPC).
Copied from the latest project-root code (**main.py v1.3.0** + `wang_landau/`
package) + the **plain Fe/MgO** dataset (`dataset/`, 13 seeds, 1297 structures,
Fe25Mg25O25 / 75 atoms).

This is the **baseline** Wang–Landau run: single mobile species (Fe), no swap
move.

## What this run does

```bash
main.py --dataset dataset --n-bins 100 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe \
    --temperatures 100,200,300,500,1000 \
    --output ./wl_output_c1 --rng 42
```

Treatment:
- **`--dataset dataset`** — plain Fe/MgO (13 seeds, 1297 structures).
- **`--n-bins 100` / `--e-max 0.40`** — g(E) over `[0, 0.40]` eV/atom relative at
  fine (100-bin) resolution.
- **`--mc-steps 20000000`** — HPC-scale WL walk budget.
- **`--small-step 0.05` / `--large-step 0.20`** — dual-scale rattle.
- **`--perturb-symbols Fe`** — rattle only the mobile Fe atoms. **No swap** (the
  plain Fe/MgO system has a single mobile species, so swaps are a no-op anyway).

## Outputs

Written to `./wl_output_c1/`: `g_of_E.csv`, `g_of_E.png`,
`thermodynamics.csv`, `heat_capacity.csv`.
