# README for AI Agents — Run 73: Extended Novelty-LCB vs Regular-LCB EMT Benchmark

Machine-readable spec for agents working on this project. Complements the
human-facing `README.md`.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/10_lcbnovel/_runs/73_novel_benchEMT/`
- **Purpose:** Extended grid EMT benchmark comparing **Novelty-LCB** (auto
  global-minimum window) vs **Regular LCB** on Ni8/Au(4,4,2) fcc100, over a
  **10-seed × 5-iteration × 4-novelty-weight** grid = **250 AGOX runs**.
- **Calculator:** EMT (fast model potential, no GPAW).
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0 + EMT). Base `python3` has **no** AGOX/ASE.

## 2. File layout

```
73_novel_benchEMT/
├── main_benchmark.py           # Extended grid benchmark (this is the entry point)
├── j_benchmark.sh              # PJM batch script (HPC launch)
├── benchmark_results/          # Output: JSON + plots + per-run DBs (regenerable)
├── novelty_lcb/                # PROVEN package (NoveltyLCBAcquisitor + LCB calc)
│   ├── __init__.py             #   re-exports NoveltyLCBAcquisitor, is_distinct, ...
│   ├── acquisitor.py           #   NoveltyLCBAcquisitor + free-func LCB calculator
│   ├── utils.py, common.py, benchmark_helpers.py
├── scripts/                    # Slab/generator builders (copied from run 7)
├── README.md                   # Human overview
├── README.AI.md                # This file (agent spec)
├── LOG.md                      # Curated, append-only action log
├── TUTORIAL.md                 # Reproduce guide with pitfalls
├── DISCUSSION.md               # Results discussion (after the run)
└── AGENTS.md                   # Governing rules (parent 10_lcbnovel)
```

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/10_lcbnovel/_runs/73_novel_benchEMT

# Compile-check
$PY -m py_compile main_benchmark.py

# Local (needs a RAM-rich node — AGOX Ray pool)
$PY main_benchmark.py

# On HPC
pjsub j_benchmark.sh           # monitor: pjstat  |  cancel: pjdel
```

### `main_benchmark.py` configuration (top-level constants)

| Constant | Value | Meaning |
|---|---|---|
| `SEED_LIST` | 41,101,201,301,401,501,601,701,801,901 | 10 independent seeds |
| `N_ITERATIONS_LIST` | 100, 200, 300, 400, 500 | iterations per run |
| `NOVELTY_WEIGHT_LIST` | 2.0, 3.0, 4.0, 5.0 | λ in `σ + λ·Novelty` |
| `KAPPA` | 2.0 | LCB / relaxation-surface parameter |
| `NOVELTY_ENERGY_ABOVE_MIN` | 1.0 eV/atom | auto-window height above live global min |
| `NOVELTY_ENERGY_PER_ATOM` | True | interpret energy_above_min in eV/atom |
| `DUP_THRESHOLD` | 1.5 | distinct-configuration fingerprint cutoff |
| `SAMPLE_SIZE` | 10 | KMeansSampler sample size |
| `USE_RAY` | True | GPR hyperparameter optimisation via Ray |
| `NUM_CANDIDATES` | `{0:[10,0], 5:[3,7]}` | generator candidate schedule |
| `RELAX_STEPS` / `START_RELAX` | 5 / 8 | relaxation settings |
| `OPT_FMAX` / `OPT_STEPS` | 0.05 / 1 | evaluator optimizer |

### Loop / run structure

`main()` loops over `N_ITERATIONS_LIST` × `SEED_LIST` × `NOVELTY_WEIGHT_LIST`:

- For each (iterations, seed): run **Regular LCB** once (λ-independent).
- For each (iterations, weight, seed): run **Novelty-LCB** once.

`run_single(seed, label, acq_type, n_iterations, novelty_weight)` runs one AGOX search
and returns a metrics dict. `build_stack(acq_type, db_path, seed, kappa, novelty_weight)`
builds the shared AGOX stack; only the acquisitor differs between the two types.

