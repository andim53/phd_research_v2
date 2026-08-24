# Auto global-minimum window mode + isolated validation (worked example)

Session detail for the `agox-novelty-lcb` skill. This captures the new
`energy_above_min` + `per_atom` window mode and the standalone mock test that
validates it without the AGOX Ray stack.

Reference implementation: `/home/think/Desktop/research/_run/10_lcbnovel/`
- `novelty_lcb/acquisitor.py` — the acquisitor with `energy_above_min` / `per_atom`.
- `test_window_logic.py` — the isolated mock test (16/16 PASS).
- `main_benchmark.py` + `j_benchmark.sh` — the regular-vs-Novelty EMT benchmark.

## The auto global-minimum window

Constructor params added (backward compatible):
```python
NoveltyLCBAcquisitor(model, descriptor, database,
                     target_energy=None,      # centered mode (legacy)
                     delta_E=0.5, novelty_weight=1.0, kappa=1.0,
                     energy_above_min=None,   # auto mode when not None
                     per_atom=False,          # eV/atom when True
                     **kwargs)
```

Window logic inside `calculate_acquisition_function`:
- `energy_above_min` set + `per_atom` False: accept iff `E <= E_min + X`
  (total eV).
- `energy_above_min` set + `per_atom` True: accept iff `(E/N) <= (E_min/N) + X`
  (X in eV/atom).
- `E_min` = live lowest finite total DFT energy in the DB
  (`_global_min_energy()`: min of `get_potential_energy()` over candidates).
- Empty DB -> no cap (accept everything until the first minimum is stored).
- No lower bound -> a candidate below the current `E_min` is still accepted.

The two new helper methods on the acquisitor:
- `_global_min_energy()` -> lowest finite candidate energy or `None`.
- `_n_atoms()` -> `len(cands[0])` from the DB (assumes uniform atom count);
  falls back to 1.

## Equivalence: per_atom vs total for fixed N

For a fixed atom count N, per-atom mode with window X (eV/atom) gives IDENTICAL
accept/reject to total mode with window `X*N`:

    (E/N) <= (E_min/N) + X   <=>   E <= E_min + N*X

So enabling `per_atom` by default changes only the unit of the knob, not the
behaviour. Test this with the equivalence check below.

## Isolated mock test (no Ray, no AGOX stack)

Build the acquisitor via `object.__new__` to bypass `__init__`'s strict
`DatabaseBaseClass` type check and observer attach:

```python
class MockModel:
    def predict_energy_and_uncertainty(self, cand): return cand._E, 0.1
class MockDescriptor:
    def get_features(self, cand): return np.array([cand._f])
class MockDB:
    def __init__(self, energies, n_atoms=75):
        self._e, self._n_atoms = energies, n_atoms
    def get_all_candidates(self):
        class C:
            def __len__(self): return self._n
        out = []
        for e in self._e:
            c = C(); c._n = self._n_atoms
            c.get_potential_energy = (lambda e=e: e)
            out.append(c)
        return out
class MockCand:
    def __init__(self, E, f=1.0): self._E, self._f, self.meta = E, f, {}
    def add_meta_information(self, k, v): self.meta[k] = v

def make_acq(energy_above_min=None, target=None, delta_E=1.0,
             db_energies=[], per_atom=False, n_atoms=75):
    acq = object.__new__(NoveltyLCBAcquisitor)
    acq.model = MockModel(); acq.descriptor = MockDescriptor()
    acq.database = MockDB(db_energies, n_atoms=n_atoms)
    acq.target_energy = target; acq.delta_E = delta_E
    acq.energy_above_min = energy_above_min; acq.per_atom = per_atom
    acq.novelty_weight = 1.0; acq.kappa = 2.0; acq._db_features = None
    return acq
```

Key cases that must pass:
- auto mode caps at `E_min + X` (or `E_min/N + X` per atom); above -> `np.isinf`.
- below-global-min still accepted (no lower bound).
- empty DB -> everything accepted (no cap).
- live `E_min` tracking: a lower min found during the run tightens/keeps the cap.
- centered legacy mode still works (backward compat).
- no-constraint mode (`target=None`, `energy_above_min=None`) accepts everything.
- equivalence: per_atom `X` == total `X*N` for fixed N.

## Why the isolated test exists

On a low-RAM node the full AGOX stack (ParallelCollector / ParallelRelaxPostprocess
Ray pools) fails with Ray `ActorUnavailableError` — environmental. The mock test
exercises the actual `calculate_acquisition_function` window logic with zero Ray, so
code changes are validated even when the full run can't proceed.
