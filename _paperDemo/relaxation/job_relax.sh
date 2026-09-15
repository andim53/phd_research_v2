#!/bin/sh
# PJM job file for DFT re-relaxation of the selected distinct structures.
# Submit from anywhere:  pjsub relaxation/job_relax.sh
#
#PJM -L rscgrp=a-pj24001864
#PJM -L vnode-core=24
#PJM --mpi proc=24
#PJM -L elapse=120:00:00
#PJM -j
#PJM -X

source ~/.bashrc
conda activate gpaw_env
module load intel
module load impi

# work from the project root (this file lives in relaxation/)
cd "$(dirname "$0")/.."

# GPAW parallel over MPI (24 procs); relax to fmax = 0.05 eV/A
mpiexec -n 24 gpaw python relaxation/relax.py \
    --manifest relaxation/selected/manifest.csv \
    --outdir relaxation/relaxed \
    --fmax 0.05 \
    --max-steps 300

# --- serial fallback (uncomment if MPI unavailable) ---
# python relaxation/relax.py --manifest relaxation/selected/manifest.csv --fmax 0.05
