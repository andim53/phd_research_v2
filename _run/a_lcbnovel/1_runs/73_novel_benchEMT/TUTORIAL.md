# TUTORIAL — Reproduce the Extended Novelty-LCB vs Regular-LCB EMT Benchmark

Step-by-step guide to run the extended grid benchmark (10 seeds × iterations 100–500 ×
novelty weight 2–5 = 250 AGOX runs) on Ni8/Au(4,4,2) with the EMT calculator, and to
interpret its outputs. Written so a fresh agent (or you) can redo the work.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0 + EMT + Ray).
  Python: `/home/think/miniconda3/envs/agox_v2/bin/python`. **Local** dev/test.
- HPC pjsub run uses **`gpaw_env`** (set in `j_benchmark.sh`) — the same env that runs
  the Fe/MgO AGOX search; it must have AGOX/ASE/EMT.
- A RAM-rich node / HPC cluster with PJM batch (`pjsub`, 24-core node in
  `j_benchmark.sh`) because the AGOX `ParallelCollector`/`ParallelRelaxPostprocess` use
  a Ray pool that OOMs a low-RAM machine.

## Step 1 — Understand what the benchmark does

The benchmark compares two acquisitors on the **same** system, seeds, generators,
sampler, relaxer and evaluator — only the acquisitor differs:

- **Regular LCB**: `μ(x) − κ·σ(x)`, minimized.
- **Novelty-LCB**: `σ(x) + λ·Novelty(x)`, maximized, within an **auto global-minimum
  energy window** `E/N ≤ E_min/N + X` (per atom, `X` = 1.0 eV/atom).

It sweeps a grid of `SEED_LIST` (10 seeds) × `N_ITERATIONS_LIST` (100–500) ×
`NOVELTY_WEIGHT_LIST` (2.0–5.0). Regular LCB runs once per (iterations × seed);
Novelty-LCB runs once per (iterations × weight × seed). Total **250 AGOX runs** — a
large compute job.

## Step 2 — Compile-check

```bash
cd /home/think/Desktop/research/_run/a_lcbnovel/1_runs/73_novel_benchEMT
/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile main_benchmark.py
```

Expected: no output, exit 0. (LSP/IDE may flag AGOX imports under base `python3` —
ignore those; the env python is authoritative.)

## Step 3 — Review the configuration

The grid is set by top-level constants at the top of `main_benchmark.py`:

- `SEED_LIST = [41,101,201,301,401,501,601,701,801,901]`
- `N_ITERATIONS_LIST = [100,200,300,400,500]`
- `NOVELTY_WEIGHT_LIST = [2.0,3.0,4.0,5.0]`
- `KAPPA = 2.0`, `NOVELTY_ENERGY_ABOVE_MIN = 1.0` (per_atom), `DUP_THRESHOLD = 1.5`.

Edit these lists to change the grid. They are read directly by the loop in `main()`.

## Step 4 — Run the benchmark

```bash
# Local (needs a RAM-rich node):
/home/think/miniconda3/envs/agox_v2/bin/python main_benchmark.py

# On HPC:
pjsub j_benchmark.sh        # monitor: pjstat  |  cancel: pjdel
```

Expected startup output (echoed by `main()`): the grid summary and the run counts
(50 Regular + 200 Novelty = 250 total). Then one block per run, ending with each run's
`distinct / evals / best_E / time`. After all runs it writes the JSON, the grid plot
and the discovery plot.

## Step 5 — Outputs

Written to `benchmark_results/`:

- `benchmark_results.json` — flat list of every run's metrics: `seed`,
  `n_iterations`, `novelty_weight` (None for regular), `kappa`, `n_evals`,
  `n_distinct`, `n_duplicates`, `best_E`, `e_range`, `distinct_energies`,
  `all_energies`, timing; plus the grid parameters and the 250-run total.
- `benchmark_grid.png` — 5×3 grid of panels (rows = iteration values). Each panel
  plots a metric (best energy / distinct configs / duplicate evals) vs
  `novelty_weight`, with mean ± std over the 10 seeds for Novelty-LCB and the
  Regular-LCB mean as a dashed reference line.
- `benchmark_discovery.png` — discovery curves (cumulative distinct configs vs
  cumulative evals) per iteration block, one line per λ plus the Regular-LCB average.
- Per-run databases `i{iter}[_l{weight}]_run{NN}_{acq}_db.db`.

## Step 6 — Interpret the results

Key questions the grid answers:

1. **Effect of λ (2–5):** does a stronger novelty weight change diversity (distinct
   configs) vs energy optimality (best E)? Look at the slope of the panels in
   `benchmark_grid.png` vs `novelty_weight`.
2. **Effect of budget (100–500):** does a longer run change the duplicate rate or the
   discovery plateau? Compare rows across `benchmark_grid.png` / the panels in
   `benchmark_discovery.png`.
3. **Seed spread:** the ±std bars in the grid plot show how much each configuration
   varies across the 10 seeds (statistical reliability).

For a written discussion, update `DISCUSSION.md` (per-graph what/means/implies/outcome,
grounded in the JSON numbers).

## Common pitfalls

1. **`cannot pickle 'sqlite3.Connection'`** — never pass bound methods into
   `LowerConfidenceBoundCalculator`; use `functools.partial` over module-level free
   functions (already fixed in the copied `novelty_lcb` package).
2. **`LocalOptimizationEvaluator` missing `calculator`** — kwargs key must be
   `calculator`, not `calc` (set correctly in `evaluator_kwargs`).
3. **Ray `ActorUnavailableError` on low RAM** — the AGOX parallel pool needs a
   RAM-rich node / HPC. Don't run the full 250-run benchmark on a small local machine.
4. **Large job** — 250 runs × up to 500 iterations is slow; submit via
   `pjsub j_benchmark.sh` and monitor with `pjstat`. Consider trimming the lists for a
   quick smoke test first.
5. **Env split — local vs HPC.** Local compile/dev uses `agox_v2`; the HPC batch run
   uses `gpaw_env` (set in `j_benchmark.sh`). Base `python3` has no AGOX.
6. **`USE_RAY`** — `True` is fine on the HPC node; on a low-RAM local node it can OOM
   the GPR actors. `False` reduces actors but does not remove the parallel pool.

## Verification checklist

- [ ] `py_compile main_benchmark.py` passes under `agox_v2`
- [ ] `main()` echoes the correct grid (10 seeds, iter 100–500, λ 2–5) and 250-run total
- [ ] `benchmark_results.json` contains 250 entries (50 regular + 200 novelty)
- [ ] `benchmark_grid.png` and `benchmark_discovery.png` are generated
- [ ] Per-run DB files are named `i{iter}[_l{weight}]_run{NN}_{acq}_db.db`
- [ ] Results discussed in `DISCUSSION.md`
