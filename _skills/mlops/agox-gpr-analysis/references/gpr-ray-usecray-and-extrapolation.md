# GPR Ray ActorUnavailableError fix + "unphysical energy" mechanism

Session-derived durable notes (Fe/MgO multi-seed nested-sampling run,
`_run/8_nested_sampling/`). Two debugging/explanation lessons worth keeping.

## Fix: `GPR(use_ray=False)` — Ray ActorUnavailableError under memory pressure

**Symptom:** script crashes at the very first `GPR(...)` constructor, before any
training or run:

```
  gpr = build_gpr(structures)
  gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
  ...
  ray.exceptions.ActorUnavailableError: The actor ... is unavailable:
  The actor is temporarily unavailable: IOError: The actor was restarted.
```

Independently of `--perturb` / `--n-iters`. It is purely environmental, not a code
bug: the identical script succeeds when less RAM is in use.

**Root cause:** `GPR` defaults to `use_ray=True`. In `__init__` it calls
`pool_add_module(self)` → `ray.get(futures)`, spawning **one Ray actor per CPU**
(4 on a typical node) to hold copies of the model for parallel hyperparameter
optimization. When memory is ~95–100% full (concurrent DFT jobs + IDE/LSP servers +
Hermes gateways), the OS/Ray kills an actor → ActorUnavailableError (or a Ray OOM
kill at lower pressure).

**Fix (verified against `agox/models/GPR/GPR.py`):**
```python
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(), use_ray=False)
```
With `use_ray=False`, the `else` branch runs: it does **not** call
`pool_add_module` (no actors → the error is structurally impossible) and sets
`n_optimize = 1` (single-process hyperparameter optimization).

**Trade-offs:**
- Training runs on 1 process instead of 4 → a bit slower (~2 min → a few minutes on
  1297 points). Does not change the sampling math or analysis.
- Avoids Ray temp-folder noise.
- For long jobs, scale out by submitting many **independent single-process** jobs
  (one per temperature / per seed) rather than MPI-parallelising one sampler — the
  sampler is single-process by design after this fix.

## "Extrapolate to unphysical energies" — mechanism

Large `--perturb` makes the Fingerprint GPR return nonsense energies
(thousands of eV; observed posterior E_mean ≈ +700 eV vs. real range ~ −400 eV).

**Mechanism** (`structure → Fingerprint 720-d → GPR.predict_energy()`):
1. GPR trained on 1297 structures whose descriptors lie in a tight 720-D region.
2. `--perturb` adds Gaussian noise to atom positions *before* the likelihood is
   computed, so the GPR energy drives nested sampling.
3. The Fingerprint bins radial distances (`rc1=6 Å`, `binwidth=0.2`) and angles;
   even a modest shake redistributes counts across the histogram bins.
4. A GP is only trustworthy when interpolating. Once the perturbed descriptor sits
   far from *every* training point, kernel covariances → 0 and the prediction is
   pulled back to the GP prior mean — a large, physically meaningless offset. Result:
   nonsense energies (thousands of eV) instead of the physical range.

**Evidence observed:** with `--perturb 0.5`, the log showed `Replacing 2 unphysical
live points` and `E_boundary = 2414.7 eV`, posterior `E_mean = +724 eV`.

**Handling:** `|E_gpr| > 1e4 eV` → `log_likelihood` returns `-inf`,
`_filter_unphysical()`/`sample_constrained()` drop/redraw those points. This keeps the
run stable but is a **pragmatic filter, not a physical guarantee** — a structure can
sit just inside 1e4 yet still be a corrupt extrapolation, silently biasing the
posterior/evidence. Hence keep `--perturb` small (0.01 Å) or 0.

## Species-restricted perturbation (deposit layer only)

To perturb only the deposition species (Fe) and leave the Mg/O substrate fixed, build
an index mask from the first structure's symbols and reuse it:

```python
symbols = np.array(db_structures[0].get_chemical_symbols())
self.perturb_indices = np.where(np.isin(symbols, ["Fe"]))[0]
def sample_from_prior(self):
    base = self.db_structures[self.rng.integers(0, len(self.db_structures))].copy()
    if self.perturb > 0:
        n = self.rng.normal(0, self.perturb, (len(self.perturb_indices), 3))
        base.positions[self.perturb_indices] += n
    return base
```

## Literature parameters vs this script (Partay 2021, Yang 2024)

- **Live-set size K** (script: `--n-live`) is the central accuracy lever:
  phase-space volume `Γ_i = Γ_0·[K/(K+1)]^i`, error in ln Γ ∝ 1/√K. Paper guidance:
  bulk K = 500–5000 (N = 32–256 atoms, L = 100s–1000s, 10^5–10^7 iterations); surfaces
  (Yang 2024) = 80 walkers per free particle × 250 iter/walker
  (= 320 000 iterations at full coverage).
- **Walk length L** is the MC decorrelation length for cloned configurations; the
  minimum sufficient L *decreases* as K grows. The papers clone-and-diffuse; our
  DB-resample + small-perturb prior has no explicit L — the main structural gap.
- **Iteration count** is set by the minimum temperature to resolve and scales
  ~linearly with K.
- **Temperature β is NOT a sampling parameter in the papers** — applied only in
  post-processing to evaluate Z(β) at any T from a single run. Our sampler instead
  puts `L(x) = exp(-β·(E − E_ref))` inside the likelihood (fixed-temperature NS), so
  the posterior/evidence here are T-specific.