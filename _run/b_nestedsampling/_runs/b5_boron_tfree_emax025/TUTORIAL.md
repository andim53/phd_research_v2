# TUTORIAL — Reproduce run b5_boron_tfree_emax025 (temperature-free NS, B-doped Fe/MgO)

Step-by-step guide to reproduce this run in isolation. Level: intermediate.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0) for local runs:
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- HPC pjsub (PJM) for the batch run (`gpaw_env`, set in `j_b5_boron_ns.sh`).
- Dataset present in this dir: `dataset/seed_*/1_db/db_*.db` (5 DBs, Fe25Mg25O25B7).

## Step 0 — What this run does

Runs nested sampling on the **B-doped** Fe/MgO dataset (5 seeds, seed_0..4, B doped
into the Fe layer) in **temperature-free mode**, with the same NS parameters as the
reference `_analysist/1_result/1_no_prior_control`, plus a relative high-energy cut:

```
main.py --temperature-free --temperatures 100,200,300,500,1000 \
        --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B \
        --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

- **Temperature-free:** beta is kept OUT of the likelihood; the sampler does one
  energy-constrained top-down pass (per Pártay 2021 / Yang 2024). Z(β), free energy
  `F = -k_B T ln Z`, and the posterior are evaluated in post-processing at each
  temperature in `--temperatures`.
- `--perturb-symbols Fe,B` moves **both Fe and B** atoms during prior sampling
  (multi-symbol support in the latest `nested_sampler.py`); Mg/O stay fixed.
- `--e-max-per-atom 0.25` keeps structures within 0.25 eV/atom of the dataset minimum
  (relative), dropping higher-energy structures (181 of 496 remain) so the GPR fit is
  not broken (a tighter cut than b2's 0.67).

## Step 1 — Local run

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b5_boron_tfree_emax025
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B \
    --e-max-per-atom 0.25 --output ./ns_output_tfree_emax025 --rng 42
```

For a quick sanity check you can lower `--n-live`/`--n-iters` (e.g. 20/30).

## Step 2 — HPC launch

```bash
pjsub j_b5_boron_ns.sh
```

- Header: 64 cores, `gpaw_env`, 120 h (same as the reference `j_nested.sh`).
- The job runs the single temperature-free invocation with `OMP_NUM_THREADS=1`.

## Step 3 — Outputs & verification

Outputs land in `ns_output_tfree_emax025/`:
- `evidence_history.csv` — iteration, Z (one row per iteration).
- `thermodynamics.csv` — T, β, logZ, Z, F=−k_B T ln Z (one row per temperature).
- `posterior_T{KKK}/` — per-temperature posterior structures + `posterior_summary.csv`.
- `samples.csv`, `final_live_energies.csv`, `posterior_structures/*.xsf`.
- `analysis/` — state-density / landscape analysis.

Sanity checks:
- The sampler prints `[NestedSampler] Perturbing N atoms of symbol(s) ['Fe', 'B']`
  (should be 25 Fe + 7 B = 32 atoms).
- The `--e-max-per-atom 0.25` filter line shows the dropped/remaining count.
- `thermodynamics.csv` should show Z increasing and F becoming less negative as T
  rises (physical).
- Live energies converge toward the filtered E_ref; `unphys: 0` in a healthy run.

## Pitfalls

- **`scripts` module required (ModuleNotFoundError).** `nested_sampling/state_density.py`
  does `from scripts.plot_structure_landscape import plot_structure_landscape`. For the
  run to import, `plot_structure_landscape.py` MUST be present at
  `nested_sampling/scripts/plot_structure_landscape.py` (resolved via the package dir
  on sys.path). This run has it.
- **Env:** job uses `gpaw_env`; if AGOX imports fail, edit `j_b5_boron_ns.sh` to
  `conda activate agox_v2`.
- **Unphysical energies:** some boron seeds contain high-energy structures; the
  `|E|<1e4` filter handles gross outliers, and `--e-max-per-atom 0.25` drops them
  before training/sampling.
- **Composition:** the dataset must be uniform (Fe25Mg25O25B7) for the single
  Fingerprint descriptor — do not mix with non-B structures.

## Verification checklist

- [ ] Sampler log confirms `['Fe', 'B']` perturbed (32 atoms)
- [ ] `--e-max-per-atom 0.25` filter line shows dropped/remaining count
- [ ] `thermodynamics.csv` has one row per temperature; Z ↑, F less negative with T
- [ ] `posterior_T*` dirs written for each temperature
- [ ] Output dir contains evidence_history.csv + posterior_structures/*.xsf + analysis/
- [ ] Run via the env python (or HPC job)
