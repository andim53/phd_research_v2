---
name: simulation-analysis
description: Use when performing AGOX simulation and database analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [analysis, agox, simulation, research, python]
    related_skills: [arxiv, grounded-citations]
---

# AGOX Simulation Analysis Pipeline

## Overview

This skill provides procedures for running simulation analysis scripts located in `/home/think/Desktop/research/_analysist/codes`. These scripts were converted from `main_analyst.ipynb` and handle database processing, structural sampling, landscape generation (PES), Kernel Density Estimation (KDE), Principal Component Analysis (PCA), Density of States (DOS), energy progression, and multi-trajectory evaluation for AGOX atomistic simulations.

## When to Use

- When the user asks to perform analysis on simulation databases (`.db` files) in `1_result/`.
- When running specific analysis steps (database inspection, structural clustering, sampling, PES landscape plotting, energy distributions).
- When executing individual python scripts from `/home/think/Desktop/research/_analysist/codes/`.

## Unified Analysis Runner & Refactoring

To address code duplication across the numerous incremental scripts in `codes/`, a unified runner program has been introduced at `/home/think/Desktop/research/_analysist/run_analysis.py`, along with a comprehensive step-by-step refactoring guide saved at `/home/think/Desktop/research/_md/analysis_refactoring_guide.md`.

### Executing the Unified Program

Instead of running individual duplicated scripts, use the unified runner:
```bash
cd /home/think/Desktop/research/_analysist
python run_analysis.py --mode pes
python run_analysis.py --mode dos --plot-type overlay
python run_analysis.py --mode energy
python run_analysis.py --mode pca
python run_analysis.py --mode all
```

## Multi-Index Analysis Runner (indices 22–36, 67–69)

For computing and plotting data across the requested simulation index groups, use the
consolidated runner `run_analysis_indices.py` at `/home/think/Desktop/research/_analysist/`.
It chains, per index: (1) plotting style from `codes/07_plotting_style_and_label_configuration.py`,
(2) the database processing loop (`codes/12_database_processing_loop.py` → `scripts/process_database.py`),
(3) landscape analysis & evaluation (`codes/14_landscape_analysis_and_evaluation_script.py` → `scripts/plot_structure_landscape.py`),
and (4) the plot-probability statistical-mechanics analysis (`codes/76_plot_probability.py`).

**Environment (critical):** the base `python3` lacks ASE/AGOX. Always run with the
`agox_v2` conda env (ASE 3.25.0, AGOX 3.10.2, pandas, scipy, matplotlib):
```bash
cd /home/think/Desktop/research/_analysist
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices latt_sweep_1,fe_concentration,latt_on_mgo,ml_rattle
# or individual indices / groups:
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices 22,67,69
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices 33 --skip-probability
```
Groups: `latt_sweep_1`=[22..26], `fe_concentration`=[27..31], `latt_on_mgo`=[32..36], `ml_rattle`=[67,68,69].
Outputs land in `0_analy/idx_<N>/` (trajectories, XSFs, `data_<N>.csv`, `progression_seed_split_<N>.png`, `conf_space.png`, `binding_probability_vs_temperature.png`).
Note: `32_dos` has no DB (precomputed DOS only) and is correctly skipped; single-frame DBs skip the KDE probability stage.

## Script Directory Structure

All executable analysis scripts reside at:
`/home/think/Desktop/research/_analysist/codes/`

Key script groups:
1. **Database & Processing:**
   - `03_database_inspection_script.py` - Inspects AGOX databases within iteration bounds.
   - `10_directory_and_dataset_configuration.py` - Sets up output directories and dataset paths.
   - `12_database_processing_loop.py` & `87_database.py` - Processes simulation databases, extracts trajectories and XSF files, plots progress.
2. **Sampling & Clustering:**
   - `01_structural_sampling_error.py` - Structural sampling using KMeans and energy filtering.
   - `54_kmeans.py` - KMeans descriptor clustering.
3. **Landscape & DOS & PCA:**
   - `05_landscape_generation_and_density_plotter.py` - Rugged Potential Energy Surface (PES) and DOS KDE side-by-side plots.
   - `14_landscape_analysis_and_evaluation_script.py` - PCA on structural fingerprints and landscape visualization.
   - `52_dos.py`, `90_pes.py`, `92_probability_density.py` - Density of states and probability analysis.
4. **Energy & Height Analysis:**
   - `58_energy_progression.py`, `59_energy_progression.py`, `60_energy_progression.py` - Energy progression across iterations.
   - `38_height_density.py`, `64_make_graph_of_height.py` - Height span and Z-position density analysis.

## Execution Procedure

1. **Navigate to working directory or execute directly using absolute paths:**
   ```bash
   cd /home/think/Desktop/research/_analysist
   python codes/<script_name>.py
   ```
2. **Verify Environment and Dependencies:**
   - Ensure ASE (Atomic Simulation Environment) and AGOX are installed and active in the Python environment.
   - Ensure paths to database files (e.g., `1_result/.../db_0.db`) are correctly configured in the target script before execution.
3. **Review Output Artifacts:**
   - Check generated files in `0_analy/` or current working directory (`.png`, `.xsf`, `.traj`, etc.).

## Common Pitfalls

- **Incorrect relative paths inside scripts:** Some scripts expect to be run from `/home/think/Desktop/research/_analysist` or reference `1_result/` relative to the working directory. Always execute Python scripts with the working directory set to `/home/think/Desktop/research/_analysist`.
- **Missing database files:** Ensure target AGOX database paths exist before running inspection or processing scripts.

## Verification Checklist

- [ ] Working directory set to `/home/think/Desktop/research/_analysist`
- [ ] Required Python environment (ASE, AGOX, numpy, matplotlib, scipy) active
- [ ] Target `.py` script executed successfully from `codes/`
- [ ] Output plots (`.png`) or data files verified in output directories
