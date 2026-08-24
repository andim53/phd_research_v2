# Benchmarking a custom AGOX acquisitor against the stock one (EMT surrogate)

Reusable recipe for comparing a custom acquisitor (e.g. `NoveltyLCBAcquisitor`) against
a stock AGOX one (`LowerConfidenceBoundAcquisitor`) on a **cheap EMT surrogate system**,
so you can iterate on acquisition behaviour without burning DFT. Grounded in
`_run/a_lcbnovel/main_benchmark.py` (Ni8 / Au(4,4,2) fcc100, EMT) and its ancestor
`_run/6_lcbnovel_benchmark/run.py`.

## When to use

- You changed a custom acquisitor and want a quantitative before/after against stock LCB.
- Validating that the auto global-minimum window / per-atom window actually improves
  diversity or duplicates vs regular LCB.
- Any cheap, fast head-to-head of acquisition strategies on a small model.

## Recipe

1. **Pick a small EMT system.** e.g. `Ni8` on `Au(4,4,2)` fcc100 (run 6 / 10 default):
   `fcc100("Au", size=(4,4,2), vacuum=5.0)`, `pbc=[True,True,False]`, confinement_z=4,
   EMT calculator. Fast, local, no Ray-heavy DFT.
2. **Build ONE shared stack**, switch only the acquisitor:
   ```python
   def build_stack(acq_type, db_path, seed):
       # system, database, descriptor, GPR, KMeansSampler, ParallelCollector,
       # ParallelRelaxPostprocess (model=acquisitor.get_acquisition_calculator()),
       # LocalOptimizationEvaluator(calculator=EMT(), ...)
       if acq_type == "regular_lcb":
           acq = LowerConfidenceBoundAcquisitor(model=model, kappa=2.0, order=3)
       elif acq_type == "novelty_lcb":
           acq = NoveltyLCBAcquisitor(model=model, descriptor=desc, database=db,
                                      energy_above_min=X, per_atom=True,
                                      novelty_weight=1.5, kappa=2.0, order=3)
       ...
       return AGOX(collector, relaxer, acq, evaluator, database, seed=seed)
   ```
3. **Multiple seeds for statistics** (`SEED_LIST=[41,101,201,301,401]`, `N_ITERATIONS=30`),
   each acquisitor on the SAME seeds → per-seed DB, then aggregate.
4. **Metrics** (reuse run-6's `get_distinct_configurations` greedy fingerprint clustering):
   - distinct configurations found (lower-energy-first, threshold on raw fingerprint distance),
   - best energy, energy range,
   - duplicate evaluations = n_evals − n_distinct,
   - discovery curves (cumulative distinct vs cumulative evals, averaged),
   - paired differences (novelty − regular) per run + aggregate stats.
5. **Outputs**: `benchmark_results.json` (params + per-run dicts) + 2 PNG plots
   (per-run bar/line comparison, discovery curves; pair-difference panels).

## Pitfall — per_atom window X scales with atom count

With `per_atom=True`, the window cap is `E_min/N + X` per atom → the **total** cap is
`E_min + X*N`. On a 40-atom Au+Ni cell, `X=1.0` eV/atom = **40 eV above global min** —
effectively no constraint. If the user asks for "1 eV/atom" on a small system, flag this
and pick a much smaller value (e.g. 0.1 eV/atom → 4 eV cap) or use total-eV mode. Always
state the resulting total cap in the run log (`X * N`).

## Environment / Ray

- `ParallelCollector` / `ParallelRelaxPostprocess` use a Ray pool internally, so the
  benchmark **cannot complete on a low-RAM node** (`ray.exceptions.ActorUnavailableError`,
  environmental). `use_ray=False` on the GPR alone does NOT remove Ray (the parallel
  components still need the pool). Run the full benchmark on the HPC cluster or a
  RAM-rich node; set `USE_RAY=False` to cut GPR actor churn but expect Ray for the pool.
- Validate the acquisitor **window logic in isolation** (no Ray) with mock
  model/descriptor/database via `object.__new__(Acquisitor)` + attribute assignment
  (`test_window_logic.py` pattern) before spending a full benchmark run.
