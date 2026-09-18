#!/bin/sh

# Fe-B/MgO with the three-generator (permutation) schedule — HPC submission for `data/febmgo_v2`.
#
# Provenance: copied from `data/febmgo/job_b_3.sh`; the resource request is unchanged
# (vnode-core=24, mpi proc=24, elapse 120 h) and matches `ncores = 24` in ./main.py.  NOTE this
# differs from the Co runs, which ask for `mpi proc=9` (data/cofe_v2/*/job.sh) — kept as each model
# was allocated originally so neither run's throughput changes.
#
# Submit from THIS directory:  cd data/febmgo_v2 && pjsub job.sh
#   pjstat            job status
#   pjdel <jobid>     cancel
# The run is a plain seed loop over 0..102 (see ./main.py); it exits when the 120 h walltime is
# reached, so keep re-submitting until the model has >= 13 searches at the full 100-iteration
# budget — a search only counts as completed if `run_selection.py` (FULL_ITERATIONS = 100) accepts
# it.  To resume without redoing finished seeds, set the loop's start at the first missing seed.

#PJM -L rscgrp=a-pj24001864
##PJM -L rscgrp=a-batch
#PJM -L vnode-core=24
#PJM --mpi proc=24
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
