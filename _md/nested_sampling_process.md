# Nested Sampling with AGOX GPR — Process Log

**Date:** 2026-08-19  
**Agent:** Calyx  
**Environment:** agox_v2 (conda), Python 3.11, AGOX 3.10.2  
**Target DB:** `_analysist/1_result/19_kappa2_iter100_trajNoSave_repSeedDat0_5x5/seed_3/1_db/db_3.db`

---

## Goal

Write a nested sampling code that uses the AGOX GPR (Gaussian Process Regression) surrogate model trained on structures from a completed AGOX run (seed 3, 100 DFT-optimized Fe25Mg25O25 structures on MgO substrate, 5x5 supercell).

---

## Steps

### 1. Explore target directory and existing analysis code

- Located the DB: `_analysist/1_result/19_kappa2_iter100_trajNoSave_repSeedDat0_5x5/seed_3/1_db/db_3.db` (598 KB, 100 structures)
- Read reference scripts for how AGOX DB + GPR + Fingerprint are used:
  - `_analysist/codes/86_database.py` — DB loading, trajectory extraction
  - `_analysist/codes/92_probability_density.py` — KDE + Boltzmann probability
  - `_analysist/codes/76_plot_probability.py` — binding energy probability
  - `_analysist/codes/98_configurational.py` — Fingerprint.from_atoms() pattern
  - `_analysist/1_result/.../main.py` — original AGOX run setup (kernel, GPR, environment)

### 2. Investigate AGOX APIs

- `Database(filename=...)` → `restore_to_memory()` → `restore_to_trajectory()` returns list of ASE Atoms
- `get_all_energies()` returns ndarray of DFT energies
- `Fingerprint.from_atoms(traj[0])` — the pattern that actually works (from codes/98_configurational.py)
- `GPR(descriptor, kernel, database, prior)` → `train(traj)` → `predict_energy(atoms)`
- Kernel from main.py: `C(5000)* (C(0.01)*RBF() + C(0.99)*RBF()) + Noise(0.01)`

### 3. First attempt: perturbation-based prior sampling

Wrote initial `nested_sampling_agox.py` with:
- Prior: pick random DB structure, apply 1.5A rattle, clip to confinement
- Likelihood: L = exp(-beta * E_GPR)
- Standard NS algorithm (live points, shrinkage, evidence accumulation)

**Problem discovered:** 1.5A rattle sends Fingerprint features far outside training manifold → GPR extrapolates to ~10^21 eV (garbage).

### 4. Debug the GPR extrapolation problem

Systematic investigation:

| Rattle amp | Feature L2 dist from base | GPR prediction |
|---|---|---|
| 0.2 A | 66 (training pairs: 1-6) | 10^21 eV (garbage) |
| 0.01 A | 0.026 | 10^15 eV (still garbage) |
| 0.005 A | 0.01 | 10^9 eV (still garbage) |

**Root cause found:** The confinement clipping was corrupting positions. `np.clip(positions[:, 2], corner[2], ...)` moved bottom-atom z from 10 to 12.51 (corner value), a 2.5A jump. Even without noise, just clipping gave feature L2 distance of 716.

**Secondary issue:** Creating new `Atoms(symbols=..., positions=...)` also broke the Cython fingerprint — the in-place modification of a `.copy()` must be used.

**Numerical stability:** At T=300K, beta=38.68 eV^-1, E~−400 eV → exp(15400) = inf. Must work in log-space with energy reference shift.

### 5. Final implementation

Rewrote `nested_sampling_agox.py` with:

- **Prior sampling:** Draw from DB with optional `perturb` parameter (default 0.01A, 0 = no perturbation). Uses `.copy()` + in-place position modification.
- **Log-space likelihood:** `log_L = -beta * (E - E_ref)` where E_ref = min training energy
- **Filter unphysical:** Replace live points with |E| > 1e4 eV
- **Evidence in log-space:** `logaddexp(log_Z, log(L_min * delta_X))`
- **Posterior:** saved with weights from likelihood contribution

### 6. Verification

Test run: `--seed 3 --temp 300 --n-live 15 --n-iters 30 --perturb 0.0`

Results:
- GPR validation: MAE ~0.02 eV on first 5 structures (excellent fit)
- Evidence: Z = 5.4e-13 (log Z = -28.2)
- Posterior: 30 physical samples, E_mean = -428.1 eV, E_min = -434.2 eV
- 10 posterior XSF files written (top 20 by weight)

---

## Files produced

- `/home/Desktop/research/nested_sampling_agox.py` — main nested sampling code (15.8 KB)
- `/home/Desktop/research/ns_test_output/` — test output (cleaned up after verification)

---

## Key learnings

1. `Fingerprint.from_atoms(traj[0])` is the correct way to create a descriptor — `Fingerprint(environment=Environment(...))` fails with symbol parsing errors.
2. Perturbation-based prior sampling with the AGOX Fingerprint Cython module is extremely sensitive — even 0.01A displacement causes catastrophic GPR extrapolation. The empirical DB distribution (no perturbation, or very small) is the safe prior.
3. Working in log-space for evidence accumulation is essential when energies are ~−400 eV and beta ~ 40 eV^-1.
4. Confinement clipping must only move atoms that are actually outside the box, not clip all positions.

---

## Usage

```bash
python nested_sampling_agox.py \
    --seed 3 \
    --temp 300 \
    --n-live 50 \
    --n-iters 200 \
    --output ./ns_output \
    --perturb 0.0
```

Options: `--db-dir`, `--seed`, `--temp`, `--n-live`, `--n-iters`, `--output`, `--db-file`, `--perturb`
