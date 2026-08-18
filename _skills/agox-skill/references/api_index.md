# AGOX API index (verified against 3.10.2)

Signatures captured with `inspect.signature` from the installed package. All classes are
`Observer` (and therefore `Module`) subclasses unless noted.

## Orchestrator

```python
from agox import AGOX, State
AGOX(*args, seed: int = None, candidate_instanstiator=None,
     attach: bool = True, report: bool = True, verbosity: int | None = None)
AGOX.run(N_iterations, verbose=True, hide_log=True)   # NOTE: `run`, not `run_optimization`
```
`AGOX` is an `ObserverHandler` + `FinalizationHandler`. Pass the module objects as
positional `*args`; they attach as observers in `order`. `seed` sets `np.random.seed`.

## Environments

```python
from agox.environments import Environment
Environment(template, numbers=None, symbols=None, print_report=True, **kwargs)
```
Key methods: `get_confinement()` -> dict, `get_constraints()` -> list,
`get_template()`, `get_all_numbers()`, `get_all_species()`, `get_box_constraint()`,
`get_missing_indices()`, `set_numbers()`, `match()`, `plot()`.
`template` is usually an empty `Atoms('', cell=...)`; `symbols` e.g. `"Au6"` sets
stoichiometry.

## Databases

```python
from agox.databases import Database
Database(filename: str = 'db.db', initialize: bool = False, write_interval: int = 1,
         call_initialize: bool = True, store_meta_information: bool = True, **kwargs)
```
Key methods: `get_all_candidates()`, `get_best_structure()`, `get_best_energy()`,
`get_all_energies()`, `get_all_structures_data()`, `get_recent_candidates()`,
`get_most_recent_candidate()`, `store_candidate()`, `write()`, `get_last_id()`.
Backed by ASE's `db` (SQLite). Also: `agox.databases.database_concurrent`,
`agox.databases.concurrent_ordered`.

## Evaluators

```python
from agox.evaluators import LocalOptimizationEvaluator, SinglePointEvaluator
LocalOptimizationEvaluator(calculator, optimizer=<class 'ase.optimize.bfgs.BFGS'>,
    optimizer_run_kwargs=None, optimizer_kwargs=None, fix_template=True,
    constraints=None, store_trajectory=True, **kwargs)
SinglePointEvaluator(calculator, **kwargs)
```
`LocalOptimizationEvaluator` reads `gets={'get_key': 'candidates'}`, relaxes each with the
ASE optimizer, writes `evaluated_candidates`. `calculator` is any ASE calculator
(e.g. `SubprocessGPAW`, `EMT`, or a plain `GPAW`).

## Generators

```python
from agox.generators import (RattleGenerator, RandomGenerator, CenterOfGeometryGenerator,
    SteepestDescentGenerator, PermutationGenerator, ReplaceGenerator, ReuseGenerator,
    SamplingGenerator, ComplementaryEnergyGenerator, SymmetryGenerator,
    SymmetryRattleGenerator, SymmetryPermutationGenerator, MDgenerator)

RattleGenerator(n_rattle=3, rattle_amplitude=3, replace=True, attempts=100, **kw)
RandomGenerator(contiguous=True, attempts=100, may_nucleate_at_several_places=None,
                replace=True, **kw)
CenterOfGeometryGenerator(selection_percentages={'low':0.25,'high':0.5},
    extra_radius_amplitude=1, extra_radius_params={'low':-0.5,'high':3}, **kw)
SteepestDescentGenerator(use_xy_only=False, replace=True, **kw)
PermutationGenerator(max_number_of_swaps=1, rattle_strength=0.0, use_xy_only=False,
                     ignore_H=False, write_candidates_to_disk=False, replace=True, **kw)
ReplaceGenerator(n_replace=5, amplitude=3, **kw)
```
Generators take `environment=`, `sampler=`, and `order=` and typically
`**environment.get_confinement()`. `RattleGenerator`/`PermutationGenerator`/`RandomGenerator`
need a `sampler` to pick their base candidate(s).

## Samplers

```python
from agox.samplers import (KMeansSampler, MetropolisSampler, GeneticSampler, KernelSimSampler,
    FixedSampler, SpectralGraphSampler, ConcurrentTemperingSampler, ReplicaExchangeSampler)

KMeansSampler(descriptor=None, model=None, sample_size=10, max_energy=5, **kw)
MetropolisSampler(temperature=1, gets={'get_key':'evaluated_candidates'}, **kw)
GeneticSampler(comparator=None, population_size=10, gets={'get_key':'evaluated_candidates'},
               order=6, using_add_all=True, **kw)
KernelSimSampler(descriptor, kernel, size=5, ...)   # NOTE: KernelSimSampler, not KernelSimilaritySampler
FixedSampler(sample, p=None)
```
`KMeansSampler` clusters candidates by a `descriptor`; `MetropolisSampler` picks by a
Metropolis criterion on energy. `sample_size` = number sampled per iteration.

