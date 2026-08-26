# Run a4 — Novelty-LCB Fe/MgO search (seed 3, 500 iterations, kappa=3)

Self-contained run directory under `_runs/`, fully independent of the project root.
Everything needed to launch and understand this run lives here.

## What this run is

A single-seed AGOX global-optimization search depositing 25 Fe atoms on a fixed
MgO(001) substrate (Mg25O25 + Fe25 = 75 atoms), using the **Novelty-LCB** acquisition
function `a(x) = σ(x) + λ·Novelty(x)` with the **auto global-minimum energy window**
(`energy_above_min = 1.0` eV/atom, `per_atom=True`). Physics and stack are identical to
the project root `main.py`.

## Treatment — what differs from the sibling runs

The kappa runs (a4/a5/a6) are **kappa sweeps** of the standard a2 run
(`a2_mgofe_Seed3_Iter500`, kappa=2.0): same seed (3), same 500 iterations, but a
different `KAPPA` (the LCB surrogate-relaxation surface parameter).

| Run | seed | N_ITERATIONS | KAPPA |
|---|---|---|---|
| a2 | 3 | 500 | 2.0 |
| **a4** (this) | 3 | 500 | **3.0** |
| a5 | 3 | 500 | 4.0 |
| a6 | 3 | 500 | 5.0 |

Higher kappa makes the surrogate-relaxation surface more aggressive about exploiting
predicted low-energy regions (`E − kappa·sigma`); the kappa sweep probes how sensitive
the Novelty-LCB search is to this relaxation trade-off.

## Key configuration

- `SEED = 3`, `N_ITERATIONS = 500`, `KAPPA = 3` (set in `j_novEperAtom.sh`)
- `main.py` is run with `--kappa "${KAPPA}"`; kappa is a CLI flag (default KAPPA=2.0),
  threaded into the acquisitor's `get_acquisition_calculator()` LCB calculator.
- Energy window: auto global-minimum, `energy_above_min = 1.0` eV/atom (`per_atom=True`)
- `NOVELTY_WEIGHT = 1.5` (λ)
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

To change the run, edit `SEED=`, `N_ITERATIONS=`, and/or `KAPPA=` at the top of
`j_novEperAtom.sh` — never pass `-x` to `pjsub`.

## Outputs (regenerable, gitignored)

- `output/seed_3/1_db/db_3.db` — AGOX database of explored candidates
- `output/seed_3/0_result/0_xsf/` — structure files
- `output_seed_3.txt` — GPAW log (in cwd)

## Files

```
j_novEperAtom.sh    # PJM batch script (seed 3, 500 iterations, kappa=3)
main.py             # Novelty-LCB AGOX stack (latest from project root, v1.1.0)
novelty_lcb/        # proven package (latest, versioned, serialization fix)
scripts/            # slab/generator builders (latest from project root)
README.md           # this file
TUTORIAL.md         # how to reproduce THIS run
```

Code + docs tracked in git; `output/` and `*.db` are regenerable artifacts.
