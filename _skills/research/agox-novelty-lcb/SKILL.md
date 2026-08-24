---
name: agox-novelty-lcb
description: "Use when running or debugging AGOX Novelty-LCB searches."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agox, novelty, lcb, gpr, acquisition, structure-search]
    related_skills: [agox, agox-run-code, agox-novel-filter, agox-nested-sampling, simulation-analysis]
---

# Novelty-LCB Structure Search on AGOX

## Overview

Novelty-LCB is a diversity-focused acquisition function for AGOX global-optimization
searches (e.g. depositing Fe atoms on a fixed MgO substrate). It maximises

    a(x) = sigma(x) + lambda * Novelty(x)

within an energy window `[E_target - delta_E, E_target + delta_E]`. It is NOT an
energy-minimiser: it seeks regions the GPR surrogate is uncertain about AND that are
structurally new, while staying inside a chosen energy band.

Reusable implementation lives in the local `novelty_lcb` package (an AGOX
`AcquisitorBaseClass` subclass). Copies exist per-project; the canonical fixed copy is
in `/home/think/Desktop/research/_run/10_lcbnovel/novelty_lcb/`.

## When to Use

- Running a Novelty-LCB vs regular-LCB AGOX search (benchmark or production).
- Debugging the classic "cannot pickle 'sqlite3.Connection'" Ray serialization crash.
- Explaining how the acquisitor, sampler, and relaxation surface fit together.

## Environment

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX + ASE). Base `python3`
  has NO AGOX/ASE.
- **Env split (Fe/MgO runs):** local dev/test uses `agox_v2`; the HPC pjsub heavy run
  uses `gpaw_env` (set in the `.sh` batch script).
- `matplotlib.use('Agg')` before plotting in headless runs.

## Acquisition mechanics (verified in code)

1. `calculate_acquisition_function(candidates)` returns the **NEGATED** value `-a(x)`
   because AGOX sorts **ascending** (lowest value = best = selected first). The
   candidate with the largest TRUE a(x) ends up most negative and is picked first.
2. Out-of-window candidates (predicted `E` outside `[target-delta_E, target+delta_E]`)
   get `+np.inf` in the sorting space and are never selected.
3. `Novelty(x) = min_{i in DB} ||f(x) - f(x_i)||_2` — minimum Euclidean distance in the
   FULL fingerprint descriptor space (e.g. 720-dim for Fe/MgO), **no PCA**. Empty DB ->
   novelty 0 -> pure uncertainty sampling.
4. `sigma(x)` = GPR predictive std from `model.predict_energy_and_uncertainty`; kernel
   posterior uncertainty vs training points in feature space.
5. **Relaxation surface:** selected candidates are pre-relaxed on the LCB surface
   `E - kappa*sigma` via `get_acquisition_calculator()` -> `LowerConfidenceBoundCalculator`,
   NOT on the full a(x). Novelty is a discrete min-distance with no well-defined force,
   so it cannot drive relaxation. Then the survivors are evaluated by the real calculator
   (e.g. GPAW).

## Energy window modes (incl. the auto global-minimum mode)

There are **two** window modes, controlled by constructor kwargs:

- **Centered mode (legacy):** `target_energy ± delta_E`. Requires the energy band to be
  known in advance — which forced a regular-LCB run first. Out-of-window candidates get
  `+inf`.
- **Auto global-minimum mode (default now):** pass `energy_above_min=X`. The window is
  anchored to the **live lowest energy in the DB** and searches a set amount above it,
  so **no prior regular-LCB calibration run is needed**:
    - `per_atom=False` (total eV): window = `(-inf, E_min + X]`.
    - `per_atom=True` (eV/atom, RECOMMENDED): both the candidate predicted `E` and the
      global min `E_min` are divided by the atom count `N`, so `X` is in eV/atom and the
      window is size-independent (choose 0.5-2 eV/atom directly).
      window = `(-inf, E_min/N + X]` per atom.
    - `E_min` is recomputed each acquisition round from the DB (`get_all_candidates`),
      so it tracks new minima as they are found; there is **no lower bound**, so a new
      lower global minimum can still be discovered. Empty DB -> no cap (search freely).
    - For a fixed atom count `N`, `per_atom` mode with `X` is exactly equivalent to total
      mode with `X*N` (same accept/reject). Verify this with the isolated test below.
  - Backward compatible: `energy_above_min=None` falls back to the centered mode.

