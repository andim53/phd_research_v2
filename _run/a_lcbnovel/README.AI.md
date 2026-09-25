# README for AI Agents — Project 10 (`a_lcbnovel`)

Machine-readable spec for agents working on this project. This complements the
human-facing `README.md`.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/a_lcbnovel/`
- **Purpose:** Faithful repair + re-host of the Fe/MgO Novelty-LCB AGOX search from
  `_run/7_lcbnovel_mgofe`, under the AI-Agent Project Workflow.
- **Physics:** 25 mobile Fe atoms deposited on a fixed MgO(001) substrate
  (Mg25O25 + Fe25 = 75 atoms), Novelty-LCB acquisition, GPAW LCAO/dzp DFT.
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0 + GPAW). Base `python3` has **no** AGOX/ASE/GPAW.

## 2. File layout

```
a_lcbnovel/
├── main.py                     # Entry point: per-seed AGOX run (CLI)
├── main_benchmark.py           # EMT benchmark: regular LCB vs Novelty-LCB (auto window)
├── main_benchmark_sweep.py     # Sweep: kappa x novelty_weight impact on Novelty-LCB
├── test_window_logic.py        # Isolated unit tests of the auto window logic
├── energy_stats.py             # Energy distribution of the LCB-only dataset
├── smoke_test_serialization.py # Cheap local validation of the serialization fix
├── j_novel.sh                  # PJM batch script (HPC launch, one seed per job)
├── j_benchmark.sh              # PJM batch script for the EMT benchmark (HPC)
├── j_benchmark_sweep.sh        # PJM batch script for the kappa x lambda sweep (HPC)
├── benchmark_results/          # Benchmark output (JSON + PNG; regenerable)
├── novelty_lcb/                # PROVEN package (copied from run 7, contains fix)
│   ├── __init__.py             #   re-exports NoveltyLCBAcquisitor, is_distinct, fingerprint_distance
│   ├── acquisitor.py           #   NoveltyLCBAcquisitor + free-func LCB calculator
│   ├── utils.py, common.py, benchmark_helpers.py
├── scripts/                    # Slab/generator builders (copied from run 7)
│   ├── build_mgo_stack.py, build_fe_stack.py, build_heteroStruct.py
│   ├── hetero_struct_randomize.py, plot_structure.py
├── README.md                   # Human overview
├── README.AI.md                # This file (agent spec)
├── LOG.md                      # Curated, append-only action log
├── transcript.log              # Raw tool-call / run-output transcript
├── TUTORIAL.md                 # Reproduce + repair guide with pitfalls
├── VERSIONS.md                 # Version manifest: every source file's __version__
├── 1_runs/                      # Self-contained run dirs (per-seed a-runs + benchmarks)
│   ├── a1_mgofe_Seed3_Iter300/  #   per-seed a-run: 300 iters (README+TUTORIAL + j_*.sh + main.py + scripts/ + novelty_lcb/)
│   ├── a2_mgofe_Seed3_Iter500/  #   per-seed a-run: 500 iters
│   ├── a3_mgofe_Seed3_Iter700/  #   per-seed a-run: 700 iters
│   ├── a4_mgofe_Seed3_Iter500_k3/  #   kappa sweep (κ=3)
│   ├── a5_mgofe_Seed3_Iter500_k4/  #   kappa sweep (κ=4); base for λ sweep
│   ├── a6_mgofe_Seed3_Iter500_k5/  #   kappa sweep (κ=5)
│   ├── a7_mgofe_Seed3_Iter500_k4_nw2/  #   novelty_weight sweep (λ=2)
│   ├── a8_mgofe_Seed3_Iter500_k4_nw3/  #   novelty_weight sweep (λ=3)
│   ├── a9_mgofe_Seed3_Iter500_k4_nw4/  #   novelty_weight sweep (λ=4)
│   ├── a10_mgofeb_Seed3_Iter500/ #   B-doped Fe/MgO+B (B7Fe25 mobile layer); first doping run
│   └── 73_novel_benchEMT/       #   full benchmark project (doc trio + main_benchmark*.py + j_benchmark*.sh)
├── 2_analysist/                 # Analysed results + heavy-run/benchmark project dirs
│   ├── run_analysis_indices.py  #   multi-seed analysis runner (3-stage pipeline, for 71/72)
│   ├── run_analysis_a_runs.py   #   single-seed analysis runner (for per-seed a-runs)
│   ├── scripts/                 #   copied deps: process_database.py, plot_structure_landscape.py,
│   │                           #     calculate_relative_energy.py
│   ├── 71_novel_runEWindow/     #   heavy multi-seed run, manual window (−411.6/25 eV), 13 seeds
│   ├── 72_novel_AutoGlob_1eVperAtomAboveGlob/  #   heavy multi-seed run, auto-glob window, 13 seeds
│   ├── 73_novel_benchEMT/       #   extended EMT benchmark results + DISCUSSION.md
│   ├── 74_novel_benchSweep/     #   kappa×λ sweep results + DISCUSSION.md
│   ├── a1_mgofe_Seed3_Iter300/  # … per-run a-run analysis dirs (README/TUTORIAL + analysis_a_runs/)
│   └── …a10_mgofeb_Seed3_Iter500/
└── .gitignore                  # ignores outputs/results (*.db/*.png/*.traj/...); code + docs tracked
```

### 2a. `1_runs/` and `2_analysist/`

- **`1_runs/`** — self-contained run directories. Each HPC run (or benchmark) is its
  own dir, holding **everything** it needs (job script, main script, and copies of
  `scripts/` and `novelty_lcb/`), independent of the project root. Naming:
  **`<NN>_<descriptor>`** (e.g. `a1_mgofe_Seed3_Iter300`, `a10_mgofeb_Seed3_Iter500`).
  **HPC per-seed Fe/MgO a-runs** (`a1`–`a10`) carry a per-run **`README.md` +
  `TUTORIAL.md`** specific to that run's treatment (seed, iteration budget, kappa,
  novelty_weight, or doping); **standalone benchmarks** (e.g. `73_novel_benchEMT`)
  carry the full doc trio inside their own dir. Run copies of `main.py`, `scripts/`,
  and `novelty_lcb/` are kept in sync with the latest versioned project root. Tracked
  in git (code + docs), subject to the regenerable-data exclusions.
- **`2_analysist/`** — analysed results, the heavy multi-seed run dirs, and the
  benchmark output dirs, kept separate from `1_runs/`. The repo-root `.gitignore`
  anticipates an abstract `0_analy/` (staging) / `1_result/` (final) layout, but in
  this project the heavy-run/benchmark **project dirs sit directly here**
  (`71_novel_runEWindow/`, `72_novel_AutoGlob_1eVperAtomAboveGlob/`,
  `73_novel_benchEMT/`, `74_novel_benchSweep/`), as do per-a-run `a1…a10/` dirs
  (each with README/TUTORIAL + `analysis_a_runs/`). Outputs are
  regenerable/gitignored.
- **`2_analysist/run_analysis_indices.py`** — self-contained **multi-seed** analysis
  runner (mirrors the sibling b_nestedsampling
  `/home/think/Desktop/research/_run/b_nestedsampling/2_analysist/run_analysis_indices.py`,
  adapted to this project). Loads all `seed_*/1_db/db_*.db` directly from a
  `--dataset` dir. Imports only the local `2_analysist/scripts/` deps
  (`plot_structure_landscape.py`, `process_database.py`, `calculate_relative_energy.py`).
  Scoped to the multi-seed heavy runs **71** and **72** (the flat benchmark dirs 73/74
  are excluded — no `seed_*` layout). Stages: ① best-so-far progression (per-seed),
  ② PCA landscape, ③ Boltzmann probability. CLI: `--dataset --outdir --e-max
  --normalize-density --start-iter`. Supports two-phase `--extract` /
  `--plot-from-json` (single self-describing `analysis_data.json` → bit-identical
  PNGs, DB-free). Outputs → per-run `<run>/analysis_indices/`.
- **`2_analysist/run_analysis_a_runs.py`** — self-contained **single-seed** analysis
  runner for the per-seed a-runs (e.g. `a1_mgofe_Seed3_Iter300/output`). Same 3-stage
  pipeline but labels the progression by the actual seed number and writes
  `progression_seed_split_Seed3.png`. Same CLI + two-phase `--extract` /
  `--plot-from-json`. Outputs → per-run `<run>/analysis_a_runs/`.
- **Per-analysis `DISCUSSION.md`** — each analysis dir carries a `DISCUSSION.md`
  stating the **exact running command + params** (a `## Running script` section) and
  discussing the results, mirroring the b_nestedsampling convention. Analysis outputs
  are gitignored (regenerable); the runners + `scripts/` are tracked.

