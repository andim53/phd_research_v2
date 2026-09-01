# Run a9 — Novelty-LCB Fe/MgO search (seed 3, 500 iter, kappa=4, novelty_weight=4.0)

Self-contained run directory under `1_runs/`, fully independent of the project root.
Everything needed to launch and understand this run lives here.

## What this run is

A single-seed AGOX global-optimization search depositing 25 Fe atoms on a fixed
MgO(001) substrate (Mg25O25 + Fe25 = 75 atoms), using the **Novelty-LCB** acquisition
function `a(x) = σ(x) + λ·Novelty(x)` with the **auto global-minimum energy window**
(`energy_above_min = 1.0` eV/atom, `per_atom=True`). Physics and stack are identical to
the project root `main.py`.

## Treatment — what differs from the sibling runs

The a7/a8/a9 runs are a **novelty_weight sweep** built from the base run
`a5_mgofe_Seed3_Iter500_k4` (kappa=4, novelty_weight=1.5). Same seed (3), same 500
iterations, same kappa (4) — only `NOVELTY_WEIGHT` differs.

| Run | seed | N_ITERATIONS | KAPPA | NOVELTY_WEIGHT |
|---|---|---|---|---|
| a5 (base) | 3 | 500 | 4 | 1.5 |
| a7 | 3 | 500 | 4 | 2.0 |
| a8 | 3 | 500 | 4 | 3.0 |
| **a9** (this) | 3 | 500 | 4 | **4.0** |

`NOVELTY_WEIGHT` is λ in `a(x) = σ + λ·Novelty`. Higher λ weights structural novelty
more heavily against pure uncertainty, pushing the search harder toward structurally
distinct basins.

## Key configuration

- `SEED = 3`, `N_ITERATIONS = 500`, `KAPPA = 4`, `NOVELTY_WEIGHT = 4` (set in
  `j_novEperAtom.sh`)
- `main.py` is run with `--kappa "${KAPPA}"` and `--novelty-weight "${NOVELTY_WEIGHT}"`;
  both are CLI flags (defaults KAPPA=2.0, NOVELTY_WEIGHT=1.5) threaded into the
  acquisitor.
- Energy window: auto global-minimum, `energy_above_min = 1.0` eV/atom (`per_atom=True`)
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

To change the run, edit `SEED=`, `N_ITERATIONS=`, `KAPPA=`, and/or `NOVELTY_WEIGHT=` at
the top of `j_novEperAtom.sh` — never pass `-x` to `pjsub`.

## Outputs (regenerable, gitignored)

- `output/seed_3/1_db/db_3.db` — AGOX database of explored candidates
- `output/seed_3/0_result/0_xsf/` — structure files
- `output_seed_3.txt` — GPAW log (in cwd)

## Files

```
j_novEperAtom.sh    # PJM batch script (seed 3, 500 iter, kappa=4, novelty_weight=4)
main.py             # Novelty-LCB AGOX stack (latest from project root, v1.1.1)
novelty_lcb/        # proven package (latest, versioned, serialization fix)
scripts/            # slab/generator builders (latest from project root)
README.md           # this file
TUTORIAL.md         # how to reproduce THIS run
```

Code + docs tracked in git; `output/` and `*.db` are regenerable artifacts.
