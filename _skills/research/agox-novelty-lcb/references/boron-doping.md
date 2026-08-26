# Boron doping onto Fe/MgO (from 66_MgOFe_20B) — added to Novelty-LCB

Session-specific detail for wiring **B dopant atoms into the Fe deposition layer** of
the a_lcbnovel Novelty-LCB Fe/MgO stack, adapted from the standard-LCB example project
`/home/think/Desktop/research/_archive/_analysist/1_result/66_MgOFe_20B`. This is how a
"Boron addition onto Fe/MgO" run (e.g. `_runs/a10_mgofeb_Seed3_Iter500`) is built.

## The two helper pieces (copied from 66_MgOFe_20B/scripts)

1. **`add_adsorbate_to_hollows(atoms, symbol, height, num_atoms, seed)`** — shuffles the
   Fe atoms, groups them into **quartets of 4 Fe**, and places one B above the center of
   each quartet (z = mean Fe z + `height`). Returns `atoms + adsorbates`.
2. **`GlobalPermutationGenerator(max_number_of_swaps, rattle_strength, ...)`** — an AGOX
   `GeneratorBaseClass` that swaps two different species (Fe↔B here) in a seed candidate,
   rattles them under the confinement/steric checks. Used as a 3rd generator so the search
   can rearrange B positions. Both must be added to `scripts/` and get a module-level
   `__version__` (VERSIONS.md policy).

## CRITICAL PITFALL — the requested B count is capped at floor(Fe/4)

`add_adsorbate_to_hollows` caps `num_atoms` at the number of **complete 4-Fe quartets**:
for a 25-Fe deposition layer the max is `floor(25/4) = 6` B. Requesting 10 silently
yields 6 — **no error, no warning**. This is a real user-facing gotcha:
- The user asked for "10 B"; the system physically only has 6 hollow sites (25 Fe / 4).
- Confirm the actual count with the owner ("based on the max boron site of the system")
  rather than silently hard-coding the impossible number.
- To get MORE than floor(Fe/4) you must modify the helper (overlapping/relaxed quartets,
  a different placement rule) — it is not just a CLI value.

## How it is wired into main.py (opt-in, default OFF)

Keep the feature **off by default** so the root `main.py` and every existing run keep
their pure Fe/MgO behavior. Add a module-level count that is `0` by default:

```python
NUM_ATOMS_ADD = 0     # number of B dopant atoms in the Fe deposition layer
SYMBOL_ADD = "B"
Z_HEIGHT_ADD = 0
NUM_CANDIDATES_B = {0: [20, 0, 0], 10: [10, 5, 5], 25: [0, 10, 10]}  # 3-gen schedule
```

Per-seed, in `main()`: copy the deposition slab, and only when `NUM_ATOMS_ADD > 0` call
`add_adsorbate_to_hollows(...)` and print the resulting formula so the B count is
visible in the log:

```python
dep = slab_deposition.copy()
if NUM_ATOMS_ADD > 0:
    dep = add_adsorbate_to_hollows(dep, symbol=SYMBOL_ADD, height=Z_HEIGHT_ADD,
                                   num_atoms=NUM_ATOMS_ADD, seed=seed)
    print(f"  Doped deposition layer with {NUM_ATOMS_ADD} {SYMBOL_ADD} atoms -> {dep.get_chemical_formula()}")
env = build_environment(slab_substrate.copy(), dep)
```

In `build_stack`, when `NUM_ATOMS_ADD > 0`, append `GlobalPermutationGenerator` as a 3rd
generator and switch the collector to `NUM_CANDIDATES_B`; otherwise keep the 2-generator
`NUM_CANDIDATES`. Because the B is added to the fixed deposition slab, the composition
is uniform across all candidates, so the single global Fingerprint descriptor stays valid.

## New-run wiring (a10 example)

- `_runs/a10_mgofeb_Seed3_Iter500/` copied from a sibling, then `NUM_ATOMS_ADD = 6` in
  its `main.py` and defaults in `j_novEperAtom.sh` (KAPPA=2, NOVELTY_WEIGHT=1.5).
- Verify cheaply BEFORE the heavy run (no GPAW): build the Fe slab with the agox_v2
  python and assert the doped formula is `B6Fe25` (31 mobile atoms; 81 total with the
  fixed Mg25O25).
- Full cell = fixed Mg25O25 (50) + mobile B6Fe25 (31) = 81 atoms.

## The CLI-flag parameterization pattern (kappa / novelty_weight / any sweep knob)

When the owner asks for a sweep over a stack parameter, do **not** hard-code it per run
dir. Instead add a CLI flag to the single versioned root `main.py`, mirroring the
existing iteration pattern, so all run dirs stay syncable with one file:

- Add `--<param>` (e.g. `--kappa`, `--novelty-weight`) to the argparse in `main()`, with
  the module-level constant as default.
- Thread it through `build_stack(..., kappa=..., novelty_weight=...)` into the acquisitor
  (or calculator), not hard-coded in the stack.
- Put a `PARAM=<value>` variable at the top of each run's `j_*.sh` and pass
  `--param "${PARAM}"` on the python line — mirroring how `SEED=` / `N_ITERATIONS=` work.
- Bump `main.py` version (minor for a new flag/feature), update `VERSIONS.md`, sync the
  updated `main.py` into ALL run dirs (the AGENTS "keep run copies current" policy), and
  record old→new in `LOG.md`. Defaults unchanged means existing runs behave the same.
