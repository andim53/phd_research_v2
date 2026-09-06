# README for AI Agents — Project `c_landausampling`

Machine-readable spec for agents working on this project. Complements the
human-facing `README.md`. Read `AGENTS.md` (governing rules) and `LOG.md`
(action log) first.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/c_landausampling/`
- **Purpose:** Wang–Landau flat-histogram sampling of the density of states
  `g(E)` on an AGOX GPR surrogate trained over a combined multi-seed AGOX
  dataset. Sibling of `b_nestedsampling` (same problem, different algorithm).
- **Physics:** 75-atom Fe25Mg25O25 (25 mobile Fe on fixed MgO(001)); also B3
  (78-atom B3Fe25Mg25O25) and B7 (82-atom B7Fe25Mg25O25) doped variants.
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0). Base `python3` has **no** AGOX/ASE. HPC batch
  (`j_wanglandau.sh`) activates `gpaw_env` (standing convention) — see caveat.

## 2. File layout

```
c_landausampling/
├── main.py                    # Entry point: load dataset -> train GPR -> WangLandauSampler -> thermodynamics (v1.5.0)
├── wang_landau/               # package
│   ├── __init__.py            #   re-exports WangLandauSampler, load_all_seeds, build_gpr, validate_gpr, K_B, g_of_E_to_thermodynamics
│   ├── wang_landau_sampler.py #   WangLandauSampler (flat-histogram density of states, v1.4.0)
│   ├── parallel_wl.py         #   Mode A parallel WL (v1.5.0): shared-state Ray actors, run_parallel_walkers
│   ├── gpr_training.py        #   load_all_seeds, build_gpr, validate_gpr
│   ├── thermodynamics.py      #   g_of_E_to_thermodynamics, heat_capacity_from_thermo
│   └── utils.py               #   K_B constant, shift_energies, _logsumexp
├── dataset/                   # Fe/MgO AGOX seed DBs (seed_3..15, 13 DBs, 1297 structs) + main.py + scripts
├── dataset_boron3/            # B3-doped (7 DBs, B3Fe25Mg25O25, 78 atoms)
├── dataset_boron/             # B7-doped (5 DBs, B7Fe25Mg25O25, 82 atoms)
├── j_wanglandau.sh            # PJM batch script (HPC launch)
├── smoke_test_wang_landau.py  # cheap local validation (fake 1-atom double-well GPR, v1.3.0)
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md / PROMPTS.md / QNA.md
├── 1_runs/                     # self-contained HPC run dirs: c1_mgofe_N40_Emax04, c2_boron3_N40_Emax04, c3_parallel_w500
├── 2_analysist/                # per-run analysed results (c1, c2) + analyze_wl_outputs.py + DISCUSSION.md
├── _archives/                 # archived artifacts
└── _tmp/                      # scratch output (holds main_wanglandau_1d.f reference + wl_output_c*_relax* runs)
```

### 2a. `1_runs/` and `2_analysist/` (per the run-directory convention)
- **`1_runs/<NN>_<descriptor>/`** — self-contained HPC run dirs, each holding
  `j_*.sh` + `main*.py` + copies of `scripts/` and `wang_landau/`, launchable in
  isolation. HPC runs carry a per-run `README.md` + `TUTORIAL.md`.
  - `c1_mgofe_N40_Emax04` — plain Fe/MgO, main.py **v1.4.0** (serial).
  - `c2_boron3_N40_Emax04` — B3-doped, main.py **v1.4.0** (serial).
  - `c3_parallel_w500` — plain Fe/MgO, main.py **v1.5.0** (`--n-walkers 500`,
    Mode A parallel). Contains `parallel_wl.py`; **note:** its `README.md`/job
    script still say `c1_parallel_w500` (copy not fully renamed).
- **`2_analysist/`** — per-run analysed results, one self-contained dir per run
  mirroring `1_runs/`, plus root-level analysis scripts (`analyze_wl_outputs.py`)
  and a `DISCUSSION.md`. Outputs regenerable/gitignored; analysis code + per-run
  docs tracked.

### 2b. Source-code versioning
Every in-scope source file carries a module-level `__version__ = "X.Y.Z"`
(semver). `VERSIONS.md` is the single-source manifest. **Bump rule:** patch on
every code edit; minor on API/behavior changes. On every edit: bump
`__version__`, update `VERSIONS.md`, record old→new in `LOG.md`. In-scope:
`main.py`, `wang_landau/`, `smoke_test_wang_landau.py`. `dataset/`, `1_runs/`
snapshots are **not** individually versioned.

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/c_landausampling

# Compile-check everything
$PY -m py_compile main.py wang_landau/*.py smoke_test_wang_landau.py

# Quick local smoke test (fake double-well GPR; no heavy training)
$PY smoke_test_wang_landau.py

# Full production run (default dataset Fe/MgO)
$PY main.py --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42

# B-doped datasets
$PY main.py --dataset dataset_boron3 ... --output ./wl_output_boron3
$PY main.py --dataset dataset_boron  ... --output ./wl_output_boron

# Mode A parallel WL (v1.5.0): N walkers share one H/ln_g via Ray actors
$PY main.py --dataset dataset --n-bins 100 --e-max 0.40 --mc-steps 30000 \
    --relax-steps 100 --n-walkers 500 --output ./wl_output_parallel --rng 42

# HPC launch (reads existing dataset/seed_*/1_db/db_*.db)
pjsub j_wanglandau.sh
```

Note: `run_parallel_walkers` lives in `wang_landau/parallel_wl.py` and is
imported directly by `main.py` (`from wang_landau.parallel_wl import
run_parallel_walkers`); it is **not** re-exported from `wang_landau/__init__.py`.

