# TUTORIAL — Reproduce run b9_femgo_walk_emax04_exclworst_noxsf_novelty

This reproduces the nested-sampling run in
`_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty/`: **plain Fe/MgO** (13 seeds),
temperature-free, `--e-max-per-atom 0.4`, windowed seeding `[0.3, 0.35]`, dual-scale
MC walk with `--walk-exclude-worst`, `--no-posterior-xsf`, and the new
**`--novelty-threshold 1.0`** initial live-set de-duplication (v1.7.0).

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
    --e-max-per-atom 0.4 \
    --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
    --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
    --walk-exclude-worst \
    --no-posterior-xsf \
    --novelty-threshold 1.0 --novelty-max-attempts 500 \
    --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty --rng 42
```

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty
pjsub j_b9_femgo_walk_emax04_exclworst_noxsf_novelty.sh
```

## What each flag does

- `--temperature-free` — beta kept out of the likelihood; post-processes Z/F/posterior
  at `--temperatures`.
- `--e-max-per-atom 0.4` — drop DB structures above 0.4 eV/atom relative to the min.
- `--e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000` — windowed
  initial-live seeding (anchor in [0.30, 0.35] eV/atom; rest capped at 0.35).
- `--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both` —
  dual-scale constrained MC walk (50 trials, small 0.05 / large 0.40, 50/50 both).
- `--walk-exclude-worst` — the walk clones ONLY from live points EXCLUDING the worst
  (Fortran-style).
- `--no-posterior-xsf` — skip writing posterior `.xsf` files; `posterior_summary.csv`
  is still written.
- `--novelty-threshold 1.0 --novelty-max-attempts 500` — de-duplicate the INITIAL live
  set in AGOX Fingerprint space: each initial live point must be ≥ 1.0 from all
  already-kept ones; retry up to 500 draws, else accept the most-novel candidate.
  Applied only at `initialize()`; GPR training and the run use the full DB.

## Note on --no-posterior-xsf

The automatic state-density / landscape analysis still runs (it uses in-memory posterior
structures, not the xsf). Only saved-run re-analysis (`--analyze-only`) needs the xsf and will not
work with this run.

## Verification

- Live log shows the windowed-start anchor rel energy in `[0.30, 0.35]` and all initial live
  points ≤ 0.35.
- `unphys: 0`; live-energy range converges toward `E_ref`.
- `samples.csv`, `final_live_energies.csv`, `thermodynamics.csv`,
  `posterior_T*/posterior_summary.csv` (no `.xsf`), and `analysis/` PNGs are produced.
- The final state-density/landscape analysis runs without the `plot_structure_landscape 's'`
  TypeError (the correct `plot_structure_landscape.py` is bundled).
- The initial live set is de-duplicated: the live-log / sampler note confirms the novelty
  threshold is active (`--novelty-threshold 1.0`).
