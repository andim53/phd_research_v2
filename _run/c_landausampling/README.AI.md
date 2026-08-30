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
├── main.py                    # Entry point: load dataset -> train GPR -> WangLandauSampler -> thermodynamics
├── wang_landau/               # package
│   ├── __init__.py            #   re-exports WangLandauSampler, load_all_seeds, build_gpr, validate_gpr, K_B, g_of_E_to_thermodynamics
│   ├── wang_landau_sampler.py #   WangLandauSampler (flat-histogram density of states)
│   ├── gpr_training.py        #   load_all_seeds, build_gpr, validate_gpr
│   ├── thermodynamics.py      #   g_of_E_to_thermodynamics, heat_capacity_from_thermo
│   └── utils.py               #   K_B constant, shift_energies, _logsumexp
├── dataset/                   # Fe/MgO AGOX seed DBs (seed_3..15, 13 DBs, 1297 structs) + main.py + scripts
├── dataset_boron3/            # B3-doped (7 DBs, B3Fe25Mg25O25, 78 atoms)
├── dataset_boron/             # B7-doped (5 DBs, B7Fe25Mg25O25, 82 atoms)
├── j_wanglandau.sh            # PJM batch script (HPC launch)
├── smoke_test_wang_landau.py  # cheap local validation (fake 1-atom double-well GPR)
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md / PROMPTS.md
├── _runs/                     # (scaffolded) self-contained run dirs (HPC)
├── _analysist/                # (scaffolded) per-run analysed results
├── _archives/                 # (scaffolded) archived artifacts
└── _tmp/                      # scratch output (holds main_wanglandau_1d.f reference)
```

### 2a. `_runs/` and `_analysist/` (scaffolded, per the run-directory convention)
- **`_runs/<NN>_<descriptor>/`** — self-contained HPC run dirs, each holding
  `j_*.sh` + `main*.py` + copies of `scripts/` and `wang_landau/`, launchable in
  isolation. HPC runs carry a per-run `README.md` + `TUTORIAL.md`.
- **`_analysist/`** — per-run analysed results, one self-contained dir per run
  mirroring `_runs/`, plus root-level analysis scripts and an archived
  `_archive/`. Outputs regenerable/gitignored; analysis code + per-run docs
  tracked.

### 2b. Source-code versioning
Every in-scope source file carries a module-level `__version__ = "X.Y.Z"`
(semver). `VERSIONS.md` is the single-source manifest. **Bump rule:** patch on
every code edit; minor on API/behavior changes. On every edit: bump
`__version__`, update `VERSIONS.md`, record old→new in `LOG.md`. In-scope:
`main.py`, `wang_landau/`, `smoke_test_wang_landau.py`. `dataset/`, `_runs/`
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
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42

# B-doped datasets
$PY main.py --dataset dataset_boron3 ... --output ./wl_output_boron3
$PY main.py --dataset dataset_boron  ... --output ./wl_output_boron

# HPC launch (reads existing dataset/seed_*/1_db/db_*.db)
pjsub j_wanglandau.sh
```

### `main.py` CLI
| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `dataset` | `dataset` \| `dataset_boron3` \| `dataset_boron`. |
| `--n-bins` | `40` | Energy bins. |
| `--e-min` / `--e-max` | `0.0` / `0.40` | Bin range (eV/atom rel). |
| `--small-step` / `--large-step` | `0.05` / `0.40` | Walk displacement scales (Å). |
| `--perturb-symbols` | `Fe` | Atoms to rattle. |
| `--flatness-criterion` | `0.80` | Flatness threshold. |
| `--check-interval` | `5000` | Flatness check interval. |
| `--n-stages-standard` | `14` | Halvings before 1/t switch. |
| `--swap-prob` | `0.0` | Probability of choosing a swap (permutation) move instead of a rattle per MC step; requires ≥2 mobile species, else no-op. |
| `--max-swaps` | `1` | Max swaps per swap move (random 1..max). |
| `--swap-rattle` | `0.05` | Gaussian displacement (Å) applied to the two swapped atoms. |
| `--mc-steps` | `2000000` | WL MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Thermodynamics temperatures. |
| `--start-from-top` | on | Init at top of bin range. |
| `--output` | `./wl_output` | Output dir. |
| `--rng` | `42` | Seed. |
| `--use-ray` | off | Enable Ray in GPR. |

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
   too large the Fingerprint GPR predicts `|E|>1e4 eV`; such trials are treated
   as out-of-range (rejected) in `_energy_of`/`run`.
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