### 2b. Source-code versioning

Every in-scope source file carries a module-level `__version__ = "X.Y.Z"` (semver).
`VERSIONS.md` is the single-source manifest of current versions.

- **Bump rule:** patch (`1.0.0 → 1.0.1`) on every code edit; minor (`1.0.1 → 1.1.0`)
  on API/behavior changes.
- **When you edit a file, bump its `__version__`, update `VERSIONS.md`, and record
  the old→new version in `LOG.md`.** In-scope files are the root `main*.py`,
  `novelty_lcb/`, `scripts/`, test/smoke/energy_stats, and `2_analysist/`
  runner+scripts. Duplicated snapshots under `1_runs/` and `dataset/` are **not**
  individually versioned (see `VERSIONS.md`).
- `__version__` sits after the shebang/docstring and any `from __future__` import.

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/a_lcbnovel

# Validate serialization fix (cheap, no GPAW) — MUST pass before a real run
$PY smoke_test_serialization.py

# Compile-check everything
$PY -m py_compile main.py novelty_lcb/*.py scripts/*.py

# Local structure build check (no DFT)
$PY -c "from main import build_slabs; s,d,st=build_slabs(); print(s.get_chemical_formula(), len(s), st)"

# Single seed locally (NOT with GPAW — SubprocessGPAW needs a cluster node)
$PY main.py --seed 3 --n-iterations 2 --out-root ./output

# HPC launch (uses gpaw_env; edit SEED=3 in j_novel.sh to change the seed)
pjsub j_novel.sh

# EMT benchmark (regular vs Novelty-LCB auto window) — needs a RAM-rich node / HPC
$PY main_benchmark.py      # local
pjsub j_benchmark.sh           # on HPC

# Sweep benchmark (kappa x novelty_weight) — needs a RAM-rich node / HPC
$PY main_benchmark_sweep.py      # local
pjsub j_benchmark_sweep.sh       # on HPC

# Analyse Fe/MgO heavy-run results (71, 72) — self-contained in 2_analysist
cd 2_analysist
$PY run_analysis_indices.py --dataset 71_novel_runEWindow/dataset --outdir 71_novel_runEWindow/analysis_indices
$PY run_analysis_indices.py --dataset 72_novel_AutoGlob_1eVperAtomAboveGlob/dataset --outdir 72_novel_AutoGlob_1eVperAtomAboveGlob/analysis_indices

# Analyse a per-seed a-run (single seed) — run_analysis_a_runs.py
$PY run_analysis_a_runs.py --dataset a1_mgofe_Seed3_Iter300/output --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
# two-phase: --extract writes analysis_data.json; --plot-from-json replots PNGs DB-free
$PY run_analysis_a_runs.py --dataset a1_mgofe_Seed3_Iter300/output --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs --extract
$PY run_analysis_a_runs.py --plot-from-json a1_mgofe_Seed3_Iter300/analysis_a_runs/analysis_data.json --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
```

### `main.py` CLI

| Flag | Default | Meaning |
|---|---|---|
| `--seed N` | `None` | Single seed (overrides range) |
| `--seed-start` / `--seed-end` | `3` / `104` | Inclusive seed range |
| `--n-iterations` | `100` | AGOX iterations |
| `--out-root` | `./output` | Root dir; `out-root/seed_<N>/{0_result,1_db}` |

## 4. Dependencies & environment

- Conda env **`agox_v2`** (AGOX 3.10.2, ASE 3.25.0, GPAW, Ray) — **local** dev/test.
- HPC pjsub heavy run uses **`gpaw_env`** (set in `j_novel.sh`).
- `matplotlib.use("Agg")` before plotting in headless runs (smoke test does this).
- Ray is started internally by AGOX (parallel pool); harmless stderr noise expected.
- For GPR hyperparameter optimisation, `use_ray=False` avoids Ray actors on low-RAM
  local nodes (see pitfalls), but on the 64-core HPC node Ray is fine and expected.

## 5. Inputs / Outputs

**Inputs:** none external — the Fe/MgO slab is built from first principles in
`build_slabs()` (MgO/Fe bulk lattice constants, `build_*_stack` scripts).

**Outputs** (per seed under `--out-root/seed_<N>/`):
- `1_db/db_<N>.db` — AGOX sqlite database of explored candidates.
- `0_result/0_xsf/` — structure files (slab_mgofe.xsf, slab_fe.xsf, heteroStruct.xsf).
- `output_seed_<N>.txt` — GPAW output log (written in cwd).
- `generated_structures/` — HeteroStructRandomize outputs (regenerable).

These are regenerable artifacts and are gitignored (`.gitignore` excludes `*.db`,
`*.xsf`, `*.out`, `generated_structures/`); code + docs are tracked.

## 6. Error handling & edge cases

1. **Ray sqlite-pickle crash** (`cannot pickle 'sqlite3.Connection'`) — the run-7
   bug. Root cause: acquisitor passed bound methods into `LowerConfidenceBoundCalculator`,
   dragging the sqlite-backed `Database` into the Ray pool. **Fix (present in the
   copied package):** `get_acquisition_calculator()` returns
   `LowerConfidenceBoundCalculator(model, partial(lcb_acquisition_energy, kappa=...),
   partial(lcb_acquisition_force, kappa=...))` using **module-level free functions**.
   Validate with `smoke_test_serialization.py`.
2. **`LocalOptimizationEvaluator.__init__() missing 'calculator'`** — wiring bug:
   the kwargs key must be `calculator`, not `calc`. `main.py` passes it positionally.
3. **Energy window mode** — the default is the **auto global-minimum** mode. With
   `per_atom=True` (default), the window is `(-inf, E_min/N + X]` per atom, where `E_min`
   is the live lowest DFT energy in the DB, `N` the atom count, and `X` =
   `energy_above_min` (in `main.py`, `NOVELTY_ENERGY_ABOVE_MIN`, default 1.0 eV/atom).
   Per-atom is size-independent (choose 0.5–2 eV/atom directly). Set `per_atom=False`
   to use total eV. Backward-compatible centered mode (`target_energy ± ΔE`) is
   available by setting `energy_above_min=None`. The window compares against predicted
   absolute energy `E`.
4. **GPAW needs HPC** — `SubprocessGPAW(..., ncores=64, mode=lcao, basis=dzp)` targets a
   64-core cluster node. Do not run the full `main.py` locally with GPAW.
5. **Composition uniformity** — all candidates must share one stoichiometry/atom count
   for a single global `Fingerprint` descriptor. The Fe/MgO setup is uniform by
   construction (MgO substrate fixed, Fe deposited).
6. **Benchmark needs RAM for the Ray pool** — `main_benchmark.py` uses AGOX's
   `ParallelCollector`/`ParallelRelaxPostprocess` (Ray pool). On a low-RAM node it
   fails with Ray `ActorUnavailableError` (environmental). Run it on a RAM-rich node
   or HPC (`pjsub j_benchmark.sh`). `USE_RAY=False` in the benchmark reduces GPR actors but
   does not remove the parallel pool. `test_window_logic.py` covers the window logic
   standalone (no Ray).

## 7. Provenance / references

- Upstream project (buggy): `_run/7_lcbnovel_mgofe/` (`main.py`, `j_novel.sh`,
  `j_novel.sh.6543317.out` = the crash log).
- Troubleshooting guide: `_md/for-agent/novelty_lcb_agox_troubleshooting.md`
  (bugs A/B/C, AGOX internals, verification checklist).
- Related downstream analysis: `_run/8_nested_sampling/`, `_run/9_novelFilter/`.
- Skills: `agox`, `agox-novel-filter`, `agox-nested-sampling`, `simulation-analysis`,
  `agox-run-code`.
