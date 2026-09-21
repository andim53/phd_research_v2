#!/bin/sh
# setup.sh — make select_reopt/ a STANDALONE dir: copy the input AGOX DBs into ./data/.
#
# This dir is self-contained: all inputs (the AGOX DBs under ./data/) and outputs
# (./out_select_reopt/) live inside it — nothing is pulled from outside at run time.
# Run this once to stage the DBs from the repo's data/17_PPt (read-only source).
# Idempotent: existing DBs are kept.
#
# Usage:
#   ./setup.sh
#   # optional: point at a different source root
#   SRC_ROOT=/path/to/data/17_PPt ./setup.sh

set -e
THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$THIS_DIR"
SRC_ROOT="${SRC_ROOT:-../../data/17_PPt}"

# leaf_key -> source leaf dir (relative to SRC_ROOT)
copy_leaf() {
  key="$1"; src="$2"
  for db in "$SRC_ROOT/$src"/seed_*/1_db/db_*.db; do
    [ -e "$db" ] || continue
    seed=$(basename "$(dirname "$(dirname "$db")")")
    mkdir -p "data/$key/$seed/1_db"
    if [ ! -f "data/$key/$seed/1_db/$(basename "$db")" ]; then
      cp "$db" "data/$key/$seed/1_db/"
      echo "  staged $key/$seed/$(basename "$db")"
    else
      echo "  keep existing $key/$seed/$(basename "$db")"
    fi
  done
}

echo "Staging AGOX DBs from $SRC_ROOT into $THIS_DIR/data"
copy_leaf 2_20P      "2_plus3cell/2_20P"
copy_leaf 3_30P      "2_plus3cell/3_30P"
copy_leaf 1_3x3_20P  "0_plus5cell/1_3x3_20P"
copy_leaf 2_3x3_30P  "0_plus5cell/2_3x3_30P"

echo "Done. select_reopt/ is standalone (DBs in ./data/)."
echo "Submit per leaf: cd $THIS_DIR && pjsub job_2_20P.sh (and job_3_30P.sh, job_1_3x3_20P.sh, job_2_3x3_30P.sh)"
