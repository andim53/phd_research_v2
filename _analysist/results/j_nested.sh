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

##Batch
##pjsub
##pjstat
##pjdel
##pjshowrsc --rg

##.bashrc
##module load intel
##module load impi
##PATH="$HOME/bin:$HOME/FLAPW/bin:$PATH"

##mpiexec python ./main.py
python ./run_nested_sampling.py --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe --output ./ns_output_T300_100_1000_0.01 --rng 42
