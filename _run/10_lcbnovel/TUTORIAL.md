# TUTORIAL — Reproduce & repair the Novelty-LCB Fe/MgO search

Step-by-step guide to reproduce this project from scratch, validate the fix, and
launch the heavy search. Written so a fresh agent (or you) can redo the work.

## Prerequisites

- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0 + GPAW + Ray).
  Python: `/home/think/miniconda3/envs/agox_v2/bin/python`.
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

One PJM job per seed (scale-out by array submission). Each seed builds its own stack.

```bash
pjsub j_novel.sh                  # seed 3
pjsub -x SEED=5 j_novel.sh        # any specific seed
# monitor: pjstat   |   cancel: pjdel
```

Outputs per seed: `output/seed_<N>/1_db/db_<N>.db`, `0_result/0_xsf/*.xsf`,
`output_seed_<N>.txt` (GPAW log), `generated_structures/`.

## Step 5 — CALIBRATE the Novelty-LCB energy window (before trusting results)

The placeholder window `target_energy=0.0, delta_E=1.0` (in `main.py`) is a TODO and
may exclude most/all candidates. Procedure:

1. Run a short **standard-LCB** search (switch `NoveltyLCBAcquisitor` → the stock
   `LowerConfidenceBoundAcquisitor`, or run 7's alternative) to map the energy band
   that AGOX actually explores.
2. Read the range of candidate energies from the resulting DB.
3. Set `NOVELTY_TARGET_ENERGY` = band centre, `NOVELTY_DELTA_E` ≈ 0.5–1.0 eV half-width.
4. Re-launch. **Do not draw conclusions from Novelty-LCB results before calibration.**

## Step 6 — Analyse results (downstream, optional)

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
3. **Uncalibrated energy window** — placeholder `0.0/1.0` excludes candidates until
   calibrated (Step 5). Always calibrate first.
4. **Env mismatch** — original `j_novel.sh` used `gpaw_env`; this project needs
   `agox_v2`. Already fixed in `j_novel.sh`.
5. **Base `python3` has no AGOX** — always use `/home/think/miniconda3/envs/agox_v2/bin/python`.
6. **`use_ray` on low-RAM nodes** — GPR defaults to `use_ray=True` (spawns one Ray
   actor per CPU); on a small machine this can OOM. On the 64-core HPC node Ray is
   fine and expected.

## Verification checklist

- [ ] `py_compile` passes for main.py, novelty_lcb/*.py, scripts/*.py
- [ ] `smoke_test_serialization.py` prints `RESULT: PASS`
- [ ] Local structure build produces a 75-atom Mg25O25Fe25 slab
- [ ] (HPC) one seed completes without a Ray serialization error
- [ ] Energy window calibrated before interpreting Novelty-LCB results
