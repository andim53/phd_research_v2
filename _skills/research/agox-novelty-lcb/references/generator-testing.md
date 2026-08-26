# Testing each main.py generator standalone (test_generators.py, 2026-08-26)

When the owner wants to "test each generator" of the Novelty-LCB `main.py` without
running the full search (no GPAW, no collector/acquisitor), write a standalone script
at the project root that reuses main.py's own slab/environment/generator wiring and
writes candidate structures to a scratch dir. Worked example: `test_generators.py` in
`/home/think/Desktop/research/_run/a_lcbnovel/`.

## Structure (reuse main.py, don't re-implement)

Import main.py's exact builders/config so the test exercises the SAME environment and
generator wiring as the real search:

```python
from main import (build_slabs, build_environment, NUM_ATOMS_ADD, SYMBOL_ADD,
                  Z_HEIGHT_ADD, NUM_CANDIDATES_B, VACUUM, A_MGO, A_FE, DIST_Z_FE2O,
                  SUPERCELL, MGO_LAYER_NUMBER, FE_LAYER_NUMBER,
                  CONFINEMENT_CELL_HEIGHT_MULTIPLYER, SAMPLE_SIZE, RATTLE_AMPLITUDE,
                  HETERO_RATTLE_AMPLITUDE)
from agox.generators import RattleGenerator
from agox.samplers import FixedSampler
from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows
from scripts.global_permutation_generator import GlobalPermutationGenerator
```

## Build the 3 generators exactly as build_stack does

Same kwargs as `build_stack` (confinement from `environment.get_confinement()`,
`n_rattle`, amplitudes). Order matches main.py: `[HeteroStructRandomize,
RattleGenerator, GlobalPermutationGenerator]`.

## Enabling B doping so ALL 3 generators are exercised

`GlobalPermutationGenerator` only does meaningful work when there is more than one
active species (it swaps Fe<->B). The base Fe25 layer is single-species, so to test the
permutation generator you MUST enable B doping (`add_adsorbate_to_hollows` ->
B6Fe25). Otherwise the permutation generator is inert.

## Invocation + FixedSampler chain (63_w1b / 66_MgOFe_20B pattern)

- HeteroStructRandomize is built from scratch: `generators[0](sampler=None,
  environment=env)[0]`.
- Rattle and Permutation are chained from the hetero candidate:
  `sampler = FixedSampler(hetero_candidate)` then `generators[i](sampler, env)[0]`.
- Write each to a scratch dir as `<gen>_candidate_<i>.xsf` (e.g. `hetero_candidate_0.xsf`).

## Pitfalls

1. **The permutation generator is SLOW** (an attempts-based steric-check loop). A
   10-sample x 3-generator run took a few minutes; the candidate files are written
   progressively, so a foreground 180s timeout may fire mid-run — run it in the
   background (`notify_on_complete`) and poll `_tmp/` for progress rather than
   assuming it hung.
2. **Use the agox_v2 env python** — base `python3` has no ASE/AGOX (Pyright/LSP will
   flag the imports; ignore, the env python is authoritative).
3. **Scratch outputs must be gitignored** — add the output dir (e.g. `_tmp/`) and any
   `generated_structures/` to the project `.gitignore`; `.xsf` is usually already
   ignored by the repo's `*.xsf` rule. Only the test script itself is tracked.
4. Give the script module-level `__version__` and register it in `VERSIONS.md` (the
   project's source-versioning policy), like any in-scope root file.
5. Sanity-check the .xsf atom count after writing (should equal the full cell atom
   count, e.g. 81 for B6Fe25 + Mg25O25).
