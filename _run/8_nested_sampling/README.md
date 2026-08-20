# Nested Sampling on the combined multi-seed Fe/MgO AGOX dataset

Run script: `run_nested_sampling.py`

## What it does
1. Loads **every** structure from **every** seed database in
   `dataset/seed_*/1_db/db_*.db` (seeds 3–15, 1297 structures total, all
   Mg25O25Fe25 / 75 atoms).
2. Trains a single AGOX GPR surrogate on the combined 1297 structures (AGOX
   kernel recipe from `dataset/main.py`).
3. Runs the `NestedSampler` from the `nested_sampling` package on the combined
   dataset (log-space evidence accumulation, `log L = -beta*(E - E_ref)`).

## Environment
Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```

## Usage
```
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```

Options:
- `--temp`      temperature (K), default 300
- `--n-live`    number of live points, default 50
- `--n-iters`   nested-sampling iterations, default 300
- `--perturb`   perturbation amplitude (Å) for prior sampling, default 0.01
- `--output`    output directory, default `./ns_output_allseeds`
- `--rng`       RNG seed, default 42

## Outputs (written to `--output`)
- `evidence_history.csv`  — iteration, evidence Z
- `log_evidence.csv`      — iteration, log Z
- `final_live_energies.csv` — live-point energies at termination
- `posterior_structures/posterior_*.xsf` — top-20 weighted posterior structures
