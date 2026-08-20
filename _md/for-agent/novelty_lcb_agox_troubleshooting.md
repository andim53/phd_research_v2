# Novelty-LCB × AGOX — Integration Debugging & Troubleshooting Reference

**Session:** 2026-08-20
**Environment:** `agox_v2` conda env — AGOX 3.10.2 + ASE 3.25.0
**Python:** `/home/think/miniconda3/envs/agox_v2/bin/python` (base `python3` has no AGOX/ASE)
**Related docs in this dir:** `novelty_lcb_acquisitor_documentation.md` (acquisitor design),
`novelty_lcb_benchmark_discussion.md` (Au₁₀ cluster benchmark).

---

## Purpose of this file

This is the operational reference for **integrating `NoveltyLCBAcquisitor` into a real
AGOX run** and **debugging the errors that come up**. It records three bugs hit across
two production runs (Fe/MgO slab in `_run/7_lcbnovel_mgofe`, Ni₈/Au benchmark in
`_run/6_lcbnovel_benchmark`), their root causes, the fixes, and the AGOX internals
needed to reason about them. If you ask Calyx to do a related task (extend the
acquisitor, build another run script, debug a new AGOX error), this file is the
starting point.

---

## 1. The production pattern (how NoveltyLCBAcquisitor is wired in)

Both run scripts use this canonical stack, which mirrors AGOX's own GOFEE test scripts
(`agox/test/run_tests/tests_gofee/script_gofee_bulk_emt.py`):

```python
# Model + database
database = Database(filename=db_path, order=5)
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

# Collector → relaxer → acquisitor → evaluator → database, in order
collector = ParallelCollector(generators=generators, sampler=sampler,
                              environment=env, num_candidates=..., order=1)
relaxer   = ParallelRelaxPostprocess(model=acquisitor.get_acquisition_calculator(),
                                     constraints=env.get_constraints(),
                                     optimizer_run_kwargs={"steps": RELAX_STEPS},
                                     start_relax=..., order=2)
acquisitor = NoveltyLCBAcquisitor(model=model, descriptor=descriptor, database=database,
                                  target_energy=..., delta_E=..., novelty_weight=..., order=3)
evaluator = LocalOptimizationEvaluator(calculator=calc, gets={"get_key": "prioritized_candidates"},
                                       optimizer_run_kwargs={"fmax":0.05,"steps":1},
                                       constraints=env.get_constraints(), store_trajectory=False, order=4)

agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
agox.run(N_iterations=N)
```

Key points:
- The **collector must run before the relaxer** (order 1 < 2), and the relaxer runs on
  the **acquisition calculator**, not on the real DFT calculator.
- The **real calculator** goes into the `LocalOptimizationEvaluator` (order 4).
- `AGOX.run(N_iterations=...)` — the method is `run`, not `run_optimization`.

---

## 2. Bug A — `get_acquisition_calculator` not implemented

### Symptom

```
File "main.py", line 171, in <module>
    model=acquisitor.get_acquisition_calculator(),
NotImplementedError: 'get_acqusition_calculator' is not implemented for this acquisitor
```

### Root cause

`AcquisitorBaseClass.get_acquisition_calculator()` (in
`agox/acquisitors/ABC_acquisitor.py`) is **not abstract** — it just
`raise NotImplementedError`. AGOX's stock `LowerConfidenceBoundAcquisitor` overrides it
to return an `AcquisitonCalculatorBaseClass` (specifically `LowerConfidenceBoundCalculator`,
in `agox/acquisitors/LCB.py`) that the `ParallelRelaxPostprocess` uses to pre-relax
candidates on the cheap surrogate. `NoveltyLCBAcquisitor` did not override it, so any
run that passes `model=acquisitor.get_acquisition_calculator()` into the relaxer crashes.

### Fix

Implement `get_acquisition_calculator()` to return a `LowerConfidenceBoundCalculator`.
The novelty term (`min` distance to DB in descriptor space) is a **discrete** quantity,
not differentiable w.r.t. atomic positions, so it has no well-defined force. The
relaxation surface is therefore the LCB part, `E - kappa*sigma`, whose energy/force
gradients are analytic in the GPR. The novelty term still drives *selection* via
`calculate_acquisition_function`; it only cannot drive *relaxation*.

---

## 3. Bug B — `cannot pickle 'sqlite3.Connection' object` (Ray serialization)

### Symptom

Appears in `ray_relax/ray_relax.py` `__init__` at `self.model_key = self.pool_add_module(model)`:

```
ray.exceptions ... TypeError: Could not serialize the put value
<agox.acquisitors.LCB.LowerConfidenceBoundCalculator object ...>:
cannot pickle 'sqlite3.Connection' object
```

`ParallelRelaxPostprocess` pushes the acquisition calculator (and recursively its
submodules) into the Ray pool via `ray.put(module)` (`agox/utils/ray/pool.py:add_module`).
The calculator's object graph must be picklable.

### Root cause (subtle)

The original fix for Bug A passed **bound methods** as the acquisition functions:

