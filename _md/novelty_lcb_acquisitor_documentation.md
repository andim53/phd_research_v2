# Novelty-LCB Acquisition Function for AGOX

**Created:** 2026-08-19  
**Environment:** `agox_v2` conda env — AGOX 3.10.2 + ASE 3.25.0  
**Python:** `/home/miniconda3/envs/agox_v2/bin/python`

---

## 1. Motivation — Why This Exists

### The problem with pure uncertainty sampling

A standard GPR model is only confident (or only uncertain) in a fairly local neighborhood of its training data. If you select candidates purely by uncertainty `σ(x)`, you risk repeatedly visiting the vicinity of the same local minimum rather than discovering genuinely new ones.

### The energy-window problem

If you care about structures within a specific energy range (e.g., "find all structures with energy between −2.8 and −2.2 eV"), a standard LCB acquisitor (`E − κσ`) has no built-in mechanism to restrict selection to that window. You need an explicit filter.

### The novelty solution

Add a **novelty** term based on structural distance to the existing database:

$$\text{Novelty}(x) = \min_{i \in \text{DB}} d_{\text{fingerprint}}(x, x_i)$$

A candidate is "novel" only if it is far from **every** structure discovered so far — not just far from one. This pushes the search to unexplored regions of structure space.

---

## 2. The Acquisition Function

### Full definition

$$a(x) = \sigma(x) + \lambda \cdot \text{Novelty}(x)$$

subject to:

$$E_{\text{target}} - \Delta E \le \mu(x) \le E_{\text{target}} + \Delta E$$

Candidates outside the energy window are excluded by assigning `a(x) = −∞` (in the true acquisition space), which maps to `+∞` in the sorting space used by AGOX (so they are never picked).

### Parameters

| Parameter | Meaning |
|---|---|
| `σ(x)` | GPR prediction uncertainty (eV) |
| `λ` (`novelty_weight`) | Weight balancing uncertainty vs. novelty |
| `Novelty(x)` | Minimum Euclidean distance in fingerprint space to any DB structure |
| `E_target` | Center of the energy window (eV) |
| `ΔE` (`delta_E`) | Half-width of the energy window (eV) |

When `λ = 0`, the acquisitor reduces to pure uncertainty sampling within the energy window. When the database is empty, `Novelty(x) = 0` for all candidates.

### Duplicate rejection

Before storing a newly evaluated structure, the same novelty distance can be used as a duplicate filter:

```python
def is_distinct(candidate, database, descriptor, threshold=0.1):
    return min(descriptor.distance(candidate, s) for s in database.structures) > threshold
```

This ensures structurally similar variants of the same local minimum are not stored as separate, independent basins.

---

## 3. Code Architecture

### File layout

```
/home/Desktop/research/
├── novelty_lcb_acquisitor.py   # The acquisitor class + utilities
├── test_novelty_lcb.py         # Verification tests (mocks)
├── graph_novelty_lcb_concept.py  # Concept visualization script
└── novelty_lcb_concept.png     # Generated figure (3 panels)
```

### Class hierarchy

```
AcquisitorBaseClass (AGOX acquisitors/ABC_acquisitor.py)
 └── NoveltyLCBAcquisitor  (this module)

Existing LCB family in AGOX for comparison:
 AcquisitorBaseClass
  ├── LowerConfidenceBoundAcquisitor  (LCB.py: F = E − κσ)
  │   ├── LCBPenaltyAcquisitor       (LCB_penalty.py: + α·n_D)
  │   └── PowerLowerConfidenceBoundAcquisitor  (LCB_power.py: σ^power)
```

### Key design decisions

**Negated sorting.** AGOX's `AcquisitorBaseClass.sort_according_to_acquisition_function` sorts **ascending** — lowest value = best = selected first. Our acquisition function is a *maximization* (`higher a(x) = better`). We therefore return `−a(x)` from `calculate_acquisition_function`, so the candidate with the largest true `a(x)` gets the most negative sorting value and is picked first.

