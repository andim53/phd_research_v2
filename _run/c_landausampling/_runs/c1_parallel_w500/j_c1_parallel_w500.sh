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

echo "Wang-Landau density of states, plain Fe/MgO (dataset) — Mode A parallel walkers."
echo "Params: --n-bins 100 --e-max 0.40 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe --relax-steps 100 --temperatures 100,200,300,500,1000 --start-from-min --rng 42."
echo "Parallel (Mode A): --n-walkers 500, all walkers share one H/ln_g via Ray actors."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset --n-bins 100 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe --relax-steps 100 --temperatures 100,200,300,500,1000 --start-from-min --n-walkers 500 --output ./wl_output_c1_parallel_w500 --rng 42

echo "Done."