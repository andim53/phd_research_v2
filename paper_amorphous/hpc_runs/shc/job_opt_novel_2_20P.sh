#!/bin/sh
# Run B — FLAPW SHC for traj opt_novel_2_20P.traj (independent, self-contained).
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has gpaw + agox; `pflapw` invoked under this env — spec C2).
# STANDALONE: FLAPW calc files + this traj live in this dir.
# Produces SHC for every structure in this traj -> ./shc_out.
#
#   pjsub job_opt_novel_2_20P.sh

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

# Stage the FLAPW calc dir (flapw.py, README_MT-default, pflapw, opt/).
./setup_calc.sh

TRAJ=opt_novel_2_20P.traj
OUT=./shc_out

python main.py --traj "$TRAJ" --outdir "$OUT"

echo "Run B complete for $TRAJ -> $OUT"