`E_min` is the lowest **total** energy from `c.get_potential_energy()` (ASE convention);
the window compares against the GPR's **absolute predicted total energy** `E`. Setting
`target_energy=0` does NOT mean "search near 0 eV" — total energies are ~ -400 eV for a
75-atom Fe/MgO slab, so a window around 0 excludes everything. 0 only makes sense for
relative energies (formation energy / shifted E_ref).

## The KMeansSampler's role (often confused)

`KMeansSampler` sits BETWEEN the collector and the acquisitor. It thins the pool of
ALREADY-EVALUATED (relaxed + scored) structures down to a diverse representative set
before the acquisitor scores them:
- Clusters structures by fingerprint features (sklearn KMeans).
- `n_clusters = 1 + min(sample_size - 1, floor(len(energies)/5))` — AUTOMATIC, capped at
  `sample_size`; you do not pick the cluster count.
- Energy criterion: `max_energy=5` eV filter drops anything >5 eV above the lowest,
  and within each cluster the LOWEST-energy member is kept.
- Result: <= sample_size representatives (one per structural basin) so a basin of
  near-duplicates can't dominate the novelty/uncertainty scoring.

## Critical pitfall: Ray sqlite-pickle serialization

**Symptom:** crash at the FIRST stack build with
`TypeError: Could not serialize ... cannot pickle 'sqlite3.Connection' object`, or
`ray.util.inspect_serializability` reports a FAIL on a `LowerConfidenceBoundCalculator`.

**Root cause:** the acquisitor's `get_acquisition_calculator()` passed BOUND METHODS
(`self._acquisition_energy`) into `LowerConfidenceBoundCalculator`. A bound method
captures the whole acquisitor instance, including its sqlite-backed `Database` (a live
`sqlite3.Connection`), which breaks `ray.put` serialization. The GPR model itself is
fine (its `database=` kwarg only wires an observer via `self.attach(database)`, it does
NOT store `self.database`).

**Fix:** pass module-level FREE FUNCTIONS wrapped in `functools.partial` so only scalar
`kappa` is captured:

```python
def lcb_acquisition_energy(E, sigma, kappa=1.0): return E - kappa*sigma
def lcb_acquisition_force(E, F, sigma, sigma_force, kappa=1.0): return F - kappa*sigma_force
# in get_acquisition_calculator():
return LowerConfidenceBoundCalculator(
    self.model,
    partial(lcb_acquisition_energy, kappa=self.kappa),
    partial(lcb_acquisition_force, kappa=self.kappa),
)
```

**Validate cheaply (no heavy DFT):** build a tiny EMT system, call
`get_acquisition_calculator()`, then assert `pickle.dumps(calc)` succeeds AND
`ray.util.inspect_serializability(calc)` has 0 FAIL markers AND
`ParallelRelaxPostprocess(model=calc, ...)` constructs AND a 2-iteration
`agox.run()` completes. See `scripts/smoke_test_serialization.py`.

## Validating window logic standalone (no Ray)

When the full AGOX stack can't run (low-RAM node -> Ray `ActorUnavailableError`), you can
still validate the acquisitor's window logic in isolation with mock objects — NO Ray, NO
AGOX stack. Key trick: build the acquisitor with `object.__new__(NoveltyLCBAcquisitor)`
and assign attributes manually to bypass `__init__`'s strict `DatabaseBaseClass` type
check / observer attach:

```python
acq = object.__new__(NoveltyLCBAcquisitor)
acq.model = MockModel(); acq.descriptor = MockDescriptor()
acq.database = MockDB(energies, n_atoms=75)
acq.target_energy = None; acq.delta_E = 1.0
acq.energy_above_min = X; acq.per_atom = True
acq.novelty_weight = 1.0; acq.kappa = 2.0; acq._db_features = None
vals = acq.calculate_acquisition_function([MockCand(E)])
# assert np.isinf(vals[0]) is True/False as expected
```

