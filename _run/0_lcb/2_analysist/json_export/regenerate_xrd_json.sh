#!/bin/bash
# Per-structure commands to REGENERATE each xrd_out PNG AND emit xrd_plots.json
# Run each from: /home/think/Desktop/research/_run/0_lcb/2_analysist (pymat_xrd env)
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# --- 11_bTa/10_fxg_5b/xrd_out ---
$PY_X scripts/xrd_simulate_crystallinity.py --manifest "11_bTa/10_fxg_5b/xrd_out/manifest.json" --outdir "11_bTa/10_fxg_5b/xrd_out" --json

# --- 11_bTa/11_p_Ta10b/xrd_out ---
$PY_X scripts/xrd_simulate_crystallinity.py --manifest "11_bTa/11_p_Ta10b/xrd_out/manifest.json" --outdir "11_bTa/11_p_Ta10b/xrd_out" --json

# --- 11_bTa/7_fxg_0b/xrd_out ---
$PY_X scripts/xrd_simulate_crystallinity.py --manifest "11_bTa/7_fxg_0b/xrd_out/manifest.json" --outdir "11_bTa/7_fxg_0b/xrd_out" --json

# --- 11_bTa/8_fxg_1b/xrd_out ---
$PY_X scripts/xrd_simulate_crystallinity.py --manifest "11_bTa/8_fxg_1b/xrd_out/manifest.json" --outdir "11_bTa/8_fxg_1b/xrd_out" --json

# --- 11_bTa/9_fxg_3b/xrd_out ---
$PY_X scripts/xrd_simulate_crystallinity.py --manifest "11_bTa/9_fxg_3b/xrd_out/manifest.json" --outdir "11_bTa/9_fxg_3b/xrd_out" --json

