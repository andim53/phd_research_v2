# Complete Guide & Tutorial: `run_analysis_indices.py`

> Author: Calyx (Hermes Agent)
> Scope: full end-to-end documentation for using
> `/home/think/Desktop/research/_analysist/run_analysis_indices.py`
> — from environment setup and dependencies, through every command, to the
> meaning of every output file. Written for both first-time users and future
> sessions that need a reliable reference.

---

## Table of Contents

1. What this script does
2. Prerequisites & environment (CRITICAL)
3. Installing / verifying dependencies
4. File and directory layout
5. Quick start (TL;DR)
6. Command-line reference
7. Worked examples (all cases)
8. What happens inside (the 4 stages)
9. Output files explained
10. Group & index reference table
11. Troubleshooting
12. FAQ
13. Extending the script

---

## 1. What this script does

`run_analysis_indices.py` is a single consolidated runner that performs the
full AGOX simulation-analysis pipeline for one or more "indices" (top-level
simulation folders under `1_result/`). For each index it runs, in order:

1. **Plotting style** — applies the fixed researcher style from
   `codes/07_plotting_style_and_label_configuration.py` (serif font, boxed
   tick marks with visible minor ticks, thick axes, the
   `$E_i-E_{glob}$ (eV/atom)` energy label).
2. **Database processing loop** — from `codes/12_database_processing_loop.py`
   using `scripts/process_database.py`. Loads every `seed_*` database for the
   index, filters iterations `>= 10`, writes combined and per-seed
   trajectories, a relative-energy CSV, individual XSF frames, and a
   best-so-far convergence plot.
3. **Landscape analysis & evaluation** — from
   `codes/14_landscape_analysis_and_evaluation_script.py` using
   `scripts/plot_structure_landscape.py`. Builds an AGOX Fingerprint
   descriptor, reduces structure space to 1D via PCA (eigenvector of the
   covariance matrix), and draws the conformation landscape (scatter +
   Gaussian-KDE state-density panel).
4. **Plot probability (statistical mechanics)** — from
   `codes/76_plot_probability.py`. Builds a Gaussian-KDE over binding
   energies, then runs a Boltzmann/partition-function loop over five
   temperatures to produce a probability-vs-energy plot.

The indices covered are grouped as:

| Group name | Indices | Folders |
|------------|---------|---------|
| `latt_sweep_1` | 22, 23, 24, 25, 26 | `22_latt_0` … `26_latt_100` |
| `fe_concentration` | 27, 28, 29, 30, 31 | `27_fe_con0` … `31_fe_con20` |
| `latt_on_mgo` | 32, 33, 34, 35, 36 | `32_dos`, `33_latt_25_mgo` … `36_latt_100_mgo` |
| `ml_rattle` | 67, 68, 69 | `67_2ml`, `68_ratt_min1`, `69_ratt_min05` |

---

## 2. Prerequisites & environment (CRITICAL)

**Do NOT run this with the system `python3`.** The base interpreter
(`/home/think/miniconda3/bin/python`, Python 3.13) does **not** have ASE or
AGOX installed, and the `agox` env is missing `pandas`. Running with the wrong
interpreter produces `ModuleNotFoundError: No module named 'ase'` or
`'pandas'`.

The correct interpreter is the **`agox_v2`** conda environment:

```
/home/think/miniconda3/envs/agox_v2/bin/python
```

Verified package set in `agox_v2` (Python 3.11.13):

| Package | Version |
|---------|---------|
| ase (Atomic Simulation Environment) | 3.25.0 |
| agox | 3.10.2 |
| numpy | 1.26.4 |
| pandas | 3.0.5 |
| scipy | 1.16.1 |
| matplotlib | 3.11.1 |

> Note: the older `agox` env (AGOX 3.9.0) also has ASE but lacks pandas, so it
> will crash in `process_database`. Always use `agox_v2`.

The script itself forces the `Agg` (headless) matplotlib backend via
`matplotlib.use('Agg')`, so it works on a server/CLI with no display. The
`FigureCanvasAgg is non-interactive, and thus cannot be shown` warning emitted
by `process_database.py` is harmless.

---

## 3. Installing / verifying dependencies

