# TUTORIAL — Reproduce & repair the Novelty-LCB Fe/MgO search

Step-by-step guide to reproduce this project from scratch, validate the fix, and
launch the heavy search. Written so a fresh agent (or you) can redo the work.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0 + GPAW + Ray).
  Python: `/home/think/miniconda3/envs/agox_v2/bin/python`.  **Local** dev/test.
- HPC pjsub heavy run uses **`gpaw_env`** (set in `j_novel.sh`).
- AGOX Fe/MgO upstream code: `_run/7_lcbnovel_mgofe/` (the buggy-but-most-complete
  attempt to repair from).
- HPC cluster with PJM batch (for the heavy run) — `pjsub`, 64-core GPAW nodes.

## Step 0 — Understand what "reproduce run 7" means

Run 7 **never completed**: it crashed at seed 3 with
`cannot pickle 'sqlite3.Connection' object`. The acquisitor fix was applied *after*
the failed run and never re-tested. So the task is to (a) copy the fixed package,
(b) re-wire `main.py`, (c) validate the fix cheaply, then (d) launch on HPC.

## Step 1 — Copy the proven code

```bash
SRC=/home/think/Desktop/research/_run/7_lcbnovel_mgofe
DST=/home/think/Desktop/research/_run/10_lcbnovel
mkdir -p $DST/novelty_lcb $DST/scripts
cp $SRC/novelty_lcb/*.py $DST/novelty_lcb/
cp $SRC/scripts/{build_mgo_stack,build_fe_stack,build_heteroStruct,hetero_struct_randomize,plot_structure}.py $DST/scripts/
```

## Step 2 — Compile-check

```bash
cd /home/think/Desktop/research/_run/10_lcbnovel
/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile main.py novelty_lcb/*.py scripts/*.py
```

Expected: no output, exit 0. (LSP/IDE may flag AGOX imports under base `python3` —
ignore those; the env python is authoritative.)