**Out-of-window → +∞.** Candidates outside the energy window receive `+np.inf` in the sorting space, which sorts them last (effectively excluded).

**Live feature cache.** The acquisitor maintains a cached numpy array of all database fingerprint features. It is:
1. Seeded from existing DB contents on construction (`_rebuild_feature_cache`)
2. Extended incrementally when new candidates are stored (`_on_database_store` observer)

This avoids recomputing features for the entire database on every acquisition evaluation.

**Database attachment.** Follows the same pattern as `LCBPenaltyAcquisitor`:
```python
self.add_observer_method(
    self._on_database_store,
    gets={}, sets={},
    order=self.order[0],
    handler_identifier="database",
)
self.attach(database)
```

---

## 4. Files Reference

### `novelty_lcb_acquisitor.py`

| Symbol | Type | Purpose |
|---|---|---|
| `NoveltyLCBAcquisitor` | class | Main acquisitor — implements the novelty-LCB formula with energy window |
| `is_distinct()` | function | Pre-storage duplicate filter using the same novelty distance |
| `fingerprint_distance()` | function | Convenience: Euclidean distance between two structures' fingerprints |

#### `NoveltyLCBAcquisitor` constructor

```python
NoveltyLCBAcquisitor(
    model: ModelBaseClass,        # GPR or other surrogate
    descriptor: DescriptorBaseClass,  # Fingerprint, SOAP, etc.
    database: DatabaseBaseClass,  # AGOX Database
    target_energy: float,         # Center of energy window (eV)
    delta_E: float = 0.5,         # Half-width of energy window (eV)
    novelty_weight: float = 1.0,  # λ: weight of novelty term
    **kwargs,                     # Passed to AcquisitorBaseClass (order, gets, sets, ...)
)
```

#### `NoveltyLCBAcquisitor` methods

| Method | Purpose |
|---|---|
| `calculate_acquisition_function(candidates)` | Returns negated `a(x)` for sorting (out-of-window → +∞) |
| `print_information(candidates, values)` | Prints table with E, σ, novelty, true a(x) |
| `do_check(**kwargs)` | Returns `model.ready_state` |
| `attach_to_database(database)` | Validates DB, registers observer, seeds feature cache |
| `_rebuild_feature_cache()` | Recomputes `_db_features` from all DB candidates |
| `_on_database_store(database, state)` | Observer callback: extends cache when new candidates stored |

#### `is_distinct` signature

```python
def is_distinct(
    candidate: StandardCandidate,
    database: DatabaseBaseClass,
    descriptor: DescriptorBaseClass,
    threshold: float = 0.1,
) -> bool:
```

Returns `True` if the candidate is farther than `threshold` from **all** database entries in fingerprint space.

#### `fingerprint_distance` signature

```python
def fingerprint_distance(
    descriptor: DescriptorBaseClass,
    a: StandardCandidate,
    b: StandardCandidate,
) -> float:
```

Euclidean distance between two structures' fingerprint feature vectors.

---

## 5. Tutorial — Using NoveltyLCBAcquisitor in an AGOX Run

### 5.1 Minimal working example

