# Nested Sampling over the combined multi-seed Fe/MgO AGOX dataset — reusable run guide

**Date:** 2026-08-20
**Agent:** Calyx
**Run dir:** `/home/think/Desktop/research/_run/8_nested_sampling/`
**Env:** `agox_v2` conda (AGOX 3.10.2 + ASE 3.25.0), Python 3.11

---

## 1. Purpose of this file

This captures everything needed to redo, extend, or adapt the multi-seed nested
sampling run. Use it as a self-contained reference the next time you ask for a related
task (different temperature, live points, iterations, perturbation, or a different
dataset/system built the same way). It complements `nested_sampling_process.md` (the
earlier single-seed, seed-3-only work on the `_analysist/.../5x5` DB) — this document
is the **multi-seed combined-dataset** variant.

---

## 2. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (base `python3` has NO AGOX/ASE)
- Skills to load first: `agox` (package API), `agox-run-code` (run-script conventions).
- For headless plots: `matplotlib.use('Agg')` before any plotting import.
- GPR uses Ray internally (auto-starts a local Ray instance); set `use_ray=False` to
  disable (it just runs hyperparameter optimization on 1 process).

---

## 3. The dataset (this run)

- Location: `dataset/seed_*/1_db/db_*.db`
- Seeds used: **3 through 15** → 13 databases
- Total structures: **1297**
- Composition: **Mg25O25Fe25** (75 atoms), uniform across EVERY seed (verified)
- Energy range: **-436.909 eV .. -386.292 eV**
- `dataset/stop_16/` and `dataset/trash/` also exist but are excluded (glob only
  matches `seed_*/1_db/db_*.db`).

### Critical pre-check (do this before any combined training)
Confirm all structures share one composition/atom count so a single Fingerprint
descriptor + single GPR are valid. If compositions differ, you must split by
composition or use a local descriptor (SparseGPR). Quick check:

```python
from collections import Counter
counts = Counter(); n_atoms = set()
for a in all_structures:
    counts[tuple(a.get_chemical_symbols())] += 1
    n_atoms.add(len(a))
print(len(counts), n_atoms)   # expect 1 distinct composition, 1 atom count
```

---

## 4. AGOX / GPR API facts (verified against the installed package)

- `Database(filename=...)` → `restore_to_memory()` → `restore_to_trajectory()` returns
  a list of ASE `Atoms`. Energies via `a.get_potential_energy()`.
- **`GPR.train(training_data)` takes a bare list of `Atoms`.** The `database=` kwarg
  passed to `GPR.__init__` is NOT used by `train` or `predict_energy` — so combining
  several DBs is clean: just concatenate trajectories and train on the combined list.
- `GPR(descriptor, kernel, prior=Repulsive())`; `predict_energy(atoms)` returns a float.
- Descriptor: `Fingerprint.from_atoms(traj[0])` is the correct constructor pattern
  (the `Fingerprint(environment=Environment(...))` form can fail to parse symbols).
- GPR signature: `GPR(descriptor, kernel, prior=None, single_atom_energies=None,
  n_optimize=None, optimizer_maxiter=100, centralize=True, filter=EnergyFilter(),
  use_ray=True, **kwargs)`.
- `train(training_data: List[Atoms])`; `predict_energy(atoms)`.

---

## 5. GPR kernel recipe (invariant, from `dataset/main.py`)

```python
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

bk = 0.01
kernel = (C(5000, (1, 1e5)) *
          (C(bk, (bk, bk)) * RBF() +
           C(1 - bk, (1 - bk, 1 - bk)) * RBF())
          + Noise(0.01, (0.01, 0.01)))
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
gpr.train(all_structures)
```

---

## 6. What "feature dim 720" means (Fingerprint descriptor)

`Fingerprint.create_features(atoms).shape[1]` returns **720** for any Fe/MgO structure.
Breakdown (verified against the descriptor internals):

- Species = 3 (Fe, Mg, O).
- **2-body / radial part = 180**: 6 distinct pair ("bond") types (3 same-species
  Fe–Fe, Mg–Mg, O–O + 3 cross Fe–Mg, Fe–O, Mg–O) × 30 radial bins
  (`Nbins1 = ceil(rc1/binwidth) = ceil(6/0.2) = 30`). 6 × 30 = 180.
- **3-body / angular part = 540**: 18 distinct triple types × 30 angular bins
  (`Nbins2 = 30`, from `binwidth2 = π/Nbins2`). 18 × 30 = 540.
- Total = 180 + 540 = **720**.

It is a fixed dimension for this system, so GPR treats each structure as a point in a
720-D feature space and measures similarity via the kernel. Default Fingerprint
params: `rc1=6, rc2=4, binwidth=0.2, Nbins=30, use_angular=True`.

---

## 7. The run script

**File:** `/home/think/Desktop/research/_run/8_nested_sampling/run_nested_sampling.py`

Flow:
1. Load combined dataset (glob `seed_*/1_db/db_*.db`, concatenate structures +
   energies).
2. Train one GPR on all 1297 structures.
3. Run `NestedSampler` from the local `nested_sampling` package:
   - `beta = 1/(K_B·T)`, log-likelihood `log L = -beta·(E - E_ref)` (E_ref = min training E)
   - prior = empirical DB distribution + optional position perturbation (`perturb`)
   - evidence accumulated in log space
