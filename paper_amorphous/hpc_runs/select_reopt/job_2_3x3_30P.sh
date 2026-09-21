#!/bin/sh
# Run A — leaf 2_3x3_30P (per-leaf wrapper). Sets LEAF and submits the shared template.
#   pjsub job_2_3x3_30P.sh
export LEAF=2_3x3_30P
exec ./job_genkai_mpi.sh