## Step 3 — Validate the serialization fix (cheap, no GPAW)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python smoke_test_serialization.py
```

This builds a tiny EMT system and walks the exact run-7 crash path
(`get_acquisition_calculator()` → `ParallelRelaxPostprocess`). Expected final line:

```
RESULT: PASS -- run-7 serialization crash is fixed at code level.
```

If it FAILS, the acquisition calculator still drags a non-picklable object into the
Ray pool. Debug with `ray.util.inspect_serializability(calc)` and check the acquisitor
passes `functools.partial(...)` over **module-level** functions (not bound methods).

## Step 4 — Launch the heavy search on HPC

Each heavy run lives in its own **self-contained directory** under `_runs/`, named
`<NN>_<descriptor>` (e.g. `1_mgofe_Seed3_Iter300`). `cd` into the run dir, then
`pjsub` its job script. The seed and iteration count are set by editing `SEED=` and
`N_ITERATIONS=` at the top of that run's `j_*.sh` (the owner prefers this over
passing `-x SEED=N`). The job activates `gpaw_env` (NOT `agox_v2`).

```bash
cd /home/think/Desktop/research/_run/10_lcbnovel/_runs/<NN>_<descriptor>   # e.g. 1_mgofe_Seed3_Iter300
# edit SEED= / N_ITERATIONS= in j_*.sh if needed
pjsub j_*.sh            # e.g. j_novEperAtom.sh — runs the seed set in the script
# monitor: pjstat   |   cancel: pjdel
```

The `_runs/<NN>_<descriptor>/` dir carries everything the job needs (its own
`main.py`, `scripts/`, `novelty_lcb/`), so it is fully isolated from the project
root. For a new run, copy the latest per-seed dir, bump the `<NN>` index, and adjust
the `SEED=` / `N_ITERATIONS=` in its job script. Standalone benchmarks
(e.g. `73_novel_benchEMT`) are full projects under `_runs/` with their own
README/LOG/TUTORIAL.

Outputs per seed: `output/seed_<N>/1_db/db_<N>.db`, `0_result/0_xsf/*.xsf`,
`output_seed_<N>.txt` (GPAW log), `generated_structures/` — all regenerable.

## Step 4b — Where analysed results go

Analysed/intermediate results go in **`_analysist/`** (sibling of `_runs/`), kept
separate from raw runs. The repo-root `.gitignore` anticipates
`0_analy/` (staging), `1_result/` (final), and `main_analyst.ipynb` /
`main_test.ipynb` (notebooks). Analysis outputs are regenerable/gitignored.

## Step 4c — Analyse the Fe/MgO heavy-run results (idx 71, 72)

A self-contained analysis runner lives at `_analysist/run_analysis_indices.py`
(mirrors the sibling `/home/think/Desktop/research/_analysist/run_analysis_indices.py`,
adapted to this project; imports only the `_analysist/scripts/` deps copied next to
it). It runs the 3-stage pipeline on the Fe/MgO heavy runs **71** and **72**:
① `process_database` (AGOX `.db` → trajectory/xsf/csv, `start_iter=10`),
② PCA landscape, ③ Boltzmann probability vs temperature.

```bash
cd /home/think/Desktop/research/_run/10_lcbnovel/_analysist
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py --idx 71
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py   # all (71, 72)
# optional: --e-max 0.8 --normalize-density --skip-probability
```

The `FOLDER_MAP` points each index at the DB root that holds `seed_*/1_db/`
(`71_novel_runEWindow/output`, `72_novel_AutoGlob_1eVperAtomAboveGlob/output`).
**73/74 are excluded** — their flat `benchmark_results/` layout has no `seed_*` dirs,
so `process_database` would find nothing; those benchmarks have their own analysis
(DISCUSSION.md, benchmark_results JSON). Outputs → `0_analy/idx_<N>/`:
`1_xsf_traj/traj_<N>.traj`, `data_<N>.csv`, `progression_*.png`, `2_im/conf_space.png`,
`2_im/binding_probability_vs_temperature.png`.

> **Git note:** this project is part of the parent repo
> (`/home/think/Desktop/research`), whose `.gitignore`'s `_analysist/0_analy/` rules
> target the *parent's* `_analysist` — not this nested one. A project-level
> `.gitignore` was added so `_analysist/0_analy/` and `_analysist/1_result/` (and
> `*.db/*.png/*.traj/*.xsf/*.csv/*.out`) stay untracked; only the runner +
> `_analysist/scripts/` code is committed.

## Step 5 — Energy-window: auto global-minimum mode (default)

The Novelty-LCB window now defaults to the **auto global-minimum** mode in **energy
per atom**, so no manual calibration / prior regular-LCB run is needed. The acquisitor
anchors the window to the live lowest DFT energy in the DB (`E_min`), divides by the
atom count `N`, and searches a set amount above it:

    window (per atom) = (-inf, E_min/N + X]   with X = NOVELTY_ENERGY_ABOVE_MIN (default 1.0 eV/atom)

`E_min` is recomputed each acquisition round from the current DB, so it tracks new
minima as they are found; there is no lower bound, so a new lower global minimum can
still be discovered.

**Choosing X (per-atom).** Values are size-independent — choose directly in eV/atom
(e.g. 0.5 eV/atom = tight, 2 eV/atom = permissive). Set `NOVELTY_ENERGY_ABOVE_MIN` in
`main.py`.

**Total-eV mode (alternative).** Set `NOVELTY_ENERGY_PER_ATOM = False` to interpret X
in total eV (e.g. 5–10 eV for this 75-atom system). For a fixed N, per-atom and total
modes are equivalent up to scaling by N.

**Manual centered mode (alternative).** Set `energy_above_min = None` and pass
`target_energy`/`delta_E` to reproduce the old centered window
`[target_energy − ΔE, target_energy + ΔE]`. For reference, the LCB-only `./dataset`
band is ≈ [−436.9, −386.3] eV (centre ≈ −411.6 eV); see `energy_stats.py` to map it.
This mode is not needed for the default run.

## Step 6 — EMT benchmark (optional)

> The **extended** grid benchmark (10 seeds × iter 100–500 × λ 2–5 = 250 runs) lives
> as its own full project at **`_runs/73_novel_benchEMT/`** (see its README). The
> steps below describe the parent-project benchmark (`main_benchmark.py` /
> `main_benchmark_sweep.py`), which run from the project root.

`main_benchmark.py` compares **regular LCB** vs **Novelty-LCB** (using the auto
global-minimum per-atom window) on the Ni8 / Au(4,4,2) fcc100 surface with the EMT
calculator. It is a fast, low-cost way to validate the auto-window acquisitor end to
end (5 seeds, N_ITERATIONS=30, same seeds for both acquisitors).

```bash
# Local (needs a RAM-rich node — the AGOX ParallelCollector/RelaxPostprocess use a
# Ray pool that OOMs on a low-RAM machine with Ray ActorUnavailableError)
/home/think/miniconda3/envs/agox_v2/bin/python main_benchmark.py

# On HPC:
pjsub j_benchmark.sh
```

What it compares (metrics, same as run 6): distinct configurations (fingerprint
clustering), best energy, energy range, duplicate evaluations, discovery curves,
plus aggregate stats and plots. Outputs to `benchmark_results/`
(`benchmark_results.json`, `benchmark_comparison.png`, `benchmark_differences.png`).

**Novelty-LCB window in the benchmark:** `energy_above_min = 0.1` eV/atom,
`per_atom=True` → cap `E_min/N + 0.1` per atom (40-atom Au+Ni cell → ~4 eV above
global min). No manual calibration / regular-LCB-first step.

### Kappa x novelty_weight sweep (optional)

`main_benchmark_sweep.py` studies the **impact of kappa and novelty_weight** on
Novelty-LCB, on the same Ni8/Au(4,4,2)-EMT system (it reuses the `main_benchmark.py`
helpers). It sweeps a grid:

- `kappa ∈ [0.5, 1.0, 2.0, 4.0]` × `novelty_weight ∈ [0.0, 0.5, 1.0, 1.5, 2.0]`
  = **20 combos**, Novelty-LCB only, **1 seed per combo** (seed 41), N_ITERATIONS=30.

```bash
/home/think/miniconda3/envs/agox_v2/bin/python main_benchmark_sweep.py   # local (RAM-rich)
pjsub j_benchmark_sweep.sh                                               # on HPC
```

Outputs to `benchmark_results/sweep_kappa_lambda/`: `sweep_results.json`,
`sweep_heatmaps.png` (distinct / best-E / duplicates as kappa×lambda heatmaps),
`sweep_curves.png` (metrics vs lambda, one line per kappa), `sweep_discovery.png`
(all discovery curves).

> **Caveat:** same as the main benchmark — uses AGOX's parallel components (Ray
> pool), so it needs enough RAM; run on a RAM-rich node / HPC.

## Step 7 — Analyse results (downstream, optional)

Once real DBs exist, the established downstream pipeline applies:
- `_run/9_novelFilter/` — greedy novelty/dedup filter + partition function.
- `_run/8_nested_sampling/` — GPR surrogate + nested sampling for the partition
  function / evidence. The combined multi-seed technique (concatenate
  `restore_to_trajectory()` lists) works because the Fe/MgO composition is uniform
  (Mg25O25Fe25 = 75 atoms). Verify composition uniformity first with
  `Counter(tuple(a.get_chemical_symbols()))`.

## Common pitfalls

1. **`cannot pickle 'sqlite3.Connection'`** — the run-7 bug. Never pass bound methods
   into `LowerConfidenceBoundCalculator`; use `functools.partial` over module-level
   free functions. Validate with the smoke test.
2. **`LocalOptimizationEvaluator` missing `calculator`** — kwargs key must be
   `calculator`, not `calc`. `main.py` passes it positionally to avoid this.
3. **Energy window mode** — default is auto global-minimum in per-atom eV (`(-inf,
   E_min/N + X]`, `X` = `NOVELTY_ENERGY_ABOVE_MIN`, default 1.0 eV/atom), so no manual
   calibration is needed. Set `NOVELTY_ENERGY_PER_ATOM=False` for total eV. To use the
   old centered mode, set `energy_above_min = None` and pass `target_energy`/`delta_E`.
4. **Env split — local vs HPC.** Local dev/test (smoke test, compile, slab build)
   uses `agox_v2`; the HPC pjsub heavy run uses `gpaw_env` (set in `j_novel.sh`).
   Don't confuse the two: `j_novel.sh` must keep `conda activate gpaw_env`.
5. **Base `python3` has no AGOX** — always use `/home/think/miniconda3/envs/agox_v2/bin/python`.
6. **`use_ray` on low-RAM nodes** — GPR defaults to `use_ray=True` (spawns one Ray
   actor per CPU); on a small machine this can OOM. On the 64-core HPC node Ray is
   fine and expected.
7. **Trailing space in run-dir names** — a run dir was accidentally created as
   `_runs/3_mgofe_Seed3_Iter700 ` (trailing space). This is error-prone with paths
   and scripts; keep run-dir names free of spaces (`<NN>_<descriptor>`). The space
   was removed via `git mv`.
8. **Keep each run dir self-contained** — always give a run its own `main*.py`,
   `scripts/`, and `novelty_lcb/` under `_runs/<NN>_<descriptor>/`; do not rely on
   the project root when launching from HPC. If a run's code diverges, copy the
   needed files into the run dir rather than importing from the parent.
9. **Bump `__version__` on every edit** — every in-scope source file carries a
   module-level `__version__ = "X.Y.Z"` (semver; baseline 1.0.0). When you edit a
   file, bump its patch version (minor for API/behavior changes), update the
   `VERSIONS.md` manifest, and record the old→new version in `LOG.md`. Keep the
   `__version__` line after any `from __future__` import (else `SyntaxError`).

## Verification checklist

- [ ] `py_compile` passes for main.py, novelty_lcb/*.py, scripts/*.py
- [ ] `smoke_test_serialization.py` prints `RESULT: PASS`
- [ ] Local structure build produces a 75-atom Mg25O25Fe25 slab
- [ ] (HPC) one seed completes without a Ray serialization error
- [ ] Energy window calibrated before interpreting Novelty-LCB results
- [ ] Run dirs follow `<NN>_<descriptor>` naming with no spaces; `_runs/` is git-tracked, `_analysist/` outputs are gitignored
- [ ] Every in-scope source file has a module-level `__version__`; `VERSIONS.md` is current and matches; `LOG.md` records the old→new version
