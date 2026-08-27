# `--perturb-symbols` accepts multiple symbols (nested_sampler)

The nested sampler's `--perturb-symbols` flag selects which atoms the prior
perturbation moves (all others stay fixed). Since v1.2.0 it accepts **MULTIPLE
comma-separated symbols**, whitespace-trimmed — e.g. `Fe,B` or `Fe, B`.

## Implementation

In `NestedSampler.__init__` (`nested_sampling/nested_sampler.py`):

```python
perturb_list = [s.strip() for s in str(perturb_symbols).split(",") if s.strip()]
symbols = np.array(db_structures[0].get_chemical_symbols())
self.perturb_indices = np.where(np.isin(symbols, perturb_list))[0]
```

## Why this matters

- On a **B-doped Fe/MgO** dataset, `--perturb-symbols Fe,B` perturbs Fe AND B atoms
  together during prior sampling — the substrate (Mg, O) stays fixed. This is the
  motivating use case.
- An earlier single-symbol-only implementation did `np.isin(symbols, [perturb_symbols])`,
  so a literal `"Fe,B"` was treated as one element → zero matches → `ValueError`. The
  help text said "Symbol(s)" (plural) but the code never split on commas — a
  help-vs-implementation mismatch to check for.

## Test

Verify parsing (no AGOX needed):
```python
def parse(s): return [x.strip() for x in str(s).split(",") if x.strip()]
# 'Fe'->['Fe'], 'Fe,B'->['Fe','B'], 'Fe, B'->['Fe','B'], 'Mg,Fe,O'->all three
```
On a plain Fe25Mg25O25 seed, `Fe,B` matches the 25 Fe (B count 0 if the seed isn't
B-doped); on a B-doped seed it additionally matches the B atoms.
