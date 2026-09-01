# TUTORIAL — Reproduce run b11_boron_walk_emax04_exclworst_noxsf_novelty

This reproduces the nested-sampling runs in
`1_runs/b11_boron_walk_emax04_exclworst_noxsf_novelty/`: **B-doped Fe/MgO** (5 seeds,
Fe25Mg25O25B7, 82 atoms), temperature-free, `--e-max-per-atom 0.4`, windowed seeding
`[0.3, 0.35]`, dual-scale MC walk with `--walk-exclude-worst`, `--no-posterior-xsf`,
`--novelty-threshold 1.0`, `--perturb-symbols Fe,B` (v1.7.0), swept over
**`--n-iters` = 5000 / 10000 / 20000**.

## Prerequisites

- AGOX/ASE stack in conda env `agox_v2` (local dev) or `gpaw_env` (HPC via `j_*.sh`).
- Absolute python: `/home/think/miniconda3/envs/agox_v2/bin/python`.

## Reproduce (one-line, local) — per iteration value

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/1_runs/b11_boron_walk_emax04_exclworst_noxsf_novelty
# iter 5000
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 5000 --perturb 0.01 --perturb-symbols Fe,B \
    --e-max-per-atom 0.4 \
    --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
    --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
    --walk-exclude-worst \
    --no-posterior-xsf \
    --novelty-threshold 1.0 --novelty-max-attempts 500 \
    --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter5000 --rng 42
```
Repeat the same command with `--n-iters 10000` / `20000` and the matching
`..._boron_iter10000` / `..._boron_iter20000` output dir.

## Reproduce (HPC, PJM)

```bash
cd /home/think/Desktop/research/_run/b_nestedsampling/1_runs/b11_boron_walk_emax04_exclworst_noxsf_novelty
pjsub j_b11_boron_walk_emax04_exclworst_noxsf_novelty_iter5000.sh
pjsub j_b11_boron_walk_emax04_exclworst_noxsf_novelty_iter10000.sh
pjsub j_b11_boron_walk_emax04_exclworst_noxsf_novelty_iter20000.sh
```

## What each flag does

- `--temperature-free` — beta kept out of the likelihood; post-processes Z/F/posterior
  at `--temperatures`.
- `--perturb-symbols Fe,B` — BOTH Fe and B atoms move during prior sampling / the walk;
  all others (Mg/O) fixed. (This is what makes it "boron" — B is in the perturbed set.)
- `--e-max-per-atom 0.4` — drop DB structures above 0.4 eV/atom relative to the min (removes the
  known boron outliers up to ~5.6 eV/atom).
- `--e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000` — windowed
  initial-live seeding (anchor in [0.30, 0.35] eV/atom; rest capped at 0.35).
- `--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both` —
  dual-scale constrained MC walk (50 trials, small 0.05 / large 0.40, 50/50 both).
- `--walk-exclude-worst` — the walk clones ONLY from live points EXCLUDING the worst.
- `--no-posterior-xsf` — skip writing posterior `.xsf` files; `posterior_summary.csv`
  is still written.
- `--novelty-threshold 1.0 --novelty-max-attempts 500` — de-duplicate the INITIAL live
  set in AGOX Fingerprint space (applied only at `initialize()`; GPR uses the full DB).
- `--n-iters 5000/10000/20000` — the swept variable: how many NS iterations (how much of the
  prior volume is consumed, `X_final = exp(-n_iters/n_live)`).

## Note on the boron dataset

The run reads `dataset/seed_*/1_db/db_*.db` (5 boron seeds). `main.py` derives the descriptor
and `n_atoms` from the data (82 atoms), so the multi-seed GPR works for this composition. It uses
a single global Fingerprint — the boron set is uniform (Fe25Mg25O25B7), which the descriptor
requires.

## Note on --no-posterior-xsf

The automatic state-density / landscape analysis still runs (it uses in-memory posterior
structures, not the xsf). Only saved-run re-analysis (`--analyze-only`) needs the xsf and will
not work with this run.

## Verification

- Live log shows the windowed-start anchor rel energy in `[0.30, 0.35]` and all initial live
  points ≤ 0.35.
- `unphys: 0`; live-energy range converges toward `E_ref`.
- Each output dir has `samples.csv`, `final_live_energies.csv`, `thermodynamics.csv`,
  `posterior_T*/posterior_summary.csv` (no `.xsf`), and `analysis/` PNGs.
- The final state-density/landscape analysis runs without the `plot_structure_landscape 's'`
  TypeError (the correct `plot_structure_landscape.py` is bundled).
- The initial live set is de-duplicated (novelty threshold active).
- For the convergence study: `log Z` (from `thermodynamics.csv`) should plateau as
  `--n-iters` increases (5000 → 20000), and `X_final = exp(-n_iters/100)` shrinks accordingly.