If `agox_v2` already exists (it does on this machine), you only need to verify
it. If you ever need to recreate it:

```bash
# Verify the env interpreter and packages
/home/think/miniconda3/envs/agox_v2/bin/python -c \
  "import ase, agox, pandas, scipy, numpy, matplotlib; \
   print('ase', ase.__version__, 'agox', agox.__version__, \
         'mpl', matplotlib.__version__, 'np', numpy.__version__)"

# (Re)create the env only if missing — example, not required here:
conda create -n agox_v2 -c conda-forge python=3.11 agox ase pandas scipy matplotlib
```

No `pip install` is needed on this machine; everything is already satisfied in
`agox_v2`.

---

## 4. File and directory layout

Working directory for all commands: `/home/think/Desktop/research/_analysist/`

```
_analysist/
├── run_analysis_indices.py        <- the runner (this guide)
├── scripts/
│   ├── process_database.py        <- Stage 2 engine
│   ├── plot_structure_landscape.py<- Stage 3 engine
│   ├── calculate_relative_energy.py
│   └── ... (other project scripts)
├── codes/
│   ├── 07_plotting_style_and_label_configuration.py  <- Stage 1 source
│   ├── 12_database_processing_loop.py                <- Stage 2 source
│   ├── 14_landscape_analysis_and_evaluation_script.py<- Stage 3 source
│   └── 76_plot_probability.py                        <- Stage 4 source
├── 1_result/                      <- INPUT: raw simulation folders (22_*, 67_*, ...)
└── 0_analy/                       <- OUTPUT (created/updated by the script)
    └── idx_<N>/
        ├── 1_xsf_traj/traj_<N>.traj, traj_<N>.xsf, seeds/...
        ├── 1_xsf/<N>/struct_*.xsf
        ├── data_<N>.csv
        ├── progression_plots/progression_seed_split_<N>.png
        └── 2_im/conf_space.png, binding_probability_vs_temperature.png
```

The script auto-adds its own directory and `scripts/` to `sys.path`, so you
can run it from anywhere as long as you pass the absolute interpreter path and
are logically working within the repo.

---

## 5. Quick start (TL;DR)

```bash
cd /home/think/Desktop/research/_analysist

# Run EVERYTHING (all 18 indices, all 4 stages)
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py

# Check results
ls 0_analy/idx_67/2_im/
```

Expected runtime: roughly 1–2 minutes per index for the full set; the
probability stage is the slowest (KDE + per-temperature Boltzmann loop over
hundreds of frames).

---

## 6. Command-line reference

```
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    [--indices SPEC] [--skip-probability]
```

### `--indices SPEC` (optional)

Selects which indices to process. `SPEC` is a comma-separated list where each
token is either a **group name** or a bare **integer index**.

- Group names: `latt_sweep_1`, `fe_concentration`, `latt_on_mgo`, `ml_rattle`
- Integers: any index in `22..36` or `67..69` (others are unmapped and will
  raise a `KeyError` — see Troubleshooting).

If `--indices` is omitted, **all** indices are processed.

### `--skip-probability` (optional flag)

Skips Stage 4 (the statistical-mechanics probability plot). Useful when you
only want trajectories + landscape, or when debugging Stage 1–3 quickly.

### Examples

```bash
# Whole groups by name
--indices latt_sweep_1
--indices fe_concentration,latt_on_mgo,ml_rattle

# Specific indices
--indices 22,67,69
--indices 33

# Mixed
--indices ml_rattle,29

# Just landscape quickly (skip slow probability)
--indices 33 --skip-probability

# Default: everything
(no flags)
```

---

## 7. Worked examples (all cases)

### Case A — Run the full pipeline on all indices

```bash
cd /home/think/Desktop/research/_analysist
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py
```
Processes indices 22–36 and 67–69. For each: database processing → landscape →
probability. Outputs written under `0_analy/idx_<N>/`.

### Case B — Run one logical group

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices latt_sweep_1
```
Equivalent to `--indices 22,23,24,25,26`.

### Case C — Run several groups at once

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices fe_concentration,latt_on_mgo,ml_rattle
```

