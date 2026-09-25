# 1_pdos_boron3_gs — PDOS of the FeB/MgO global ground state

## What this run is
A single GPAW LCAO DOS/PDOS calculation for the **global minimum** structure of
the FeB/MgO system (Fe25 Mg25 O25 B3, 78 atoms, slab, pbc=[T,T,F]).

The structure is the lowest-energy configuration across all 7 seeds of the
`dataset_boron3` AGOX search: **seed_4, db index 86, E = −455.4124 eV**.

## Input
- `gs_boron3.traj` — the extracted ground-state structure.

## Code
- `main.py` — adapted from `_results/10_dos/main.py`. Same GPAW settings
  (LCAO, basis=dzp, PBE, spinpol, kpts=(12,12,1), npts=2000, width=0.15,
  emin/emax=−15/10, Fermi-shifted grid). The PDOS is summed **per element**
  (Fe-d l=2, O-p and B-p l=1, m=None), matching the `37_dos` output layout.
- `job_dos.sh` — PJM batch script (HPC, `gpaw_env`).

## Output
- `dos_gs.csv` — columns: energy, total_dos_up/down/sum,
  total_Fe_d_up/down, total_O_p_up/down, total_B_p_up/down.

## How to run (HPC)
```bash
pjsub job_dos.sh
```

## Note on naming
Run dir index 1 under `_run/0_pdos/_runs/`. The 0_pdos project has no AGENTS.md;
this follows the general `_runs/<NN>_<descriptor>` convention.
