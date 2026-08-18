---
name: agox
description: "Use when writing or debugging AGOX code (atomistic global optimization: generators, samplers, models, collectors, Environment, Database, AGOX.run) in the agox_v2 conda env. AGOX 3.10.2 + ASE 3.25.0."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agox, global-optimization, ase, materials-science, simulation, gpaw]
    related_skills: [gpaw, simulation-analysis]
---

# AGOX (Atomistic Global Optimization X)

## Overview

AGOX is a framework for atomistic global optimization built on ASE. Every piece of the
search — candidate generators, samplers, surrogate models, acquisition functions,
collectors, evaluators, databases, environments — is a `Module` that plugs into a central
event loop as an `Observer`. This skill is grounded in the exact install in the `agox_v2`
conda env: **AGOX 3.10.2** paired with **ASE 3.25.0**, at
`/home/think/miniconda3/envs/agox_v2/lib/python3.11/site-packages/agox`.

## When to Use

- Writing or debugging an AGOX runscript (`AGOX(...)` + `.run(N_iterations)`).
- Choosing/instantiating a generator, sampler, model, acquisitor, collector, or evaluator.
- Setting up an `Environment` (confinement cell, template, stoichiometry) or `Database`.
- Wiring modules together via `gets`/`sets`/`order`, or fixing ordering errors.

Do NOT use for: the analysis pipeline scripts under `_analysist/` (see the
`simulation-analysis` skill), or raw GPAW/DFT itself (see the `gpaw` skill).

## Environment

Invoke the env's Python by absolute path (base `python3` has no AGOX/ASE):

```
/home/think/miniconda3/envs/agox_v2/bin/python
```

Set `matplotlib.use('Agg')` **before** importing anything that plots (headless runs).
AGOX's `SubprocessGPAW` helper (see below) wraps GPAW for parallel/async evaluation.

## Architecture

- `Module` (`agox/module.py`) — base class for everything. Holds a `Writer`, `surname`
  (name suffix for disambiguation), `use_cache`, `cache_key`.
- `Observer(Module)` — base for all computational modules. Key constructor params:
  - `gets` / `sets`: lists of dicts declaring which keys the module **reads from** /
    **writes to** the per-iteration `State` cache (e.g. `gets={"get_key": "candidates"}`).
    This is the dataflow wiring between modules.
  - `order`: list of ints/floats; **lower executes first** (e.g. `order=1` before `order=4`).
  - `surname`, `verbosity` (via `Module`).
- `State` (`agox/main/state.py`) — per-iteration cache carrying `candidates`,
  `evaluated_candidates`, etc., dispatched to observers in `order`.
- `AGOX(ObserverHandler, FinalizationHandler)` — the orchestrator. Instantiate with the
  module objects as positional args, then call `.run(N_iterations)`.
  - `AGOX(*args, seed=None, candidate_instanstiator=None, attach=True, report=True,
    verbosity=None)`
  - `AGOX.run(N_iterations, verbose=True, hide_log=True)` — **the method is `run`, not
    `run_optimization`.**

Standard dataflow (and typical default `order`s): generator (`order=1`) → writes
`candidates`; evaluator (`order=2`) → reads `candidates`, writes `evaluated_candidates`;
sampler (`order=3`) → reads `evaluated_candidates`; database (`order=4`) → stores results.
Set `order` on each module you pass to `AGOX` to control the pipeline explicitly.

## Canonical runscript (verified from the shipped test suite)

```python
import matplotlib; matplotlib.use("Agg")
import numpy as np
from ase import Atoms
from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.samplers import MetropolisSampler
from agox.helpers import SubprocessGPAW

calc = SubprocessGPAW(mode={"name": "lcao"}, xc="PBE")   # note: mode is a dict

template = Atoms("", cell=np.eye(3) * 12)                # empty template, defines cell
environment = Environment(template=template, symbols="Au6",
                          confinement_cell=np.eye(3) * 6,
                          confinement_corner=np.array([3, 3, 3]))
database = Database(filename="db0.db", order=4)
sampler = MetropolisSampler(temperature=0.25, order=3)
rattle_generator = RattleGenerator(**environment.get_confinement(),
                                   environment=environment, sampler=sampler, order=1)
evaluator = LocalOptimizationEvaluator(
    calc, gets={"get_key": "candidates"}, store_trajectory=False,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5}, order=2,
    constraints=environment.get_constraints())

agox = AGOX(rattle_generator, database, sampler, evaluator, seed=42)
agox.run(N_iterations=10)
```

