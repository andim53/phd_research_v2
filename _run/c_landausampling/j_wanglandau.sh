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

echo "Wang-Landau density of states on the existing dataset (seed_3..15)."
echo "WL options (--mc-steps / --n-bins / --e-max): see TUTORIAL.md."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset --n-bins 40 --e-max 0.40 --mc-steps 20000000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000 --output ./wl_output_dataset --rng 42

echo "Done."
