# Run b5_boron_tfree_emax025 — Temperature-free NS on B-doped Fe/MgO

Run directory: `_runs/b5_boron_tfree_emax025/` (self-contained, launchable on HPC)
Copied from the latest project-root code (`main.py` v1.2.0 + `nested_sampling/`
package) + the B-doped dataset (`dataset_boron/`, copied as `dataset/`).

## What this run does

Runs the **nested-sampling pipeline** (`main.py`) on the **B-doped Fe/MgO** dataset in
**temperature-free mode**, with the **same NS parameters as the reference run**
`_analysist/1_no_prior_control`, plus a **relative high-energy cut**:

```
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B \
        --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

Key features:
- **Temperature-free mode** — beta kept OUT of the likelihood (energy-constrained
  top-down pass, per Pártay 2021 / Yang 2024). The partition function Z(β), free
  energy F = −k_B T ln Z, and the posterior are evaluated in post-processing at each
  `--temperatures` value (100,200,300,500,1000 K) from one run.
- **B-doped** dataset (Fe25Mg25O25B7, 5 seeds) with **B included in the perturbation**
  via `--perturb-symbols Fe,B` (both Fe and B atoms are moved during prior sampling).
- **`--e-max-per-atom 0.25`** — keeps structures within 0.25 eV/atom of the dataset
  minimum (relative energy), dropping higher-energy structures (181 of 496 remain) so
  the GPR fit is not broken. Same control as the GPR-accuracy code.

## Error explanation & fix (this run)

**Observed failure (same as b4_tfree_emax025):** the run can crash at the final
**state-density / landscape analysis** with

```
TypeError: plot_structure_landscape() got an unexpected keyword argument 's'
```

at `nested_sampling/state_density.py:130` (in `make_landscape`). The nested-sampling
itself completes successfully; the crash is only in the optional landscape plotting.

**Root cause:** the run's `nested_sampling/scripts/plot_structure_landscape.py` was
copied from the stale `dataset_boron/scripts/` version, which does **not** accept an
`s` argument, but the current `state_density.py` calls `plot_structure_landscape(..., s=5, ...)`.

**Fix (applied):** copied the correct `plot_structure_landscape.py` (accepts `s=25`)
from the reference `_analysist/1_no_prior_control/nested_sampling/scripts/`
into `nested_sampling/scripts/`. Verified: accepts `s=` and all kwargs `state_density.py`
passes (none missing); compiles. Resubmit `pjsub j_b5_boron_ns.sh` to complete the
analysis.

## Dataset (boron)

- Copied from `dataset_boron/` into this run as `dataset/` (main.py reads `./dataset`).
- Composition: **Fe25Mg25O25B7** (7 B atoms doped into the Fe layer), 5 seeds (0-4),
  100 structures each (seed_4 has 96).
- Note: some seeds (2-4) contain structures with unphysically high energies
  (up to ~5.6 eV/atom above the minimum); the GPR's `|E|<1e4` physical filter handles
  gross outliers, and `--e-max-per-atom 0.25` drops them before training/sampling.

## Environment

- HPC batch (`j_b5_boron_ns.sh`) activates `gpaw_env` (standing HPC convention). The
  script needs AGOX/ASE (agox_v2 locally). If it fails on AGOX imports, switch
  `conda activate gpaw_env` → `conda activate agox_v2`.
- Local run:
  `/home/think/miniconda3/envs/agox_v2/bin/python main.py [options]`

## Usage (local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b5_boron_tfree_emax025
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B \
    --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

## Usage (HPC)

```bash
pjsub j_b5_boron_ns.sh
```

## Outputs (`ns_output_tfree_emax025/`)

- `evidence_history.csv`, `log_evidence.csv`, `final_live_energies.csv`
- `posterior_summary.csv`, `posterior_structures/posterior_*.xsf`
- `samples.csv`, `thermodynamics.csv` (T, β, logZ, Z, F=−k_B T ln Z)
- `posterior_T{KKK}/` per-temperature posterior dirs (temperature-free post-processing)
- `analysis/` — state-density / landscape analysis (training/posterior)

## Contents

- `main.py` — latest project-root version (v1.2.0), self-contained
- `nested_sampling/` — package (NestedSampler, train_gpr, state_density, utils) incl.
  the required `scripts/plot_structure_landscape.py`
- `dataset/` — B-doped seed DBs (5 DBs, Fe25Mg25O25B7; gitignored)
- `j_b5_boron_ns.sh` — PJM batch script (64 cores, gpaw_env)
- `README.md` / `TUTORIAL.md` — this run's docs