### Case D — Run a single specific index

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices 67
```
Good for focused re-runs after editing a single folder's data.

### Case E — Mixed selection

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices ml_rattle,29
```
Expands to `67,68,69,29`.

### Case F — Fast pass (skip probability)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices 33 --skip-probability
```
Produces trajectory + landscape only.

### Case G — Capturing logs

Because the conda wrapper prints harmless noise to stderr, capture clean logs:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --indices 22,67 > run.log 2>&1
grep -E "INDEX|STEP|saved|skip" run.log
```

---

## 8. What happens inside (the 4 stages)

For each requested index `N`:

### Stage 1 — Plotting style (applied once at import)
`plt.rcParams.update({...})` sets the global matplotlib style. No per-index
work; it just guarantees every figure matches the `07` convention.

### Stage 2 — `step1_database_processing(N)`
- Maps `N` → its input folder via `db_paths_for()`.
- Calls `process_database(dir_path=..., file_idx=N, dir_out=0_analy/idx_N, ...)`.
- Inside `process_database`:
  - Globs `seed_*`-style seed directories; for flat folders (no `seed_*`) it
    falls back to `<root>/1_db/db_0.db`.
  - Loads each AGOX `Database`, filters `iteration >= start_iter` (10).
  - Concatenates all frames into one master trajectory; writes
    `1_xsf_traj/traj_N.traj` and `.xsf`.
  - Writes per-seed trajectories under `1_xsf_traj/seeds/`.
  - Computes relative energy per atom (`calculate_relative_energy`).
  - Writes `data_N.csv` and individual `1_xsf/N/struct_*.xsf` frames.
  - Plots the best-so-far convergence curve →
    `progression_plots/progression_seed_split_N.png`.

### Stage 3 — `step2_landscape(N)`
- Reads `0_analy/idx_N/1_xsf_traj/traj_N.traj`.
- Collects valid potential energies; normalizes per atom.
- Builds AGOX `Fingerprint` features, centers them, computes the covariance
  matrix, and projects onto the top eigenvector (`X_eigen`).
- Calls `plot_structure_landscape(...)` → `2_im/conf_space.png`.

### Stage 4 — `step3_probability(N)`
- Walks the index input folder and loads **every** `*.db` found (all seeds).
- Computes binding energies; builds a Gaussian KDE over the relative binding
  energy grid (1000 points).
- For temperatures `[298.15, 348.60, 447.875, 547.15, 646.425]` K:
  - Intensive Gibbs level `G = grid - kB*T*ln(density)`
  - Boltzmann weights `exp(-beta * (delta_G * n_fe))`, partition function `Z`,
    probability `P = weights / Z`.
- Plots all five `P(E)` curves → `2_im/binding_probability_vs_temperature.png`.

**Guard clauses (no crashes, just skips):**
- If `traj_N.traj` is missing → Stage 3 prints a warning and skips.
- If no `*.db` exists for the index (e.g. `32_dos` ships only precomputed DOS
  CSVs) → Stage 4 skips.
- If fewer than 2 frames are found → KDE needs ≥2 samples, so Stage 4 skips
  with a clear message.

---

## 9. Output files explained

Inside `0_analy/idx_<N>/`:

| File | Stage | Meaning |
|------|-------|---------|
| `1_xsf_traj/traj_<N>.traj` / `.xsf` | 2 | Master combined trajectory of all seeds (filtered iter≥10). |
| `1_xsf_traj/seeds/<N>_seed_*.traj/.xsf` | 2 | Per-seed trajectory files. |
| `1_xsf/<N>/struct_*.xsf` | 2 | Individual structure frames (magmom arrays stripped for XSF compatibility). |
| `data_<N>.csv` | 2 | Table: `index, energy, relative_energy, relative_energy_per_atom`. |
| `progression_plots/progression_seed_split_<N>.png` | 2 | Best-so-far energy convergence per seed (Seed 0 bold black). |
| `2_im/conf_space.png` | 3 | Conformation landscape: 1D PCA projection vs energy + KDE density. |
| `2_im/binding_probability_vs_temperature.png` | 4 | Probability P(E) at the five temperatures. |

---

## 10. Group & index reference table