### `main.py` CLI
| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `dataset` | `dataset` \| `dataset_boron3` \| `dataset_boron`. |
| `--n-bins` | `40` | Energy bins. |
| `--e-min` / `--e-max` | `0.0` / `0.40` | Bin range (eV/atom rel). |
| `--small-step` / `--large-step` | `0.05` / `0.20` | Walk displacement scales (Å). Large reduced from 0.40 (v1.3.0) to avoid GPR-extrapolation escapes. |
| `--perturb-symbols` | `Fe` | Atoms to rattle. |
| `--flatness-criterion` | `0.80` | Flatness threshold. |
| `--check-interval` | `5000` | Flatness check interval. |
| `--n-stages-standard` | `14` | Halvings before 1/t switch. |
| `--swap-prob` | `0.0` | Probability of choosing a swap (permutation) move instead of a rattle per MC step; requires ≥2 mobile species, else no-op. |
| `--max-swaps` | `1` | Max swaps per swap move (random 1..max). |
| `--swap-rattle` | `0.05` | Gaussian displacement (Å) applied to the two swapped atoms. |
| `--relax-steps` | `0` | Basin-hopping GPR relax: if > 0, relax each trial with this many BFGS steps on the GPR (fixing non-mobile atoms) before binning. Default 0 (off). |
| `--e-reject` | `5×e_max` | Relative energy (eV/atom) above which a trial is treated as an unphysical GPR extrapolation and REJECTED (revisits current bin) instead of being capped into the top bin. Set ≤ e_max to disable. |
| `--mc-steps` | `2000000` | WL MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Thermodynamics temperatures. |
| `--start-from-top` | off | Init at top of bin range (default off = start from the global minimum, bottom-up). |
| `--start-from-min` | off | Explicitly initialize from the global minimum (default behaviour; `--start-from-top` + `--start-from-min` → min wins). |
| `--output` | `./wl_output` | Output dir. |
| `--rng` | `42` | Seed. |
| `--use-ray` | off | Enable Ray in GPR. |
| `--n-walkers` | `1` | **Mode A parallel WL** (v1.5.0): N concurrent Wang–Landau walkers sharing one histogram `H`/`ln_g` via Ray actors; seeds `--rng+i`; flatness/refinement act on the combined histogram. `N=1` = serial. |

## 4. Dependencies & environment
- Conda env **`agox_v2`** (AGOX 3.10.2, ASE 3.25.0, Ray) — **local** dev/test.
- HPC pjsub heavy run uses **`gpaw_env`** (`j_wanglandau.sh`). **Caveat:** the
  sampling script needs the AGOX/ASE stack from `agox_v2`; if `gpaw_env` lacks
  it, switch `conda activate gpaw_env` → `conda activate agox_v2` before
  submitting.
- `matplotlib.use("Agg")` before plotting in headless runs.
- `GPR(..., use_ray=False)` default (single-process) avoids Ray actors.

## 5. Inputs / Outputs
**Inputs:** `dataset/seed_*/1_db/db_*.db` (and boron variants). No external
inputs.

**Outputs** (under `--output`): `g_of_E.csv`, `g_of_E.png`,
`thermodynamics.csv`, `heat_capacity.csv`. All regenerable/gitignored.

## 6. Error handling & edge cases
1. **No DBs matched** → `FileNotFoundError` from `load_all_seeds` if the glob is
   empty (check the dataset dir exists / --dataset spelling).
2. **Composition mismatch breaks the descriptor** — a single global `Fingerprint`
   supports one stoichiometry per dataset; each dataset is internally uniform
   (verified). Don't mix datasets in one GPR.
3. **No DB structure inside the bin range** → `RuntimeError` from
   `initialize()`; lower `--e-max` or widen the range.
4. **GPR extrapolation to unphysical energies** — with `--large-step`/`--perturb`
   too large the Fingerprint GPR predicts `|E|>1e4 eV` (treated as out-of-range in
   `_energy_of`) OR a high but finite relative energy far above the window. The
   rel-energy **extrapolation guard** (`--e-reject`, default `5×e_max`) rejects any
   trial with rel E > e_reject as unphysical — it is NOT capped into the top bin
   (which would trap the walk in a delta g(E)). Moderate over-window energies
   (e_max .. e_reject) are still capped into the top bin (Fortran behaviour). This
   fixes the c1/c2 delta-at-top-bin collapses.
5. **Ray `ActorUnavailableError`** — environmental (RAM exhaustion); avoided with
   `use_ray=False` (default).
6. **1/t switch not reached** — if `--mc-steps` is too small or
   `--n-stages-standard` too large, the run ends in the standard scheme (the
   sampler prints a NOTE). Increase `--mc-steps` or lower `--n-stages-standard`.
7. **Swap move with a single mobile species** — `--swap-prob` is ignored (with a
   WARNING) and the walk falls back to rattling only. Swap requires ≥2 distinct
   species among `--perturb-symbols` (e.g. `Fe,B` in the boron datasets).

## 7. Provenance / references
- Algorithm reference: `_tmp/main_wanglandau_1d.f` (Fortran 1D toy, kept as the
  pedagogical skeleton; `_tmp/` is gitignored scratch).
- Sibling project: `_run/b_nestedsampling/` (same problem via nested sampling).
- Literature: Wang & Landau 2001 (PRL 86, 2050); Belardinelli & Pereyra 2007
  (JCP 127, 184105) — the 1/t algorithm.
- Skills: `ai-agent-project-workflow`, `agox-nested-sampling`, `agox`,
  `simulation-analysis`, `agox-run-code`.
