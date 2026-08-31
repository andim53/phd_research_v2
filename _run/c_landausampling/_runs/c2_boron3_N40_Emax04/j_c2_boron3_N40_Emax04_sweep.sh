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

echo "Wang-Landau density of states, B3-doped (dataset_boron3) — MC-steps sweep."
echo "Params (same for all three runs): --n-bins 40 --e-max 0.40 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B; swap move ENABLED (--swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05); --temperatures 100,200,300,500,1000 --rng 42; start-from-min (v1.2.0 init fix)."
echo "Sweep: --mc-steps 10000 / 30000 / 50000 -> separate output dirs."

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 --mc-steps 10000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_sweep_10000 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 --mc-steps 30000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_sweep_30000 --rng 42

OMP_NUM_THREADS=1 python ./main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 --mc-steps 50000 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --temperatures 100,200,300,500,1000 --start-from-min --output ./wl_output_c2_sweep_50000 --rng 42

echo "Done."
