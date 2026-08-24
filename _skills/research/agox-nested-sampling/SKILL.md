---
name: agox-nested-sampling
description: "Use when running nested sampling on an AGOX GPR surrogate."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [nested-sampling, agox, gpr, partition-function, materials-science, surrogate]
    related_skills: [agox, agox-run-code, simulation-analysis, gpaw]
---

# Nested Sampling on AGOX GPR Surrogates

## Overview

Runs log-space nested sampling to estimate the partition function / evidence Z from a GPR
energy surrogate trained on AGOX global-optimization databases. The user's reusable pieces
live in `/home/think/Desktop/research/_run/8_nested_sampling/`:

- `nested_sampling/` — an importable **package** (`NestedSampler`, `train_gpr`, `utils.K_B`).
- `run_nested_sampling.py` — the run script that combines ALL seed DBs, trains one GPR, and
  runs the sampler (produced by this workflow; reuse it as the template).
- `dataset/` — the AGOX seed outputs: `seed_<N>/1_db/db_<N>.db` per seed.

This is the *sampling* half of the workflow. For building the original AGOX search itself see
the `agox` / `agox-run-code` skills; for the analysis pipeline see `simulation-analysis`.

## When to Use

- Running nested sampling on a GPR surrogate built from AGOX data.
- Combining multiple AGOX seed databases into ONE GPR training set (the key technique).
- Generating partition-function / evidence / posterior-structure estimates from an energy
  landscape sampled by AGOX.

## Environment

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0).
- Set `matplotlib.use('Agg')` before any plotting import in headless runs.
- AGOX GPR init pulls in Ray (starts a local instance); harmless, just noisy stderr.

## Key technique: combine multi-seed DBs into one GPR

The AGOX `GPR.train(training_data)` takes a **bare list of `Atoms`**, and the `database=`
kwarg you pass to `GPR(...)` is **not consumed by train/predict** — it's just a Module-level
kwarg. So you can train ONE surrogate on ALL seeds by concatenating trajectories:

```python
import glob
from agox.databases import Database

db_paths = sorted(glob.glob("dataset/seed_*/1_db/db_*.db"))
all_atoms, all_energies = [], []
for p in db_paths:
    db = Database(filename=p); db.restore_to_memory()
    traj = db.restore_to_trajectory()
    all_atoms.extend(traj)
    all_energies.extend(a.get_potential_energy() for a in traj)
# gpr.train(all_atoms)
```

**Precondition — uniform composition.** A single global descriptor
(`Fingerprint.from_atoms`) supports ONE stoichiometry only. Verify before combining:
`Counter(tuple(a.get_chemical_symbols()))` must collapse to a single distinct composition,
and `len(a)` constant. The Fe/MgO dataset is uniformly Mg25O25Fe25 / 75 atoms across all 13
seeds (seeds 3–15, 1297 structures). Check per-seed counts too — e.g. one seed may have 97
vs 100 structures.

Descriptor + kernel recipe (matches `dataset/main.py`):

```python
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

descriptor = Fingerprint.from_atoms(all_atoms[0])
bk = 0.01
kernel = (C(5000, (1, 1e5))
          * (C(bk, (bk, bk)) * RBF() + C(1 - bk, (1 - bk, 1 - bk)) * RBF())
          + Noise(0.01, (0.01, 0.01)))
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
```

Scale (verified): 1297 structures → 720-dim fingerprint, `gpr.train()` ≈ 134 s (Ray,
4 CPUs), validation deltas ≈ 0.02–0.10 eV.

## Run recipe

```bash
cd /home/think/Desktop/research/_run/8_nested_sampling
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```

`run_nested_sampling.py` already: (1) globs all `seed_*/1_db/db_*.db`, (2) trains the
combined GPR, (3) builds `NestedSampler(gpr, all_atoms, all_energies, beta=1/(K_B*T), ...)`,
(4) `initialize()` → `run(n_iterations)` → `save(output)`.

Outputs: `evidence_history.csv`, `log_evidence.csv`, `final_live_energies.csv`,
`posterior_structures/posterior_*.xsf` (top-20 weighted).

## Physics notes (verified on Fe/MgO, T=300 K, beta≈38.68 eV^-1)

- `log L = -beta * (E - E_ref)`, `E_ref` = min training energy (shifts so L is O(1) at best
  structures). Live energies start near a random prior sample (~-397 eV) and converge toward
  `E_ref` (≈ -436.9 eV) as iterations progress — good convergence sanity check is
  `E_live_max → E_ref`.
- Evidence starts astronomically small (`10^-200`-ish) and grows toward Z≈1e-4 over ~300
  iters / 50 live points. `log_evidence.csv` log_Z is the robust number; the exponentiated
  Z underflows early by design.
- GPR sometimes predicts unphysical energies (|E|>1e4); the sampler filters/replaces these.

## Common Pitfalls

1. **`GPR` `database=` kwarg is a red herring** — combine DBs by concatenating
   `restore_to_trajectory()` lists, don't try to point the model at multiple DB files.
2. **Composition mismatch breaks the descriptor** — a combined GPR only works if every
   structure has the same stoichiometry and atom count. Check `Counter` first.
3. **`nested_sampler.save()` writes `log_evidence.csv` malformed** (pre-existing bug): it
   dumps iterations and log_Z as two long transposed rows instead of one row per iteration
   (wrong `np.column_stack`). `evidence_history.csv` is correct — no data lost. If a
   downstream consumer needs per-row log_Z, regenerate from `evidence_history.csv` or patch
   the save (swap to per-row layout).
4. **Use absolute env python** — base `python3` has no AGOX/ASE.
5. **Ray noise on stderr** is expected; don't mistake it for a crash.

## Verification Checklist

- [ ] `Counter` over `get_chemical_symbols()` confirms one uniform composition across all seeds
- [ ] Run via `/home/think/miniconda3/envs/agox_v2/bin/python`
- [ ] Live-energy range converges toward `E_ref` over iterations
- [ ] `evidence_history.csv` + `posterior_structures/*.xsf` produced
- [ ] If parsing `log_evidence.csv`, re-derive from `evidence_history.csv` (save bug)
