# TUTORIAL — Reproduce run b8_femgo_walk_emax04_exclworst_noxsf

This reproduces the nested-sampling run in
`_runs/b8_femgo_walk_emax04_exclworst_noxsf/`: **plain Fe/MgO** (13 seeds),
temperature-free, `--e-max-per-atom 0.4`, windowed seeding `[0.3, 0.35]`, dual-scale
MC walk, **`--walk-exclude-worst`**, and **`--no-posterior-xsf`** (v1.6.0).

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b8_femgo_walk_emax04_exclworst_noxsf
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe \
    --e-max-per-atom 0.4 \
    --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
    --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
    --walk-exclude-worst \
    --no-posterior-xsf \
    --output ./ns_output_tfree_walk_emax04_exclworst_noxsf --rng 42
```

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/_runs/b8_femgo_walk_emax04_exclworst_noxsf
pjsub j_b8_femgo_walk_emax04_exclworst_noxsf.sh
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
  (Fortran-style; the Fortran clones a random other walker, never the one being
  replaced). Default (without this flag) is uniform-over-all.
- `--no-posterior-xsf` — skip writing the posterior `.xsf` structure files
  (`posterior_T{KKK}/`); `posterior_summary.csv` is still written.

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
