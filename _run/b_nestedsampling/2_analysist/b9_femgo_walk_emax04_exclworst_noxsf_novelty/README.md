# Run b9_femgo_walk_emax04_exclworst_noxsf_novelty — Fe/MgO NS with novelty-threshold

Run directory: `1_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty/` (self-contained,
launchable on HPC)
Copied from the latest project-root code (**v1.7.0**) + the **plain Fe/MgO (no Boron)**
dataset (13 seeds, same system as `1_runs/b8_femgo_walk_emax04_exclworst_noxsf`).

This run uses **b8's parameters** (plain Fe/MgO; e-max 0.4; window `[0.3, 0.35]`; walk on with
`--walk-exclude-worst`; `--no-posterior-xsf`) **plus the new novelty threshold**:
- **`--novelty-threshold 1.0`** — de-duplicates the INITIAL live set: each initial live point must
  be at least 1.0 apart (Euclidean distance in AGOX Fingerprint feature space) from every
  already-kept initial live point. Applied only at `initialize()`; GPR training and the run use
  the full DB.
- **`--novelty-max-attempts 500`** — max prior draws to find a novel initial live point before
  accepting the most-novel candidate anyway.

## What this run does

```bash
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --walk-exclude-worst \
        --no-posterior-xsf \
        --novelty-threshold 1.0 --novelty-max-attempts 500 \
        --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty --rng 42
```

Treatment (same as b8 + novelty):
- **Temperature-free mode** (beta kept OUT of the likelihood; Z/F/posterior post-processed at
  each `--temperatures` value, 100,200,300,500,1000 K).
- **`--e-max-per-atom 0.4`** — keep structures within 0.4 eV/atom of the dataset minimum.
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding (anchor in
  `[0.30, 0.35]` eV/atom; rest capped at 0.35).
- **`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both`** — dual-scale
  constrained MC walk.
- **`--walk-exclude-worst`** — the walk clones only from live points EXCLUDING the worst.
- **`--no-posterior-xsf`** — no `.xsf` structure files are written; `posterior_summary.csv` is
  still written (auto state-density analysis still runs).
- **`--novelty-threshold 1.0`** — the initial live set is de-duplicated in AGOX Fingerprint space
  (each initial live point ≥ 1.0 from the others).

## Outputs

Written to `./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty/`: `samples.csv`,
`final_live_energies.csv`, `thermodynamics.csv`, per-T `posterior_T{KKK}/posterior_summary.csv`
(no `.xsf`), and the automatic state-density/landscape analysis in `<output>/analysis/`.
