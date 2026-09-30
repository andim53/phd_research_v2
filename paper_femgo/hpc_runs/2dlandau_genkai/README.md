# hpc_runs/2dlandau_genkai — standalone 2D Wang–Landau production runner (genkai)

Fully standalone HPC runner for the 2D Wang–Landau simulation of the Fe/MgO
flat↔island transition (inherent-structure `g(E, ΔZ)` on a GPR surrogate, no
DFT). **Nothing runs on the laptop** — submit via `pjsub` on the HPC node.

## STANDALONE RULE
**This directory is a fully standalone system.** All inputs and necessities live
inside the dir — nothing is pulled from outside at run time. To run on the HPC,
copy the whole dir to the node and submit there independently.

## Layout
```
2dlandau_genkai/
├── main.py            # CLI: load 13 seed DBs -> train GPR -> 2D WL -> reweight -> save
│                      #   (canonical codes/2dlandau/main.py, relax-steps default 300)
├── landau_2d/         # package (generator, wang_landau_2d, gpr_training,
│                      #   thermodynamics, utils) — copied verbatim
├── data/femgo/        # training DBs (committed in-dir: seed_*/1_db/db_*.db x13)
├── job_2dlandau.sh    # pjsub production job (a-batch, 64 cores, elapse 120h)
├── README.md
└── output/            # results (regenerable, gitignored)
```

## Run
```bash
# copy this dir to the HPC node, then:
pjsub job_2dlandau.sh
```

The job uses `--use-ray` (AGOX's Ray backend parallelizes GPR
training/prediction). The WL MC walk itself is serial by design — the 64 cores
accelerate the GPR, not the walk.

## Data provenance
`data/femgo/` holds 13 training DBs (`seed_3`…`seed_15` → `1_db/db_*.db`),
copied from `paper_femgo/data/femgo` and committed in-dir (`stop_16` is
excluded by the `seed_*` glob). These are inputs, not regenerable.

## Environment
- HPC: `gpaw_env` conda env — the run uses that env's `python` (NOT `agox_v2`).
- Local smoke check (serial, no `--use-ray`, uses `agox_v2` since `gpaw_env`
  is HPC-only):
  ```bash
  cd hpc_runs/2dlandau_genkai
  /home/think/miniconda3/envs/agox_v2/bin/python main.py --mc-steps 1
  ```
  must load the 13 in-dir DBs, train the GPR, and write `output/g_of_E_dZ.json`.

## Units / parameters
E bins 35 over [0, 0.7] eV/atom; ΔZ bins 12 over [contact gap, natural island]
(film height); **relax 300 BFGS steps**; reference pass 5000; MC 100000 steps;
temperatures 298, 573, 623, 673, 773 K (critical fabrication temperatures:
deposition 298 K + annealing 573–773 K, from
`_run/b_nestedsampling/.../DISCUSSION.md`).

### Why relax-steps = 300 (inherent-structure DOS)
Calibrated on the real GPR with `fmax=0.05 eV/Å` (free quenches across the dZ
range, 6 structs/target): ~68% of non-flat quenches need ≥100 BFGS steps, and
the max-natural-dZ case needs ~184 (median 112, p90 253, max 277). The previous
`relax-steps=100` truncated most quenches — each "inherent structure" was a
mid-relaxation state, not a basin minimum, which broadened/skewed `g(E,ΔZ)` and
impeded WL flatness. 300 gives margin so the constrained walk actually quenches.
If a tighter `fmax` is used, re-calibrate.

## Fabrication-temperature references
The `--temperatures 298,573,623,673,773` series maps to the physical
deposition/annealing temperatures below (source: the b_nestedsampling analysis
`DISCUSSION.md`):

| T (K) | Process | Reference |
|---|---|---|
| ≈298 | Fe/FeCo deposition at room temperature (minimal interdiffusion) | Epitaxial Fe/MgO/Fe(001), 417% TMR at RT — arxiv:2011.08739 |
| ≈573–673 | CoFeB/MgO crystallization annealing | pmc:5304246 |
| ≈623 | Pt-capped CoFeB/MgO max-TMR annealing point | pmc:10534786 |
| ≈673 | High annealing limit (B diffusion / roughening risk) | pmc:5304246 |
| ≈773 | In situ barrier crystallization under O₂ (500 °C) | mdpi:17(10):2424 |