## Components (signatures verified against 3.10.2)

- **Generators** (`agox.generators`) — produce new candidates:
  `RattleGenerator(n_rattle=3, rattle_amplitude=3, replace=True, attempts=100, **kw)`,
  `RandomGenerator(contiguous=True, attempts=100, ...)`, `CenterOfGeometryGenerator(...)`,
  `SteepestDescentGenerator(use_xy_only=False, replace=True, **kw)`,
  `PermutationGenerator(max_number_of_swaps=1, rattle_strength=0.0, use_xy_only=False,
  ignore_H=False, ...)`, `ReplaceGenerator(n_replace=5, amplitude=3, **kw)`, plus
  `ReuseGenerator`, `SamplingGenerator`, `ComplementaryEnergyGenerator`,
  `SymmetryGenerator`, `SymmetryRattleGenerator`, `SymmetryPermutationGenerator`,
  `MDgenerator`.
- **Samplers** (`agox.samplers`) — pick candidates to feed the generator:
  `KMeansSampler(descriptor=None, model=None, sample_size=10, max_energy=5, **kw)`,
  `MetropolisSampler(temperature=1, gets={'get_key':'evaluated_candidates'}, **kw)`,
  `GeneticSampler(comparator=None, population_size=10, order=6, ...)`,
  `KernelSimSampler(...)` (**not** `KernelSimilaritySampler`), `FixedSampler(sample, p=None)`,
  `SpectralGraphSampler`, `ConcurrentTemperingSampler`, `ReplicaExchangeSampler`.
- **Models** (`agox.models`) — surrogate energy:
  `GPR(descriptor, kernel, prior=None, single_atom_energies=None, n_optimize=None, ...)`,
  `SparseGPR(sigma=0.01, sparsifier=CUR(), ...)`, `SparseGPREnsemble(N_ensemble=5, ...)`,
  `CompositionModel(**kw)`, `CalculatorModel(calculator, composition_model=True, **kw)`.
- **Acquisitors** (`agox.acquisitors`): `LowerConfidenceBoundAcquisitor(model, kappa=1, **kw)`,
  `LCBPenaltyAcquisitor(model, descriptor, penalty_scale=1.0, **kw)`,
  `PowerLowerConfidenceBoundAcquisitor(power=0, *args, **kw)`,
  `MetaInformationAcquisitor(meta_key, mode='min', **kw)`, `ReplicaExchangeAcquisitor`.
- **Collectors** (`agox.collectors`): `ParallelCollector(num_candidates=None, **kw)`,
  `StandardCollector(num_candidates, **kw)`, `ReplicaExchangeCollector`.
- **Evaluators** (`agox.evaluators`):
  `LocalOptimizationEvaluator(calculator, optimizer=BFGS, optimizer_run_kwargs=None,
  optimizer_kwargs=None, fix_template=True, constraints=[], store_trajectory=True, **kw)`,
  `SinglePointEvaluator(calculator, **kw)`.
- **Environments** (`agox.environments`):
  `Environment(template, numbers=None, symbols=None, print_report=True, **kw)` with helpers
  `get_confinement()`, `get_constraints()`, `get_template()`, `get_all_numbers()`,
  `get_box_constraint()`.
- **Databases** (`agox.databases`):
  `Database(filename='db.db', initialize=False, write_interval=1, call_initialize=True,
  store_meta_information=True, **kw)` with `get_all_candidates()`, `get_best_structure()`,
  `get_best_energy()`, `get_all_energies()`, `store_candidate()`.
