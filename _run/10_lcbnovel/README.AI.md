# README for AI Agents — Project 10 (`10_lcbnovel`)

Machine-readable spec for agents working on this project. This complements the
human-facing `README.md`.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/10_lcbnovel/`
- **Purpose:** Faithful repair + re-host of the Fe/MgO Novelty-LCB AGOX search from
  `_run/7_lcbnovel_mgofe`, under the AI-Agent Project Workflow.
- **Physics:** 25 mobile Fe atoms deposited on a fixed MgO(001) substrate
  (Mg25O25 + Fe25 = 75 atoms), Novelty-LCB acquisition, GPAW LCAO/dzp DFT.
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0 + GPAW). Base `python3` has **no** AGOX/ASE/GPAW.

## 2. File layout

```
10_lcbnovel/
├── main.py                     # Entry point: per-seed AGOX run (CLI)
├── smoke_test_serialization.py # Cheap local validation of the serialization fix
├── j_novel.sh                  # PJM batch script (HPC launch, one seed per job)
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
└── TUTORIAL.md                 # Reproduce + repair guide with pitfalls
```

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/10_lcbnovel

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
3. **Uncalibrated energy window** (`target=0.0, ΔE=1.0`) — may exclude most/all
   candidates. Must map the real energy band first (TUTORIAL step 5) before trusting
   Novelty-LCB results. Placeholder values are intentional, flagged as TODO.
4. **GPAW needs HPC** — `SubprocessGPAW(..., ncores=64, mode=lcao, basis=dzp)` targets a
   64-core cluster node. Do not run the full `main.py` locally with GPAW.
5. **Composition uniformity** — all candidates must share one stoichiometry/atom count
   for a single global `Fingerprint` descriptor. The Fe/MgO setup is uniform by
   construction (MgO substrate fixed, Fe deposited).

## 7. Provenance / references

- Upstream project (buggy): `_run/7_lcbnovel_mgofe/` (`main.py`, `j_novel.sh`,
  `j_novel.sh.6543317.out` = the crash log).
- Troubleshooting guide: `_md/for-agent/novelty_lcb_agox_troubleshooting.md`
  (bugs A/B/C, AGOX internals, verification checklist).
- Related downstream analysis: `_run/8_nested_sampling/`, `_run/9_novelFilter/`.
- Skills: `agox`, `agox-novel-filter`, `agox-nested-sampling`, `simulation-analysis`,
  `agox-run-code`.
