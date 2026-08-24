#!/bin/sh
# PJM batch script for the kappa x novelty_weight sweep benchmark
# (Novelty-LCB auto global-minimum window, Ni8/Au(4,4,2) EMT).
# Submit:  pjsub j_benchmark_sweep.sh |  monitor: pjstat  |  cancel: pjdel

##PJM -L rscgrp=a-pj24001864
#PJM -L rscgrp=a-batch
#PJM -L vnode-core=64
#PJM --mpi proc=64
#PJM -L elapse=02:00:00
#PJM -j
#PJM -X

source ~/.bashrc
conda activate gpaw_env
module load intel
module load impi

# NOTE: this benchmark uses EMT + AGOX (no GPAW). It assumes the active conda
# env has AGOX/ASE/EMT installed. gpaw_env is used to match j_novel.sh /
# j_benchmark.sh; if it lacks AGOX, switch to agox_v2.

echo "Launching kappa x novelty_weight sweep (Novelty-LCB auto global-min)"
echo "Date: $(date)"
OMP_NUM_THREADS=1 python ./main_benchmark_sweep.py

echo "Sweep done: $(date)"
