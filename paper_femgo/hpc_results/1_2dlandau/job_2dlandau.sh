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

# 2D Landau sampling — g(E, dZ) Wang-Landau on a GPR surrogate (no DFT).
# Fully standalone: everything lives in this dir. --use-ray parallelizes the
# GPR training/prediction via AGOX's Ray backend (the WL MC walk is serial).

cd "$(dirname "$0")"

export OMP_NUM_THREADS=1

# Use the gpaw_env interpreter (already activated above) — NOT agox_v2.
python main.py \
    --dataset ./data/femgo \
    --n-e-bins 35 --e-min 0.0 --e-max 0.7 \
    --n-dz-bins 12 --dz-min 0.0 --dz-max 4.5 \
    --relax-steps 100 \
    --reference-steps 5000 \
    --mc-steps 100000 \
    --temperatures 298,573,623,673,773 \
    --output ./output \
    --use-ray \
    --rng 42
