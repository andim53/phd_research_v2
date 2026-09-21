#!/bin/sh
# Run A — leaf 3_30P (per-leaf wrapper). Sets LEAF and submits the shared template.
#   pjsub job_3_30P.sh
export LEAF=3_30P
exec ./job_genkai_mpi.sh
