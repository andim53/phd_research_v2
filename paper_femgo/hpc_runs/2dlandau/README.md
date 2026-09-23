# hpc_runs/2dlandau — standalone 2D Wang–Landau production runner

Fully standalone HPC runner for the 2D Wang–Landau simulation of the Fe/MgO
flat↔island transition (inherent-structure `g(E, ΔZ)` on a GPR surrogate, no
DFT). **Nothing runs on the laptop** — submit via `pjsub` on the HPC node.

## STANDALONE RULE
**This directory is a fully standalone system.** All inputs and necessities live
inside the dir — nothing is pulled from outside at run time. To run on the HPC,
copy the whole dir to the node and submit there independently.

## Layout
```
2dlandau/
├── main.py            # CLI: load 13 seed DBs -> train GPR -> 2D WL -> reweight -> save
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
  cd hpc_runs/2dlandau
  /home/think/miniconda3/envs/agox_v2/bin/python main.py --mc-steps 1
  ```
  must load the 13 in-dir DBs, train the GPR, and write `output/g_of_E_dZ.json`.

## Units / parameters
Production params (unchanged from `paper_femgo/2dlandau/j_2dlandau.sh`):
E bins 35 over [0, 0.7] eV/atom; ΔZ bins 12 over [0, 4.5] Å; relax 100 BFGS
steps; reference pass 5000; MC 100000 steps; temperatures 100–1000 K.