4. `sampler.save(output)` writes CSVs + top-20 posterior .xsf.

### CLI options
```
--temp 300      temperature K (default 300)   -> beta = 38.68 eV^-1 at 300 K
--n-live 50     live points (default 50)
--n-iters 300   iterations (default 300)
--perturb 0.01  prior perturbation amplitude Å (default 0.01; 0 = none)
--output ./ns_output_allseeds
--rng 42        RNG seed
```

### Full run command (as executed)
```bash
cd /home/think/Desktop/research/_run/8_nested_sampling
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```

---

## 8. Verified results (this run)

- GPR trained on 1297 structures in **~134 s**; validation deltas ≈ 0.02–0.10 eV.
- Final evidence: **Z = 4.168e-04** (log Z = **-7.783**).
- Posterior: 300/300 physical; **E_mean = -432.35 eV, E_std = 6.22, E_min = -436.83 eV**
  (training min E_ref = -436.91 eV).
- Live energies converged toward E_ref as iterations progressed.

Output files (in `--output`):
| File | Contents |
|---|---|
| `evidence_history.csv` | iteration, evidence Z (one row per iteration) — correct |
| `log_evidence.csv` | iteration, log Z — **malformed, see pitfall #1** |
| `final_live_energies.csv` | live-point energies at termination |
| `posterior_structures/posterior_000..019_xsf` | top-20 weighted posterior structures |

---

## 9. Pitfalls & key learnings (read before adapting)

1. **`log_evidence.csv` from the imported package is malformed.** `NestedSampler.save()`
   in `nested_sampling/nested_sampler.py` writes it as two long transposed rows
   (all iterations on one line, all log_Z on the next) instead of one row per
   iteration. No data lost — `evidence_history.csv` is correct. To fix, change the
   `np.column_stack([[i, self.log_Z] for i in range(...)])` to `[[i, self.log_Z] for
   i in range(...)]` (drop the extra `np.column_stack`). This is a pre-existing bug in
   the package, NOT in `run_nested_sampling.py`.
2. **Verify composition uniformity before combined training** (see section 3).
3. **Prior/perturbation sensitivity.** The AGOX Fingerprint Cython descriptor is very
   sensitive to position changes; even 0.01 Å perturbation can cause GPR extrapolation
   to unphysical energies (~1e4+ eV). Keep `perturb` small (0.01 Å) or 0; the code
   filters out live points with |E| > 1e4 eV.
4. **Log-space is mandatory.** Energies ~ −400 eV and beta ~ 40 eV⁻¹ → exp(beta·E) is
   `inf`. Always accumulate evidence in log space with an E_ref shift.
5. **In-place modification must use `.copy()`.** Creating new `Atoms` objects (or
   clipping via `np.clip`) breaks the Cython fingerprint; modify a copy of an existing
   DB structure in place.
6. **GPR training takes ~2 min on 1297 structures** — factor this into runtime. A
   quick smoke test (n-live 30, n-iters 20) validates the pipeline before the full run.
7. **Run in background** for the full job (foreground timeout caps at 600 s).
8. **AGOX seed**: `AGOX.run(N_iterations)` is the method (no `run_optimization`). Not
   used in this NS script (no AGOX optimizer run), but relevant for AGOX run scripts.

---

## 10. Artifacts produced in this session

| Path | Description |
|---|---|
| `run_nested_sampling.py` | Multi-seed NS run script (loads all seeds, trains GPR, runs sampler) |
| `README.md` | Short usage/readme for the run script |
| `NESTED_SAMPLING_RUN.md` | Step-by-step log of what was done + results |
| `ns_output_allseeds/` | Full-run outputs (evidence_history.csv, final_live_energies.csv, posterior_structures/) |
| `nested_sampling/` | The imported NS package (NestedSampler, gpr_training, utils, __main__ CLI) |

### Note on the imported package's CLI (`nested_sampling/__main__.py`)
It has its own single-seed CLI (`--db-dir`, `--seed`, `--db-file`, ...) but points at a
different default DB path and only loads ONE seed. The `run_nested_sampling.py` script
is the multi-seed path.

---

## 11. Quick verification snippet (GPR timing + descriptor dim)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python -c "
import glob, numpy as np, time
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
structs=[]; en=[]
for f in sorted(glob.glob('dataset/seed_*/1_db/db_*.db')):
    db=Database(filename=f); db.restore_to_memory(); tr=db.restore_to_trajectory()
    structs+=tr; en+=[a.get_potential_energy() for a in tr]
en=np.asarray(en); print('n=',len(structs))
d=Fingerprint.from_atoms(structs[0]); print('feat dim', d.create_features(structs[0]).shape[1])
bk=0.01; k=C(5000,(1,1e5))*(C(bk,(bk,bk))*RBF()+C(1-bk,(1-bk,1-bk))*RBF())+Noise(0.01,(0.01,0.01))
g=GPR(descriptor=d,kernel=k,prior=Repulsive(),use_ray=False); t=time.time(); g.train(structs)
print('TRAIN %.1fs pred0=%.3f true=%.3f'%(time.time()-t, g.predict_energy(structs[0]), en[0]))
"
```
