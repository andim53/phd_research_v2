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

echo "Nested sampling, plain Fe/MgO (no B), temperature-free, --e-max-per-atom 0.25."
echo "Params (--n-live / --n-iters / --temperatures): see TUTORIAL.md."

OMP_NUM_THREADS=1 python ./main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --perturb-symbols Fe \
    --e-max-per-atom 0.25 \
    --output ./ns_output_tfree_emax025 --rng 42

echo "Done."
