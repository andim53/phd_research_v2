# Novelty-LCB AGOX — run-7 crash, root cause, and repair recipe

Context: `_run/7_lcbnovel_mgofe` (and `_run/6_lcbnovel_benchmark`) both *looked* like
working Novelty-LCB projects but **never completed a real run**. This is the classic
trap: the acquisition-fix was applied but never re-tested end-to-end. Always verify
with the serialization smoke test before assuming a Novelty-LCB script works.

## The crash (run 7, seed 3)

Output log tail:

```
TypeError: Could not serialize the put value
<agox.acquisitors.LCB.LowerConfidenceBoundCalculator object at 0x...>:
cannot pickle 'sqlite3.Connection' object
!!! FAIL serialization: cannot pickle 'sqlite3.Connection' object
```

No `seed_*/` dirs were ever created — the run died at the first stack build.

## Root cause

Two independent contributors:

1. **Acquisitor bound methods.** The old `get_acquisition_calculator()` passed
   `self._acquisition_energy` / `self._acquisition_force` (bound methods) into
   `LowerConfidenceBoundCalculator`. A bound method captures the whole acquisitor
   instance, which holds `self.database` — a live `sqlite3.Connection` — so `ray.put`
   fails. Fix: module-level free functions + `functools.partial(kappa=...)`.
2. **GPR does NOT store the DB.** Verified in `agox/models/ABC_model.py`:
   `GPR.__init__(database=...)` → `attach_to_database(database)` → `self.attach(database)`
   only (observer wiring); it does not store `self.database`. So the GPR pickles cleanly
   even with `database=`. The connection only leaks through objects that STORE a DB ref.

## The fix (in the canonical `novelty_lcb/acquisitor.py`)

- `lcb_acquisition_energy` / `lcb_acquisition_force` defined as module-level functions.
- `get_acquisition_calculator()` returns
  `LowerConfidenceBoundCalculator(self.model, partial(lcb_acquisition_energy, kappa=self.kappa),
  partial(lcb_acquisition_force, kappa=self.kappa))`.
- `kappa` added to the acquisitor `__init__`.

## Validation (do this before any real run)

Cheap local smoke test (tiny EMT Au system, no GPAW). It walks the exact crash path:

1. Build `NoveltyLCBAcquisitor` → `get_acquisition_calculator()`.
2. `pickle.dumps(calc)` must succeed (no sqlite in graph).
3. `ray.util.inspect_serializability(calc)` must report 0 FAIL markers.
4. `ParallelRelaxPostprocess(model=calc, ...)` must construct.
5. A 2-iteration `agox.run()` with EMT must complete with no Ray serialization error.

If any step FAILs, the calculator still drags a non-picklable object into the Ray pool;
re-check for bound methods / stored DB references.

## Wiring facts (AGOX 3.10.2)

- Canonical order: collector(1) → relaxer(2, on acquisition calculator) → acquisitor(3)
  → evaluator(4, real calculator) → database(5). Model order 0.
- `LocalOptimizationEvaluator.__init__(self, calculator, ...)` — the key is `calculator`,
  NOT `calc` (Bug C). Pass it positionally to avoid the kwargs trap.
- `AGOX.run(N_iterations=...)` is the method (not `run_optimization`).
- Both regular LCB and Novelty-LCB relax on the same LCB surface `E - kappa*sigma`.

## Faithful-repair recipe (project 10 pattern)

1. Copy the proven `novelty_lcb/` package + slab/generator `scripts/` into the new dir.
2. Rewrite `main.py` faithfully (same physics), per-seed CLI, serialization-safe wiring.
3. Compile-check + run the smoke test before trusting anything.
4. Batch launch on HPC with `pjsub j_novel.sh` (seed set by editing `SEED=`; uses
   `gpaw_env`).
5. Calibrate the Novelty-LCB energy window from a short standard-LCB run BEFORE
   interpreting results (placeholder `target=0.0, delta_E=1.0` excludes candidates).
