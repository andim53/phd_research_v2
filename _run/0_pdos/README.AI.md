# README.AI.md — Machine Spec for _run/0_pdos (PDOS calculations)

## Purpose

Compute and analyse projected density of states (PDOS) for Fe/MgO and FeB/MgO
systems with GPAW. This file is the authoritative reference for AI agents
working in this project. Read it (and LOG.md, AGENTS.md) before acting.

## Environment (invariant)

- Local analysis / smoke test: `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0 + GPAW 25.7.0). Base `python3` has **no** GPAW/ASE.
- Heavy HPC runs: `gpaw_env`, activated inside the batch script. Launch via
  plain `pjsub job_dos.sh` — never `pjsub -x`.
- LSP/IDE import errors for `gpaw`/`ase` under base `python3` are misleading;
  judge compilation with the env python's `py_compile`.

## File structure

```
_run/0_pdos/
├── README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, AGENTS.md
├── dataset_boron3/            # AGOX search data for FeB/MgO (read-only input)
│   ├── main.py                # the AGOX search script (boron doping)
│   ├── scripts/               # slab/generator builders
│   └── seed_{0..6}/1_db/db_{s}.db   # per-seed databases (100 structs each)
├── _results/                  # completed runs + analysis
│   ├── 10_dos/                # reference Fe/MgO DOS+PDOS (main.py, job_dos.sh, dos_seed_{3,4}.csv)
│   ├── 32_dos/                # earlier total-DOS run (does_results.csv)
│   ├── 37_dos/                # real per-seed Fe-3d PDOS (dos_seed_{3,4}.csv)
│   └── analyze_dos.py         # analysis/plot script
└── 1_runs/                     # self-contained HPC run dirs
    └── 1_pdos_boron3_gs/      # PDOS of FeB/MgO global ground state
        ├── main.py            # entry point (GPAW LCAO DOS/PDOS)
        ├── job_dos.sh         # PJM batch script (gpaw_env, 24 cores)
        ├── gs_boron3.traj     # the ground-state structure
        ├── README.md          # per-run overview
        └── TUTORIAL.md        # per-run reproduction
```

## Entry points

- **New heavy PDOS run:** create `1_runs/<NN>_<descriptor>/` with `main.py`
  (adapted from `_results/10_dos/main.py`), `job_dos.sh`, and the structure
  file(s). Run on HPC with `pjsub job_dos.sh`.
- **Analysis/plot:** `_results/analyze_dos.py` (mirrors notebook cell 52 of
  `_archive/2_analysist/main_analyst.ipynb`), reads `dos_seed_{seed}.csv` files
  with columns `energy, total_dos_up, total_dos_down, total_Fe_d_up,
  total_Fe_d_down`.

## The DOS/PDOS code pattern (from 10_dos/main.py)

```python
calc = GPAW(mode={"name":"lcao"}, basis="dzp", xc="PBE", spinpol=True, hund=True,
            symmetry='off', nbands='nao', maxiter=500,
            occupations={"name":"fermi-dirac","width":0.05},
            kpts=(12,12,1), convergence={"energy":1e-4,"density":1e-3}, txt=...)
atoms.calc = calc; atoms.get_potential_energy()
e_fermi = calc.get_fermi_level()
energies_grid = np.linspace(-15, 10, 2000)
doscalc = calc.dos()                      # -> DOSCalculator (GPAW 25.x)
total = doscalc.raw_dos(energies_grid + e_fermi, spin=s, width=0.15)
pdos   = doscalc.raw_pdos(energies_grid + e_fermi, a=i, l=2, m=None, spin=s, width=0.15)
```

- `calc.dos()` returns `DOSCalculator` (the old `DOS`/`PDOS` classes are gone).
- `raw_pdos(..., l, m=None)` sums over all magnetic quantum numbers → full
  d (l=2) or p (l=1) projection per atom. Sum per atom to get per-element PDOS.

## Output schema

Run `main.py` writes `dos_seed_{seed}.csv` (or `dos_gs.csv`). Canonical columns
(per-element summed, matching 37_dos):

- `energy` — Fermi-shifted grid, −15..+10 eV, npts=2000
- `total_dos_up`, `total_dos_down`, `total_dos_sum`
- `total_Fe_d_up/down`, `total_O_p_up/down`, `total_B_p_up/down` (FeB/MgO)
  — or per-atom `Fe{i}_dz2_*`, `O{i}_pz_*` (Fe/MgO reference)

## Inputs / ground-state extraction

For FeB/MgO, ground-state structures come from `dataset_boron3`:
```python
from agox.databases import Database
db = Database(filename=f'seed_{s}/1_db/db_{s}.db'); db.restore_to_memory()
trajs = db.restore_to_trajectory()          # list of Atoms
es = [a.get_potential_energy() for a in trajs]
```
Global ground state (as of this scaffold): seed 4, index 86, E = −455.4124 eV,
Fe25 Mg25 O25 B3 (78 atoms). **seed_6 db is EMPTY** — skip it in global-min loops.

## Error handling & edge cases

- A seed DB may be empty (`restore_to_trajectory()` returns `None`/empty);
  guard the global-minimum loop against it.
- `.traj`/`.xsf`/`.csv`/`.png`/`.db` are regenerable artifacts — gitignored.
  Track `main.py`, `job_*.sh`, and `.md` docs.
- Base python cannot import `gpaw`/`ase`; always use the env python.

## Provenance / versioning

See `VERSIONS.md`. Every source edit bumps the file's module-level `__version__`
and is recorded in `LOG.md`.
