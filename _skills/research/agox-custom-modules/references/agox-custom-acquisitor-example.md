# Worked Example: A Custom AGOX Acquisitor (Novelty-LCB)

Session-derived pattern for a custom acquisitor that adds a structural-novelty bonus and an
energy-window filter on top of lower-confidence-bound uncertainty sampling. Verified against
AGOX 3.10.2 in the `agox_v2` conda env (Python 3.11). The complete, working implementation
lives in the user's project at `_run/7_lcbnovel_mgofe/novelty_lcb/acquisitor.py`.

## Acquisition function

    a(x) = sigma(x) + lambda * Novelty(x)     [to MAXIMIZE]

    Novelty(x) = min_{i in DB} ||fingerprint(x) - fingerprint(x_i)||_2

subject to the energy window `E_target - delta_E <= mu(x) <= E_target + delta_E`; out-of-window
candidates are excluded.

**AGOX sorting note:** `AcquisitorBaseClass.sort_according_to_acquisition_function` sorts
**ascending** (lowest value = best = selected first). So `calculate_acquisition_function` must
return the **negated** value `-(sigma + lambda*novelty)` so the highest a(x) sorts first.
Out-of-window candidates get `+np.inf` so they always sort last (never selected). When the DB is
empty, `Novelty(x) = 0` and it reduces to pure uncertainty sampling within the window.

## Class skeleton (the interface AGOX requires)

```python
from agox.acquisitors.ABC_acquisitor import AcquisitorBaseClass

class NoveltyLCBAcquisitor(AcquisitorBaseClass):
    name = "NoveltyLCBAcquisitor"

    def __init__(self, model, descriptor, database, target_energy,
                 delta_E=0.5, novelty_weight=1.0, kappa=1.0, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.descriptor = descriptor
        self.target_energy = target_energy
        self.delta_E = delta_E
        self.novelty_weight = novelty_weight
        self.kappa = kappa
        self._db_features = None
        self.attach_to_database(database)   # registers observer; self.database now held!

    def calculate_acquisition_function(self, candidates):   # required
        # returns np array of NEGATED a(x); +inf for out-of-window
        ...

    def print_information(self, candidates, acquisition_values):  # required
        ...

    def do_check(self, **kwargs) -> bool:      # required
        return self.model.ready_state

    def get_acquisition_calculator(self):      # REQUIRED - see below
        from agox.acquisitors.LCB import LowerConfidenceBoundCalculator
        from functools import partial
        return LowerConfidenceBoundCalculator(
            self.model,
            partial(lcb_acquisition_energy, kappa=self.kappa),
            partial(lcb_acquisition_force, kappa=self.kappa),
        )
```

## The critical detail: keep acquisition functions module-level

Because the acquisitor calls `attach_to_database(database)`, it holds `self.database`, and a
`Database` owns a live `sqlite3.Connection`. If `get_acquisition_calculator` passes **bound
methods** (`self._acquisition_energy`) to `LowerConfidenceBoundCalculator`, the calculator's
pickle graph captures `self` → the DB → the sqlite connection, and `ParallelRelaxPostprocess`
crashes in `ray.put`:

    TypeError: cannot pickle 'sqlite3.Connection' object

Always define the surface functions at module scope and pass them via `functools.partial`
closed over only scalars:

```python
def lcb_acquisition_energy(E, sigma, kappa=1.0):
    return E - kappa * sigma

def lcb_acquisition_force(E, F, sigma, sigma_force, kappa=1.0):
    return F - kappa * sigma_force
```

`functools.partial` pickles just the function + scalar kwargs — no `self`, no database. The stock
`LowerConfidenceBoundAcquisitor` never needs this because it never stores a database.

## Why the relaxation surface excludes the novelty bonus

The novelty term is a **discrete** min-Euclidean-distance in descriptor space — not differentiable
w.r.t. atomic positions, so it has no well-defined force. Candidate pre-relaxation
(`ParallelRelaxPostprocess`) therefore runs on the differentiable LCB surface `E - kappa*sigma`;
the novelty bonus drives **selection only** via `calculate_acquisition_function`.

## Database-attached feature cache (optional but useful)

The acquisitor keeps `self._db_features` (shape `(n_db, n_features)` or None) and extends it on
each database-store event via an observer method:

```python
from agox.observer import Observer
from agox.main import State

self.add_observer_method(self._on_database_store, gets={}, sets={},
                         order=self.order[0], handler_identifier="database")
self.attach(database)

@Observer.observer_method
def _on_database_store(self, database, state): ...
```

When the DB is empty `_db_features is None`, so novelty defaults to 0.0 (pure uncertainty
sampling). Rebuild on demand with `self.database.get_all_candidates()` →
`self.descriptor.get_features(c).ravel()`.

## main.py wiring (order matters)

```python
database   = Database(filename=..., order=5)
descriptor = Fingerprint(environment=env)
model      = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())
sampler    = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)
collector  = ParallelCollector(generators=generators, sampler=sampler,
                               environment=environment, num_candidates=..., order=1)
acquisitor = NoveltyLCBAcquisitor(model=model, descriptor=descriptor, database=database,
                                  target_energy=..., delta_E=..., novelty_weight=..., order=3)
relaxer    = ParallelRelaxPostprocess(model=acquisitor.get_acquisition_calculator(),
                                      constraints=environment.get_constraints(),
                                      optimizer_run_kwargs={"steps": 100},
                                      start_relax=10, order=2)
evaluator  = LocalOptimizationEvaluator(calc, gets={"get_key": "prioritized_candidates"}, ...)
agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
agox.run(N_iterations=...)
```

A healthy setup log shows the AcquisitionCalculator connected to the GPR in the pool:
"Connected AcqusitionCalculator with GPR" and the full observer pipeline
(generate_candidates order1 → postprocess_candidates order2 → prioritize_candidates order3 →
evaluate order4 → store_in_database order5).

## Calibration warning

A target_energy window that is uncalibrated (e.g. `target_energy=0.0` on a system whose energy
scale is different) can exclude essentially all candidates. Calibrate it against a short
standard-LCB search first.
