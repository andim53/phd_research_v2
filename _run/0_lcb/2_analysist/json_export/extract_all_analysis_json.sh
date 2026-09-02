#!/bin/bash
# Extract (generate) the JSON data for ALL analysis_indices dirs in 2_analysist.
# For every <leaf>/analysis_indices dir, runs run_analysis_indices.py with
# --json-dir set to that same dir, so each leaf writes its 3 stage JSONs
# (stage1_progression.json, stage2_landscape.json, stage3_probability.json)
# DIRECTLY inside its own analysis_indices/ (multiple files per leaf, no
# central staging). PNGs are redrawn in the same run.
# Run from: /home/think/Desktop/research/_run/0_lcb/2_analysist
# Heavy (~1 h for all 25 leaves). Editable: EMX=0.5 eV/atom energy cap.
set -u
PY=/home/think/miniconda3/envs/agox_v2/bin/python
EMX=0.5
cd /home/think/Desktop/research/_run/0_lcb/2_analysist || exit 1

n=0
while IFS= read -r outdir; do
    [ -n "$outdir" ] || continue
    dataset=$(dirname "$outdir")          # the leaf dir holding seed_*/1_db
    n=$((n+1))
    echo "=== [$n] dataset=$dataset  outdir=$outdir ==="
    "$PY" run_analysis_indices.py --dataset "$dataset" --outdir "$outdir" \
        --json-dir "$outdir" --e-max "$EMX"
done < <(find . -type d -name analysis_indices | sort)

echo "DONE: processed $n analysis_indices dirs"
