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

echo "Wang-Landau density of states, plain Fe/MgO (dataset) — MC-steps sweep."
echo "Params (same for all three runs): --n-bins 40 --e-max 0.40 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000 --rng 42."
echo "Sweep: --mc-steps 10000 / 30000 / 50000 -> separate output dirs."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset --n-bins 40 --e-max 0.40 --mc-steps 10000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000 --output ./wl_output_c1_sweep_10000 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset --n-bins 40 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000 --output ./wl_output_c1_sweep_30000 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset --n-bins 40 --e-max 0.40 --mc-steps 50000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000 --output ./wl_output_c1_sweep_50000 --rng 42

echo "Done."
