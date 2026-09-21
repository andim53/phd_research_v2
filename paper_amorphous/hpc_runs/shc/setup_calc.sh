#!/bin/sh
# setup_calc.sh — make hpc_runs/shc/ a fully STANDALONE FLAPW calc directory.
#
# The shc/ dir is self-contained: it holds everything needed to run the SHC stage on
# the HPC as its own independent directory — the FLAPW calc files (flapw.py,
# README_MT-default, pflapw, opt/) AND the traj inputs (opt_novel_<leaf>.traj x4,
# ref_0P_gmin.traj). Copy the whole shc/ dir to the HPC node and run it there.
#
# What this script does:
#   1. Verifies the committed FLAPW calc files are present (flapw.py,
#      README_MT-default, pflapw, opt/opticsin, opt/xoptics). pflapw and opt/xoptics
#      are committed binaries (standalone on any clone/copy).
#   2. Stages the traj inputs into shc/ from the Run A output dir (select_reopt) so
#      the dir has the actual structures to run. If a traj is already present, it is
#      kept (idempotent).
#
# Usage (run once, before copying shc/ to HPC):
#   ./setup_calc.sh
#   # optional: point at a different Run A output dir
#   RUN_A_OUT=../select_reopt/out_select_reopt ./setup_calc.sh
#
# Then on the HPC node, from the copied shc/ dir:
#   for t in opt_novel_2_20P.traj opt_novel_3_30P.traj opt_novel_1_3x3_20P.traj \
#            opt_novel_2_3x3_30P.traj ref_0P_gmin.traj; do
#     TRAJ=$t pjsub job_genkai_mpi.sh
#   done

set -e
THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$THIS_DIR"

# --- 1. Verify committed FLAPW calc files -------------------------------------
MISSING=""
for f in flapw.py README_MT-default pflapw opt/opticsin opt/xoptics; do
  if [ ! -f "$f" ]; then
    MISSING="$MISSING $f"
  fi
done
if [ -n "$MISSING" ]; then
  echo "ERROR: FLAPW calc files missing in $THIS_DIR:$MISSING" >&2
  echo "  pflapw and opt/xoptics are committed binaries — re-clone/copy the repo." >&2
  exit 1
fi
echo "OK: FLAPW calc files present (flapw.py, README_MT-default, pflapw, opt/)."

# --- 2. Stage traj inputs into shc/ -------------------------------------------
RUN_A_OUT="${RUN_A_OUT:-../select_reopt/out_select_reopt}"
TRAJS="opt_novel_2_20P.traj opt_novel_3_30P.traj opt_novel_1_3x3_20P.traj \
       opt_novel_2_3x3_30P.traj ref_0P_gmin.traj"

for t in $TRAJS; do
  if [ -f "$t" ]; then
    echo "  keep existing $t"
    continue
  fi
  if [ -f "$RUN_A_OUT/$t" ]; then
    cp "$RUN_A_OUT/$t" "$THIS_DIR/$t"
    echo "  staged $t from $RUN_A_OUT"
  else
    echo "  WARN: $t not found in $RUN_A_OUT (generate via reopt.py / make_ref_traj.py)"
  fi
done

echo "Done. shc/ is standalone: FLAPW calc files + traj inputs present."
echo "Copy this dir to the HPC node, then: TRAJ=<leaf.traj> pjsub job_genkai_mpi.sh"