| Group | Index | Input folder | Note |
|-------|-------|--------------|------|
| latt_sweep_1 | 22 | 22_latt_0 | lattice 0% |
| | 23 | 23_latt_025 | lattice 2.5% |
| | 24 | 24_latt_50 | lattice 5% |
| | 25 | 25_latt_075 | lattice 7.5% |
| | 26 | 26_latt_100 | lattice 10% |
| fe_concentration | 27 | 27_fe_con0 | Fe 0% |
| | 28 | 28_fe_con5 | Fe 5% |
| | 29 | 29_fe_con10 | Fe 10% |
| | 30 | 30_fe_con15 | Fe 15% |
| | 31 | 31_fe_con20 | Fe 20% |
| latt_on_mgo | 32 | 32_dos | DOS only — **no DB, Stage 2/3/4 skipped** |
| | 33 | 33_latt_25_mgo | |
| | 34 | 34_latt_50_mgo | |
| | 35 | 35_latt_75_mgo | |
| | 36 | 36_latt_100_mgo | |
| ml_rattle | 67 | 67_2ml | 2 ML |
| | 68 | 68_ratt_min1 | rattle min 1 |
| | 69 | 69_ratt_min05 | rattle min 0.5 |

---

## 11. Troubleshooting

**`ModuleNotFoundError: No module named 'ase'` / `'pandas'`**
→ You used the wrong interpreter. Use
`/home/think/miniconda3/envs/agox_v2/bin/python`, not `python3`.

**`KeyError: <number>` when passing `--indices`**
→ You passed an index not in the `folder_map` (only 22–36 and 67–69 are
mapped). Either use a mapped index or add it to `db_paths_for()` and `GROUPS`.

**`ValueError: dataset input should have multiple elements` (KDE)**
→ A single-frame DB was sampled. The current code already guards this
(`len(rel_eb) < 2 → skip`), so if you see it, you are on an older version —
pull the fix (aggregates all seed DBs and skips when <2 frames).

**`FigureCanvasAgg is non-interactive, and thus cannot be shown`**
→ Harmless. `process_database` calls `plt.show()`; in headless `Agg` mode it
just warns. Outputs are still saved.

**`32_dos` produced no outputs**
→ Expected. `32_dos` contains only precomputed DOS CSVs, no `seed_*` DBs, so
Stages 2–4 correctly skip it.

**Conda "unexpected error" text in terminal/stderr**
→ This is noise from the conda shell hook, not a script failure. Check the
exit code (`echo $?` → 0) and the actual log lines (grep for `saved`/`skip`).

**Wrong working directory**
→ The script builds paths relative to its own location (`SCRIPT_DIR`), so you
can run it from anywhere; `1_result/` and `0_analy/` are resolved relative to
the script file, not your CWD.

---

## 12. FAQ

**Q: Can I add a new index (e.g. 70)?**
A: Yes. Add it to `folder_map` inside `db_paths_for()` and (optionally) to a
group in `GROUPS`. Then run `--indices 70`.

**Q: Can I change the temperatures or n_fe in the probability stage?**
A: Edit `step3_probability()`: `temperatures` list and `n_fe`, `E_slab`,
`mu_fe` constants.

**Q: Can I change the energy-axis limits of the landscape?**
A: Edit `E_LIMIT` (default `(0.0-0.1, 2.0+0.1, 5)`) near the top of the script.

**Q: Does it overwrite previous results?**
A: Yes — outputs are written into `0_analy/idx_<N>/` and overwritten on re-run.
Back up first if you need to keep old runs.

**Q: Why does it use `start_iter=10`?**
A: Mirrors the original `codes/12` usage (only iterations ≥ 10 are analyzed).

---

## 13. Extending the script

- **New stage:** add a `stepN_*(idx)` function and call it in `main()`'s loop.
- **New group:** extend `GROUPS`; the `--indices` parser accepts any group name.
- **New plotting style:** modify the `plt.rcParams.update({...})` block (Stage 1).
- **Different descriptor:** swap `Fingerprint` in `step2_landscape()` for another
  AGOX descriptor (keep the `.create_features(s).flatten()` interface).
- **Parallelism:** wrap the `for idx in indices:` loop in a process pool if you
  have many indices and want speed (each index is independent).

---

*End of guide.*
