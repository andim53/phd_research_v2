# TUTORIAL — Reproduce run b3_tfree_emax025 (temperature-free NS, plain Fe/MgO)

Step-by-step guide to reproduce this run in isolation. Level: intermediate.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0) for local runs:
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- HPC pjsub (PJM) for the batch run (`gpaw_env`, set in `j_b3_tfree_emax025.sh`).
- Dataset present in this dir: `dataset/seed_*/1_db/db_*.db` (13 DBs, Mg25O25Fe25).

## Step 0 — What this run does

Runs nested sampling on the **plain Fe/MgO** dataset (no B) in **temperature-free
mode** with a **relative high-energy cut**:

```
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
        --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

- **Temperature-free:** beta is kept OUT of the likelihood; the sampler does one
  energy-constrained top-down pass (per Pártay 2021 / Yang 2024). Z(β), free energy
  `F = -k_B T ln Z`, and the posterior are evaluated in post-processing at each
  temperature in `--temperatures`.
- **`--e-max-per-atom 0.25`:** keeps structures within 0.25 eV/atom of the dataset
  minimum (relative energy). Plain Fe/MgO spans ~0.67 eV/atom, so this keeps only the
  lowest-energy band, focusing the GPR + sampling on low-energy structures.
- Same NS params as the reference `1_no_prior_control`.

## Step 1 — Local run (validate on a small scale first if desired)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b3_tfree_emax025
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
    --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

For a quick sanity check you can lower `--n-live`/`--n-iters` (e.g. 20/30).

## Step 2 — HPC launch

```bash
pjsub j_b3_tfree_emax025.sh
```

- Header: 64 cores, `gpaw_env`, 120 h.
- The job runs the single temperature-free invocation with `OMP_NUM_THREADS=1`.

## Step 3 — Outputs & verification

Outputs land in `ns_output_tfree_emax025/`:
- `evidence_history.csv` — iteration, Z.
- `thermodynamics.csv` — T, β, logZ, Z, F=−k_B T ln Z (one row per temperature).
- `posterior_T{KKK}/` — per-temperature posterior structures + `posterior_summary.csv`.
- `samples.csv`, `final_live_energies.csv`, `posterior_structures/*.xsf`.
- `analysis/` — state-density / landscape analysis.

Sanity checks:
- The sampler prints the `--e-max-per-atom` filter line (structures dropped).
- `thermodynamics.csv` should show Z increasing and F becoming less negative as T
  rises (physical).
- Live energies converge toward the filtered E_ref.

## Pitfalls

- **Env:** job uses `gpaw_env`; if AGOX imports fail, edit `j_b3_tfree_emax025.sh` to
  `conda activate agox_v2`.
- **`scripts` module required:** `nested_sampling/scripts/plot_structure_landscape.py`
  MUST be present (it is, in this run) or `state_density.py` fails to import.
- **`--e-max-per-atom` is RELATIVE** to the dataset minimum (keep `E/atom − min ≤
  0.25`); 0.25 on the ~0.67 eV/atom Fe/MgO set keeps the lowest-energy band.

## Verification checklist

- [ ] Sampler log shows the `--e-max-per-atom 0.25` filter line (dropped count)
- [ ] `thermodynamics.csv` has one row per temperature; Z ↑, F less negative with T
- [ ] `posterior_T*` dirs written for each temperature
- [ ] `analysis/` produced (or `--no-analysis` used)
- [ ] Run via the env python (or HPC job)
