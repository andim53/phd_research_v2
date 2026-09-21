#!/bin/sh
# Run B — FLAPW SHC stage for amorphous Pt(P).
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has gpaw + agox; `pflapw` invoked under this env — spec C2).
# Dispatch (spec M3): ONE submission per leaf traj. Set TRAJ (and OUT) before pjsub.
#   e.g.  export TRAJ=../select_reopt/out_select_reopt/opt_novel_2_20P.traj
#         pjsub job_genkai_mpi.sh
# Repeat for each of the 4 leaves + the 0%-P reference (5 total).
#
# Expects to run FROM hpc_runs/shc/ and needs flapw.py + pflapw reachable (the FLAPW
# executable is copied from CWD into each structure dir by main.py).

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

# Which leaf traj to run (per-leaf, 4 amorphous + 1 reference). Override via env.
TRAJ="${TRAJ:-opt_novel_1_3x3_20P.traj}"
OUT="${OUT:-./shc_out}"

python main.py --traj "$TRAJ" --outdir "$OUT"

echo "Run B complete -> $OUT"
