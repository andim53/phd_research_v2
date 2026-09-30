# `hpc_runs/2dlandau_ckpt` — standalone HPC runner (checkpoint/resume)

Fully standalone copy of the **2D Wang–Landau** inherent-structure DOS sampler
`g_IS(E, ΔZ)` on the Fe/MgO GPR surrogate (no DFT), based on the current
`codes/2dlandau` including the **crash-resilient checkpoint/resume** feature
(spec `202609271240-wl2d-checkpoint-resume`, v8). Copy this whole dir to an HPC
node and submit `job_2dlandau.sh` — nothing is pulled from the laptop source
tree. Sibling of `hpc_runs/2dlandau` (the older, pre-checkpoint standalone,
kept intact).

## What's inside

```
2dlandau_ckpt/
├── main.py            # CLI (v1.1.0, checkpoint-enabled); DATA_DIR -> ./data/femgo
├── landau_2d/         # package (wang_landau_2d.py v1.2.0 = checkpoint sampler)
├── data/femgo/        # 13 seed DBs (INPUTS, force-committed; output/ ignored)
├── job_2dlandau.sh    # PJM HPC launcher (gpaw_env, --use-ray, checkpoint ON)
├── README.md / LOG.md
└── output/            # results + checkpoints (regenerable, gitignored)
```

## How to run

**HPC** (PJM): `pjsub job_2dlandau.sh` — activates `gpaw_env` (HPC-only env; NOT
`agox_v2`), `cd`s to the script dir, runs `python main.py --dataset ./data/femgo
--use-ray ...`.

Job script flags: 64 cores, elapse 120 h, `--mc-steps 100000`,
`--checkpoint-interval 100`, `--temperatures 298,573,623,673,773`,
`--relax-steps 100`, `--reference-steps 5000`.

## Checkpoint / resume (the point of this copy)

Every `--checkpoint-interval` (=100) MC steps, and on completion, the run writes
into `./output`, atomically (write tmp → rename; `ensemble.traj` **before**
`checkpoint.json` as the commit point):

- `checkpoint.json` — full WL state (`ln_g`, `H`, `accessible`, WL-phase
  counters, `step`, `ensemble_rows`) + a config header (grid, ranges, `n_atoms`,
  `E_ref`, `contact_gap`, dataset path, schema `version`).
- `ensemble.traj` — accepted structures' geometry (ASE trajectory, geometry-only).
- Step-tagged thermodynamic snapshots `g_of_E_dZ.step{N}.*`,
  `delta_z_distribution.step{N}.csv`, `ensemble.step{N}.json`, PNGs — a
  **provisional** convergence trajectory vs step. Canonical *untagged* files at
  completion hold the final result.

If the job is interrupted or hits the 120 h wallclock, **resubmit the same
script**: it auto-detects `output/checkpoint.json`, skips the reference pass +
init, and continues from the saved `step`. `--mc-steps` is an **absolute**
target: `--mc-steps < checkpoint step` → abort (no outputs); `==` → skip
sampling and re-derive outputs; `>` → run only the remaining steps.

**One run per output dir** — do not run two jobs against the same `./output`
concurrently (they race `checkpoint.json`/`ensemble.traj`). To start over on a
dir, delete `output/`'s checkpoint/traj or use a fresh copy.

## Environment split

- **HPC:** `gpaw_env` + `--use-ray` (parallelizes GPR training/prediction).
  `--use-ray` is HPC-only; `gpaw_env` does not exist on the laptop.
- **Local smoke / compile:** `agox_v2`
  (`/home/think/miniconda3/envs/agox_v2/bin/python`), no `--use-ray`.

## Acceptance (local, agox_v2)

```bash
cd paper_femgo/hpc_runs/2dlandau_ckpt
/home/think/miniconda3/envs/agox_v2/bin/python main.py --mc-steps 1 --reference-steps 5
# must load the 13 in-dir DBs (1297 structs), train GPR, write output/g_of_E_dZ.json
```

## Provenance

- Code: `codes/2dlandau` (this copy = checkpoint versions: `main.py` 1.1.0,
  `wang_landau_2d.py` 1.2.0; only `DATA_DIR` rewritten to in-dir).
- Data: `paper_femgo/data/femgo` (the GO/GOFEE run; `seed_*` glob = 13 DBs,
  `stop_16` excluded by the glob by design).
- Spec: `$SPEC_PATH/202609271240-wl2d-checkpoint-resume.md` (v8, approved +
  executed) and `$SPEC_PATH/202609231828-2dlandau-hpc-runs-standalone.md`.
- Algorithm: Wang & Landau 2001; Belardinelli & Pereyra 2007 (1/t); Fort et al.
  2015 (non-Markov WL); Torbrügge & Schnack 2007 (2D g(E,M) + reference
  histogram).
