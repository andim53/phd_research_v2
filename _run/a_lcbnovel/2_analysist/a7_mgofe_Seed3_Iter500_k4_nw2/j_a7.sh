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

SEED=3
N_ITERATIONS=500
KAPPA=4
NOVELTY_WEIGHT=2

echo "Launching Novelty-LCB Fe/MgO search: seed=${SEED}, n_iterations=${N_ITERATIONS}, kappa=${KAPPA}, novelty_weight=${NOVELTY_WEIGHT}"
OMP_NUM_THREADS=1 python ./main.py --seed "${SEED}" \
    --n-iterations "${N_ITERATIONS}" \
    --kappa "${KAPPA}" \
    --novelty-weight "${NOVELTY_WEIGHT}" \
    --out-root ./output

echo "Done seed ${SEED}."
