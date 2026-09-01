# Run b8_femgo_walk_emax04_exclworst_noxsf — Fe/MgO NS with walk-exclude-worst + no xsf

Run directory: `_runs/b8_femgo_walk_emax04_exclworst_noxsf/` (self-contained, launchable on HPC)
Copied from the latest project-root code (**v1.6.0**) + the **plain Fe/MgO (no Boron)**
dataset (13 seeds, same system as `_runs/b6_tfree_walk_emax04`).

This run uses **b6's parameters** (plain Fe/MgO) plus two new flags:
- **`--walk-exclude-worst`** — clone only from live points EXCLUDING the worst (Fortran-style),
  instead of Python's default uniform-over-all clone source.
- **`--no-posterior-xsf`** — skip writing the posterior `.xsf` structure files (fixed-T
  `posterior_structures/` and temperature-free `posterior_T{KKK}/`); the `posterior_summary.csv`
  is still written. Note: saved-run re-analysis (`--analyze-only`) will not work because it needs
  the xsf.

## What this run does

```bash
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --walk-exclude-worst \
        --no-posterior-xsf \
        --output ./ns_output_tfree_walk_emax04_exclworst_noxsf --rng 42
```

Treatment:
- **Temperature-free mode** (beta kept OUT of the likelihood; Z/F/posterior post-processed at
  each `--temperatures` value, 100,200,300,500,1000 K).
- **`--e-max-per-atom 0.4`** — keep structures within 0.4 eV/atom of the dataset minimum.
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding: one anchor live
  point in `[0.30, 0.35]` eV/atom above the global minimum; remaining live points capped at 0.35.
- **`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both`** — dual-scale
  constrained MC walk in `sample_constrained`.
- **`--walk-exclude-worst`** — the walk clones only from live points EXCLUDING the worst
  (Fortran-style), not uniformly over all.
- **`--no-posterior-xsf`** — no `.xsf` structure files are written (saves disk on heavy runs); the
  `posterior_summary.csv` is still written. The automatic state-density analysis still runs (it
  uses in-memory structures, not the xsf).

## Outputs

Written to `./ns_output_tfree_walk_emax04_exclworst_noxsf/`: `samples.csv`,
`final_live_energies.csv`, `thermodynamics.csv`, per-T `posterior_T{KKK}/posterior_summary.csv`
(no `.xsf`), and the automatic state-density/landscape analysis in `<output>/analysis/`.

## Note on --no-posterior-xsf

The automatic state-density / landscape analysis (`analysis/training/conf_space.png`,
`analysis/posterior/conf_space.png`, `comparison_state_density.png`) still runs, because it uses
the in-memory posterior `Atoms` objects, not the xsf files. Only **saved-run re-analysis**
(`--analyze-only`) needs the xsf and will not work here.
