# TUTORIAL — Reproduce the 1_pdos_boron3_gs PDOS run

## Prerequisites
- HPC access with `gpaw_env` (GPAW 25.7.0 + ASE 3.25.0), launched via `pjsub`.
- The ground-state structure `gs_boron3.traj` (already present in this dir).

## 1. Extract the ground state (already done, for reference)
```python
from agox.databases import Database
from ase.io import write

# Find the global minimum across all 7 seeds of dataset_boron3
for seed in range(7):
    db = Database(filename=f'seed_{seed}/1_db/db_{seed}.db')
    db.restore_to_memory()
    trajs = db.restore_to_trajectory()
    es = [a.get_potential_energy() for a in trajs]
    print(seed, min(es))
# Global min -> seed 4, idx 86, E=-455.4124
db = Database(filename='seed_4/1_db/db_4.db'); db.restore_to_memory()
gs = db.restore_to_trajectory()[86]
write('gs_boron3.traj', gs)
```

## 2. Launch the DOS/PDOS job
```bash
cd 1_pdos_boron3_gs
pjsub job_dos.sh
```

`job_dos.sh` runs `python ./main.py` inside `gpaw_env` on 24 cores.

## 3. Output
`dos_gs.csv` (npts=2000, E from −15 to +10 eV, Fermi-shifted):
- total_dos_up / total_dos_down / total_dos_sum
- total_Fe_d_up/down (sum of Fe d-orbital PDOS, l=2, all m)
- total_O_p_up/down (sum of O p-orbital PDOS, l=1)
- total_B_p_up/down (sum of B p-orbital PDOS, l=1)

## 4. Verification
- `main.py` compiles under `agox_v2` (same GPAW/ASE API): the `calc.dos()`
  object's `raw_dos` / `raw_pdos` calls are valid (confirmed against GPAW
  25.7.0 signatures).
- On HPC, check `output_gs.txt` for SCF convergence, then confirm the CSV has
  the expected columns and no NaNs.

## Pitfalls
- Do **not** run `python ./main.py` from the base conda — `gpaw`/`ase` only exist
  in `agox_v2` (local) and `gpaw_env` (HPC). Use the HPC `pjsub` path for the
  real run.
- `raw_pdos(..., l=2, m=None)` sums over all magnetic quantum numbers → this is
  the full d (or p) projection, matching the 37_dos `total_Fe_d`/`total_O_p`
  convention. Passing a specific `m` would give only one orbital component.
