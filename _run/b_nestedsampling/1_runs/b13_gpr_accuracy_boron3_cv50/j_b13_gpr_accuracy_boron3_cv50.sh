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

echo "GPR accuracy, 50-fold CV, bin-width 0.1 (Fe_z system), boron3 (B3Fe25Mg25O25) dataset."
echo "Params (--cv-folds / --bin-width / --e-max-per-atom): see TUTORIAL.md."

OMP_NUM_THREADS=1 python ./gpr_accuracy.py \
    --cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 \
    --e-max-per-atom 0.67 \
    --output ./out_fez

echo "Done."
