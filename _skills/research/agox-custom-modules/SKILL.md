---
name: agox-custom-modules
description: "Use when writing a custom AGOX module/acquisitor."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agox, acquisitions, ray, custom-modules, global-optimization]
    related_skills: [agox, agox-run-code, simulation-analysis]
---

# Writing Custom AGOX Modules (acquisitors, calculators, observers)

## Overview

When you subclass AGOX components (e.g. a custom acquisitor, or any `Module`/`Observer`
that gets pushed into the Ray actor pool), the AGOX framework makes hard assumptions about
the interface and about picklability. These are the two classes of failure that trip up
first-time custom modules. Grounded in AGOX 3.10.2 in the `agox_v2` conda env (Python 3.11).

## When to Use

- Subclassing `AcquisitorBaseClass` (or another `Module`) with a custom acquisition function.
- Hooking the result into `ParallelRelaxPostprocess(model=acquisitor.get_acquisition_calculator(), ...)`.
- Any module that ends up in `pool.add_module(module)` / `ray.put(module)` — which is nearly every
  observer passed to `AGOX(...)`.

## Pitfall 1 — Custom acquisitors MUST implement `get_acquisition_calculator()`

The base `AcquisitorBaseClass.get_acquisition_calculator` (in
`agox/acquisitors/ABC_acquisitor.py`) just does `raise NotImplementedError(...)`. If your
runscript does:

    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        constraints=environment.get_constraints(), ...)

and your acquisitor only overrides `calculate_acquisition_function`, it crashes **at setup** with:

    NotImplementedError: 'get_acqusition_calculator' is not implemented for this acquisitor

Fix: implement it to return an ASE calculator over the acquisition surface. Reuse the stock one
when possible:

    from agox.acquisitors.LCB import LowerConfidenceBoundCalculator
    def get_acquisition_calculator(self):
        return LowerConfidenceBoundCalculator(
            self.model,
            partial(lcb_acquisition_energy, kappa=self.kappa),
            partial(lcb_acquisition_force, kappa=self.kappa),
        )

## Pitfall 2 — Ray serialization: NEVER pass bound methods as acquisition functions

`ParallelRelaxPostprocess.__init__` calls `pool_add_module(model)` → `pool.add_module(module)` →
`ray.put(module)`. The `LowerConfidenceBoundCalculator(model, acq_energy_fn, acq_force_fn)` is what
gets serialized. If `acq_energy_fn` is a **bound method** like `self._acquisition_energy`, the
calculator's pickle graph captures the entire acquisitor instance.

That's fatal if the acquisitor stores a `Database` — a `Database` holds a live
`sqlite3.Connection`, which cannot be pickled:

    TypeError: cannot pickle 'sqlite3.Connection' object
    (from ray.put inside ParallelRelaxPostprocess.__init__ / pool.add_module)

Confusing part: the SAME calculator `pickle.dumps` fine in a minimal repro (fresh DB, no other
modules), but fails on the full main.py stack. It's not environment-dependent — it's the graph
capturing the DB via `self`. The stock `LowerConfidenceBoundAcquisitor` works because it never
stores a database.

Fix: pass **module-level free functions** that close over only scalars via `functools.partial`,
never bound methods:

    def lcb_acquisition_energy(E, sigma, kappa=1.0):
        return E - kappa * sigma

    def lcb_acquisition_force(E, F, sigma, sigma_force, kappa=1.0):
        return F - kappa * sigma_force

    # in get_acquisition_calculator:
    return LowerConfidenceBoundCalculator(
        self.model,
        partial(lcb_acquisition_energy, kappa=self.kappa),
        partial(lcb_acquisition_force, kappa=self.kappa),
    )

`functools.partial` pickles just the function + scalar kwargs — no `self`, no database.

## Pitfall 3 — Bonus terms without forces: relax on the differentiable surface only

If your acquisition function has a discrete / non-differentiable term (e.g. a structural-novelty
bonus = min Euclidean distance in descriptor space to DB structures), that term has **no
well-defined force** w.r.t. atomic positions. Don't try to force-gradient it. Relax candidates on
the differentiable LCB surface (`E - kappa·sigma`) and let the bonus term drive *selection* only
(via `calculate_acquisition_function`). This matches how AGOX's own acquisitors behave.

## Debugging workflow that works

1. Reproduce the full main.py construction in a standalone script (real slabs, real collector,
   real acquisitor) — a minimal `ray.put(calc)` can pass while the full stack fails.
2. `ray.util.inspect_serializability(calc, name='calc')` — but note it can report OK while
   `ray.put` in the full stack still fails; the reliable test is building the actual
   `ParallelRelaxPostprocess`.
3. Bisect: pickle `model` alone (OK), then `calc` (FAIL) to confirm the acquisition-function
   closure is the carrier, then confirm `calc.model is model` and that the calc holds the shared
   model.
4. `git diff` to confirm your edits are confined to your module and you didn't touch unrelated
   local edits in the runscript (e.g. a pre-existing `ncores` change).

## Reference files

- `references/agox-custom-acquisitor-example.md` — full worked Novelty-LCB acquisitor pattern
  (energy-window filter + novelty bonus + picklable LCB calculator), with the interface skeleton.

## Verification Checklist

- [ ] Env Python: `/home/think/miniconda3/envs/agox_v2/bin/python`
- [ ] `matplotlib.use('Agg')` before imports in headless runs
- [ ] Custom acquisitor implements `calculate_acquisition_function`, `print_information`,
      `do_check`, AND `get_acquisition_calculator`
- [ ] Acquisition functions passed to the calculator are module-level functions or
      `functools.partial` over scalars — NEVER bound methods
- [ ] Full main.py constructs `ParallelRelaxPostprocess` without `sqlite3.Connection` pickle error