```python
LowerConfidenceBoundCalculator(self.model, self._acquisition_energy, self._acquisition_force)
```

A bound method captures the entire `NoveltyLCBAcquisitor` instance. Because the
acquisitor stores `self.database` (a sqlite-backed `Database` holding a live
`sqlite3.Connection`), the calculator's pickle graph dragged the connection in, and
Ray serialization failed. The stock `LowerConfidenceBoundAcquisitor` never stores a
database, which is why the canonical GOFEE pattern works and this custom one broke.

**Diagnostic technique that pinpointed this:** isolate by `pickle.dumps()` on each
object. The **model** pickled fine (`model: pickle OK`), but the **calculator** failed
(`calc: pickle FAIL`). In a standalone repro with a *fresh* DB and the stock LCB the
calculator pickled OK, so the trigger was the acquisitor holding a DB reference.

### Fix

Use module-level **free functions** wrapped in `functools.partial`, so only the scalar
`kappa` is captured, not the acquisitor (and thus not the DB connection):

```python
from functools import partial

def lcb_acquisition_energy(E, sigma, kappa=1.0):
    return E - kappa * sigma

def lcb_acquisition_force(E, F, sigma, sigma_force, kappa=1.0):
    return F - kappa * sigma_force

# in get_acquisition_calculator():
return LowerConfidenceBoundCalculator(
    self.model,
    partial(lcb_acquisition_energy, kappa=self.kappa),
    partial(lcb_acquisition_force, kappa=self.kappa),
)
```

Also added `kappa: float = 1.0` to the `NoveltyLCBAcquisitor.__init__` signature.

### General lesson for AGOX + Ray

Anything placed in the Ray pool (via `pool_add_module` → `ray.put`) must be picklable.
Watch for:
- live sqlite connections (`Database.con`)
- bound methods that capture stateful parent objects
- any module holding a reference to a `Database`

`functools.partial` over module-level functions is the safe way to inject scalar params
into a calculator that must cross the Ray boundary.

---

## 4. Bug C — `LocalOptimizationEvaluator.__init__() missing 1 required positional argument: 'calculator'`

### Symptom (in `_run/6_lcbnovel_benchmark/run.py`)

```
File "run.py", line 253, in build_stack
    evaluator = LocalOptimizationEvaluator(**evaluator_kwargs)
TypeError: LocalOptimizationEvaluator.__init__() missing 1 required positional argument: 'calculator'
```

### Root cause

`LocalOptimizationEvaluator.__init__(self, calculator, ...)` names its first parameter
**`calculator`**. The benchmark built a kwargs dict with the key `calc`:

```python
evaluator_kwargs = dict(calc=sys_ij["calc"], ...)
```

`calc` is not a declared parameter, so it fell into `**kwargs` and the required
`calculator` was left unset.

### Fix

```python
evaluator_kwargs = dict(calculator=sys_ij["calc"], ...)
```

---

## 5. AGOX internals that matter (verified against 3.10.2)

### Acquisitor base — `agox/acquisitors/ABC_acquisitor.py`

- `AcquisitorBaseClass(ABC, Observer)`; defaults `gets={"get_key":"candidates"}`,
  `sets={"set_key":"prioritized_candidates"}`.
- Abstract method `calculate_acquisition_function(candidates)` → returns array of values.
- `sort_according_to_acquisition_function(candidates)` sorts **ascending** (lowest value
  = best = selected first) and attaches `acquisition_value` meta-info.
- `get_acquisition_calculator()` → NOT abstract, raises `NotImplementedError`.
- `AcquisitonCalculatorBaseClass(Calculator, Module)` — base for the calculator returned
  by `get_acquisition_calculator()`; holds `model`, exposes `ready_state`.

### Stock LCB calculator — `agox/acquisitors/LCB.py`

`LowerConfidenceBoundAcquisitor.get_acquisition_calculator()` returns
`LowerConfidenceBoundCalculator(model, acquisition_function, acquisition_force)`.
Its `calculate()` calls `model.converter(atoms, derivatives=...)`, then
`predict_energy` / `predict_uncertainty` / `predict_forces` /
`predict_uncertainty_forces`, and combines them via the supplied callables.

### Parallel relax postprocessor — `agox/postprocessors/ray_relax/ray_relax.py`

`ParallelRelaxPostprocess(model, optimizer=BFGS, constraints=[], start_relax=1, ...)`.
In `__init__` it calls `self.pool_add_module(model)` which recursively
`ray.put`s the model + its submodules onto the pool actors. On each run of a candidate
it does `remote_relax` on an actor using the model as the calculator. So the model here
**must be a picklable ASE Calculator** — which is exactly what `get_acquisition_calculator()`
returns. `start_relax` gates via `do_check` (`check_iteration_counter(start_relax)`).

### Model holds no DB attribute

`ModelBaseClass.attach_to_database(database)` (in `models/ABC_model.py`) calls
`self.attach(database)` (observer wiring) — it does **not** store a `.database`
attribute. That is why the GPR model itself pickles fine; the DB connection only leaks
into the pickle graph through objects that store a DB reference (e.g. the acquisitor).

