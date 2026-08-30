# Run a10 — Novelty-LCB Fe/MgO+B search (seed 3, 500 iterations)

Self-contained run directory under `_runs/`, fully independent of the project root.
Everything needed to launch and understand this run lives here.

## What this run is

A single-seed AGOX global-optimization search depositing **Boron-doped Fe** on a fixed
MgO(001) substrate. The MgO substrate (Mg25O25 = 50 atoms) is fixed; the mobile
deposition layer is **B6Fe25** (25 Fe + **6 B** dopant atoms = 31 mobile atoms, 81 total).
It uses the **Novelty-LCB** acquisition function `a(x) = σ(x) + λ·Novelty(x)` with the
**auto global-minimum energy window** (`energy_above_min = 1.0` eV/atom,
`per_atom=True`).

## Treatment — what differs from the sibling runs

This is the project's first **Boron-doping** run, based on the 66_MgOFe_20B example
(`_archive/_analysist/1_result/66_MgOFe_20B`). B atoms are added into the Fe deposition
layer and the search also includes a Fe↔B permutation generator.

| Feature | a1–a9 (Fe/MgO) | **a10 (this)** |
|---|---|---|
| Deposition layer | Fe25 | **B6Fe25** |
| B dopant count | 0 | **6** (max hollow sites for 25 Fe) |
| Generators | Randomize + Rattle | Randomize + Rattle + **Permutation (Fe↔B)** |
| seed | 3 | 3 |
| N_ITERATIONS | 300/500/700 | 500 |
| KAPPA | varies | 2.0 (default) |
| NOVELTY_WEIGHT | varies | 1.5 (default) |

**B count rationale:** `add_adsorbate_to_hollows` places B in hollows between groups of
4 Fe atoms, so the max number of B sites for 25 Fe is `floor(25/4) = 6`. The run uses
this maximum.

## Key configuration

- `SEED = 3`, `N_ITERATIONS = 500`, `KAPPA = 2`, `NOVELTY_WEIGHT = 1.5`
- `NUM_ATOMS_ADD = 6`, `SYMBOL_ADD = "B"` (set in `main.py`)
- Energy window: auto global-minimum, `energy_above_min = 1.0` eV/atom (`per_atom=True`)
- Generators use the B-enabled candidate schedule `{0:[20,0,0], 10:[10,5,5], 25:[0,10,10]}`
- 64-core SubprocessGPAW, LCAO/dzp, PBE, spin-polarized

## How to run

Local structure/compile checks (no GPAW):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY -m py_compile main.py novelty_lcb/*.py scripts/*.py
```

HPC launch (uses `gpaw_env`, 64-core PJM batch):

```bash
pjsub j_novEperAtom.sh
```

To change the run, edit `SEED=`, `N_ITERATIONS=`, `KAPPA=`, `NOVELTY_WEIGHT=` at the top
of `j_novEperAtom.sh`, and `NUM_ATOMS_ADD` in `main.py` — never pass `-x` to `pjsub`.

## Outputs (regenerable, gitignored)

- `output/seed_3/1_db/db_3.db` — AGOX database of explored candidates
- `output/seed_3/0_result/0_xsf/` — structure files
- `output_seed_3.txt` — GPAW log (in cwd)

## Files

```
j_novEperAtom.sh    # PJM batch script (seed 3, 500 iterations)
main.py             # Novelty-LCB Fe/MgO+B stack (v1.2.0, NUM_ATOMS_ADD=6)
novelty_lcb/        # proven package (latest, versioned, serialization fix)
scripts/            # builders + add_adsorbate_to_hollows.py + global_permutation_generator.py
README.md           # this file
TUTORIAL.md         # how to reproduce THIS run
```

Code + docs tracked in git; `output/` and `*.db` are regenerable artifacts.
