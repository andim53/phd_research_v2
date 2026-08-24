# Calibrating the Novelty-LCB energy window from an existing LCB-only dataset

## Key fact: the window is on ABSOLUTE energy
`calculate_acquisition_function` compares the candidate's **predicted** `E` against
`target_energy ± delta_E` via `if E < lo or E > hi`. So `target_energy` must be a real
energy inside the system's band — **NOT 0**. A placeholder `target=0.0` silently
excludes most/all candidates (the Fe/MgO band is ≈ −437 to −386 eV).

## Best practice: reuse an existing LCB-only run instead of a fresh short run
If the user already has a prior **LCB-only** (regular GOFEE/LCB) run of the same
system, read its energy distribution and set `target_energy` from that. This is
cheaper and more representative than launching a brand-new short run.

Fe/MgO case (verified): 13 seeds, `dataset/seed_*/1_db/db_*.db`, 1297 structures,
Mg25O25Fe25 (75 atoms). Band:
- E_min = −436.91 eV, E_max = −386.29 eV
- band centre ≈ −411.6 eV
- p1..p99 ≈ [−436.8, −391.6]

## Recipe
1. Read all seed DBs and collect energies:
   ```python
   import glob, numpy as np
   from agox.databases import Database
   E = []
   for p in sorted(glob.glob('dataset/seed_*/1_db/db_*.db')):
       db = Database(filename=p); db.restore_to_memory()
       E += [a.get_potential_energy() for a in db.restore_to_trajectory()]
   E = np.array(E)
   # report min/max/mean/median + percentiles p1..p99
   ```
   (Also verify uniform composition: `Counter(tuple(a.get_chemical_symbols()))`
   must collapse to one; here Mg25O25Fe25.)
2. **Broad / low-selectivity window** (default choice — let novelty + uncertainty
   drive the search): `target_energy` = band centre, `delta_E` = wide half-width that
   covers ~p1..p99.
   - Fe/MgO: `target_energy = -411.6`, `delta_E = 25` -> window ≈ [−436.6, −386.6].
3. **Strict local-minimum window** (focus on stable minima only): narrow to the low
   band, e.g. `target ≈ -432`, `delta_E ≈ 3`.
4. Write the chosen values into `main.py` (`NOVELTY_TARGET_ENERGY`,
   `NOVELTY_DELTA_E`) AND document the source band in the README (a "How to set
   target_energy" subsection) so the calibration is traceable.

## Keep a re-runnable helper
Save the DB-reading snippet as a permanent `energy_stats.py` in the project root
rather than a throwaway underscore-prefixed temp script — TUTORIAL/README can point
to it for re-verification, and it documents provenance.

## Notes
- The energy-window filter and the KMeansSampler's `max_energy=5` filter are
  **independent mechanisms** — don't conflate them.
- When changing systems, re-calibrate; the values above are Fe/MgO-specific.