## Models (surrogate energy)

```python
from agox.models import GPR, SparseGPR, SparseGPREnsemble, CompositionModel, CalculatorModel

GPR(descriptor, kernel, prior=None, single_atom_energies=None, n_optimize=None,
    optimizer_maxiter=100, centralize=True, filter=<EnergyFilter>, use_ray=True, **kw)
SparseGPR(sigma=0.01, centralize=False, jitter=1e-8, unc_jitter=1e-5, filter=None,
    sparsifier=<CUR>, n_optimize=0, force_data_filter=<NoneFilter>, noise=None,
    sigma_E=None, sigma_F=None, noise_E=None, noise_F=None,
    sparsification_schedule=None, train_uncertainty=False, **kw)
SparseGPREnsemble(N_ensemble=5, target_noise=0.25, prior_noise=0, *args, **kw)
CompositionModel(**kw)
CalculatorModel(calculator, composition_model=True, **kw)
```
`GPR`/`SparseGPR` are Gaussian-process regression surrogates trained on evaluated
structures, used by LCB acquisitors to drive the search. `single_atom_energies` supplies
per-species reference energies (list or `{symbol: energy}` dict).

## Acquisitors

```python
from agox.acquisitors import (LowerConfidenceBoundAcquisitor, LCBPenaltyAcquisitor,
    PowerLowerConfidenceBoundAcquisitor, MetaInformationAcquisitor, ReplicaExchangeAcquisitor)

LowerConfidenceBoundAcquisitor(model, kappa=1, **kw)
LCBPenaltyAcquisitor(model, descriptor, penalty_scale=1.0, **kw)
PowerLowerConfidenceBoundAcquisitor(power=0, *args, **kw)
MetaInformationAcquisitor(meta_key, mode='min', **kw)
```

## Collectors

```python
from agox.collectors import ParallelCollector, StandardCollector, ReplicaExchangeCollector
ParallelCollector(num_candidates=None, **kw)
StandardCollector(num_candidates, **kw)
```
`ParallelCollector` (ray-backed) parallelizes candidate evaluation.

## Candidates

```python
from agox.candidates import StandardCandidate
StandardCandidate(template=None, template_indices=None, use_cache=True, **kw)
```
An ASE `Atoms` subclass; carries energy/relaxation info. `CandidateBaseClass` is the ABC.

## Descriptors

```python
from agox.models.descriptors import (Fingerprint, SimpleFingerprint, SOAP,
    SpectralGraphDescriptor, Voronoi, VoronoiSite, ACSF, ExponentialDensity)

Fingerprint(rc1=6, rc2=4, binwidth=0.2, Nbins=30, sigma1=0.2, sigma2=0.2, gamma=2,
            eta=20, use_angular=True, *args, **kw)
SimpleFingerprint(Nbins=30, width=0.2, r_cut=3, separate_center_species=True, *args, **kw)
SOAP(r_cut=4, nmax=3, lmax=2, sigma=1.0, weight=True, periodic=True, dtype='float64',
     crossover=False, compression=None, *args, **kw)
SpectralGraphDescriptor(mode='adjacency', diagonal_mode='atomic_number',
    number_to_compare='all', descending=False, scale_factor=1.3, *args, **kw)
Voronoi(indices=None, template=None, covalent_bond_scale_factor=1.3, n_points=8,
        angle_from_central_atom=20, *args, **kw)
VoronoiSite(*args, site_mapping=..., **kw)
```

## Kernels (GPR)

```python
from agox.models.GPR.kernels.kernels import (RBF, Constant, Noise, Sum, Product,
    DotProduct, RationalQuadratic)
```
sklearn-backed covariance kernels for `GPR`/`KernelSimSampler`.

## Helpers

```python
from agox.helpers import SubprocessGPAW, GPAW_IO, Confinement
SubprocessGPAW(ncores=None, log_directory='gpaw_logs/', **kw)  # mode={"name": "lcao"}
GPAW_IO(parexe=True, par_command='mpiexec', script_name='gpaw_calc.py',
        settings_name='gpaw_settings.pckl', modules=[], **kw)
Confinement(cell=None, corner=None, indices=None, pbc=None)
```
`SubprocessGPAW` runs GPAW in a subprocess (parallel-capable). `mode` is a dict
(`{"name": "lcao"}`), and all other `**kw` are forwarded to `gpaw.GPAW` (`xc`, `h`, ...).

## Base classes / plumbing

```python
from agox import Module, Observer, Writer, State
Module(use_cache=False, surname=None, verbosity=Writer.STANDARD)
Observer(gets=None, sets=None, order=None, **kw)      # gets/sets: list[dict]; order: list
```
`Observer.attach(handler)` registers its `ObserverMethod`s; `ObserverHandler.dispatch` runs
them by `order` against the per-iteration `State`. `Writer` handles logging/verbosity.