```python
import matplotlib
matplotlib.use("Agg")

import numpy as np
from ase import Atoms

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.samplers import MetropolisSampler
from agox.models import GPR
from agox.models.descriptors import Fingerprint
from agox.models.GPR.kernels import RBF

# --- Calculator (replace with your own) ---
# from agox.helpers import SubprocessGPAW
# calc = SubprocessGPAW(mode={"name": "lcao"}, xc="PBE")

# --- Environment ---
template = Atoms("", cell=np.eye(3) * 12)
environment = Environment(
    template=template,
    symbols="Au6",
    confinement_cell=np.eye(3) * 6,
    confinement_corner=np.array([3, 3, 3]),
)

# --- Database ---
database = Database(filename="search.db", order=4)

# --- Descriptor (for novelty) ---
fingerprint = Fingerprint(
    environment=environment,
    rc1=6, rc2=4, binwidth=0.2, Nbins=30,
)

# --- Model (GPR) ---
model = GPR(
    descriptor=fingerprint,
    kernel=RBF(),
    database=database,
    order=0,
)

# --- Sampler ---
sampler = MetropolisSampler(temperature=0.25, order=3)

# --- Generator ---
generator = RattleGenerator(
    **environment.get_confinement(),
    environment=environment,
    sampler=sampler,
    order=1,
)

# --- Evaluator ---
evaluator = LocalOptimizationEvaluator(
    calc,  # your calculator
    gets={"get_key": "candidates"},
    store_trajectory=False,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5},
    order=2,
    constraints=environment.get_constraints(),
)

# --- Novelty-LCB Acquisitor ---
from novelty_lcb_acquisitor import NoveltyLCBAcquisitor

acquisitor = NoveltyLCBAcquisitor(
    model=model,
    descriptor=fingerprint,
    database=database,
    target_energy=-2.5,     # focus on structures near −2.5 eV
    delta_E=0.3,            # window: [−2.8, −2.2] eV
    novelty_weight=0.6,     # balance: 0 = pure uncertainty, high = novel structures
    order=4,                # runs after evaluator, before/with database
)

# --- Run ---
agox = AGOX(generator, database, sampler, evaluator, acquisitor, seed=42)
agox.run(N_iterations=100)
```

### 5.2 Understanding the parameters

#### `target_energy` and `delta_E`

Set these to focus the search on a specific energy range. For example:
- Targeting the lowest-energy basin: `target_energy = -3.0, delta_E = 0.5`
- Targeting a specific polymorph: `target_energy = -2.5, delta_E = 0.2`
- No constraint (accept anything): leave `target_energy = None` (all candidates pass the window filter)

#### `novelty_weight` (λ)

This is the key tuning parameter:

| λ value | Behavior |
|---|---|
| `0.0` | Pure uncertainty sampling within the energy window. Will cluster around existing local minima. |
| `0.1 – 0.5` | Slight novelty bias. Mostly uncertainty-driven, but nudges away from known structures. |
| `0.5 – 1.0` | Balanced. Good default for most searches. |
| `1.0 – 5.0` | Strong novelty preference. Will prioritize exploring new structure types even if uncertainty is moderate. |
| `> 5.0` | Novelty-dominated. May pick structurally novel but energetically irrelevant candidates. |

**Rule of thumb:** Start with `novelty_weight = 1.0` and adjust based on whether you see too many redundant structures (increase λ) or too many high-energy outliers (decrease λ).

### 5.3 Using `is_distinct` as a duplicate filter

```python
from novelty_lcb_acquisitor import is_distinct

# Before storing a newly evaluated candidate:
if is_distinct(evaluated_candidate, database, fingerprint, threshold=0.15):
    database.store_candidate(evaluated_candidate)
    print("  Stored: structurally distinct")
else:
    print("  Skipped: duplicate of existing structure")
```

The `threshold` should be chosen based on the fingerprint descriptor's typical distance scale. A good starting point is `0.1` for the default `Fingerprint` descriptor. You can calibrate by computing pairwise distances among a few known distinct structures.

### 5.4 Reading acquisition values from the run output

During a run, the acquisitor prints a table like:

```
  [  0] E=  -2.4123  σ=   0.312  novelty=   1.245  a(x)=   1.079
  [  1] E=  -2.5871  σ=   0.287  novelty=   0.432  a(x)=   0.546
  [  2] OUTSIDE ENERGY WINDOW — excluded
  [  3] E=  -2.3901  σ=   0.415  novelty=   2.103  a(x)=   1.677
```

- `E`: predicted energy from the model
- `σ`: prediction uncertainty
- `novelty`: minimum fingerprint distance to any DB structure
- `a(x)`: the true (positive) acquisition value = σ + λ·novelty
- Candidates marked "OUTSIDE ENERGY WINDOW" are excluded

