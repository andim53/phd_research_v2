# Novelty-LCB acquisitor: energy-window modes & AGOX wiring facts

Session-specific detail on the `NoveltyLCBAcquisitor` (`novelty_lcb/acquisitor.py`)
used in `_run/10_lcbnovel/`. These are the durable behaviors a future session needs
when running or extending a Novelty-LCB AGOX search.

## 1. Energy window is on ABSOLUTE predicted energy

The window is compared against the GPR's **absolute predicted total energy** `E`
(`model.predict_energy_and_uncertainty(cand)`), NOT a relative/per-atom/shifted value.

- Fe/MgO total energies are ~ -400 eV (band ≈ [-436.9, -386.3] for 75-atom
  Mg25O25Fe25). Setting `target_energy = 0` gives window [−ΔE, +ΔE] which **excludes
  everything** (every candidate gets +inf in the AGOX ascending-sort space → never
  selected → the search stalls).
- `target_energy` must be a real energy in the band, not 0. Only makes sense for
  relative energies (formation energy, shifted E_ref) — this acquisitor does NOT use
  relative energies.

## 2. Auto global-minimum mode (`energy_above_min`) — the default

Removes the old "run regular-LCB first to calibrate the window" two-step cost.

```python
NoveltyLCBAcquisitor(model, descriptor, database,
                     energy_above_min=X,   # X in eV (or eV/atom if per_atom=True)
                     per_atom=False,
                     target_energy=None,   # falls back to centered mode if energy_above_min is None
                     ...)
```

- Window = `(-inf, E_min + X]` where `E_min` = live lowest **DFT** energy in the DB
  (`_global_min_energy()`), recomputed each acquisition round so it tracks new minima.
- **No lower bound**: `E < E_min` is allowed so a genuinely new lower global minimum
  can still be discovered.
- **Empty DB** → no cap (`in_window = True`) until the first minimum exists.
- Backward compatible: if `energy_above_min is None`, falls back to the centered
  `target_energy ± delta_E` mode. If both are None, no window constraint at all.

## 3. Per-atom mode (`per_atom`)

Makes choosing X size-independent and intuitive (0.5–2 eV/atom).

- `per_atom=True` → compare `E/N <= E_min/N + X` (both E and E_min divided by atom
  count N; X in eV/atom). Requires fixed composition / atom count (true for Fe/MgO).
- Atom count `N` from `_n_atoms()` (len of first DB candidate; falls back to 1).
- For a fixed N, per-atom and total modes are **mathematically equivalent** — per-atom
  X is just total X/N. Verified by an equivalence test in `test_window_logic.py`.

## 4. AGOX `Database` resume behavior (critical for restart semantics)

`Database(filename=..., initialize=False, call_initialize=True)` — the default. On
open:
- `os.remove(filename)` only runs when `initialize=True`. So an existing DB is NOT
  wiped on re-run.
- `_initialize()` checks if the `structures` table exists; if it does, it does NOT
  recreate it and `_init_storage()` loads existing rows into memory. Candidates are
  restored; GPR + novelty rebuild from `get_all_candidates()`.
- **Implication**: re-running the same seed **continues/extends** the existing DB.
  To restart fresh you must delete `db_<seed>.db` (or use a new output path) yourself.

## 5. KMeansSampler placement & internals

`KMeansSampler` sits **between the collector and the acquisitor**; it thins the pool
of **already-evaluated** (relaxed + DFT-scored) structures to a diverse representative
set before the acquisitor scores them.

- `n_clusters = 1 + min(sample_size - 1, floor(len(energies)/5))` — automatic, capped
  at `sample_size`, grows with DB size. Not chosen manually.
- `max_energy=5` eV filter (`KMeansEnergyFilter`) drops structures > 5 eV above the
  current lowest-energy structure *before* clustering (does NOT delete from DB — only
  gates eligibility for sampling).
- Keeps the **lowest-energy member of each cluster** (`select_from_clusters`).
- Independent of the acquisitor's energy-window filter.

## 6. Verification pattern

The full AGOX path (ParallelRelaxPostprocess → Ray pool) can fail on a low-RAM node
with `ray.exceptions.ActorUnavailableError` (documented, environmental). To validate
the acquisitor window logic in isolation (no Ray/AGOX stack), build the acquisitor via
`object.__new__(NoveltyLCBAcquisitor)` + attribute assignment with mock
model/descriptor/database and call `calculate_acquisition_function` directly — see
`test_window_logic.py` in `_run/10_lcbnovel/`.
