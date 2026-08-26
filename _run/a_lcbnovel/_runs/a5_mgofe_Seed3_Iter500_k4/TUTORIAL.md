# TUTORIAL — Reproduce run a5 (Novelty-LCB Fe/MgO, seed 3, 500 iter, kappa=4)

Step-by-step guide to reproduce **this specific run** (`a5_mgofe_Seed3_Iter500_k4`)
from scratch. It is one of a kappa-sweep set (a4=3, a5=4, a6=5) built from the standard
a2 run (kappa=2.0). Everything needed is inside this directory.

## Prerequisites

- HPC cluster with PJM batch (`pjsub`) and a 64-core node running `gpaw_env`.
  This run uses GPAW LCAO/dzp DFT — do **not** run the full stack locally.
- For local compile/structure checks only: conda env `agox_v2` at
  `/home/think/miniconda3/envs/agox_v2/bin/python`.

## What to expect

- Physics: 25 Fe atoms deposited on a fixed MgO(001) substrate (75 atoms total).
- Acquisition: Novelty-LCB `a(x) = σ(x) + 1.5·Novelty(x)`.
- Energy window: auto global-minimum, 1.0 eV/atom above the live DB minimum
  (`per_atom=True`), so no prior regular-LCB calibration run is needed.
- Budget: **500 AGOX iterations**, seed 3 — same as the base a2 run.
- Treatment: **kappa = 4.0** (vs kappa 2.0 in a2, 3.0 in a4, 5.0 in a6). Kappa sets the
  LCB surrogate-relaxation surface `E − kappa·sigma`.

## Step 1 — Verify the code compiles (local, no GPAW)

```bash
cd /home/think/Desktop/research/_run/a_lcbnovel/_runs/a5_mgofe_Seed3_Iter500_k4
/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile main.py novelty_lcb/*.py scripts/*.py
```

Expected: no output, exit 0. (IDE may flag AGOX imports under base `python3` — ignore;
the env python is authoritative.)

## Step 2 — Sanity-check the structure build (local, no DFT)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python -c \
  "from main import build_slabs; s,d,st=build_slabs(); print(s.get_chemical_formula(), len(s), st)"
```

Expected: substrate `Mg25O25`, 50 atoms, strain ~3.77%. The Fe deposition layer adds 25
Fe for the full 75-atom cell.

## Step 3 — Launch on HPC

```bash
pjsub j_novEperAtom.sh
```

The script (64-core, `gpaw_env`) runs `python ./main.py --seed 3 --n-iterations 500
--kappa 4 --out-root ./output`. To change the run, edit `SEED=` / `N_ITERATIONS=` /
`KAPPA=` at the top of the script — **never** use `pjsub -x`.

## Step 4 — Verify it completed

After the job finishes, check:

```bash
ls -l output/seed_3/1_db/db_3.db      # DB populated (candidates added)
ls -l output_seed_3.txt               # GPAW log, no serialization crash
```

If it crashed at the first stack build with `cannot pickle 'sqlite3.Connection'`, the
acquisition calculator is dragging a non-picklable object into the Ray pool. The
`novelty_lcb/` package here is the fixed version (module-level free functions +
`functools.partial`), so this should not recur; validate with
`smoke_test_serialization.py` in the project root if in doubt.

## Pitfalls

1. **Do not run the full GPAW stack locally** — 64-core SubprocessGPAW needs a cluster
   node. Local `py_compile` and `build_slabs()` are enough to validate wiring.
2. **Edit the `.sh`, don't pass `-x`** — seed/iterations/kappa are set by editing the
   variables at the top of `j_novEperAtom.sh`.
3. **Outputs are regenerable** — `output/` and `*.db` are gitignored; only code + docs
   are tracked.
4. **This is the kappa=4 leg of a sweep** — keep kappa distinct from a4 (3) and a6 (5);
   change only what this run is meant to probe, so the sweep stays comparable.
