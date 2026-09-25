#!/bin/bash
# Regenerate the analysis_indices JSONs + PNGs for every leaf that has BOTH an
# analysis_indices dir AND an xrd dir, across the xrd-bearing families 11_bTa,
# 16_bW, 17_PPt (21 leaves). Uses the runner's new DEFAULT continuous probability
# density (integral P dE = 1; no --peak-norm) and --h 0.05 (sharper KDE) at
# --e-max 0.5 eV/atom. One command per leaf, grouped by material family.
# Run from: /home/think/Desktop/research/_run/0_lcb/2_analysist
# Heavy (~1 h for all 21 leaves). To skip a leaf, comment its line out.
set -u
PY=/home/think/miniconda3/envs/agox_v2/bin/python
H=0.05
EMX=0.5
cd /home/think/Desktop/research/_run/0_lcb/2_analysist || exit 1
echo "Regenerating analysis_indices with density default (integral P dE = 1), --h $H, --e-max $EMX"

# ===================== 11_bTa (Ta-B) =====================
"$PY" run_analysis_indices.py --dataset "11_bTa/7_fxg_0b"   --outdir "11_bTa/7_fxg_0b/analysis_indices"   --json-dir "11_bTa/7_fxg_0b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/8_fxg_1b"   --outdir "11_bTa/8_fxg_1b/analysis_indices"   --json-dir "11_bTa/8_fxg_1b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/9_fxg_3b"   --outdir "11_bTa/9_fxg_3b/analysis_indices"   --json-dir "11_bTa/9_fxg_3b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/10_fxg_5b"  --outdir "11_bTa/10_fxg_5b/analysis_indices"  --json-dir "11_bTa/10_fxg_5b/analysis_indices"  --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/11_p_Ta10b" --outdir "11_bTa/11_p_Ta10b/analysis_indices" --json-dir "11_bTa/11_p_Ta10b/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 16_bW (W-B) =====================
"$PY" run_analysis_indices.py --dataset "16_bW/1_w0b"     --outdir "16_bW/1_w0b/analysis_indices"     --json-dir "16_bW/1_w0b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/2_w1b"     --outdir "16_bW/2_w1b/analysis_indices"     --json-dir "16_bW/2_w1b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/3_w3b"     --outdir "16_bW/3_w3b/analysis_indices"     --json-dir "16_bW/3_w3b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/4_p_w10b"  --outdir "16_bW/4_p_w10b/analysis_indices"  --json-dir "16_bW/4_p_w10b/analysis_indices"  --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 0_plus5cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/1_3x3_20P" --outdir "17_PPt/0_plus5cell/1_3x3_20P/analysis_indices" --json-dir "17_PPt/0_plus5cell/1_3x3_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/2_3x3_30P" --outdir "17_PPt/0_plus5cell/2_3x3_30P/analysis_indices" --json-dir "17_PPt/0_plus5cell/2_3x3_30P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/3_3x3_0P"  --outdir "17_PPt/0_plus5cell/3_3x3_0P/analysis_indices"  --json-dir "17_PPt/0_plus5cell/3_3x3_0P/analysis_indices"  --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/4_3x3_10p" --outdir "17_PPt/0_plus5cell/4_3x3_10p/analysis_indices" --json-dir "17_PPt/0_plus5cell/4_3x3_10p/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 1_plus0cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/0_0P" --outdir "17_PPt/1_plus0cell/0_0P/analysis_indices" --json-dir "17_PPt/1_plus0cell/0_0P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/1_10P" --outdir "17_PPt/1_plus0cell/1_10P/analysis_indices" --json-dir "17_PPt/1_plus0cell/1_10P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/2_20P" --outdir "17_PPt/1_plus0cell/2_20P/analysis_indices" --json-dir "17_PPt/1_plus0cell/2_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/3_30P" --outdir "17_PPt/1_plus0cell/3_30P/analysis_indices" --json-dir "17_PPt/1_plus0cell/3_30P/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 2_plus3cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/0_0P" --outdir "17_PPt/2_plus3cell/0_0P/analysis_indices" --json-dir "17_PPt/2_plus3cell/0_0P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/1_10P" --outdir "17_PPt/2_plus3cell/1_10P/analysis_indices" --json-dir "17_PPt/2_plus3cell/1_10P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/2_20P" --outdir "17_PPt/2_plus3cell/2_20P/analysis_indices" --json-dir "17_PPt/2_plus3cell/2_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/3_30P" --outdir "17_PPt/2_plus3cell/3_30P/analysis_indices" --json-dir "17_PPt/2_plus3cell/3_30P/analysis_indices" --e-max "$EMX" --h "$H"

echo "DONE: all 21 leaves regenerated (density default, --h $H, --e-max $EMX)"
