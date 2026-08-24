# Novelty-LCB serialization fix + faithful-repair workflow (session 2026-08-22)

Condensed from project `_run/10_lcbnovel` (faithful repair of `_run/7_lcbnovel_mgofe`).
Complements the main example in `agox-custom-acquisitor-example.md`; reuse the
validation probe `scripts/validate_acquisitor_serialization.py` in this skill.

## Verified fact: GPR(database=...) does NOT store self.database

Constructing `GPR(descriptor, kernel, database=db, ...)` does **not** set `self.database`.
In `agox/models/ABC_model.py`, `__init__(database=...)` calls `attach_to_database(database)`,
which only does `self.attach(database)` (observer wiring) — the attribute is never assigned.
Consequence: `pickle.dumps(model)` succeeds even with `database=` passed, so the GPR is never
the carrier of the `cannot pickle 'sqlite3.Connection'` Ray failure. The sqlite connection only
leaks into a Ray-put graph through an object that stores a Database **as an attribute** — in the
Novelty-LCB acquisitor that is `self.database = database` set in its own `attach_to_database`.
When bisecting a serialization crash, look there, never at the model.

## Workflow caution: a "proven" upstream project may never have completed a run

Both `_run/6_lcbnovel_benchmark` and `_run/7_lcbnovel_mgofe` crashed at the AGOX wiring stage
(Bug C `LocalOptimizationEvaluator` `calc`→`calculator` kwarg; Bug B sqlite-pickle in
`ParallelRelaxPostprocess`) and were **never re-launched** after the fixes were written. No
result artifacts exist (`benchmark_results_surface/`, `seed_*/1_db/*.db` all absent). The run-7
crash log timestamp (15:48) predates the acquisitor fix (16:00) — the fix was never re-tested.

Lesson: before reproducing a prior project as a working template, verify its run log shows a
**completed** run AND that the expected output artifacts exist. A fix note appended to the
script is not evidence the pipeline ever ran end-to-end. Check for real outputs, not just code.

## Cheap validation before the heavy run (EMT, no DFT)

The correct pre-flight for a custom acquisitor that must cross the Ray pool: build a tiny EMT
stack that walks the exact crash path (`get_acquisition_calculator()` →
`ParallelRelaxPostprocess` → 2-iteration `AGOX.run`) and assert picklability. Use
`scripts/validate_acquisitor_serialization.py`. It verified (2026-08-22) that the fixed
Novelty-LCB acquisitor pickles cleanly:
- `pickle.dumps(calc)` OK (no sqlite in graph)
- `ray.util.inspect_serializability(calc)` → 0 FAIL markers
- `ParallelRelaxPostprocess(model=calc)` constructs cleanly
- 2-iteration `AGOX.run` with EMT completes with no Ray serialization error

A PASS here means the heavy GPAW/DFT job won't die in `ray.put`.

## Env note

Run with `/home/think/miniconda3/envs/agox_v2/bin/python` from the project root (the skill
scripts expect to import the local `novelty_lcb` package from `_PROJ`). Base `python3` has no
AGOX/ASE/GPAW. Headless: `matplotlib.use("Agg")` before plotting imports.