Mocks need: `MockModel.predict_energy_and_uncertainty(cand)`, `MockDescriptor.get_features(cand)`,
`MockDB.get_all_candidates()` returning objects with `get_potential_energy()` and `len()`
(the `_n_atoms()` helper calls `len(cands[0])`). A valuable equivalence check: for fixed
`N`, `per_atom=True` with `X` gives IDENTICAL accept/reject to `per_atom=False` with `X*N`.
See the reference below for a full worked test.

## Benchmark harness (regular LCB vs Novelty-LCB)

To compare the acquisitors on a fast system, use an EMT surface (e.g. Ni8/Au(4,4,2)
fcc100), run BOTH acquisitors on the SAME seeds with the SAME stack (only the acquisitor
differs), and reuse the run-6 metric set: distinct configurations (fingerprint
clustering), best E, energy range, duplicate evals, discovery curves, aggregate stats +
plots. This is `main_benchmark.py` + `j_benchmark.sh` (HPC) in the 10_lcbnovel project.
Both acquisitors' per-seed DBs are written under `benchmark_results/` (gitignored `*.db`).
The benchmark needs a RAM-rich node / HPC for the Ray pool.

## Common Pitfalls

1. **Never use bound methods in the acquisition calculator** — always
   `functools.partial` over module-level free functions (Ray pickling).
2. **Window is on ABSOLUTE predicted energy `E`** — `target_energy` must be a real energy
   in the band (e.g. ~ -400 eV), NOT 0; setting it to 0 excludes everything. Prefer the
   **auto global-minimum mode** (`energy_above_min` + `per_atom`) so no calibration run
   is needed. The old centered `target ± delta_E` mode requires mapping the band first.
3. **`LocalOptimizationEvaluator` missing `calculator`** — the kwargs key is
   `calculator`, not `calc`; pass positionally to avoid the trap.
4. **Uniform composition required** for a single global Fingerprint descriptor.
5. **No long comment blocks in user's `.sh` batch scripts** — the user wants bare
   scripts (see user-preference note below).
6. **AGOX Parallel* components need RAM** — `ParallelCollector` / `ParallelRelaxPostprocess`
   spawn a Ray pool; on a low-RAM node they fail with Ray `ActorUnavailableError`
   (environmental). `GPR(use_ray=False)` removes the GPR's per-CPU actors but NOT the
   parallel pool, so an EMT benchmark still needs a RAM-rich node / HPC. Validate the
   window logic standalone instead (see below), which needs no Ray.

## User preferences (this user, Fe/MgO / AGOX work)

- **Clarify before every step** — confirm task, approach, and outputs before writing
  or running code; restate understanding of provided code first.
- **pjsub launch:** use `pjsub j_novel.sh` (no `-x SEED=N`); set the seed by editing a
  `SEED=3` variable at the top of the script.
- **No verbose comment block** at the top of `.sh` batch scripts.
- **Project workflow:** when standing up a documented project, produce README (human +
  AI `README.AI.md`), an append-only `LOG.md` + raw `transcript.log`, and a `TUTORIAL.md`,
  plus an `AGENTS.md` rule file; commit after every change (confirm with owner on
  milestones). Keep the docs grounded in the actual code, not generic descriptions.
- **Explanations in README:** when the owner drops a `Note:` block asking conceptual
  questions ("what does Novelty(x) do?", "how is sigma computed?", "how is a candidate
  picked?"), replace it with a proper explanatory subsection, answered inline and
  grounded in the real source, in the same spot.

## Reference files

- `references/novelty-lcb-repair.md` — the run-7 crash transcript, root-cause analysis,
  and end-to-end repair recipe.
- `references/energy-window-calibration.md` — calibrating the legacy centered window
  from an LCB-only dataset.
- `references/auto-window-and-test.md` — the auto global-minimum mode
  (`energy_above_min` + `per_atom`), the per_atom/total equivalence proof, and the
  full isolated mock test (no Ray).
- `scripts/smoke_test_serialization.py` — cheap local Ray-picklability validation.
