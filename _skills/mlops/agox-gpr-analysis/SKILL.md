---
name: agox-gpr-analysis
description: Use when loading AGOX .db files and training GPR models.
---

# AGOX GPR Analysis

Working with AGOX databases and GPR surrogate models involves several
non-obvious pitfalls. This skill captures working patterns and failure
modes from hands-on use.

## Trigger

- Loading an AGOX `.db` file for analysis or surrogate modeling
- Training a GPR model with `Fingerprint` descriptor on AGOX structures
- Performing nested sampling or Boltzmann weighting using GPR energies
- Debugging GPR predictions returning unphysical energies (10^20+ eV)

## 1. Loading an AGOX Database

```python
from agox.databases import Database
db = Database(filename="path/to/db_N.db")
db.restore_to_memory()
traj = db.restore_to_trajectory()  # list of ASE Atoms
energies = np.array([a.get_potential_energy() for a in traj])
```

## 2. Fingerprint Descriptor — Critical

**PITFALL: `Fingerprint(environment=env)` with space-joined symbols FAILS.**

AGOX `Environment` expects a valid formula like `'Fe25Mg25O25'`. Using
`' '.join(symbols)` produces `'O Mg O Mg ...'` which raises `ValueError`
in `symbols2numbers()`.

**Use `Fingerprint.from_atoms()` instead** — the approach used by
`codes/98_configurational.py`, `codes/62_pca.py`, `codes/71_conf_space.py`:

```python
from agox.models.descriptors.fingerprint import Fingerprint
fp = Fingerprint.from_atoms(traj[0])
```

For an `Environment` with confinement (prior sampling), use
`get_chemical_formula()`:

```python
from agox.environments import Environment
env = Environment(
    template=traj[0],
    symbols=traj[0].get_chemical_formula(),  # NOT ' '.join(symbols)
    confinement_cell=..., confinement_corner=..., box_constraint_pbc=[True,True,False],
)
```

## 3. GPR Training

```python
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

kernel = C(5000,(1,1e5)) * (C(0.01,(0.01,0.01))*RBF() + C(0.99,(0.99,0.99))*RBF()) + Noise(0.01,(0.01,0.01))
gpr = GPR(descriptor=fp, kernel=kernel, database=db, prior=Repulsive())
gpr.train(traj)
```

Validation: GPR predictions on training structures should be within ~0.05 eV of DFT.

## 4. GPR Prediction Pitfalls

### 4a. Never create new Atoms via `Atoms(symbols=..., positions=...)`

**PITFALL:** The Fingerprint Cython module needs internal ASE state preserved
by `.copy()` but lost in new Atoms construction. New Atoms → GPR predicts
~10^21 eV (garbage extrapolation).

```python
# WRONG
new_struct = Atoms(symbols=base.symbols, positions=new_pos, cell=base.cell, pbc=base.pbc)
E = gpr.predict_energy(new_struct)  # UNPHYSICAL

# CORRECT — in-place modification on a copy
base_copy = base.copy()
base_copy.positions += perturbation
E = gpr.predict_energy(base_copy)  # PHYSICAL
```

### 4b. Perturbation amplitude must be ≤ 0.01A

**PITFALL:** 0.2A rattle gives fingerprint L2 distance ~66 vs typical
inter-structure distance 1–6. GPR extrapolates off-manifold to ~10^21 eV.
For nested sampling, `perturb=0` (sample DB structures directly) is safest.

### 4c. Confinement clipping must only affect out-of-bounds atoms

**PITFALL:** `np.clip(positions[:,2], corner, corner+cc)` moves ALL atoms,
including those already inside. Bottom-layer atoms at z=10 get pushed to
z=12.51 (2.5A jump).

```python
# CORRECT — only clip atoms actually outside
for dim in range(3):
    below = positions[:,dim] < corner[dim]
    above = positions[:,dim] > corner[dim] + cc[dim,dim]
    positions[below,dim] = corner[dim]
    positions[above,dim] = corner[dim] + cc[dim,dim]
```

## 5. Nested Sampling

Work in log-space to avoid overflow (T=300K, E~-400eV → exp(15480)=inf):

```python
E_ref = db_energies.min()
log_L = -beta * (E - E_ref)
log_Z = np.logaddexp(log_Z, log_L_min + np.log(delta_X))
```

## References

- `references/fingerprint-pitfalls.md`
- `references/gpr-prediction-failures.md`
