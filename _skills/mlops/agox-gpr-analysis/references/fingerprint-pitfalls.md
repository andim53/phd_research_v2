# Fingerprint Descriptor Pitfalls

## Problem 1: Space-joined symbols fail

The AGOX `Environment.__init__` calls `symbols2numbers(symbols)` which uses
ASE's `Formula` parser. Space-joined symbols like `'O Mg O Mg ...'` are not
valid ASE formulas and raise `ValueError`.

**Working approach:** `Fingerprint.from_atoms(atoms)` — internally uses
`Environment(template=atoms, symbols="", use_box_constraint=False)`.

**Source:** `_analysist/codes/98_configurational.py` line 111,
`_analysist/codes/62_pca.py` line 34, `_analysist/codes/71_conf_space.py` line 473.

## Problem 2: Creating new Atoms breaks Cython fingerprint

The Fingerprint Cython module (`angular_fingerprintFeature_cy.pyx`) expects
internal ASE state that is preserved by `Atoms.copy()` but lost when
constructing new Atoms from component arrays.

**Symptom:** `gpr.predict_energy(new_atoms)` returns ~10^21 eV.
**Fix:** Use `base.copy()` then modify `positions` in-place.

**Investigation:** Tested with `Atoms(symbols=..., positions=...)` vs
`base.copy(); base.positions += noise` — only the latter produces physical
GPR predictions.

## Problem 3: Perturbation amplitude sensitivity

Fingerprint feature space is 720-dimensional. Small position changes produce
large feature-space distances because the angular fingerprint is sensitive to
atom pair distances and angles.

| Rattle amplitude | Feature L2 distance from base | GPR prediction |
|------------------|-------------------------------|----------------|
| 0.001A           | 0.002                         | Physical (~-392 eV) |
| 0.010A           | 0.026                         | Physical |
| 0.200A           | 66                            | ~10^21 eV (garbage) |

Typical inter-structure L2 distances in training set: 1–6.

**Practical limit:** perturb ≤ 0.01A for reliable GPR predictions.
For nested sampling, `perturb=0` (sample DB structures directly without
perturbation) is the safest approach.

## Problem 4: Confinement clipping corrupts structures

`np.clip(positions[:, dim], corner[dim], corner[dim] + cc[dim, dim])`
moves ALL atoms, not just those outside the confinement box. For the
Fe/MgO 5x5 system, bottom-layer atoms at z=10 get clipped to z=12.51
(the confinement corner), a 2.5A jump.

**Fix:** Only clip atoms where `positions[:, dim] < corner[dim]` or
`positions[:, dim] > corner[dim] + cc[dim, dim]`.
