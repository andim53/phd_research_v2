# Full-pipeline HPC job (AGOX search -> nested sampling) + env caveats

Captured 2026-08 from the `b_nestedsampling` migration. The current project home is
`/home/think/Desktop/research/_run/b_nestedsampling/` (migrated from
`_run/8_nested_sampling`, which is left intact as the archive source). Its HPC job
script `j_nestedsampling.sh` runs the **whole pipeline in one job**, unlike the old
sampling-only `job.sh`.

## Job shape: search first, then sample

The job runs `dataset/main.py` (the AGOX GPAW search that GENERATES the seed DBs)
before `run_nested_sampling.py` (the GPR nested sampler that consumes them):

```sh
cd ./dataset
OMP_NUM_THREADS=1 python ./main.py          # AGOX search -> dataset/seed_<N>/1_db/db_<N>.db
cd ..
OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
    --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 \
    --perturb-symbols Fe --output ./ns_output_T300_100_1000_0.01 --rng 42
```

Key wiring detail:
- `run_nested_sampling.py` hardcodes `DATASET_DIR = <project>/dataset` and globs
  `seed_*/1_db/db_*.db`. So the search MUST write its DBs into `./dataset` for the
  sampler to find them. The job achieves this by `cd dataset` before `python ./main.py`
  (dataset/main.py writes `seed_<N>/...` relative to cwd, has no CLI, and loops all
  seeds 3..104 in one job).
- `dataset/main.py` uses `SubprocessGPAW(ncores=24)` → the PJM header requests
  **24 cores** (`vnode-core=24 / mpi proc=24`), NOT 64. The sampler is single-process
  after `use_ray=False`, so the DFT search step sets the core count.
- Bare `.sh` style per the standing convention (echo lines only, no comment blocks);
  a literature-parameter note belongs in TUTORIAL.md, not the script.

## Env caveat: gpaw_env vs agox_v2

The HPC job does `conda activate gpaw_env` (standing convention). BUT:
- **Locally there is NO `gpaw_env`** — the available conda envs are
  `agox, agox_v2, flapw-build, pymat_xrd`.
- `agox_v2` has AGOX 3.10.2 + ASE 3.25.0 **and** GPAW → it runs BOTH scripts locally.
- On HPC, `gpaw_env` is the standing env and has AGOX/ASE (it generated the original
  dataset via `dataset/job_5x5_9.sh`).
- If an HPC job fails on AGOX imports, switch the `conda activate` line to `agox_v2`.
  Always check which envs actually exist on the target machine before assuming a job
  env is present (verify with `ls /home/think/miniconda3/envs/`).

## Literature note placement

The user asked for a "literature-scale parameters" note (Pártay 2021 K=500–5000,
Yang 2024 80 walkers/free particle, Chatbipho 2025) alongside the conservative
`--n-live 100 --n-iters 1000` defaults. Per the standing "keep batch scripts bare"
rule, that note goes in **TUTORIAL.md**, not the `.sh`; the script only `echo`s a
pointer to it. The full K/L table already lives in this skill's
`references/supercomputer_and_literature.md`.
