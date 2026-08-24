# AGOX subpackage map (3.10.2)

One-line purpose per module/package under `agox/`. Grouped by role in the search loop.

## Core / orchestration

- `module.py` — `Module` base class (Writer, surname, cache, submodule discovery).
- `observer/` — `Observer` base (`gets`/`sets`/`order`), `ObserverHandler`,
  `ObserverMethod`, `FinalizationHandler`.
- `main/` — `agox.py` (`AGOX` orchestrator, `.run(N_iterations)`), `state.py` (`State`
  per-iteration cache).
- `writer/` — `Writer` logging/verbosity.

## Search-loop components

- `generators/` — new-candidate generators: `RattleGenerator`, `RandomGenerator`,
  `CenterOfGeometryGenerator`, `SteepestDescentGenerator`, `PermutationGenerator`,
  `ReplaceGenerator`, `ReuseGenerator`, `SamplingGenerator`, `ComplementaryEnergyGenerator`,
  `Symmetry*Generator`s, `MDgenerator`.
- `samplers/` — candidate selection: `KMeansSampler`, `MetropolisSampler`, `GeneticSampler`,
  `KernelSimSampler`, `FixedSampler`, `SpectralGraphSampler`, `ConcurrentTemperingSampler`,
  `ReplicaExchangeSampler`.
- `evaluators/` — energy/structure evaluation: `LocalOptimizationEvaluator`,
  `SinglePointEvaluator`, `RattleEvaluator`.
- `collectors/` — candidate collection/parallelization: `ParallelCollector` (ray),
  `StandardCollector`, `ReplicaExchangeCollector`.
- `databases/` — persistent storage (ASE db): `Database`, `database_concurrent`,
  `concurrent_ordered`, `database_utilities`.
- `environments/` — `Environment` (template, confinement, stoichiometry), `DatabaseEnvironment`.
- `candidates/` — `StandardCandidate` (Atoms subclass), `CandidateBaseClass`.
- `postprocessors/` — post-relax transforms: `relax`, `centering`, `surface_centering`,
  `minimum_dist`, `disjoint_filtering`, `wrap`, `ray_relax`.

## Surrogate models & acquisition

- `models/` — `GPR`, `SparseGPR`, `SparseGPREnsemble`, `CompositionModel`, `CalculatorModel`;
  subdirs: `GPR/` (kernels, etc.), `descriptors/` (Fingerprint, SimpleFingerprint, SOAP,
  SpectralGraphDescriptor, Voronoi, VoronoiSite, ACSF, ExponentialDensity), `priors/`,
  `datasets/`, `schnetpack/` (SchNet integration).
- `acquisitors/` — `LowerConfidenceBoundAcquisitor`, `LCBPenaltyAcquisitor`,
  `PowerLowerConfidenceBoundAcquisitor`, `MetaInformationAcquisitor`,
  `ReplicaExchangeAcquisitor`.
- `models/GPR/kernels/kernels.py` — RBF, Constant, Noise, Sum, Product, DotProduct,
  RationalQuadratic.

## Analysis & utilities

- `analysis/` — `SearchAnalysis`, `SearchData`, `plot/`, `criterion/`, `property/`,
  `search_analysis.py`, `search_data.py`.
- `utils/` — `cache`, `constraints/`, `filters/`, `metrics/`, `plot/`, `ray/`,
  `sparsifiers/`, `thermodynamics/`, `graph_sorting`, `numerical_derivative`,
  `jupyter_interactive`, `convert_database`.
- `helpers/` — `Confinement`, `GPAW_IO`, `SubprocessGPAW` (GPAW subprocess wrapper).
- `cli/` — `agox` command-line entry (`main`).
- `test/` — test suite incl. `test/run_tests/tests_bh/script_bh_*.py` canonical runscripts
  (cluster/surface/bulk x EMT/GPAW/VASP/CHGNet/ORCA).

## Notes

- `__all__` is redefined to `[]` at the bottom of some `__init__.py` files (e.g.
  `generators/__init__.py`), so `from agox.<pkg> import *` is unreliable — use explicit
  imports.
- The `agox` top-level `__init__.py` exports `Module`, `Observer`, `Writer`, `State`,
  `AGOX`, `main`, `__version__`.
