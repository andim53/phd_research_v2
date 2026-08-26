# Kappa x novelty_weight sweep benchmark (worked example)

Session detail for the `agox-novelty-lcb` skill. Captures how to sweep the two
Novelty-LCB tuning knobs over the same EMT surface as the baseline benchmark, and the
reusable "import + override module config" pattern for reusing a sibling benchmark's
helpers without duplicating them.

Reference implementation (in `/home/think/Desktop/research/_run/a_lcbnovel/`, renamed
from `10_lcbnovel`):
- `main_benchmark_sweep.py` — the sweep driver.
- `j_benchmark_sweep.sh` — PJM batch script (gpaw_env, 64-core, elapse 02:00:00).
- Reuses `main_benchmark.py` (`build_system`, `build_stack`, `run_single`,
  `compute_discovery_curve`).

## What it sweeps

Grid (full cross product, Novelty-LCB ONLY):
- `KAPPA_LIST = [0.5, 1.0, 2.0, 4.0]`
- `NOVELTY_WEIGHT_LIST = [0.0, 0.5, 1.0, 1.5, 2.0]`
- = 20 combos, 1 fixed seed per combo (seed 41), N_ITERATIONS=30.

The acquisitor stays in auto global-minimum per-atom window mode
(`energy_above_min=0.1` eV/atom, `per_atom=True`) — the knobs being swept are
`kappa` (LCB relaxation surface width) and `novelty_weight` (lambda, novelty term
weight), NOT the window.

## Reusable pattern: import a sibling benchmark + override module config

To keep the swept system byte-identical to the baseline benchmark without copying the
helpers:

```python
import main_benchmark as mb

def run_combo(kappa, novelty_weight, seed=41, n_iterations=30):
    # save originals
    old = {k: getattr(mb, k) for k in
           ("KAPPA", "NOVELTY_WEIGHT", "N_ITERATIONS", "NOVELTY_ENERGY_ABOVE_MIN",
            "NOVELTY_ENERGY_PER_ATOM", "DUP_THRESHOLD", "OUTDIR")}
    mb.KAPPA = kappa
    mb.NOVELTY_WEIGHT = novelty_weight
    mb.N_ITERATIONS = n_iterations
    mb.NOVELTY_ENERGY_ABOVE_MIN = 0.1
    mb.NOVELTY_ENERGY_PER_ATOM = True
    mb.DUP_THRESHOLD = 1.5
    combo_out = os.path.join(OUTDIR, f"k{kappa}_l{novelty_weight}")
    os.makedirs(combo_out, exist_ok=True)
    mb.OUTDIR = combo_out
    try:
        result = mb.run_single(seed, f"k{kappa}_l{novelty_weight}", "novelty_lcb")
        result["kappa"] = kappa
        result["novelty_weight"] = novelty_weight
        return result
    finally:
        for k, v in old.items():
            setattr(mb, k, v)
```

Key points:
- `mb.run_single(seed, label, "novelty_lcb")` reads `mb.KAPPA`, `mb.NOVELTY_WEIGHT`,
  `mb.NOVELTY_ENERGY_ABOVE_MIN`, `mb.NOVELTY_ENERGY_PER_ATOM`, `mb.DUP_THRESHOLD`, and
  `mb.OUTDIR` at call time — so overriding them works. `build_stack` wires them into the
  acquisitor.
- **Restore in `try/finally`** so a failed combo does not corrupt later combos.
- Route each combo's DB into its own subdir so DBs don't collide.

## Outputs

Written to `benchmark_results/sweep_kappa_lambda/`:
- `sweep_results.json` — full per-combo results dicts (metrics + kappa/lambda).
- `sweep_heatmaps.png` — 3 heatmaps (distinct / best-E / duplicates) as kappa x lambda.
- `sweep_curves.png` — each metric vs lambda, one line per kappa.
- `sweep_discovery.png` — all combos' discovery curves overlaid.

## Validation without running the full sweep

`py_compile` the sweep driver, then a lightweight import check that the grid + helpers
resolve (no AGOX run):

```python
import itertools, main_benchmark_sweep as s
len(list(itertools.product(s.KAPPA_LIST, s.NOVELTY_WEIGHT_LIST)))  # 20
callable(s.mb.run_single) and callable(s.mb.build_system)          # True
```

## Caveat

Same as the baseline benchmark: `main_benchmark.py` uses AGOX `ParallelCollector` /
`ParallelRelaxPostprocess` (Ray pool), which OOMs on low-RAM nodes with
`ActorUnavailableError`. Run the sweep on a RAM-rich node / HPC (`pjsub j_benchmark_sweep.sh`).
Validate the window logic standalone with `test_window_logic.py` instead (no Ray).
