#!/bin/sh
##PJM -L rscgrp=a-pj24001864
#PJM -L rscgrp=a-batch
#PJM -L vnode-core=64
#PJM --mpi proc=64
#PJM -L elapse=120:00:00
#PJM -j
#PJM -X

source ~/.bashrc
conda activate gpaw_env
module load intel
module load impi

# 2D Landau sampling with CHECKPOINT/RESUME — g(E, dZ) Wang-Landau on a GPR
# surrogate (no DFT). Fully standalone: everything lives in this dir.
# Every --checkpoint-interval steps it writes output/checkpoint.json +
# output/ensemble.traj + step-tagged thermodynamic snapshots. If this job is
# interrupted or hits the 120 h wallclock, RESUBMIT THE SAME SCRIPT and it
# auto-resumes from the last checkpoint (--mc-steps is an absolute target; only
# the remaining steps run). Use a fresh/copied dir to start over.
#
# --use-ray parallelizes GPR training/prediction via AGOX's Ray backend (the WL
# MC walk is serial). Temperatures = physical deposition/annealing series.

cd "$(dirname "$0")"

export OMP_NUM_THREADS=1

# Use the gpaw_env interpreter (already activated above) — NOT agox_v2.
python main.py \
    --dataset ./data/femgo \
    --n-e-bins 35 --e-min 0.0 --e-max 0.7 \
    --n-dz-bins 12 \
    --relax-steps 100 \
    --reference-steps 5000 \
    --mc-steps 100000 \
    --checkpoint-interval 100 \
    --temperatures 298,573,623,673,773 \
    --output ./output \
    --use-ray \
    --rng 42
