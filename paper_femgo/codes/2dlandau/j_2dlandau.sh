#!/bin/bash
# 2D Landau sampling — g(E, dZ) Wang-Landau on a GPR surrogate (no DFT).
# Heavy production run. pjsub on the HPC (gpaw_env; switch to agox_v2 if the
# AGOX/ASE stack is missing there).

#PJM -L rscgrp=regular
#PJM -L node=1
#PJM -L elapse=24:00:00
#PJM --mpi proc=1
#PJM -j
#PJM -S

cd /home/think/Desktop/research/paper_femgo/2dlandau

source /home/think/miniconda3/etc/profile.d/conda.sh
conda activate gpaw_env

export OMP_NUM_THREADS=1

PY=/home/think/miniconda3/envs/agox_v2/bin/python

$PY main.py \
    --dataset /home/think/Desktop/research/paper_femgo/data/femgo \
    --n-e-bins 35 --e-min 0.0 --e-max 0.7 \
    --n-dz-bins 12 \
    --relax-steps 100 \
    --reference-steps 5000 \
    --mc-steps 100000 \
    --temperatures 100,200,300,500,1000 \
    --output ./output \
    --rng 42
