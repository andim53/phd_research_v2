#!/bin/sh

# Fe-Co-B/MgO — HPC submission for `data/cofe_v2/fecobmgo`.
#
# Provenance: copied from `data/_archive/fecobmgo/job_CoFeB.sh`; the resource request is unchanged
# (vnode-core=16, mpi proc=9, elapse 120 h) and matches `ncores = 16` in ./main.py.  Note the
# boron-free counterpart asks for vnode-core=24 (../fecomgo/job.sh) — that is how the two models
# were allocated originally, and it is kept so as not to change either run's throughput.
#
# Submit from THIS directory:  cd data/cofe_v2/fecobmgo && pjsub job.sh
#   pjstat            job status
#   pjdel <jobid>     cancel
# The run is a plain seed loop over 0..102 (see ./main.py); it exits when the 120 h walltime is
# reached, so keep re-submitting until each model has >= 13 searches at the full 100-iteration
# budget — a search only counts as completed if `run_selection.py` (FULL_ITERATIONS = 100) accepts
# it.  To resume without redoing finished seeds, set the loop's start at the first missing seed.

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
python ./main.py
