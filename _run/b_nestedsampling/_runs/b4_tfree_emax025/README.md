# Run b4_tfree_emax025 — Temperature-free NS on plain Fe/MgO, e-max-per-atom 0.25

Run directory: `_runs/b4_tfree_emax025/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`main.py` v1.2.0 + `nested_sampling/`
package) + the plain **Fe/MgO (no Boron)** dataset (13 seeds, same system as
`_analysist/1_result/1_no_prior_control`).

## What this run does

Runs the nested-sampling pipeline (`main.py`) on the **plain Fe/MgO** dataset
(no B), in **temperature-free mode**, with **`--e-max-per-atom 0.25`** (relative to
the dataset minimum):

```
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

Key features:
- **Temperature-free mode** — beta kept OUT of the likelihood (energy-constrained
  top-down pass, per Pártay 2021 / Yang 2024). The partition function Z(β), free
  energy F = −k_B T ln Z, and the posterior are evaluated in post-processing at each
  `--temperatures` value (100,200,300,500,1000 K) from one run.
- **`--e-max-per-atom 0.25`** — keeps structures within 0.25 eV/atom of the dataset
  minimum (relative energy), dropping higher-energy structures. Plain Fe/MgO spans
  ~0.67 eV/atom, so this keeps only the lowest-energy band (~0.25 eV/atom), focusing
  the GPR training and sampling on the most relevant low-energy structures.
- Same NS params as the reference `1_no_prior_control`: `--n-live 100 --n-iters 1000
  --perturb 0.01 --perturb-symbols Fe --rng 42`.

## Dataset

- Plain **Fe/MgO** (no Boron), 13 seeds (seed_3..15), 1297 structures, all
  Mg25O25Fe25 / 75 atoms — same system as `1_no_prior_control`. Copied from the
  project-root `dataset/` into this run as `dataset/`.

## Environment

- HPC batch (`j_b4_tfree_emax025.sh`) activates `gpaw_env` (standing HPC convention).
  If it fails on AGOX imports, switch `conda activate gpaw_env` →
  `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python main.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b4_tfree_emax025
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
    --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

## Usage (HPC)

```bash
pjsub j_b4_tfree_emax025.sh
```

## Outputs (`ns_output_tfree_emax025/`)

- `evidence_history.csv`, `log_evidence.csv`, `final_live_energies.csv`
- `posterior_summary.csv`, `posterior_structures/posterior_*.xsf`
- `samples.csv`, `thermodynamics.csv` (T, β, logZ, Z, F=−k_B T ln Z)
- `posterior_T{KKK}/` per-temperature posterior dirs (temperature-free post-processing)
- `analysis/` — state-density / landscape analysis

## Contents

- `main.py` — latest project-root version (v1.2.0), self-contained
- `nested_sampling/` — package (NestedSampler, train_gpr, state_density, utils) incl.
  the required `scripts/plot_structure_landscape.py`
- `dataset/` — plain Fe/MgO seed DBs (13 DBs, Mg25O25Fe25; gitignored)
- `j_b4_tfree_emax025.sh` — PJM batch script (64 cores, gpaw_env)
- `README.md` / `TUTORIAL.md` — this run's docs
