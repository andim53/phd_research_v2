# TUTORIAL — Reproduce run b5_boron_ns_emax025 (nested sampling on B-doped Fe/MgO)

Step-by-step guide to reproduce this run in isolation. Level: intermediate.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0) for local runs:
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- HPC pjsub (PJM) for the batch run (`gpaw_env`, set in `j_b5_boron_ns.sh`).
- Dataset present in this dir: `dataset/seed_*/1_db/db_*.db` (5 DBs, Fe25Mg25O25B7).

## Step 0 — What this run does

Runs the nested-sampling pipeline (`main.py`) on the **B-doped** Fe/MgO dataset
(5 seeds, seed_0..4, B doped into the Fe layer), with the same NS parameters as the
reference `_analysist/1_result/1_no_prior_control`, plus a relative high-energy cut:

```
main.py --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 \
        --perturb-symbols Fe,B --e-max-per-atom 0.25 \
        --output ./ns_output_T300_100_1000_0.01 --rng 42
```

`--perturb-symbols Fe,B` moves **both Fe and B** atoms during prior sampling
(multi-symbol support in the latest `nested_sampler.py`); Mg/O stay fixed.
`--e-max-per-atom 0.25` keeps structures within 0.25 eV/atom of the dataset minimum
(relative), dropping higher-energy structures so the GPR fit is not broken (a tighter
cut than b2's 0.67).

## Step 1 — Local run

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b5_boron_ns_emax025
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 \
    --perturb-symbols Fe,B --e-max-per-atom 0.25 \
    --output ./ns_output_T300_100_1000_0.01 --rng 42
```

For a quick sanity check you can lower `--n-live`/`--n-iters` (e.g. 20/30).

## Step 2 — HPC launch

```bash
pjsub j_b5_boron_ns.sh
```

- Header: 64 cores, `gpaw_env`, 120 h (same as the reference `j_nested.sh`).
- The job runs the single invocation with `OMP_NUM_THREADS=1`.

## Step 3 — Outputs & verification

Outputs land in `ns_output_T300_100_1000_0.01/`:
- `evidence_history.csv` — iteration, Z (one row per iteration).
- `log_evidence.csv` — iteration, log Z (malformed layout; use evidence_history).
- `final_live_energies.csv`, `posterior_summary.csv`,
  `posterior_structures/posterior_*.xsf`.
- `analysis/` — state-density / landscape analysis.

Sanity checks:
- The sampler prints `[NestedSampler] Perturbing N atoms of symbol(s) ['Fe', 'B']`
  (should be 25 Fe + 7 B = 32 atoms).
- The `--e-max-per-atom 0.25` filter line shows the dropped/remaining count.
- Live energies converge toward E_ref; `unphys: 0` in a healthy run.

## Pitfalls

- **`scripts` module required (ModuleNotFoundError).** `nested_sampling/state_density.py`
  does `from scripts.plot_structure_landscape import plot_structure_landscape`. For the
  run to import, `plot_structure_landscape.py` MUST be present at
  `nested_sampling/scripts/plot_structure_landscape.py` (resolved via the package dir
  on sys.path). When creating an NS run dir, always copy it (e.g.
  `cp <src>/plot_structure_landscape.py nested_sampling/scripts/`). This run has it.
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
- [ ] Output dir contains evidence_history.csv + posterior_structures/*.xsf + analysis/
- [ ] Live energies converge toward E_ref
- [ ] Run via the env python (or HPC job)
