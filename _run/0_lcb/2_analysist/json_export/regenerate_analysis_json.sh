#!/bin/bash
# Per-structure commands to REGENERATE each analysis_indices PNG AND emit its
# companion JSON (stage1/2/3_*.json) under <outdir>/analysis_json.
# Run each from: /home/think/Desktop/research/_run/0_lcb/2_analysist
# (one command per structure; run individually or all in a loop)
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
echo "# Each emits JSON to <analysis_indices>/analysis_json (default) + redraws the 3 PNGs"

# --- 11_bTa/10_fxg_5b ---
$PY run_analysis_indices.py --dataset "11_bTa/10_fxg_5b" --outdir "11_bTa/10_fxg_5b/analysis_indices" --e-max 0.5

# --- 11_bTa/11_p_Ta10b ---
$PY run_analysis_indices.py --dataset "11_bTa/11_p_Ta10b" --outdir "11_bTa/11_p_Ta10b/analysis_indices" --e-max 0.5

# --- 11_bTa/7_fxg_0b ---
$PY run_analysis_indices.py --dataset "11_bTa/7_fxg_0b" --outdir "11_bTa/7_fxg_0b/analysis_indices" --e-max 0.5

# --- 11_bTa/8_fxg_1b ---
$PY run_analysis_indices.py --dataset "11_bTa/8_fxg_1b" --outdir "11_bTa/8_fxg_1b/analysis_indices" --e-max 0.5

# --- 11_bTa/9_fxg_3b ---
$PY run_analysis_indices.py --dataset "11_bTa/9_fxg_3b" --outdir "11_bTa/9_fxg_3b/analysis_indices" --e-max 0.5

# --- 15_bPt/1_pt0b ---
$PY run_analysis_indices.py --dataset "15_bPt/1_pt0b" --outdir "15_bPt/1_pt0b/analysis_indices" --e-max 0.5

# --- 15_bPt/2_pt1b ---
$PY run_analysis_indices.py --dataset "15_bPt/2_pt1b" --outdir "15_bPt/2_pt1b/analysis_indices" --e-max 0.5

# --- 15_bPt/3_pt3b ---
$PY run_analysis_indices.py --dataset "15_bPt/3_pt3b" --outdir "15_bPt/3_pt3b/analysis_indices" --e-max 0.5

# --- 15_bPt/4_p_pt10b ---
$PY run_analysis_indices.py --dataset "15_bPt/4_p_pt10b" --outdir "15_bPt/4_p_pt10b/analysis_indices" --e-max 0.5

# --- 16_bW/1_w0b ---
$PY run_analysis_indices.py --dataset "16_bW/1_w0b" --outdir "16_bW/1_w0b/analysis_indices" --e-max 0.5

# --- 16_bW/2_w1b ---
$PY run_analysis_indices.py --dataset "16_bW/2_w1b" --outdir "16_bW/2_w1b/analysis_indices" --e-max 0.5

# --- 16_bW/3_w3b ---
$PY run_analysis_indices.py --dataset "16_bW/3_w3b" --outdir "16_bW/3_w3b/analysis_indices" --e-max 0.5

# --- 16_bW/4_p_w10b ---
$PY run_analysis_indices.py --dataset "16_bW/4_p_w10b" --outdir "16_bW/4_p_w10b/analysis_indices" --e-max 0.5

# --- 17_PPt/0_plus5cell/1_3x3_20P ---
$PY run_analysis_indices.py --dataset "17_PPt/0_plus5cell/1_3x3_20P" --outdir "17_PPt/0_plus5cell/1_3x3_20P/analysis_indices" --e-max 0.5

# --- 17_PPt/0_plus5cell/2_3x3_30P ---
$PY run_analysis_indices.py --dataset "17_PPt/0_plus5cell/2_3x3_30P" --outdir "17_PPt/0_plus5cell/2_3x3_30P/analysis_indices" --e-max 0.5

# --- 17_PPt/0_plus5cell/3_3x3_0P ---
$PY run_analysis_indices.py --dataset "17_PPt/0_plus5cell/3_3x3_0P" --outdir "17_PPt/0_plus5cell/3_3x3_0P/analysis_indices" --e-max 0.5

# --- 17_PPt/0_plus5cell/4_3x3_10p ---
$PY run_analysis_indices.py --dataset "17_PPt/0_plus5cell/4_3x3_10p" --outdir "17_PPt/0_plus5cell/4_3x3_10p/analysis_indices" --e-max 0.5

# --- 17_PPt/1_plus0cell/0_0P ---
$PY run_analysis_indices.py --dataset "17_PPt/1_plus0cell/0_0P" --outdir "17_PPt/1_plus0cell/0_0P/analysis_indices" --e-max 0.5

# --- 17_PPt/1_plus0cell/1_10P ---
$PY run_analysis_indices.py --dataset "17_PPt/1_plus0cell/1_10P" --outdir "17_PPt/1_plus0cell/1_10P/analysis_indices" --e-max 0.5

# --- 17_PPt/1_plus0cell/2_20P ---
$PY run_analysis_indices.py --dataset "17_PPt/1_plus0cell/2_20P" --outdir "17_PPt/1_plus0cell/2_20P/analysis_indices" --e-max 0.5

# --- 17_PPt/1_plus0cell/3_30P ---
$PY run_analysis_indices.py --dataset "17_PPt/1_plus0cell/3_30P" --outdir "17_PPt/1_plus0cell/3_30P/analysis_indices" --e-max 0.5

# --- 17_PPt/2_plus3cell/0_0P ---
$PY run_analysis_indices.py --dataset "17_PPt/2_plus3cell/0_0P" --outdir "17_PPt/2_plus3cell/0_0P/analysis_indices" --e-max 0.5

# --- 17_PPt/2_plus3cell/1_10P ---
$PY run_analysis_indices.py --dataset "17_PPt/2_plus3cell/1_10P" --outdir "17_PPt/2_plus3cell/1_10P/analysis_indices" --e-max 0.5

# --- 17_PPt/2_plus3cell/2_20P ---
$PY run_analysis_indices.py --dataset "17_PPt/2_plus3cell/2_20P" --outdir "17_PPt/2_plus3cell/2_20P/analysis_indices" --e-max 0.5

# --- 17_PPt/2_plus3cell/3_30P ---
$PY run_analysis_indices.py --dataset "17_PPt/2_plus3cell/3_30P" --outdir "17_PPt/2_plus3cell/3_30P/analysis_indices" --e-max 0.5

