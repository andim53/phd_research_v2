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

echo "Nested sampling, plain Fe/MgO (no B), temperature-free."
echo "Params: --e-max-per-atom 0.4; window [0.3,0.35]; --walk (steps 50, small 0.05, large 0.40, mode both); --walk-exclude-worst; --no-posterior-xsf; --novelty-threshold 1.0."

OMP_NUM_THREADS=1 python ./main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --perturb-symbols Fe \
    --e-max-per-atom 0.4 \
    --e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000 \
    --walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both \
    --walk-exclude-worst \
    --no-posterior-xsf \
    --novelty-threshold 1.0 --novelty-max-attempts 500 \
    --output ./ns_output_tfree_walk_emax04_exclworst_noxsf_novelty --rng 42

echo "Done."
