# Extended Novelty-LCB vs Regular-LCB Benchmark (EMT) — Run 73

## What this benchmark does

This is the **extended EMT benchmark** of the Novelty-LCB acquisition function against
plain Regular-LCB, run on a fast model system: **Ni8 deposited on an Au(4,4,2) fcc100
surface**, evaluated with the **EMT** calculator.

The purpose is to map how the search behaves as two parameters are pushed to larger
values than the earlier 5-seed / 30-iteration / λ=1.5 benchmark (project 73, single
config):

- **more seeds** — 10 independent seeds for better statistics,
- **more iterations** — 100, 200, 300, 400, 500 per run,
- **higher novelty weight λ** — 2.0, 3.0, 4.0, 5.0 in `a(x) = σ(x) + λ·Novelty(x)`.

The physics and pipeline are unchanged from the parent Novelty-LCB work: both
acquisitors share the same system, generators, sampler, relaxer and evaluator; only the
acquisitor differs. Novelty-LCB uses the **auto global-minimum energy window** (no
manual calibration / regular-LCB-first step).

## Why this benchmark exists

The earlier single-config benchmark (5 seeds, 30 iterations, λ=1.5) suggested two
questions worth probing on a larger grid:

1. **Does a higher novelty weight λ (2–5) change the exploration / diversity balance?**
   At λ=1.5 the novelty term had a small, never-negative diversity edge but a
   consistent energy penalty vs regular LCB.
2. **Does giving the search more iterations (100–500) change the picture?** Longer runs
   let each acquisitor explore further, which could alter the duplicate-heavy behaviour
   seen at 30 iterations (~97% duplicates).

This grid benchmark answers those questions with 250 AGOX runs.

## How it works

- **Acquisitors (only difference between the two):**
  - **Regular LCB** (`LowerConfidenceBoundAcquisitor`): `μ(x) − κ·σ(x)`, **minimized**.
  - **Novelty-LCB** (`NoveltyLCBAcquisitor`): `σ(x) + λ·Novelty(x)`, **maximized**,
    subject to the energy window `E/N ≤ E_min/N + X` (per atom), where `Novelty(x)` is
    the min fingerprint distance to all DB structures.
- **Same stack both ways:** Au fcc100 template, `Ni8` deposited, EMT calculator,
  Fingerprint descriptor (720-dim), GPR surrogate with a compound RBF kernel, KMeans
  sampler, `ParallelCollector` / `ParallelRelaxPostprocess` (Ray pool).
- **Grid:** `SEED_LIST` (10) × `N_ITERATIONS_LIST` (5) × `NOVELTY_WEIGHT_LIST` (4).
- **Run count:**
  - Regular LCB: once per (iterations × seed) = **50 runs**.
  - Novelty-LCB: once per (iterations × weight × seed) = **200 runs**.
  - **Total = 250 AGOX runs** — this is a large compute job; run it on the HPC node.

## Key configuration

| Parameter | Value | Meaning |
|---|---|---|
| `SYMBOLS` / `TEMPLATE_SIZE` | `Ni8` / `Au(4,4,2)` | Deposited cluster / substrate |
| `CALCULATOR` | EMT | Fast model potential |
| `SEED_LIST` | 41,101,201,301,401,501,601,701,801,901 | 10 independent seeds |
| `N_ITERATIONS_LIST` | 100, 200, 300, 400, 500 | Iterations per run |
| `NOVELTY_WEIGHT_LIST` | 2.0, 3.0, 4.0, 5.0 | λ in `σ + λ·Novelty` |
| `KAPPA` | 2.0 | LCB / relaxation-surface parameter |
| `NOVELTY_ENERGY_ABOVE_MIN` | 1.0 eV/atom (per_atom) | Window height above live global min (≈ +40 eV on 40 atoms) |
| `DUP_THRESHOLD` | 1.5 | Fingerprint-distance cutoff for "distinct configuration" |

## How to use it

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/a_lcbnovel/1_runs/73_novel_benchEMT

# Local (needs a RAM-rich node — the AGOX ParallelCollector/RelaxPostprocess use a Ray
# pool that OOMs on a low-RAM machine with Ray ActorUnavailableError)
$PY main_benchmark.py

# On HPC:
pjsub j_benchmark.sh
```

## Outputs

Written to `benchmark_results/`:

- `benchmark_results.json` — flat list of every run's metrics, each entry carrying
  `seed`, `n_iterations`, `novelty_weight` (None for regular), `kappa`, plus
  distinct configs, best energy, energy range, duplicates, eval counts and timing.
  Also records the grid parameters and the 250-run total.
- `benchmark_grid.png` — a 5×3 grid of panels (one row per iteration value) showing
  best energy, distinct configs and duplicate evals vs `novelty_weight`, with the
  Regular-LCB reference line overlaid.
- `benchmark_discovery.png` — discovery curves (cumulative distinct configs vs
  cumulative evals) per iteration block, one line per λ plus the Regular-LCB average.
- Per-run databases `i{niter}[_l{weight}]*_db.db` (one per AGOX run; regenerable).

These are regenerable artifacts and are gitignored.

## Key decisions & tradeoffs

| Decision | Choice | Why |
|---|---|---|
| Model system | Ni8/Au(4,4,2), EMT | Fast surrogate to run 250 searches cheaply and study parameter trends |
| Grid | 10 seeds × 5 iterations × 4 weights | Full factorial to separate the effects of seeds, budget and λ |
| Iteration range | 100–500 | Probes whether longer runs change the duplicate-heavy / diversity picture seen at 30 |
| Novelty weight range | 2.0–5.0 | Extends beyond the earlier λ=1.5 to test stronger diversity pressure |
| Regular LCB runs | once per (iterations × seed) | Regular is independent of λ, so it is not repeated per weight |
| Output data | flat JSON list + grid/discovery plots | One self-contained record of all 250 runs |

## Status

- [x] `main_benchmark.py` edited to the extended grid (10 seeds, iter 100–500, λ 2–5).
- [x] Script compiles under `agox_v2`.
- [ ] Benchmark submitted / run on HPC (`pjsub j_benchmark.sh`).
- [ ] Results analysed (see `DISCUSSION.md` once the run completes).

See `README.AI.md` for the agent-facing spec, `TUTORIAL.md` for how to reproduce the
run, and `LOG.md` for the action log.