The candidate with the **highest** `a(x)` is selected for evaluation.

### 5.5 Choosing a descriptor for novelty

The novelty distance is computed in the descriptor's feature space. Different descriptors give different notions of "structural similarity":

| Descriptor | Feature space | Best for |
|---|---|---|
| `Fingerprint` | Radial + angular distribution (Oganov-Valle style) | General-purpose, captures both radial and angular structure |
| `SimpleFingerprint` | Simplified radial distribution | Faster, coarser notion of similarity |
| `SOAP` | Smooth overlap of atomic positions | More sensitive to local atomic environments |
| `SpectralGraphDescriptor` | Graph spectrum of atomic connectivity | Topological differences |

The `Fingerprint` descriptor (default in AGOX) is a good starting point. If you find that novelty isn't discriminating well (all candidates have similar novelty values), try `SOAP` for finer discrimination.

### 5.6 Energy window without a model

If you don't have a trained GPR model yet, you can still use the energy window as a filter by providing a `target_energy` and `delta_E`. The acquisitor's `do_check` gates on `model.ready_state`, so it won't select candidates until the model is trained. Before that, candidates pass through without being prioritized.

If you want to use the energy window purely as a filter (without uncertainty or novelty), set `novelty_weight = 0` and use a dummy model that returns constant uncertainty.

---

## 6. Concept Visualization

The script `graph_novelty_lcb_concept.py` produces a 3-panel figure (`novelty_lcb_concept.png`) that graphs the complete idea:

**Panel 1 — Energy Landscape:**
- True PES (black dashed)
- GPR mean prediction μ(x) (blue)
- GPR ±σ(x) uncertainty band (orange)
- Energy window [E_target − ΔE, E_target + ΔE] (green band)
- Database structures (red dots)
- Selected candidate (green star)

**Panel 2 — Novelty:**
- Novelty(x) = min_i d_fp(x, x_i) as a function of position (purple)
- DB positions marked with vertical lines

**Panel 3 — Acquisition Function:**
- a(x) = σ(x) + λ·Novelty(x) within the energy window (green)
- Out-of-window regions shown as excluded (red markers at bottom)
- Selected candidate marked with star and annotated

Run it:
```bash
/home/miniconda3/envs/agox_v2/bin/python graph_novelty_lcb_concept.py
```

---

## 7. Verification

Run the test suite:
```bash
/home/miniconda3/envs/agox_v2/bin/python test_novelty_lcb.py
```

### Test coverage

| Test | What it verifies |
|---|---|
| **Test 1: Basic** | Acquisition values correct (σ + λ·novelty, negated for sorting), metadata attached, sort order correct (highest a(x) first) |
| **Test 2: Empty DB** | When database is empty, novelty = 0, reduces to pure uncertainty sampling |
| **Test 3: Window exclusion** | Candidates outside [E_target − ΔE, E_target + ΔE] get +inf (never selected) |
| **Test 4: is_distinct** | Correctly identifies distinct vs. duplicate structures; empty DB always returns True |
| **Test 5: fingerprint_distance** | Returns correct Euclidean distance between two fingerprint vectors |
| **Test 6: λ scaling** | λ = 0 gives tie (same σ), λ = 2 makes far candidate win |

All 6 tests pass. The test suite uses mock objects (MockModel, MockDatabase, MockDescriptor) that implement the AGOX base class interfaces, so the exercice the real code paths.

---

## 8. How It Fits Into the Existing AGOX LCB Family

| Acquisitor | Formula | Goal | Energy window? | Novelty? |
|---|---|---|---|---|
| `LowerConfidenceBoundAcquisitor` | `F = E − κσ` | Minimize energy, explore uncertainty | No | No |
| `LCBPenaltyAcquisitor` | `F = E − κσ + α·n_D` | Penalize repeated descriptor values | No | Discrete count only |
| `PowerLowerConfidenceBoundAcquisitor` | `F = E − κσ^p` | Power-law uncertainty scaling | No | No |
| **`NoveltyLCBAcquisitor`** | **`a = σ + λ·min_d_fp`** | **Maximize uncertainty + novelty within energy window** | **Yes** | **Yes (continuous)** |

