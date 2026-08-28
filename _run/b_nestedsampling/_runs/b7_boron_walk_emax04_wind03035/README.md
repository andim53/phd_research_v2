# Run b7_boron_walk_emax04_wind03035 — Temperature-free NS on B-doped Fe/MgO, e-max 0.4, windowed start + dual-scale walk

Run directory: `_runs/b7_boron_walk_emax04_wind03035/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`main.py` v1.4.0 + `nested_sampling/`
package) + the **B-doped** dataset (`dataset_boron/`, copied as `dataset/`, 5 seeds).

This run uses **exactly the same parameters as `_runs/b6_tfree_walk_emax04`** but on
the **boron (B-doped Fe/MgO)** system instead of plain Fe/MgO. The only differences
from b6 are the dataset (Fe25Mg25O25B7, 82 atoms, 5 seeds) and
`--perturb-symbols Fe,B` (B atoms also move during prior sampling / the walk).

## What this run does

```bash
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --output ./ns_output_tfree_walk_emax04 --rng 42
```

Treatment (same as b6, applied to boron):

- **Temperature-free mode** — beta kept OUT of the likelihood (Pártay 2021 / Yang 2024);
  Z(β), F = −k_B T ln Z, and the posterior are post-processed at each
  `--temperatures` value (100,200,300,500,1000 K).
- **`--e-max-per-atom 0.4`** — keep structures within 0.4 eV/atom of the dataset
  minimum (relative energy), dropping higher-energy outliers before GPR training and
  sampling. (The boron dataset is known to contain outliers up to ~5.6 eV/atom above
  the minimum; this cut removes them.)
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding: ONE
  initial live point (the "worst") found by bounded-attempt search in
  `[0.30, 0.35]` eV/atom above the global minimum; remaining live points uniform,
  capped at 0.35. The run starts near 0.3–0.35 eV/atom and descends, keeping all
  lower-energy structures.
- **`--walk`** — dual-scale constrained MC walk in `sample_constrained`: clone a
  random surviving live point and evolve with `--walk-steps 50` Gaussian trials
  (small 0.05 Å, large 0.40 Å, `--walk-mode both` = 50/50), accepting steps below
  the current energy boundary; falls back to rejection draws if the walk fails.
- **`--perturb-symbols Fe,B`** — both Fe and B atoms move; all others (Mg/O) fixed.

## Scripts / package versions

- `main.py` and `nested_sampling/` copied from the project root at **v1.4.0**.
- `nested_sampling/scripts/plot_structure_landscape.py` copied from
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/` — the CORRECT
  version that accepts `s=`, so the final landscape analysis will not crash with the
  `TypeError: ... 's'` bug.

## Outputs

Written to `./ns_output_tfree_walk_emax04/`: `samples.csv`, `final_live_energies.csv`,
`thermodynamics.csv`, per-T posterior dirs `posterior_T{KKK}/`, plus the automatic
state-density/landscape analysis in `<output>/analysis/`.
