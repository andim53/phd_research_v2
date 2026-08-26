# Run a1 — Novelty-LCB Fe/MgO search (seed 3, 300 iterations)

Self-contained run directory under `_runs/`, fully independent of the project root.
Everything needed to launch and understand this run lives here.

## What this run is

A single-seed AGOX global-optimization search depositing 25 Fe atoms on a fixed
MgO(001) substrate (Mg25O25 + Fe25 = 75 atoms), using the **Novelty-LCB** acquisition
function `a(x) = σ(x) + λ·Novelty(x)` with the **auto global-minimum energy window**
(`energy_above_min = 1.0` eV/atom, `per_atom=True`). Physics and stack are identical to
the project root `main.py`.

## Treatment — what differs from the sibling runs

| Run | seed | N_ITERATIONS | j script |
|---|---|---|---|
| **a1** (this) | 3 | **300** | `j_novEperAtom.sh` |
| a2 | 3 | 500 | `j_novEperAtom.sh` |
| a3 | 3 | 700 | `j_novEperAtom.sh` |

This is the **shortest** of the three per-seed runs. It exists to give a quick, cheap
first check of the Novelty-LCB Fe/MgO search before the longer 500 / 700 runs. All three
are otherwise identical (same `main.py`, same seed, same window config) — only the
iteration budget differs.

## Key configuration

- `SEED = 3`, `N_ITERATIONS = 300` (set in `j_novEperAtom.sh`)
- Energy window: auto global-minimum, `energy_above_min = 1.0` eV/atom (`per_atom=True`)
- `NOVELTY_WEIGHT = 1.5` (λ), `KAPPA = 2.0` (LCB relaxation surface)
- 64-core SubprocessGPAW, LCAO/dzp, PBE, spin-polarized

## How to run

Local structure/compile checks (no GPAW):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY -m py_compile main.py novelty_lcb/*.py scripts/*.py
$PY -c "from main import build_slabs; s,d,st=build_slabs(); print(s.get_chemical_formula(), len(s), st)"
```

HPC launch (uses `gpaw_env`, 64-core PJM batch):

```bash
pjsub j_novEperAtom.sh
```

To change the run, edit `SEED=` and/or `N_ITERATIONS=` at the top of `j_novEperAtom.sh`
— never pass `-x` to `pjsub`.

## Outputs (regenerable, gitignored)

- `output/seed_3/1_db/db_3.db` — AGOX database of explored candidates
- `output/seed_3/0_result/0_xsf/` — structure files
- `output_seed_3.txt` — GPAW log (in cwd)

## Files

```
j_novEperAtom.sh    # PJM batch script (seed 3, 300 iterations)
main.py             # Novelty-LCB AGOX stack (latest from project root)
novelty_lcb/        # proven package (latest, versioned, serialization fix)
scripts/            # slab/generator builders (latest from project root)
README.md           # this file
TUTORIAL.md         # how to reproduce THIS run
```

Code + docs tracked in git; `output/` and `*.db` are regenerable artifacts.
