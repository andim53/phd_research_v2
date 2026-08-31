# Run c2_boron3_N40_Emax04 — Wang–Landau on B3-doped (dataset_boron3)

Run directory: `_runs/c2_boron3_N40_Emax04/` (self-contained, launchable on HPC).
Copied from the latest project-root code (**main.py v1.2.0** + `wang_landau/`
package) + the **B3-doped** dataset (`dataset_boron3/`, 7 seeds, B3Fe25Mg25O25 /
78 atoms).

This run exercises the **swap (permutation) move** for a multi-species system
(B + Fe mobile).

## What this run does

```bash
main.py --dataset dataset_boron3 --n-bins 100 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe,B \
    --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 \
    --temperatures 100,200,300,500,1000 \
    --output ./wl_output_c2 --rng 42
```

Treatment:
- **`--dataset dataset_boron3`** — B3-doped (7 seeds, B3Fe25Mg25O25, 78 atoms).
- **`--n-bins 100` / `--e-max 0.40`** — g(E) over `[0, 0.40]` eV/atom relative at
  fine (100-bin) resolution.
- **`--mc-steps 20000000`** — HPC-scale WL walk budget.
- **`--small-step 0.05` / `--large-step 0.20`** — dual-scale rattle.
- **`--perturb-symbols Fe,B`** — both mobile species are rattled.
- **`--swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05`** — **swap move ENABLED**:
  on 20% of MC steps a swap move exchanges the positions of a B and an Fe atom
  (random `1..2` swaps) and rattles them by 0.05 Å. This explores the
  chemical (species-arrangement) degrees of freedom, which rattle alone cannot.

## Outputs

Written to `./wl_output_c2/`: `g_of_E.csv`, `g_of_E.png`,
`thermodynamics.csv`, `heat_capacity.csv`.
