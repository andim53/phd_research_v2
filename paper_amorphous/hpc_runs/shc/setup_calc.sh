#!/bin/sh
# setup_calc.sh — stage the HPC FLAPW calc directory for Run B (shc/).
#
# The FLAPW calc directory is SELF-CONTAINED: it must contain, in this dir,
#   flapw.py          (the ASE FLAPW calculator — a standalone .py, NOT a package;
#                      `from flapw import FLAPW` resolves because flapw.py sits in the
#                      CWD where main.py runs)
#   README_MT-default (read by flapw.py write_lapwin from CWD)
#   pflapw            (the FLAPW SCF/SOC binary, run as ./pflapw — large HPC build)
#   opt/              (xoptics binary + opticsin, read by prepare_optics)
# The small source/config files (flapw.py, README_MT-default, opt/opticsin) are
# committed. The large HPC binaries (pflapw, opt/xoptics) are gitignored and staged
# here from the FLAPW calc source before submit (they are HPC-built artifacts, not
# committed in git).
#
# Usage (on the HPC node / after copying this project up):
#   export FLAPW_CALC_SRC="/home/think/Desktop/research/paper_amorphous/tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW"
#   ./setup_calc.sh
#   # then for each leaf:  TRAJ=... pjsub job_genkai_mpi.sh
#
# If FLAPW_CALC_SRC is unset, falls back to the standard repo tmp path.

set -e
THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
FLAPW_CALC_SRC="${FLAPW_CALC_SRC:-/home/think/Desktop/research/paper_amorphous/tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW}"

if [ ! -f "$FLAPW_CALC_SRC/pflapw" ]; then
  echo "ERROR: FLAPW calc source not found at $FLAPW_CALC_SRC (set FLAPW_CALC_SRC)" >&2
  exit 1
fi

echo "Staging FLAPW calc dir from $FLAPW_CALC_SRC into $THIS_DIR"
cp "$FLAPW_CALC_SRC/pflapw"        "$THIS_DIR/pflapw"
cp "$FLAPW_CALC_SRC/README_MT-default" "$THIS_DIR/README_MT-default"
cp "$FLAPW_CALC_SRC/flapw.py"      "$THIS_DIR/flapw.py"
mkdir -p "$THIS_DIR/opt"
cp "$FLAPW_CALC_SRC/opt/opticsin"  "$THIS_DIR/opt/opticsin"
cp "$FLAPW_CALC_SRC/opt/xoptics"   "$THIS_DIR/opt/xoptics"
chmod +x "$THIS_DIR/pflapw" "$THIS_DIR/opt/xoptics"
echo "Done. pflapw + opt/xoptics staged; python files present."
echo "Submit: cd $THIS_DIR && TRAJ=<leaf.traj> pjsub job_genkai_mpi.sh"
