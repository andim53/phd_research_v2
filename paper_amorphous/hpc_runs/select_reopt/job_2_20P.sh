#!/bin/sh
# Run A — leaf 2_20P (per-leaf wrapper). Sets LEAF and submits the shared template.
#   pjsub job_2_20P.sh
export LEAF=2_20P
exec ./job_genkai_mpi.sh
