# AGOX Simulation Analysis — Step-by-Step Guide (Indices 22–36, 67–69)

Calyx — generated for the `_analysist` pipeline. This guide explains how to compute and
plot data for the requested simulation indices using the project's existing analysis
code (plotting style `07`, database processing loop `12`, landscape analysis `14`, and
plot-probability `76`), consolidated into a single runner.

## 0. Targets

| Group | Indices | Source folders |
|-------|---------|----------------|
| Lattice sweep (1) | 22, 23, 24, 25, 26 | `22_latt_0` … `26_latt_100` |
| Fe concentration | 27, 28, 29, 30, 31 | `27_fe_con0` … `31_fe_con20` |
| Lattice on MgO | 32, 33, 34, 35, 36 | `32_dos`, `33_latt_25_mgo` … `36_latt_100_mgo` |
| 2ML / rattle | 67, 68, 69 | `67_2ml`, `68_ratt_min1`, `69_ratt_min05` |

## 1. Environment (IMPORTANT)

The base `python3` does NOT have ASE/AGOX. Use the `agox_v2` conda environment, which
has ASE 3.25.0, AGOX 3.10.2, pandas, scipy, matplotlib already installed:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python --version
```

Activate it (or always call that interpreter directly).

## 2. What the pipeline does (4 stages per index)

The runner `run_analysis_indices.py` (in `_analysist/`) chains four stages:

### Stage 1 — Plotting style (`codes/07_plotting_style_and_label_configuration.py`)
Applies the researcher's fixed `rcParams` (serif font, boxed ticks with visible minor
ticks, linewidth 1.5) and the energy label `E = r'$E_{i}-E_{glob}$ (eV/atom)'`.

### Stage 2 — Database processing loop (`codes/12_database_processing_loop.py`
→ `scripts/process_database.py`)
For each `(dir_path, file_idx)` it:
- Discovers `seed_*` directories, loads each `1_db/db_<n>.db` via AGOX `Database`,
- Filters iterations `>= start_iter` (10),
- Writes a combined trajectory `traj_<idx>.traj/.xsf`,
- Writes per-seed trajectories under `seeds/`,
- Computes relative energy per atom (`calculate_relative_energy`),
- Saves `data_<idx>.csv` and individual XSF frames,
- Plots the best-so-far convergence `progression_seed_split_<idx>.png`.

### Stage 3 — Landscape analysis & evaluation (`codes/14_landscape_analysis_and_evaluation_script.py`
→ `scripts/plot_structure_landscape.py`)
Reads `traj_<idx>.traj`, builds a Fingerprint descriptor, reduces to 1D via PCA
(eigenvector of the covariance matrix), and plots the conformation landscape
(scatter + Gaussian-KDE state-density panel) → `conf_space.png`.

### Stage 4 — Plot probability (`codes/76_plot_probability.py`)
Loads the index's first `.db`, computes binding energies, builds a Gaussian KDE, then
runs the statistical-mechanics loop over temperatures
`[298.15, 348.60, 447.875, 547.15, 646.425] K` using a Boltzmann partition function
(per-atom intensive Gibbs level × `n_fe`). Output: `binding_probability_vs_temperature.png`.

## 3. Run it

From `/home/think/Desktop/research/_analysist`:

```bash
# All 15 indices (4 groups)
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py

# One group
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices latt_sweep_1
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices fe_concentration
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices latt_on_mgo
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices ml_rattle

# Selected indices
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices 22,67,69

# Skip the (slow) probability stage
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --indices 33 --skip-probability
```

## 4. Output layout

All results land under `_analysist/0_analy/idx_<N>/`:

```
0_analy/idx_22/
├── 1_xsf_traj/traj_22.traj, traj_22.xsf, seeds/...
├── 1_xsf/22/struct_*.xsf
├── data_22.csv
├── progression_plots/progression_seed_split_22.png
└── 2_im/conf_space.png, binding_probability_vs_temperature.png
```

## 5. Notes & pitfalls

- **Backend**: matplotlib uses the `Agg` (non-interactive) backend; `plt.show()` warnings
  in `process_database` are harmless.
- **Single-frame DBs**: index 29 (and similar) may hold only one structure; KDE then has
  too few samples. The runner detects this and skips the probability stage with a message
  rather than crashing.
- **`32_dos`**: has no `seed_*` directories and no `.db` (it ships pre-computed DOS CSVs);
  `process_database` falls back to flat mode but finds no structures, and the probability
  stage is skipped for it.
- **Fingerprint descriptor** requires the same chemical system as the training trajectory;
  all seeds in a folder share the same species, so PCA is consistent.

## 6. Verification checklist

- [ ] Running under `agox_v2` env (ASE + AGOX present)
- [ ] `0_analy/idx_<N>/1_xsf_traj/traj_<N>.traj` exists
- [ ] `conf_space.png` and `progression_seed_split_<N>.png` produced
- [ ] `binding_probability_vs_temperature.png` produced (unless DB too small)
