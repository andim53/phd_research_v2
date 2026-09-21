#!/bin/sh
# Run A — leaf 1_3x3_20P (per-leaf wrapper). Sets LEAF and submits the shared template.
#   pjsub job_1_3x3_20P.sh
export LEAF=1_3x3_20P
exec ./job_genkai_mpi.sh
