# Run b12_boron3_walk_emax04_exclworst_noxsf_novelty — B3-doped Fe/MgO NS, iteration sweep

Run directory: `1_runs/b12_boron3_walk_emax04_exclworst_noxsf_novelty/` (self-contained,
launchable on HPC)
Copied from the latest project-root code (**v1.7.0**) + the **boron3** dataset
(`dataset_boron3/`, copied as `dataset/`, **6 non-empty seeds**; seed_6 is empty and excluded).

This run uses **exactly b11's parameters** applied to the **boron3** system. The only difference
from b11 is the dataset composition: b11 used B-doped Fe/MgO (Fe25Mg25O25B7, 82 atoms, 5 seeds),
whereas this run uses **B3-doped Fe/MgO (B3Fe25Mg25O25, 78 atoms, 6 seeds)**. `--perturb-symbols
Fe,B` moves both Fe and B atoms. It is swept over **three `--n-iters` values**: **5000, 10000,
20000**. Three job scripts, one per iteration count, each writing its own output directory.

## What this run does

```bash
# three job scripts differ ONLY in --n-iters and the output dir:
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters <5000|10000|20000> --perturb 0.01 --perturb-symbols Fe,B \
        --e-max-per-atom 0.4 \
        --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
        --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
        --walk-exclude-worst \
        --no-posterior-xsf \
        --novelty-threshold 1.0 --novelty-max-attempts 500 \
        --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron3_iter<5000|10000|20000> --rng 42
```

## Job scripts

| Script | `--n-iters` | Output dir |
|---|---|---|
| `j_b12_..._iter5000.sh` | 5000 | `ns_output_..._boron3_iter5000` |
| `j_b12_..._iter10000.sh` | 10000 | `ns_output_..._boron3_iter10000` |
| `j_b12_..._iter20000.sh` | 20000 | `ns_output_..._boron3_iter20000` |

Launch with `pjsub j_b12_..._iter<...>.sh` (PJM, 64 cores, `gpaw_env`).

Treatment (b11 params applied to boron3):
- **Temperature-free mode** (beta kept OUT of the likelihood; Z/F/posterior post-processed at
  each `--temperatures` value, 100,200,300,500,1000 K).
- **boron3 dataset** (B3Fe25Mg25O25, 78 atoms, 6 seeds) with **B included in the perturbation**
  via `--perturb-symbols Fe,B`.
- **`--e-max-per-atom 0.4`** — keep structures within 0.4 eV/atom of the dataset minimum (448 of
  597 remain).
- **`--e-window-lo 0.3 --e-window-hi 0.35`** — windowed initial-live seeding (anchor in
  `[0.30, 0.35]` eV/atom; rest capped at 0.35).
- **`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both`** — dual-scale
  constrained MC walk; **`--walk-exclude-worst`** clones only from live points excluding the worst.
- **`--no-posterior-xsf`** — no `.xsf` structure files are written; `posterior_summary.csv` is
  still written.
- **`--novelty-threshold 1.0`** — the initial live set is de-duplicated in AGOX Fingerprint space.
- **`--n-iters`** — the swept variable (5000 / 10000 / 20000).

## Outputs

Each job writes to its own `./ns_output_..._boron3_iter<...>/`: `samples.csv`,
`final_live_energies.csv`, `thermodynamics.csv`, per-T `posterior_T{KKK}/posterior_summary.csv`
(no `.xsf`), and the automatic state-density/landscape analysis in `<output>/analysis/`.
