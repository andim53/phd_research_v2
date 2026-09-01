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

echo "Wang-Landau density of states, B3-doped (dataset_boron3)."
echo "Params: --n-bins 40 --e-max 0.40 --mc-steps 20000000 --perturb-symbols Fe,B; swap move ENABLED (--swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05)."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 --mc-steps 20000000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --temperatures 100,200,300,500,1000 --output ./wl_output_c2 --rng 42

echo "Done."
