# TUTORIAL — Reproduce run a10 (Novelty-LCB Fe/MgO+B, seed 3, 500 iterations)

Step-by-step guide to reproduce **this specific run** (`a10_mgofeb_Seed3_Iter500`) from
scratch. It is the project's first Boron-doping run, based on the 66_MgOFe_20B example.
Everything needed is inside this directory.

## Prerequisites

- HPC cluster with PJM batch (`pjsub`) and a 64-core node running `gpaw_env`.
  This run uses GPAW LCAO/dzp DFT — do **not** run the full stack locally.
- For local compile/structure checks only: conda env `agox_v2` at
  `/home/think/miniconda3/envs/agox_v2/bin/python`.
- Reference example for the B-doping approach:
  `/home/think/Desktop/research/_archive/2_analysist/1_result/66_MgOFe_20B`.

## What to expect

- Physics: **B6Fe25** deposition on a fixed MgO(001) substrate (Mg25O25 + B6Fe25 =
  81 atoms). B atoms are placed in Fe-hollows via `add_adsorbate_to_hollows`.
- Acquisition: Novelty-LCB `a(x) = σ(x) + 1.5·Novelty(x)`, auto global-minimum window
  at 1.0 eV/atom (`per_atom=True`).
- Generators: Randomize + Rattle + **GlobalPermutationGenerator** (Fe↔B swaps), with the
  B-enabled candidate schedule `{0:[20,0,0], 10:[10,5,5], 25:[0,10,10]}`.
- Budget: **500 AGOX iterations**, seed 3, kappa 2.0, novelty_weight 1.5 (defaults).
- B count: **6** = max hollow sites for 25 Fe (`floor(25/4)`).

## Step 1 — Verify the code compiles (local, no GPAW)

```bash
cd /home/think/Desktop/research/_run/a_lcbnovel/1_runs/a10_mgofeb_Seed3_Iter500
/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile main.py novelty_lcb/*.py scripts/*.py
```

Expected: no output, exit 0. (IDE may flag AGOX imports under base `python3` — ignore;
the env python is authoritative.)

## Step 2 — Sanity-check the B-doped structure (local, no DFT)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python -c \
"from scripts.build_fe_stack import build_fe_stack; from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows; from ase.build import surface, bulk; slab=build_fe_stack(surface(bulk('Fe','bcc',a=2.870190,cubic=True),(0,0,1),layers=1,vacuum=20),num_layers=1,vacuum=20).repeat((5,5,1)); d=add_adsorbate_to_hollows(slab,symbol='B',height=0,num_atoms=6,seed=3); print(d.get_chemical_formula(), len(d))"
```

Expected: `B6Fe25`, 31 atoms (the mobile layer). The full cell is 81 atoms with the
fixed Mg25O25 substrate.

## Step 3 — Launch on HPC

```bash
pjsub j_novEperAtom.sh
```

The script (64-core, `gpaw_env`) runs `python ./main.py --seed 3 --n-iterations 500
--kappa 2 --novelty-weight 1.5 --out-root ./output`. To change the run, edit `SEED=` /
`N_ITERATIONS=` / `KAPPA=` / `NOVELTY_WEIGHT=` in the script, or `NUM_ATOMS_ADD` in
`main.py` — **never** use `pjsub -x`.

## Step 4 — Verify it completed

After the job finishes, check:

```bash
ls -l output/seed_3/1_db/db_3.db      # DB populated (candidates added)
ls -l output_seed_3.txt               # GPAW log, no serialization crash
grep "Doped deposition layer" output_seed_3.txt   # should show B6Fe25
```

If it crashed at the first stack build with `cannot pickle 'sqlite3.Connection'`, the
acquisition calculator is dragging a non-picklable object into the Ray pool. The
`novelty_lcb/` package here is the fixed version (module-level free functions +
`functools.partial`), so this should not recur; validate with
`smoke_test_serialization.py` in the project root if in doubt.

## Pitfalls

1. **Do not run the full GPAW stack locally** — 64-core SubprocessGPAW needs a cluster
   node. Local `py_compile` and the structure check above are enough to validate wiring.
2. **B count is capped by the system** — `add_adsorbate_to_hollows` places B in 4-Fe
   hollows, so the max is `floor(25/4) = 6`. Requesting more silently yields 6.
3. **Edit the `.sh`, don't pass `-x`** — seed/iterations/kappa/weight are set by editing
   the variables at the top of `j_novEperAtom.sh`.
4. **Outputs are regenerable** — `output/` and `*.db` are gitignored; only code + docs
   are tracked.
5. **Composition is uniform by construction** — B is added to the initial deposition
   slab, so all candidates share B6Fe25 and the single global Fingerprint stays valid.
