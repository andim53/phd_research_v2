#!/bin/sh
# Run A — novelty+force filter + DFT re-opt of amorphous Pt-P minima.
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has BOTH gpaw and agox — spec M2/G1).
#
#   pjsub job_genkai_mpi.sh
#
# Expects to be run FROM the hpc_runs/select_reopt/ directory, with the repo path
# to data/17_PPt available at $PPAP_DATA (or the default below).

#PJM -L rscgrp=a-batch
#PJM -L vnode-core=24
#PJM --mpi proc=24
#PJM -L elapse=120:00:00
#PJM -j
#PJM -X

source ~/.bashrc
conda activate gpaw_env
module load intel
module load impi

# Location of the raw Pt-P db leaves (read-only). Override if the HPC copy differs.
PPAP_DATA="${PPAP_DATA:-/home/think/Desktop/research/paper_amorphous/data/17_PPt}"

PY=python
OUT=./out_select_reopt
mkdir -p "$OUT"

# Stage 1: novelty + force filter over the 4 amorphous leaves (per-leaf, 3 minima each)
$PY filter_select.py \
  --outdir "$OUT" \
  --leaves \
    "$PPAP_DATA/2_plus3cell/2_20P:2_20P" \
    "$PPAP_DATA/2_plus3cell/3_30P:3_30P" \
    "$PPAP_DATA/0_plus5cell/1_3x3_20P:1_3x3_20P" \
    "$PPAP_DATA/0_plus5cell/2_3x3_30P:2_3x3_30P" \
  --n-per-leaf 3 --it-min 10 --e-max 0.5

# Stage 2: DFT re-opt the selected minima to strict fmax, write opt_novel_<leaf>.traj x4
$PY reopt.py --selroot "$OUT" --outdir "$OUT" --fmax 0.05

echo "Run A complete."
