# Force filter + nested novel filter, and minima verification

Session-specific detail for `_run/9_novelFilter` beyond the core filter in
SKILL.md. Captures why force-filtering matters and how to wire it before the
novel filter.

## CRITICAL: raw AGOX structures are NOT converged local minima

The raw structures in `dataset/seed_*/1_db/db_*.db` carry genuine single-point
DFT energies but **large residual forces**, because the original evaluator used
`optimizer_run_kwargs={"fmax": 0.05, "steps": 1}` — only ~1 DFT relaxation step
per candidate (they were pre-relaxed on the surrogate/LCB surface, then given a
single-point DFT energy). Measured on Fe/MgO (75 atoms, 1297 structures):

- max|Fe force| : min 0.176, **median ~1.30**, max 10.08 eV/A
- **0 structures** in any novel threshold set had max|force| < 0.5 eV/A.

Consequence: a strict local-minimum check (`max|force| < fmax`, e.g. 0.05) on the
raw structures **rejects 100%**. Do NOT assume the DB holds converged minima.
"Capture only the minimum" requires EITHER a force filter (keep only
near-converged structures) OR a genuine DFT re-relaxation of the kept set.

## Force metric: mobile Fe atoms only

The 50-atom MgO substrate (all Mg+O at the bottom layer, z≈10.0) was held fixed
by the original `Environment` via `FixAtoms(indices=arange(len(template)))`.
It naturally carries large forces and should be EXCLUDED from the force measure.
Measure `max|force|` over the 25 mobile **Fe** atoms only:

```python
fe_idx = [i for i, s in enumerate(atoms.get_chemical_symbols()) if s == "Fe"]
fe_fmax = np.abs(forces[fe_idx]).max()
```

## Force filter + nested novel filter (`run_force_novel_filter.py`)

Pipeline (per force threshold): load ALL raw structures → force-filter (keep
`max|Fe force| < fthr`) → novel-filter the survivors (fixed threshold, default
1.0) → write `force_<v>/` folder + `force_comparison.csv`.

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_force_novel_filter.py --outdir ./force_output
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py --outdir ./force_output --prefix force_
```

Verified results (raw 1297 in, novel thr 1.0):
| force thr (eV/A) | force survivors | novel distinct kept | kept E range (eV) |
|---|---|---|---|
| 0.5 | 27 (2.1%) | 6 | -418.6 .. -417.1 |
| 1.0 | 338 (26.1%) | 44 | -436.9 .. -404.1 |
| 1.5 | 786 (60.6%) | 87 | -436.9 .. -391.5 |
| 2.0 | 1006 (77.6%) | 124 | -436.9 .. -391.5 |
| 2.5 | 1086 (83.7%) | 138 | -436.9 .. -391.5 |
| 3.0 | 1133 (87.4%) | 139 | -436.9 .. -391.5 |

Key observation: at the tightest threshold (0.5) the global minimum (-436.9)
does NOT survive — the ground-state geometry is not well-relaxed in the raw DB;
the most-relaxed structures cluster around -418 eV. As the threshold loosens the
true ground state enters.

## `--prefix` flag on run_analysis_thresholds.py

`run_analysis_thresholds.py` originally globbed only `thr_<v>/` folders. It now
accepts `--prefix <name>` so it can process `force_<v>/` (or any other prefix)
folders. Folder discovery: `startswith(prefix)`. The `--thresholds` CLI also
prepends the prefix.

## DFT re-relaxation to genuine minima (`relax_and_partition.py`)

To obtain TRUE minima for a minima-only partition function, re-relax the kept
structures with real DFT (GPAW) to a strict fmax, then keep only those with
residual `max|force| < fmax`. Use the GPAW parameters verbatim from
`dataset/main.py` (lcao/dzp, PBE, spinpol, pulay mixer, nbands='nao', kpts=(1,1,1),
convergence energy 1e-4 / density 1e-3 / eigenstates 1e-3, occupations
fermi-dirac width 0.05, hund=True, maxiter 100). Re-fix the MgO substrate with
`FixAtoms(indices=substrate_indices)` and relax only the 25 Fe atoms with
`ase.optimize.BFGS(..., fmax=...)`. Cache results keyed by source filename so
nested thresholds reuse already-relaxed structures.

Cost note: a full 75-atom Fe/MgO slab DFT relaxation is slow (~40 s/SCF iter on
one core). Run in background; a single SCF point needs a large enough cell (a
3x3x3 box fails with `GridBoundsError: Atom too close to edge` — use the real
14.35x14.35x20 cell).

## Example-pairs per threshold (`save_example_pairs.py`)

Because kept structures are pairwise > threshold, the closest pair among a
threshold's kept set sits just ABOVE the threshold. This script finds that pair
(separated by ~the threshold distance) and writes two XSFs per threshold plus a
`pairs_summary.csv`. Verified pair distances land essentially on the threshold
(0.25→0.2502, 0.5→0.5000, 1.0→1.0002, 1.5→1.5007, 2.0→2.0001) — a strong
confirmation of the interpretation.
