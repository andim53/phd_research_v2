#!/bin/sh
# Run A — leaf 2_20P: novelty+force filter + DFT re-opt (independent, self-contained).
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has BOTH gpaw and agox — spec M2/G1).
# STANDALONE: inputs (./data/) and outputs (./out_select_reopt/) live in this dir.
# Produces this leaf's single opt_novel_2_20P.traj.
#
#   pjsub job_2_20P.sh

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

LEAF=2_20P
PY=python
OUT=./out_select_reopt
mkdir -p "$OUT"

# Stage 1: novelty + force filter for this leaf (reads ./data/, in-dir).
$PY filter_select.py \
  --outdir "$OUT" \
  --leaves "$LEAF" \
  --n-per-leaf 3 --it-min 10 --e-max 0.5

# Stage 2: DFT re-opt this leaf's selected minima -> opt_novel_2_20P.traj
$PY reopt.py --selroot "$OUT" --outdir "$OUT" --fmax 0.05 --leaf "$LEAF"

echo "Run A complete for leaf $LEAF -> $OUT/opt_novel_${LEAF}.traj"
