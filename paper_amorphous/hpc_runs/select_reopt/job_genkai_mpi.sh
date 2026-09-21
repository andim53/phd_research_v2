#!/bin/sh
# Run A — novelty+force filter + DFT re-opt of amorphous Pt-P minima.
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has BOTH gpaw and agox — spec M2/G1).
#
# STANDALONE: this dir is self-contained. All inputs (the AGOX DBs under ./data/)
# and outputs (./out_select_reopt/) live inside this directory — nothing is pulled
# from outside. Copy the whole select_reopt/ dir to the HPC node and run it there.
#
# PER-LEAF DISPATCH (spec select-reopt-per-leaf): ONE leaf per submission, each
# producing that leaf's single opt_novel_<leaf>.traj. Set LEAF before pjsub, or use
# the per-leaf wrappers (job_<leaf>.sh) which set LEAF for you.
#
#   export LEAF=2_20P
#   pjsub job_genkai_mpi.sh
#   # or: pjsub job_2_20P.sh   (wrapper sets LEAF=2_20P)
# Repeat for each of the 4 leaves (2_20P, 3_30P, 1_3x3_20P, 2_3x3_30P).

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

# Which leaf to process (one per submission). Override via env.
LEAF="${LEAF:?set LEAF to one of: 2_20P 3_30P 1_3x3_20P 2_3x3_30P}"

PY=python
OUT=./out_select_reopt
mkdir -p "$OUT"

# Stage 1: novelty + force filter for THIS leaf only (reads ./data/, in-dir).
$PY filter_select.py \
  --outdir "$OUT" \
  --leaves "$LEAF" \
  --n-per-leaf 3 --it-min 10 --e-max 0.5

# Stage 2: DFT re-opt THIS leaf's selected minima -> opt_novel_<leaf>.traj
$PY reopt.py --selroot "$OUT" --outdir "$OUT" --fmax 0.05 --leaf "$LEAF"

echo "Run A complete for leaf $LEAF -> $OUT/opt_novel_${LEAF}.traj"
