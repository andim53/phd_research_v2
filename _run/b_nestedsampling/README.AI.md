# README for AI Agents — Project `b_nestedsampling`

Machine-readable spec for agents working on this project. Complements the
human-facing `README.md`. Read `AGENTS.md` (governing rules) and `LOG.md`
(action log) first.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/b_nestedsampling/`
- **Purpose:** Nested sampling over the combined multi-seed Fe/MgO AGOX dataset,
  using a single GPR surrogate trained on all 1297 structures. Re-hosted from
  `_run/8_nested_sampling` under the AI-Agent Project Workflow.
- **Physics:** 75-atom Fe25Mg25O25 structures (25 mobile Fe on fixed MgO(001)),
  evidence/partition-function `Z` via log-space nested sampling.
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0). Base `python3` has **no** AGOX/ASE. HPC batch
  (`j_nestedsampling.sh`) activates `gpaw_env` (standing convention) — see caveat.

## 2. File layout

```
b_nestedsampling/
├── main.py                     # Entry point (renamed from run_nested_sampling.py): load seeds -> train GPR -> NestedSampler -> analyze
├── nested_sampling/             # PROVEN package (migrated from 8_nested_sampling)
│   ├── __init__.py              #   re-exports NestedSampler, train_gpr, K_B, analyze_state_density...
│   ├── nested_sampler.py        #   NestedSampler (log-space evidence accumulation)
│   ├── gpr_training.py          #   train_gpr helper
│   ├── state_density.py         #   analyze_state_density, analyze_saved_output, load_saved_run
│   └── utils.py                 #   K_B constant, shift_energies
├── scripts/                     # Clean slab/generator builders used by dataset/main.py
│   ├── build_mgo_stack.py, build_fe_stack.py, build_heteroStruct.py
│   ├── hetero_struct_randomize.py, plot_structure.py
├── dataset/                     # AGOX seed outputs (seed_3..15, stop_16; DBs gitignored)
│   ├── main.py                  #   original AGOX search that produced the DBs
│   ├── job_5x5_9.sh, scripts/   #   dataset generator scripts
│   └── seed_<N>/{0_result,1_db/db_<N>.db}
├── j_nestedsampling.sh          # PJM batch script (HPC launch)
├── README.md                    # Human overview
├── README.AI.md                 # This file (agent spec)
├── LOG.md                       # Curated, append-only action log
├── transcript.log               # Raw tool-call / run-output transcript (gitignored)
├── TUTORIAL.md                  # Reproduce + pitfalls + verification
├── VERSIONS.md                  # Version manifest: every source file's __version__
├── AGENTS.md                    # Governing rules for AI agents
├── PROMPTS.md                   # Prompt log + grammar-notes scaffold
├── _runs/                       # (scaffolded) self-contained run dirs (HPC)
├── _analysist/                  # (scaffolded) analysis outputs (0_analy/, 1_result/)
├── _archives/                   # (scaffolded) archived artifacts
└── _tmp/                        # (scaffolded) scratch output
```

### 2a. `_runs/` and `_analysist/` (scaffolded, per the run-directory convention)
- **`_runs/<NN>_<descriptor>/`** — self-contained HPC run dirs, each holding
  `j_*.sh` + `main*.py` + copies of `scripts/` and `nested_sampling/`, launchable
  in isolation. HPC per-seed runs carry a per-run `README.md` + `TUTORIAL.md`.
- **`_analysist/`** — analysed/intermediate results (`0_analy/`, `1_result/`,
  notebooks). Outputs regenerable/gitignored; analysis code tracked.
- **`_archives/`** — archived artifacts; **`_tmp/`** — scratch output. Both
  gitignored.

### 2b. Source-code versioning
Every in-scope source file carries a module-level `__version__ = "X.Y.Z"`
(semver). `VERSIONS.md` is the single-source manifest.
- **Bump rule:** patch (`1.0.0 → 1.0.1`) on every code edit; minor
  (`1.0.1 → 1.1.0`) on API/behavior changes.
- **On every edit:** bump `__version__`, update `VERSIONS.md`, record old→new in
  `LOG.md`.
- In-scope: `main.py`, `nested_sampling/`, `scripts/`.
  `dataset/` and `_runs/` snapshots are **not** individually versioned.
- Pre-existing **function-local** `__version__` values in `scripts/*.py` are left
  untouched (module-level one added).

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/b_nestedsampling

# Compile-check everything
$PY -m py_compile main.py nested_sampling/*.py scripts/*.py

# Quick smoke run (full GPR train, tiny sampler)
$PY main.py --temp 300 --n-live 30 --n-iters 20 \
    --perturb 0.01 --output /tmp/ns_smoke --rng 42

# Full production run
$PY main.py --temp 300 --n-live 50 --n-iters 300 \
    --perturb 0.01 --output ./ns_output_allseeds --rng 42

# Standalone re-analysis of a finished run (no re-train)
$PY main.py --analyze-only ./ns_output_allseeds --output ./analysis_out

# HPC launch (nested sampling only; reads existing dataset/seed_*/1_db/db_*.db)
#   - activates gpaw_env; 24 cores
#   - edit main.py args in j_nestedsampling.sh to change NS params
#   - optional AGOX search step (dataset/main.py) documented in TUTORIAL
pjsub j_nestedsampling.sh
```

### `main.py` CLI
| Flag | Default | Meaning |
|---|---|---|
| `--temp` | `300` | Temperature (K); sets `beta=1/(k_B*T)`. Fixed-T mode only. |
| `--temperature-free` | off | Temperature-free NS: beta kept OUT of the likelihood (energy-constrained top-down pass); post-processes Z/F/posterior at `--temperatures`. |
| `--temperatures` | `100,200,300,500,1000` | Comma-separated T (K) for temperature-free post-processing. |
| `--n-live` | `50` | Number of live points (evidence resolution ∝ 1/√K). |
| `--n-iters` | `300` | Number of nested-sampling iterations. |
| `--perturb` | `0.01` | Perturbation amplitude (Å) on perturbed atoms during prior sampling. |
| `--perturb-symbols` | `Fe` | Element(s) perturbed; comma-separated for multiple (e.g. `Fe,B`); all others stay fixed. |
| `--output` | `./ns_output_allseeds` | Output directory. |
| `--rng` | `42` | RNG seed (reproducibility). |
| `--analysis-dir` | `<--output>/analysis` | Analysis output dir. |
| `--no-analysis` | off | Skip automatic analysis. |
| `--analyze-only <DIR>` | None | Re-run analysis on a saved run. |

## 4. Dependencies & environment
- Conda env **`agox_v2`** (AGOX 3.10.2, ASE 3.25.0, Ray) — **local** dev/test.
- HPC pjsub heavy run uses **`gpaw_env`** (`j_nestedsampling.sh`). **Caveat:**
  the sampling script needs the AGOX/ASE stack from `agox_v2`; if `gpaw_env`
  lacks it, switch `conda activate gpaw_env` → `conda activate agox_v2` before
  submitting (the original notes flagged this).
- `matplotlib.use("Agg")` before plotting in headless runs.
- `GPR(..., use_ray=False)` in `main.py` avoids Ray actors
  (`ActorUnavailableError` on low-RAM nodes). Single-process → scale out by
  submitting many independent jobs.

## 5. Inputs / Outputs
**Inputs:** `dataset/seed_*/1_db/db_*.db` (13 DBs, 1297 structures, uniform
Mg25O25Fe25). No external inputs.

**Outputs** (under `--output`): `evidence_history.csv`, `log_evidence.csv`,
`final_live_energies.csv`, `posterior_summary.csv`,
`posterior_structures/posterior_*.xsf`. Analysis under `<--output>/analysis/`.
All regenerable/gitignored.

## 6. Error handling & edge cases
1. **No DBs matched** → `FileNotFoundError` from `load_all_seeds` if the glob is
   empty.
2. **Composition mismatch breaks the descriptor** — a single global `Fingerprint`
   supports one stoichiometry. The Fe/MgO set is uniform (verified: 1297 ×
   Mg25O25Fe25).
3. **`log_evidence.csv` is malformed** (pre-existing package bug) — iterations and
   log_Z are written as two transposed rows. No data lost; `evidence_history.csv`
   is correct. Regenerate per-row log_Z from `evidence_history.csv` if needed.
4. **GPR extrapolation to unphysical energies** — with `--perturb` too large the
   Fingerprint GPR predicts |E|>1e4 eV. `log_likelihood` returns `-inf` for
   |E|>1e4 and `_filter_unphysical()` drops those points. Use `--perturb 0.01`
   (or 0). Note: the |E|<1e4 filter is a pragmatic threshold, not a physical
   guarantee.
5. **Ray `ActorUnavailableError`** — environmental (RAM exhaustion); avoided with
   `use_ray=False` (already set in `main.py`).
6. **Degenerate KDE** — analysis skips a panel if a set has <2 distinct energies
   (where `gaussian_kde` would be singular).

## 7. Provenance / references
- Upstream (migrated from): `_run/8_nested_sampling/` — `run_nested_sampling.py`
  (now `main.py` here), `nested_sampling/` package, `dataset/`, `job.sh`,
  `README.md`, `NESTED_SAMPLING_RUN.md` (786-line notes split into
  README/LOG/TUTORIAL here).
- Related: `_run/a_lcbnovel/` (Novelty-LCB search), `_run/9_novelFilter/`
  (analysis pipeline the state-density module is modeled on), `_run/8_nested_sampling`.
- Literature: Pártay/Csányi/Bernstein 2021 (EPJB 94, 159); Yang/Pártay/Wexler 2024
  (PCCP 26, 13862) — see TUTORIAL "Discussion".
- Skills: `ai-agent-project-workflow`, `agox-nested-sampling`, `agox`,
  `simulation-analysis`, `agox-run-code`.
