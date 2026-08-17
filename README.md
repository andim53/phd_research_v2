# PHD Research — AGOX Analysis & XRD Simulation

This repository contains the simulation analysis pipeline and XRD tooling for a computational materials science PhD project. Two main components:

---

## 1. AGOX Analysis Pipeline (`_analysist/`)

A multi-stage analysis pipeline built on [AGOX](https://github.com/agox/agox) (Atomistic Global Optimization) that processes simulation databases, generates structure landscapes, and computes temperature-dependent binding probabilities.

### Quick Start

```bash
cd _analysist
/home/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py
```

### What it does (4-stage chain per index)

1. **Database Processing** — Reads AGOX `.db` files from `1_result/<idx>*/seed_*/db_*.db`, extracts trajectories, and produces energy progression plots.
2. **Landscape Analysis** — PCA on fingerprint features + energy to produce a configuration space landscape (`conf_space.png`).
3. **Binding Probability vs. Temperature** — KDE-based statistical mechanics analysis; Boltzmann-weighted probability curves at multiple temperatures (`binding_probability_vs_temperature.png`).

### Index Groups

| Group | Indices | Description |
|---|---|---|
| `latt_sweep_1` | 22–26 | Lattice constant sweep |
| `fe_concentration` | 27–31 | Fe concentration series |
| `latt_on_mgo` | 32–36 | Lattice on MgO substrate (idx 32 is DOS-only, no .db) |
| `ml_rattle` | 67–69 | 2ML / rattle studies |

### Running a subset

```bash
# By group name
python run_analysis_indices.py --indices latt_sweep_1,ml_rattle

# By individual index
python run_analysis_indices.py --indices 22,27,67

# Skip the probability stage
python run_analysis_indices.py --skip-probability
```

### Directory layout

```
_analysist/
├── 1_result/          # Raw AGOX DB outputs (results per index)
├── 0_analy/           # Analysis outputs (plots, XSF structures)
├── codes/             # Reference scripts (01–98, numbered by creation order)
├── scripts/           # Imported modules: process_database, plot_structure_landscape, calculate_relative_energy
├── run_analysis_indices.py   # Main entry point
└── main_analyst.ipynb / main_test.ipynb   # Jupyter analysis notebooks
```

---

## 2. XRD Simulation (`xrd/`)

Simulated X-ray diffraction patterns for bcc metals using Pymatgen's `XRDCalculator` with Cu K-alpha radiation and Gaussian peak broadening.

### `xrd/main.py`

Simulates XRD for **Tungsten (W)** or **Tantalum (Ta)** (set `material_option` at the top). Produces a 3x3x3 bcc supercell, computes the diffraction pattern over 2θ = 30–50°, applies FWHM broadening, and saves `ta_comparison_xrd.png`.

### `xrd/main_amorph.py`

Related amorphous-material XRD handling (see source for details).

---

## Environment

- **AGOX analysis**: requires the `agox_v2` conda environment at `/home/miniconda3/envs/agox_v2/`. This env has ASE 3.25.0, AGOX 3.10.2, pandas, scipy, matplotlib.
- The default system Python (`/home/miniconda3/bin/python`) does NOT have ASE/AGOX — always use the absolute path to the `agox_v2` interpreter.
- Matplotlib must use the `Agg` backend for headless execution (already set in `run_analysis_indices.py`).

---

## Notes

- `__trash/`, `_archive/`, `_md/`, `_run/` contain earlier drafts, archived runs, and miscellaneous artifacts — not part of the main pipeline.
- The `.gitignore` currently tracks most analysis outputs. Large binary outputs (`.xsf`, `.db`, `.png`) may be excluded depending on repo policy.
- `run.log1`, `run.log2` are run logs from previous pipeline executions.

---

## License

(Choose your license here — e.g. MIT, GPL-3.0, or "see LICENSE file")