The key differences:
1. **Maximization** vs. minimization — we want high uncertainty AND high novelty, not low energy
2. **Energy window** — explicit filter on predicted energy
3. **Continuous novelty** — minimum Euclidean distance in fingerprint space, not a discrete count penalty
4. **Duplicate rejection** — `is_distinct()` provides a standalone pre-storage filter

---

## 9. Tips and Pitfalls

**Pitfall 1: Forgetting to negate.** AGOX sorts ascending. If you return raw `a(x)` instead of `−a(x)`, the lowest `a(x)` (worst candidates) get selected first.

**Pitfall 2: Energy window too narrow.** If `delta_E` is too small relative to the model's prediction uncertainty, no candidates may fall in the window and the acquisitor will select nothing. Monitor the print output for "OUTSIDE ENERGY WINDOW" messages.

**Pitfall 3: Novelty weight too high.** If `novelty_weight >> 1`, the novelty term dominates and candidates are selected purely for being different, regardless of energy or uncertainty. Start low and increase gradually.

**Pitfall 4: Descriptor choice for novelty.** The fingerprint distance depends on the descriptor. If your descriptor is insensitive to the structural features you care about, novelty won't help. Test by computing pairwise distances among known distinct structures.

**Pitfall 5: Empty database on first iteration.** On the very first iteration, the database is empty and novelty = 0 for all candidates. This is expected — the acquisitor reduces to pure uncertainty sampling until structures are stored.

**Pitfall 6: Cache staleness.** The feature cache is updated via the database observer (`_on_database_store`). If you manually add candidates to the database without going through the normal AGOX dispatch, call `_rebuild_feature_cache()` to refresh.

---

## 10. Extending This Work

### Adding a force-based novelty term

The current implementation uses only energy uncertainty. You could extend it to include force uncertainty:

$$a(x) = \sigma_E(x) + \lambda_E \cdot \text{Novelty}(x) + \lambda_F \cdot \|\sigma_F(x)\|$$

This would require accessing `predict_uncertainty_forces` from the model.

### Using a different distance metric

The current novelty uses Euclidean distance in fingerprint space. Alternatives:
- Cosine distance: `1 - dot(f1, f2) / (‖f1‖·‖f2‖)`
- Mahalanobis distance (uses the covariance of the training features)
- Weighted distance (weight different fingerprint bins differently)

### Combining with other acquisitors

You could chain this with a `PowerLowerConfidenceBoundAcquisitor` by using the novelty term as an additional modifier on top of the power-law LCB, though this would require a custom class.

---

## Appendix: Benchmark Results

A benchmark comparing Novelty-LCB vs Regular LCB on a free Au₁₀ cluster with EMT calculator is documented in `novelty_lcb_benchmark_discussion.md` in this directory.

**Key findings:**
- On a free cluster with a wide energy window, both acquisitors find the same number of distinct minima — the novelty term doesn't help because the descriptor space is high-dimensional and the window is too broad to filter.
- The novelty LCB's main value is in surface-adsorbate systems with dense structural clusters, tight energy windows, and enumeration of distinct minima within a target energy range.
- The energy window constraint is the more impactful feature; the novelty term is a secondary refinement.
- A `novelty_weight` of 1.0–2.0 is a good starting range; tune based on how many duplicate/mini-variation structures you see.

### Adaptive λ

Instead of a fixed `novelty_weight`, you could make λ adaptive:
- Increase λ when the database grows (more structures to be novel relative to)
- Decrease λ when few candidates pass the energy window (need to broaden search)
- Anneal λ over iterations (explore broadly early, exploit later)
