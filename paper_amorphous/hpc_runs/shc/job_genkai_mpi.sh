#!/bin/sh
# Run B — FLAPW SHC stage for amorphous Pt(P).
# Submit on HPC via pjsub (NEVER run on the laptop).
# Env: gpaw_env (has gpaw + agox; `pflapw` invoked under this env — spec C2).
# Dispatch (spec M3): ONE submission per leaf traj. Set TRAJ (and OUT) before pjsub.
#   e.g.  export TRAJ=../select_reopt/out_select_reopt/opt_novel_2_20P.traj
#         pjsub job_genkai_mpi.sh
# Repeat for each of the 4 leaves + the 0%-P reference (5 total).
#
# Calc dir is SELF-CONTAINED: flapw.py + README_MT-default + pflapw + opt/ all live
# in this dir (flapw.py is a standalone .py read from CWD, NOT a pip package; pflapw
# and opt/xoptics are staged by ./setup_calc.sh — never commit the big binaries).

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

# Which leaf traj to run (per-leaf, 4 amorphous + 1 reference). Override via env.
TRAJ="${TRAJ:-opt_novel_1_3x3_20P.traj}"
OUT="${OUT:-./shc_out}"

python main.py --traj "$TRAJ" --outdir "$OUT"

echo "Run B complete -> $OUT"