## 4. Dependencies & environment

- Conda env **`agox_v2`** (AGOX 3.10.2, ASE 3.25.0, EMT, Ray) — local dev/test.
- HPC pjsub run uses **`gpaw_env`** (set in `j_benchmark.sh`; same env that runs the
  Fe/MgO AGOX search — assumes it has AGOX/ASE/EMT).
- `matplotlib.use("Agg")` before plotting (headless-safe).
- Ray is started internally by AGOX (parallel pool); harmless stderr noise expected.
- On low-RAM local nodes `USE_RAY=True` can OOM the GPR actors
  (`ActorUnavailableError`); the benchmark is intended for a RAM-rich node / HPC.

## 5. Inputs / Outputs

**Inputs:** none external — the Ni8/Au(4,4,2) slab is built in `build_system()` from
first principles (ASE `fcc100` template + deposited `Ni8`).

**Outputs** (in `benchmark_results/`):
- `benchmark_results.json` — flat list of every run's metrics (seed, n_iterations,
  novelty_weight [None for regular], kappa, n_evals, n_distinct, n_duplicates,
  best_E, e_range, distinct_energies, all_energies, timing) plus the grid parameters
  and the 250-run total.
- `benchmark_grid.png` — 5×3 grid of panels (rows = iterations) showing best energy,
  distinct configs, duplicates vs `novelty_weight`, with Regular-LCB reference line.
- `benchmark_discovery.png` — discovery curves per iteration block, one line per λ +
  the Regular-LCB average.
- `i{niter}[_l{weight}]_run{NN}_{acq}_db.db` — per-run AGOX sqlite databases
  (regenerable).

All outputs are regenerable artifacts and gitignored.

## 6. Error handling & edge cases

1. **Ray sqlite-pickle crash** (`cannot pickle 'sqlite3.Connection'`) — the run-7 bug.
   Root cause: passing bound methods into `LowerConfidenceBoundCalculator` drags the
   sqlite-backed `Database` into the Ray pool. **Fix (present in the copied package):**
   `get_acquisition_calculator()` returns `LowerConfidenceBoundCalculator(model,
   partial(lcb_acquisition_energy, kappa=...), partial(lcb_acquisition_force,
   kappa=...))` using **module-level free functions**.
2. **`LocalOptimizationEvaluator.__init__() missing 'calculator'`** — kwargs key must
   be `calculator`, not `calc`; `main_benchmark.py` passes it in `evaluator_kwargs`.
3. **Energy window mode** — auto global-minimum, per-atom: window `(-inf, E_min/N + X]`
   with `X` = `NOVELTY_ENERGY_ABOVE_MIN` (1.0 eV/atom → ≈ +40 eV on the 40-atom cell).
   No manual calibration / regular-LCB-first step.
4. **Benchmark needs RAM for the Ray pool** — `ParallelCollector` /
   `ParallelRelaxPostprocess` use Ray; on a low-RAM node this fails with
   `ActorUnavailableError`. Run on a RAM-rich node / HPC (`pjsub j_benchmark.sh`).
   `USE_RAY=False` reduces GPR actors but does not remove the parallel pool.
5. **Large job** — 250 AGOX runs; a full local run is slow / memory-heavy. Prefer HPC.
6. **DB naming** — labels include iteration and (for novelty) weight so per-run
   databases never collide: `i{iter}_run{NN}_regular_db.db` and
   `i{iter}_l{weight}_run{NN}_novelty_db.db`.

## 7. Provenance / references

- Parent project: `_run/10_lcbnovel/` (Novelty-LCB Fe/MgO, AGENTS.md governing rules).
- Earlier single-config benchmark: `_analysist/1_result/73_novel_benchEMT/`
  (5 seeds, 30 iterations, λ=1.5 — the run this grid extends).
- Related sweep: `_analysist/1_result/74_novel_benchSweep/`
  (kappa × novelty_weight on the same system, 1 seed per combo).
- Skills: `agox`, `agox-run-code`, `ai-agent-project-workflow`, `simulation-analysis`.
