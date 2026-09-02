#!/bin/bash
# Collect EVERY plotted-data JSON (stage1/2/3_*.json from analysis_indices, and
# xrd_plots.json from xrd_out) into this json_export/ staging dir, preserving the
# family/leaf path. Run from: /home/think/Desktop/research/_run/0_lcb/2_analysist
# (Run AFTER the regenerate_*_json.sh commands have produced the JSONs.)
set -u
BASE="/home/think/Desktop/research/_run/0_lcb/2_analysist"
DEST="/home/think/Desktop/research/_run/0_lcb/2_analysist/json_export"
cd "$BASE" || exit 1
mkdir -p "$DEST"
echo "Collecting analysis_indices stage JSONs ..."
find "$BASE" -path '*/analysis_indices/analysis_json/stage*.json' -type f | while read -r f; do
    rel=${f#"$BASE"/}
    mkdir -p "$DEST/$(dirname "$rel")"
    cp "$f" "$DEST/$rel"
    echo "  $rel"
done
echo "Collecting xrd_out JSONs (xrd_plots.json + manifest.json) ..."
find "$BASE" -path '*/xrd_out/*.json' -type f | while read -r f; do
    rel=${f#"$BASE"/}
    mkdir -p "$DEST/$(dirname "$rel")"
    cp "$f" "$DEST/$rel"
    echo "  $rel"
done
echo
echo "Collected JSON count: $(find "$DEST" -name '*.json' -type f | wc -l)"
echo "Staged under: $DEST"