### Database — `agox/databases/database.py`

`Database(filename=..., order=...)` opens `sqlite3.connect(filename, timeout=600)` and
stores it as `self.con`. The connection is **not picklable**. Any object holding a
Database in a Ray-put context will fail.

### Ordering convention

`order` is a list; lower executes first. Canonical: collector(1) → relaxer(2) →
acquisitor(3) → evaluator(4) → database(5). Model typically `order=0`.
`gets`/`sets` wiring is manual — verify every `get_key` has a producer.

---

## 6. Verification checklist (do these before claiming a fix works)

1. **Compile**: `/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile run.py novelty_lcb/*.py`
2. **Instantiate** the evaluator/calculator in the env with a mock or real calc:
   `LocalOptimizationEvaluator(calculator=EMT(), ...)` — confirms the wiring is correct.
3. **Pickle test** for anything going into the Ray pool:
   `pickle.dumps(calculator)` must succeed; if not, walk the object graph for sqlite
   connections / bound methods.
4. **Faithful repro**: rebuild the actual stack (real slabs, generators, acquisitor,
   relaxer) and confirm `ParallelRelaxPostprocess` constructs — this is the point where
   Bugs A and B both surfaced.
5. **Full run**: run `main.py` / `run.py` and confirm it passes the setup phase and
   enters the optimization loop (observer report printed, iterations run).

---

## 7. Important caveats for actual production runs

- **Uncalibrated energy window.** Both scripts ship with placeholder values
  (`_run/7_lcbnovel_mgofe/main.py`: `NOVELTY_TARGET_ENERGY = 0.0`, `delta_E = 1.0`;
  `_run/6_lcbnovel_benchmark/run.py`: `target_energy = 0.0`, `delta_E = 2.0`). These are
  **not calibrated** and may exclude most/all candidates. Run a short standard-LCB
  search first to map the energy band, then set `target_energy` to the band centre and
  `delta_E` to ~half-width. Trusting the numbers before calibration will mislead you.
- **Machine resources.** The Fe/MgO script targets a 64-CPU / 128 GB HPC node
  (`ncores=64` in the local working copy). On a small machine (e.g. 4 CPU / 7 GB) Ray
  can hit `ActorUnavailableError` from OOM/resource exhaustion mid-run — that is **not**
  a code bug, it is a hardware limit. Run heavy jobs on the cluster.
- **Seed loop.** `_run/7_lcbnovel_mgofe/main.py` iterates `for seed in range(3, 105)`,
  writing `seed_<n>/0_result`, `seed_<n>/1_db`. Each seed builds its own stack.

---

## 8. Repro scripts (pattern)

To reproduce Bug B, build the real stack up to and including the relaxer:

```python
import matplotlib; matplotlib.use("Agg")
import numpy as np, ray
# ... build environment, database, descriptor, GPR, NoveltyLCBAcquisitor ...
calc = acquisitor.get_acquisition_calculator()
ray.util.inspect_serializability(calc, name="calc")   # surfaces the sqlite connection
from agox.postprocessors import ParallelRelaxPostprocess
relaxer = ParallelRelaxPostprocess(model=calc, constraints=env.get_constraints(),
                                   optimizer_run_kwargs={"steps":5}, start_relax=1, order=2)
```

`ray.util.inspect_serializability(obj)` is the fastest way to locate the non-picklable
attribute in a large object graph.

---

## 9. File locations

| Item | Path |
|---|---|
| Fe/MgO run script | `/home/think/Desktop/research/_run/7_lcbnovel_mgofe/main.py` |
| Fe/MgO novelty_lcb package | `/home/think/Desktop/research/_run/7_lcbnovel_mgofe/novelty_lcb/` |
| Benchmark run script | `/home/think/Desktop/research/_run/6_lcbnovel_benchmark/run.py` |
| Benchmark novelty_lcb package | `/home/think/Desktop/research/_run/6_lcbnovel_benchmark/novelty_lcb/` |
| AGOX acquisitor base | `/home/think/miniconda3/envs/agox_v2/lib/python3.11/site-packages/agox/acquisitors/ABC_acquisitor.py` |
| Stock LCB + calculator | `.../agox/acquisitors/LCB.py` |
| Parallel relax postprocessor | `.../agox/postprocessors/ray_relax/ray_relax.py` |
| Ray pool | `.../agox/utils/ray/pool.py`, `.../agox/utils/ray/pool_user.py` |
| GPR model | `.../agox/models/GPR/GPR.py`, `.../agox/models/ABC_model.py` |
| Database | `.../agox/databases/database.py` |
| Canonical GOFEE example | `.../agox/test/run_tests/tests_gofee/script_gofee_bulk_emt.py` |

---

## 10. Related skills

Load the `agox` skill (`skill_view(name="agox")`) for the full component API and
canonical runscript before writing/debugging AGOX code. Also relevant:
`gpaw` (DFT), `simulation-analysis` (db/simulation analysis), `agox-gpr-analysis`
(loading .db + training GPR).
