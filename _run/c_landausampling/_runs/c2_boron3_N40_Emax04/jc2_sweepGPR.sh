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

echo "Wang-Landau density of states, B3-doped (dataset_boron3) — GPR-relax sweep."
echo "Params (same for all four runs): --n-bins 100 --e-max 0.40 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe,B; swap move ENABLED (--swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05); --mc-steps 30000 --temperatures 100,200,300,500,1000 --rng 42; start-from-min."
echo "GPR relax sweep: --relax-steps 10 / 30 / 50 / 100 (BFGS steps per trial) -> separate output dirs."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 100 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --relax-steps 10 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_relax10 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 100 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --relax-steps 30 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_relax30 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 100 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --relax-steps 50 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_relax50 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 100 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.20 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --relax-steps 100 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_relax100 --rng 42

echo "Done."
