#!/bin/sh
# Run A — novelty+force filter + DFT re-opt of amorphous Pt-P minima.
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has BOTH gpaw and agox — spec M2/G1).
#
# STANDALONE: this dir is self-contained. All inputs (the AGOX DBs under ./data/)
# and outputs (./out_select_reopt/) live inside this directory — nothing is pulled
# from outside. Copy the whole select_reopt/ dir to the HPC node and run it there.
#
#   pjsub job_genkai_mpi.sh

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

PY=python
OUT=./out_select_reopt
mkdir -p "$OUT"

# Stage 1: novelty + force filter over the 4 amorphous leaves (per-leaf, 3 minima each).
# Reads the DBs from ./data/ (in-dir, standalone).
$PY filter_select.py \
  --outdir "$OUT" \
  --leaves 2_20P 3_30P 1_3x3_20P 2_3x3_30P \
  --n-per-leaf 3 --it-min 10 --e-max 0.5

# Stage 2: DFT re-opt the selected minima to strict fmax, write opt_novel_<leaf>.traj x4
$PY reopt.py --selroot "$OUT" --outdir "$OUT" --fmax 0.05

echo "Run A complete."
