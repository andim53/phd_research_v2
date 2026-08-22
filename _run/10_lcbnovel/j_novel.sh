#!/bin/sh
# PJM batch script for the Novelty-LCB Fe/MgO search (project 10_lcbnovel).
# Fujitsu PJM cluster. Submit one job per seed (array) so the search scales out.
#
# Usage:
#   pjsub j_novel.sh            # runs seed from env PJM_... or defaults to 3
#   pjsub -x SEED=5 j_novel.sh  # run a specific seed
#
# NOTE (from run 7): the original script activated `gpaw_env`, but this project
# is written for the `agox_v2` env. Use agox_v2 here.

##PJM -L rscgrp=a-pj24001864
#PJM -L rscgrp=a-batch
#PJM -L vnode-core=64
#PJM --mpi proc=64
#PJM -L elapse=120:00:00
#PJM -j
#PJM -X

source ~/.bashrc
conda activate agox_v2
module load intel
module load impi

# Seed to run (override with pjsub -x SEED=N)
SEED=${SEED:-3}
N_ITERATIONS=${N_ITERATIONS:-100}

echo "Launching Novelty-LCB Fe/MgO search: seed=${SEED}, n_iterations=${N_ITERATIONS}"
OMP_NUM_THREADS=1 python ./main.py --seed "${SEED}" \
    --n-iterations "${N_ITERATIONS}" \
    --out-root ./output

echo "Done seed ${SEED}."
