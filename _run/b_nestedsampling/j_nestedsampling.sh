#!/bin/sh

##PJM -L rscgrp=a-pj24001864
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

echo "Nested sampling on the existing dataset (seed_3..15)."
echo "NS options (--n-live / --n-iters): see TUTORIAL.md."

OMP_NUM_THREADS=1 python ./main.py --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe --output ./ns_output_T300_100_1000_0.01 --rng 42

echo "Done."
