# Run b6_tfree_walk_emax04 — Temperature-free NS on plain Fe/MgO, e-max 0.4, windowed start + dual-scale walk

Run directory: `1_runs/b6_tfree_walk_emax04/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`main.py` v1.4.0 + `nested_sampling/`
package) + the plain **Fe/MgO (no Boron)** dataset (13 seeds, same system as
`2_analysist/1_no_prior_control`).

## What this run does

Runs the nested-sampling pipeline (`main.py`) on the **plain Fe/MgO** dataset
(no B), in **temperature-free mode**, combining the three newer features:

```bash
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --output ./ns_output_tfree_walk_emax04 --rng 42
```

Key features / treatment (what differs from sibling runs):

- **Temperature-free mode** — beta kept OUT of the likelihood (energy-constrained
  top-down pass, per Pártay 2021 / Yang 2024). Z(β), F = −k_B T ln Z, and the
  posterior are evaluated in post-processing at each `--temperatures` value
  (100,200,300,500,1000 K) from one run.
- **`--e-max-per-atom 0.4`** — keeps structures within 0.4 eV/atom of the dataset
  minimum (relative energy), dropping higher-energy outliers before GPR training
  and sampling.
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding: ONE
  initial live point (the "worst") is found by bounded-attempt search in
  `[0.30, 0.35]` eV/atom above the global minimum; the remaining live points are
  uniform draws capped at 0.35. So the run **starts near 0.3–0.35 eV/atom** and
  descends, while keeping all lower-energy structures.
- **`--walk`** — dual-scale constrained MC walk (Fortran-style clone-and-walk) in
  `sample_constrained`: clones a random surviving live point and evolves it with
  `--walk-steps 50` Gaussian trials (small 0.05 Å, large 0.40 Å, `--walk-mode both`
  = 50/50), accepting steps below the current energy boundary. Falls back to
  rejection draws if the walk fails.
- Same base NS params as the reference `1_no_prior_control`/b4:
  `--n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe --rng 42`.

## Scripts / package versions

- `main.py` and `nested_sampling/` copied from the project root at **v1.4.0**
  (includes the dual-scale walk and windowed-seeding features).
- `nested_sampling/scripts/plot_structure_landscape.py` copied from
  `2_analysist/1_no_prior_control/nested_sampling/scripts/` — the CORRECT
  version that accepts `s=`, so the final state-density/landscape analysis will not
  crash with the `TypeError: plot_structure_landscape() got an unexpected keyword
  argument 's'` bug.

## Outputs

Written to `./ns_output_tfree_walk_emax04/`: `samples.csv`, `final_live_energies.csv`,
`thermodynamics.csv`, per-T posterior dirs `posterior_T{KKK}/`, plus the automatic
state-density/landscape analysis in `<output>/analysis/`.
