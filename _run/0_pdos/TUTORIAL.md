# TUTORIAL.md — Reproduce the 0_pdos PDOS project

## Prerequisites

- `agox_v2` conda env for local analysis / smoke tests:
  `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2, ASE 3.25.0, GPAW 25.7.0).
- HPC access with `gpaw_env` for heavy DOS/PDOS runs (`pjsub` batch).

## Step 1 — Understand the project layout

```
_run/0_pdos/
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md
├── dataset_boron3/   # FeB/MgO AGOX search data (input)
├── _results/         # completed DOS/PDOS runs + analysis
└── 1_runs/            # self-contained HPC run dirs
```

## Step 2 — Extract a ground-state structure (FeB/MgO)

```python
# env python: /home/think/miniconda3/envs/agox_v2/bin/python
from agox.databases import Database
from ase.io import write

for seed in range(7):
    db = Database(filename=f'dataset_boron3/seed_{seed}/1_db/db_{seed}.db')
    db.restore_to_memory()
    trajs = db.restore_to_trajectory()
    es = [a.get_potential_energy() for a in trajs]
    print(seed, min(es))

# Global min -> seed 4, idx 86, E=-455.4124 (Fe25 Mg25 O25 B3, 78 atoms)
db = Database(filename='dataset_boron3/seed_4/1_db/db_4.db'); db.restore_to_memory()
gs = db.restore_to_trajectory()[86]
write('gs_boron3.traj', gs)
```

## Step 3 — Run a DOS/PDOS calculation

Copy the reference `_results/10_dos/main.py`, adapt the structure input and the
PDOS projection, place in `1_runs/<NN>_<descriptor>/`, and add `job_dos.sh`.

Launch on HPC:
```bash
cd 1_runs/<NN>_<descriptor>
pjsub job_dos.sh      # runs: python ./main.py  (gpaw_env, 24 cores)
```

Output: `dos_seed_{seed}.csv` / `dos_gs.csv` (Fermi-shifted, −15..+10 eV,
2000 pts) with total spin DOS + per-element PDOS columns.

## Step 4 — Analyse / plot the PDOS

```bash
cd _results
/home/think/miniconda3/envs/agox_v2/bin/python analyze_dos.py
```
Reads `37_dos/dos_seed_{3,4}.csv` by default; edit `seed_map`/`DOS_DIR` to
point at other data. Produces `dos_comparison_{overlay,subplot}.png`.

## Pitfalls

- Base `python3` has **no** GPAW/ASE — always use `agox_v2` for local checks.
- `calc.dos()` returns `DOSCalculator` in GPAW 25.x (the old `DOS`/`PDOS`
  classes are removed). Use `raw_dos` / `raw_pdos(..., l, m=None, spin, width)`.
- A seed DB may be empty; guard global-minimum loops (e.g. `seed_6` is empty).
- Keep `.sh` batch scripts bare; set env via `conda activate gpaw_env` inside.

## Verification checklist

- [ ] `main.py` compiles: `/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile main.py`
- [ ] Structure loads with expected composition/natoms/pbc.
- [ ] HPC job `pjsub`ed; `output_*.txt` shows SCF convergence.
- [ ] CSV has expected columns, no NaNs.
