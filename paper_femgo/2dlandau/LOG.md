# LOG.md — `paper_femgo/2dlandau` (append-only)

## 2026-09-22 — Initial build from approved spec v5

Built the `2dlandau` sub-project from `$SPEC_PATH/202609221952-2dlandau-g-e-deltaz.md`
(v5, approved) inside `paper_femgo`. Deliverables:

- `landau_2d/` package: `generator.py` (DeltaZGenerator), `wang_landau_2d.py`
  (WangLandau2DSampler), `gpr_training.py` (reused verbatim from d_landauPlus),
  `thermodynamics.py` (reweight_2d, E_min_curve), `utils.py`.
- `main.py` (CLI), `smoke_test_2dlandau.py` (fake 2-Fe double-well GPR),
  `real_gpr_check.py` (real-GPR wiring + M3 spot-check), `j_2dlandau.sh`,
  `README.AI.md`, this LOG.md.

Verification (real execution):
- `py_compile` clean on all modules.
- **smoke_test_2dlandau.py → PASS.** Generator realizes ΔZ exactly; ceiling holds;
  2D WL walk visits multiple (E,ΔZ) cells and reaches 1/t; ⟨ΔZ(T)⟩ is genuinely
  T-dependent (≈3.0 Å @100 K → ≈0 Å @1000 K) and ΔF_flat_island changes sign
  ~400 K (flat↔island transition).
- **real_gpr_check.py → COMPLETE.** GPR trained on 1297 structs (720-d
  Fingerprint); GPR-vs-DFT delta ~±0.1 eV; 8-step walk accepts 2 structures.

### Fixes applied during the build (recorded per AGENTS rule 4)
1. **Generator in-plane placement (M3, critical).** First version randomized Fe
   in-plane positions uniformly over the cell. The real-GPR check showed
   catastrophic extrapolation (E ~ 1e18–1e21 eV) because the training Fe sits on
   a 5×5 MgO(001) hollow-site lattice. **Fix:** pin Fe in-plane to the reference
   structure's adsorption sites; randomize only z-heights (`in_plane_jitter=0`
   default). Re-checked: E −413.9 eV (flat) / −385.3 eV (tall), physical.
2. **Ceiling box floor (C1/m2).** `_ceiling_box` first set the box bottom at
   `z_contact` (floor+ceiling, contradicting "ceiling-only"). **Fix:** bottom at
   `substrate_top`, ceiling at `z_contact + ΔZ`; bottom Fe held by the adsorption
   well, not hard-pinned.
3. **Reweighting overflow.** `reweight_2d` computed `w = exp(−βE)/g` directly,
   which over/underflows over WL's ln_g range. **Fix:** full log-space
   (`logw = −βE_total − ln_g[i,j]`).
4. **Smoke-test toy.** Iterated 2-Fe → 3-Fe → 2-Fe to avoid a quartic-barrier
   singular Hessian ("Eigenvalues did not converge"); final toy is a double well
   in dZ × weak harmonic in mean height (full-rank forces).

Version bumps: generator.py 1.0.0→1.1.0 (in-plane change); smoke test 1.0.0→1.1.0.

## 2026-09-22 — ΔZ redefined as film height + natural-island cap

The v5 spec's "z-spread" ΔZ definition (max−min over Fe) collapsed when tested on
the real GPR: the bottom Fe dropped toward the surface and inflated the spread, so
the axis covered only 3/12 ΔZ bins (7/420 cells). Owner decision (2026-09-22):

- **ΔZ = film height** `max(z_Fe) − z_substrate_top` (fixed substrate reference).
- **Cap the range at the natural island height** (5.725 Å, the global-min
  structure's film height). Above it the Fe sink back, so the cap makes the
  z-ceiling bind at every target → no sinking, no inflation.

Changes:
- `generator.py`: `fe_film_height` (axis) + keep `fe_z_spread` (label only); top Fe
  placed at `z_substrate_top + ΔZ`; `draw_target_dz(dz_min, dz_max)`. 1.1.0→1.2.0.
- `wang_landau_2d.py`: `fe_axis` = film height; ceiling at `z_substrate_top + ΔZ`;
  proposal draws `[dz_min, dz_max]`; `label(atoms)` uses z-spread; defaults
  `dz_min=2.08, dz_max=5.73`. 1.0.0→1.1.0.
- `main.py`: `--dz-min`/`--dz-max` default to `None` and are measured at runtime
  (contact gap / natural-island height).
- `real_gpr_check.py`, `map_accessible.py`: film-height axis + measured range.
- `smoke_test_2dlandau.py`: rewritten to film height (1.1.0→1.2.0).

Verification (real execution):
- `py_compile` clean; **smoke test PASS** (accessible cells 37, T-dependent ⟨ΔZ(T)⟩).
- **map_accessible (80 proposals, real GPR): ΔZ spans 2.10→5.65 Å across all 12/12
  ΔZ bins** (was 3/12), distinct E bins 7/35, accessible cells 28/420. E is a thin
  band 0.20→0.34 eV/atom (inherent-structure, as per C2), rising with film height.
  Top ΔZ bin (5.57 Å) is the widest spread (0.118 eV/atom) → extrapolation, M3.
- `real_gpr_check.py` wiring still COMPLETE (M3 spot-check now at film-height
  extremes 2.08 / 5.73 Å).

## 2026-09-23 — dz-min crash fix (spec 202609232043)

First HPC result (`hpc_results/1_2dlandau`) crashed with `ValueError: high - low < 0`
at `generator.py:89` (`rng.uniform(z_contact, top_z)`). Root cause: the job script
passed stale `--dz-min 0.0 --dz-max 4.5` (old z-spread range), so the generator drew
`dZ_target < contact_gap (2.08)`, making `top_z < z_contact`.

Fix (spec v3, approved):
- Dropped `--dz-min`/`--dz-max` from all three job scripts (source `j_2dlandau.sh`,
  `hpc_runs/2dlandau/job_2dlandau.sh`, `hpc_results/1_2dlandau/j1_8c_1kStep.sh`) so
  `main.py` defaults the range to `[contact_gap 2.08, natural-island 5.73]`.
- Defensive `top_z = max(top_z, z_contact)` clamp in `generator.__call__`
  (belt-and-suspenders; fails soft if a bad range is ever passed).
- `generator.py` 1.2.0→1.2.1 (all three copies).

Verification (real execution): `main.py --mc-steps 1 --reference-steps 5` (no dz
flags) → `dZ range (film height): [2.080, 5.725]`, `dz_min=2.08`,
`dz_max=5.724565966311513` in `g_of_E_dZ.json`, exit 0. Crash gone.
