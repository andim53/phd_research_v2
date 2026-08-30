# Run b10_femgo_walk_emax04_exclworst_noxsf_novelty — Fe/MgO NS, iteration sweep

Run directory: `_runs/b10_femgo_walk_emax04_exclworst_noxsf_novelty/` (self-contained,
launchable on HPC)
Copied from the latest project-root code (**v1.7.0**) + the **plain Fe/MgO (no Boron)**
dataset (13 seeds, same system as `_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty`).

This run is **exactly b9's treatment** (plain Fe/MgO; temperature-free; `--e-max-per-atom 0.4`;
window `[0.3, 0.35]`; `--walk` with `--walk-exclude-worst`; `--no-posterior-xsf`;
`--novelty-threshold 1.0`) swept over **three `--n-iters` values**: **5000, 10000, 20000**.
Three job scripts, one per iteration count, each writing its own output directory.

## What this run does

```bash
# three job scripts differ ONLY in --n-iters and the output dir:
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters <5000|10000|20000> --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --walk-exclude-worst \
        --no-posterior-xsf \
        --novelty-threshold 1.0 --novelty-max-attempts 500 \
        --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter<5000|10000|20000> --rng 42
```

## Job scripts

| Script | `--n-iters` | Output dir |
|---|---|---|
| `j_b10_..._iter5000.sh` | 5000 | `ns_output_..._novelty_iter5000` |
| `j_b10_..._iter10000.sh` | 10000 | `ns_output_..._novelty_iter10000` |
| `j_b10_..._iter20000.sh` | 20000 | `ns_output_..._novelty_iter20000` |

Launch with `pjsub j_b10_..._iter<...>.sh` (PJM, 64 cores, `gpaw_env`).

Treatment (identical to b9, swept over iterations):
- **Temperature-free mode** (beta kept OUT of the likelihood; Z/F/posterior post-processed at
  each `--temperatures` value, 100,200,300,500,1000 K).
- **`--e-max-per-atom 0.4`** — keep structures within 0.4 eV/atom of the dataset minimum.
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding (anchor in
  `[0.30, 0.35]` eV/atom; rest capped at 0.35).
- **`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both`** — dual-scale
  constrained MC walk; **`--walk-exclude-worst`** clones only from live points excluding the worst.
- **`--no-posterior-xsf`** — no `.xsf` structure files are written; `posterior_summary.csv` is
  still written.
- **`--novelty-threshold 1.0`** — the initial live set is de-duplicated in AGOX Fingerprint space.
- **`--n-iters`** — the swept variable (5000 / 10000 / 20000). Larger iterations consume more of
  the prior volume (`X_final = exp(-n_iters/n_live)` becomes smaller), for a convergence study of
  `log Z`.

## Outputs

Each job writes to its own `./ns_output_..._iter<...>/`: `samples.csv`,
`final_live_energies.csv`, `thermodynamics.csv`, per-T `posterior_T{KKK}/posterior_summary.csv`
(no `.xsf`), and the automatic state-density/landscape analysis in `<output>/analysis/`.
