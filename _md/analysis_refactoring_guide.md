# Simulation Analysis Code Refactoring Guide

## 1. Executive Summary & Problem Diagnosis

The analysis repository located at `/home/think/Desktop/research/_analysist/codes/` contains over 50 individual Python scripts. Many of these scripts represent iterative notebook conversions or incremental variations (e.g., scripts numbered 58-60 for energy progression, 73-76 for probability plotting, 80-82 for mathematical ratios, and 32-34 for DOS reference finding). 

This proliferation of files causes:
- High code duplication and maintenance overhead.
- Magic numbers and hardcoded parameters across duplicated scripts.
- Difficulty in running end-to-end analysis pipelines cleanly.

This guide outlines a step-by-step procedure to eliminate duplication, consolidate scripts into a modular library, and provide a single unified runner program (`run_analysis.py`).

---

## 2. Step-by-Step Refactoring Strategy

### Step 1: Categorize and Group Duplicated Scripts
Identify functional domains across the codebase:
1. **Potential Energy Surface (PES) & Landscape Generation** (`90_pes.py`, `05_landscape...`, `71_conf_space.py`)
2. **Density of States (DOS) & Electronic Structure** (`52_dos.py`, `32_find_ref_for_dos.py`, etc.)
3. **Energy Progression & Trajectory Tracking** (`58_energy_progression.py`, `59_energy_progression.py`, `60_energy_progression.py`)
4. **Structural Sampling & Clustering (KMeans / PCA)** (`54_kmeans.py`, `62_pca.py`)

### Step 2: Extract Core Logic into Reusable Functions
Replace hardcoded scripts with parameterized functions taking configurations (e.g., input directories, complexity factors, seed mappings, plot types).

### Step 3: Implement a Unified CLI Runner (`run_analysis.py`)
Combine all main analysis components into a single command-line tool with subcommands or flags:
- `--mode pes`: Generates potential energy surface and probability density landscapes.
- `--mode dos`: Plots and compares electronic density of states (PDOS).
- `--mode energy`: Analyzes energy progression across simulation iterations.
- `--mode pca`: Performs dimensionality reduction and clustering on structural descriptors.

---

## 3. Unified Analysis Program (`run_analysis.py`)

The unified program resides at `/home/think/Desktop/research/_analysist/run_analysis.py`. It consolidates the core analysis modules into a single execution entry point.

### Usage Examples:
```bash
cd /home/think/Desktop/research/_analysist
python run_analysis.py --mode pes
python run_analysis.py --mode dos --plot-type overlay
python run_analysis.py --mode energy
python run_analysis.py --mode pca
```

---

## 4. Verification & Maintenance
- Ensure required packages (`numpy`, `pandas`, `matplotlib`, `scipy`, `ase`) are installed.
- Verify generated plots in `0_analy/` output directories.
- Update Hermes skills (`simulation-analysis`) whenever refactored pipelines or new analysis modules are added.