- **Candidates** (`agox.candidates`): `StandardCandidate(template=None, template_indices=None,
  use_cache=True, **kw)` (an ASE `Atoms` subclass used throughout).
- **Descriptors** (`agox.models.descriptors`): `Fingerprint(rc1=6, rc2=4, binwidth=0.2,
  Nbins=30, ...)`, `SimpleFingerprint(Nbins=30, width=0.2, r_cut=3, ...)`,
  `SOAP(r_cut=4, nmax=3, lmax=2, sigma=1.0, ...)`, `SpectralGraphDescriptor(...)`,
  `Voronoi(...)`, `VoronoiSite(...)`, `ACSF`, `ExponentialDensity`.
- **Kernels** (`agox.models.GPR.kernels.kernels`): `RBF`, `Constant`, `Noise`, `Sum`,
  `Product`, `DotProduct`, `RationalQuadratic` (sklearn-backed).
- **Helpers** (`agox.helpers`): `SubprocessGPAW(ncores=None, log_directory='gpaw_logs/',
  **kw)` — GPAW run in a subprocess; **`mode` is passed as a dict** `{"name": "lcao"}`,
  not a string. `GPAW_IO(...)`, `Confinement(cell=None, corner=None, indices=None, pbc=None)`.
- **Analysis** (`agox.analysis`): `SearchAnalysis`, `SearchData`, plus `plot`, `criterion`,
  `property`.

Full signatures in `references/api_index.md`; module layout in `references/module_map.md`.

## Common Pitfalls

1. **The run method is `AGOX.run(N_iterations)`** — there is no `run_optimization`.
2. **`SubprocessGPAW` wants `mode={"name": "lcao"}` (a dict), not `mode="lcao"`** — this
   differs from the raw `gpaw.GPAW` interface. It also writes logs to `gpaw_logs/` by default.
3. **`gets`/`sets` wiring is manual.** If a module's `gets={"get_key": ...}` key is never
   `set` by an upstream module (or the `order` is wrong), the run silently does nothing or
   crashes. Verify each module's `get_key` has a producer and each `order` is monotonic.
4. **`order` is a list**, e.g. `order=4` is normalized to `[4]`; lower runs first. Generators
   must run before the evaluator before the sampler before the database.
5. **Generator + Environment must agree on confinement**: splat
   `**environment.get_confinement()` into the generator and pass
   `constraints=environment.get_constraints()` to the evaluator, or candidates fall outside
   the cell / violate constraints.
6. **`from agox.generators import *` (and several other `__init__`s) yields nothing** — the
   package's `__all__` is reset to `[]` at the bottom of some `__init__.py` files. Always use
   explicit imports (`from agox.generators import RattleGenerator`).
7. **Sampler class names**: it's `KernelSimSampler`, not `KernelSimilaritySampler`.
8. **Metals/relaxation cost**: `LocalOptimizationEvaluator` runs a full local relaxation per
   candidate; use `optimizer_run_kwargs={"fmax":..., "steps":...}` and keep `steps` modest
   for smoke tests, else one iteration is very slow.
9. **Empty template pattern**: the `template` is usually `Atoms("", cell=...)`; candidates
   are `StandardCandidate` (Atoms subclass) generated within it. Don't expect a full atom
   geometry in `template`.
10. **Seed reproducibility**: pass `seed=` to `AGOX(...)`, which calls `np.random.seed`.

## Reference files

- `references/api_index.md` — full constructor signatures for every component class.
- `references/module_map.md` — purpose of each subpackage/module.

## Verification Checklist

- [ ] Env Python invoked as `/home/think/miniconda3/envs/agox_v2/bin/python`
- [ ] `matplotlib.use('Agg')` set before imports in headless runs
- [ ] `AGOX(...)` instantiated with the module objects, then `.run(N_iterations)`
- [ ] Every `gets` key has a matching upstream `sets` producer; `order`s are monotonic
- [ ] Generator uses `**environment.get_confinement()`; evaluator gets
      `constraints=environment.get_constraints()`
- [ ] Explicit imports (no `from agox.<pkg> import *`)
