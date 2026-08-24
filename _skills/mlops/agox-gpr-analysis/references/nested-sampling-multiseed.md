# Multi-seed nested sampling — combined-dataset recipe

Verbatim working recipe from the `_run/8_nested_sampling/` session (Fe/MgO, seeds
3–15, 1297 structures, all Mg25O25Fe25 / 75 atoms). Extends the SKILL.md nested
sampling section with the multi-seed combine step and two session-specific pitfalls.

## 0. Verify composition uniformity before combining

A single `Fingerprint` descriptor + single `GPR` is only valid if every structure
shares one composition/atom count. Check first:

```python
from collections import Counter
counts = Counter(); n_atoms = set()
for a in all_structures:
    counts[tuple(a.get_chemical_symbols())] += 1
    n_atoms.add(len(a))
print(len(counts), n_atoms)   # expect 1 distinct composition, 1 atom count
```

If compositions differ you MUST split by composition or switch to a local
descriptor (`SparseGPR`).

## 1. Combine multiple seed DBs

See module `nested_sampling/` package for the canonical `NestedSampler`; the run
script at `.../8_nested_sampling/run_nested_sampling.py` does the combine:

```python
import glob
from agox.databases import Database
db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
structures, energies = [], []
for p in db_paths:
    db = Database(filename=p); db.restore_to_memory()
    traj = db.restore_to_trajectory()
    structures.extend(traj)
    energies.extend(a.get_potential_energy() for a in traj)
energies = np.asarray(energies, dtype=float)
```

**KEY FACT: the `database=` kwarg passed to `GPR.__init__` is NOT used by
`train()` or `predict_energy()`.** `GPR.train(training_data)` takes a bare
`List[Atoms]`. So combining DBs is clean: just concatenate trajectories and call
`gpr.train(structures)` on the combined list. One descriptor built via
`Fingerprint.from_atoms(structures[0])`, one kernel, one `prior=Repulsive()`.

## 2. Workflow with the local `nested_sampling` package

The `_run/8_nested_sampling/nested_sampling/` package exposes
`NestedSampler`, `train_gpr`, and `K_B`. Usage (import via sys.path shim):

```python
from nested_sampling.nested_sampler import NestedSampler
sampler = NestedSampler(gpr=gpr, db_structures=structs, db_energies=energies,
                        n_live=50, beta=1.0/(K_B*T), temperature=300.0,
                        perturb=0.01, rng=np.random.default_rng(42))
sampler.initialize(); sampler.run(n_iterations=300); sampler.save(out_dir)
```

Param semantics (for writing docs/notes):
- `n_live` — number of live points; classic Skilling NS. Each iteration removes the
  worst-likelihood live point and replaces it with a better one; prior volume shrinks
  as `exp(-i/n_live)`. Higher = finer evidence resolution, more cost.
- `temperature`/`beta` — `beta = 1/(k_B·T)`; enters likelihood
  `L = exp(-beta*(E - E_ref))`. Sets how strongly low-E structures are favored.
  `T=300K -> beta=38.68 eV^-1`; each eV above best costs factor ~10^-17.
- `Z` = model evidence / partition function `∫ L·π dx` = posterior normalizer;
  gives free energy `F = -k_B T ln Z`. Track `log Z` because likelihoods span
  hundreds of orders of magnitude (this run: Z went ~10^-242 -> 4.2e-4) — linear
  arithmetic over/underflows float64.

## 3. PITFALL: `log_evidence.csv` from the package's `save()` is malformed

`NestedSampler.save()` writes `log_evidence.csv` with
`np.column_stack([[i, self.log_Z] for i in ...])` — the extra `np.column_stack`
dumps all iterations on one row and all log_Z on the next (transposed), instead of
one row per iteration. No data is lost (`evidence_history.csv` is correct), but the
file is unusable as-is. Fix: drop the outer `np.column_stack`, write
`[[i, self.log_Z] for i in ...]`.

## 4. Fe-only perturbation (deposition layer) instead of all atoms

Default prior perturbs ALL atoms (substrate + deposition). To move only the
deposition layer (e.g. Fe, keeping MgO substrate fixed), identify indices once in
`__init__` and reuse per draw:

```python
symbols = np.array(db_structures[0].get_chemical_symbols())
self.perturb_indices = np.where(np.isin(symbols, [perturb_symbols]))[0]  # ["Fe"]
...
def sample_from_prior(self):
    base = self.db_structures[self.rng.integers(0, len(self.db_structures))].copy()
    if self.perturb > 0:
        noise = self.rng.normal(0, self.perturb, (len(self.perturb_indices), 3))
        base.positions[self.perturb_indices] += noise
    return base
```

Still respect SKILL.md 4b: keep amplitude ≤ 0.01 Å.

## 5. Runtime benchmark (this machine)

GPR training on 1297 combined structures ~134 s (Ray single-node, 4 CPU).
Prediction deltas ~0.02–0.10 eV. Full NS run (50 live, 300 iters) completes in a
few minutes on top of training. Smoke-test with n-live 30 / n-iters 20 first.