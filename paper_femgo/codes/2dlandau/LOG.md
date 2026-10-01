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

## 2026-09-27 — checkpoint / resume (spec 202609271240, v8)

Added crash-resilient checkpointing + resume to the 2D WL sampler per approved
spec v8 (clarify-me + inspect-me cycle).

Changes:
- `wang_landau_2d.py` 1.1.0→1.2.0: `state_dict()`/`load_state()` (I/O-free
  sampler); `run()` gains `checkpoint_interval` + `checkpoint_callback` (fires
  every N steps and on completion).
- `main.py` 1.0.0→1.1.0: `--checkpoint-interval` (default 100); auto-resume from
  `--output/checkpoint.json` (skips reference pass + init); C1 config-header
  guard (fail-loud on mismatch); M2 target rules (`mc_steps < checkpoint` →
  abort, `==` → re-derive, `>` → resume); M1 two-file commit (`ensemble.traj`
  before `checkpoint.json`) + load consistency; m2 per-checkpoint step-tagged
  thermodynamic snapshots (`*.step{N}.*`); atomic writes (tmp→rename); G4
  corrupt/unknown-schema checkpoint → warn + fresh.
- `README.md`: checkpoint/resume section + `--checkpoint-interval` flag row +
  m6 "one run per output dir" note.

Fixes during the build (AGENTS rule 4):
1. **Traj format bug.** `ase_write(tmp, structs)` inferred format from the
   `.tmp` extension → `UnknownFileTypeError`. Fix: `format="traj"` + tmp
   cleanup on failure.
2. **Traj unreadable on resume.** The stored agox `BoxConstraint` dict can't be
   reconstructed by ASE's `dict2constraint` → `ValueError` reading
   `ensemble.traj`. Fix: write the traj **geometry-only** (strip constraints +
   calculator) — resume only needs coordinates.

Verification (real execution, agox_v2, real GPR 1297 structs):
- `py_compile` PASS on `main.py` + `wang_landau_2d.py`.
- **G1 resume smoke test** (`--checkpoint-interval 2 --relax-steps 10
  --reference-steps 12`): leg A `--mc-steps 2` → checkpoint at step 2, traj 2
  frames, `*.step2.*` snapshots; leg B `--mc-steps 4` → `[RESUME] loaded
  checkpoint at step 2 ... Reference pass + init SKIPPED`, ran 2 more steps,
  `Total MC steps = 4`; final `step=4`, `rows=4`, `traj frames=4` (readable),
  `H sum=4` (accumulated, not reset), `accessible=11` (preserved), `ln_g`
  nonzero cells=4. Both step2 and step4 snapshots present.
- **M2 branches:** `--mc-steps 1` (< checkpoint 4) → `[ABORT]`, no outputs;
  `--mc-steps 4` (==) → `[DONE] skipping sampling, re-deriving`; `--mc-steps 4`
  after step-2 checkpoint (`>`) → resumed 3–4.
- **C1/G2/G4 guards (unit):** config mismatch → SystemExit abort; corrupt /
  missing-config / wrong-schema checkpoint → warn + fresh (None).

Version bumps: wang_landau_2d.py 1.1.0→1.2.0; main.py 1.0.0→1.1.0.

## 2026-09-29 — reference/MC step + timing progress logging (spec 202609291759)

Added progress + wall-time logging to the reference pass and the MC walk per
approved spec v2 (clarify-me + inspect-me cycle; folded C1, M1, M2, M3).

Changes:
- `wang_landau_2d.py` 1.2.0→1.3.0: `_reference_pass()` emits a
  `ref <n>/<N> | <avg> ms/proposal | elapsed | ETA` line every
  `progress_interval` proposals, with a `n == reference_steps` fallback so it
  always fires ≥1 line (C1); `initialize()` adds a one-line
  `init walker selected after k proposal(s) in <dur>` report (M1); `run()` gains
  a `progress_interval` knob (default 10) and augments the step line with
  `<avg> ms/step | elapsed | ETA`, plus an end-of-run `MC walk wall time`
  summary. All timing prints use `flush=True` (HPC stdout is block-buffered, M2);
  `elapsed` = current-process segment, `ETA = avg × remaining` (M3). New
  `_fmt_dur` human-duration helper.
- `main.py` 1.1.0→1.2.0: `--progress-interval` (default 10) + plumb to sampler;
  `--reference-steps` default 2000→500.

Verification (real execution, agox_v2):
- `py_compile` clean on all modules.
- **smoke_test_2dlandau.py → PASS.** `ref` lines every 10 proposals (300 total),
  `init walker selected` one-liner, MC `step 1000/2000` lines with
  `ms/step | elapsed | ETA`, `MC walk wall time` summary. Physics unchanged.
- **main.py end-to-end** (`--reference-steps 5 --mc-steps 2 --progress-interval 10`,
  real GPR 1297 structs): C1 fallback emitted exactly one `ref 5/5` line
  (interval 10 > ref 5); init one-liner; `MC walk wall time = 6.2s`; outputs
  written. exit 0.

Note: `main.py` default `--dataset` (`codes/data/femgo`) is stale — the real
data is `paper_femgo/data/femgo`; runs must pass `--dataset` explicitly (or fix
`DATA_DIR`). Pre-existing, unrelated to this change.

## 2026-10-01 — configurable fmax + stall-drop inherent-structure definition (spec 202610012247, v8)

Added a configurable max-force threshold that defines what counts as an
inherent structure, per approved spec v8 (clarify-me + inspect-me cycle; folded
C1, M1, M2, m1, m2, G1(a), G2, G3, G4).

Changes:
- `landau_2d/wang_landau_2d.py` 1.3.0→1.4.0: new `fmax` ctor param (default
  0.1); `relax_steps` ctor default 100→300 (matches CLI). `_relax` now runs
  `opt.run(fmax=self.fmax, ...)` and **always recomputes** the final max force
  from the ending geometry (`np.abs(get_forces()).max()` — ASE has no
  `maxforce` attr; FixAtoms zeroes the fixed substrate, so this is the free-Fe
  residual, same convention as `probe_optionA_fmax.py`). `_propose` tries up to
  4 attempts (1 + 3 retries, each a fully fresh draw); a structure only counts
  as an inherent structure if its final max-force <= fmax; stalled quenches
  increment `n_stalled_trials` and retry; if all stall the proposal is dropped
  (`n_proposals_dropped` += 1, returns a dropped marker so callers hit the
  existing reject path). Stall counters persisted in `state_dict`/`load_state`
  (graceful `.get` for old checkpoints). m1: WARN if `fmax < 0.02` or the
  reference-pass drop rate > 50%.
- `main.py` 1.3.0→1.4.0: `--fmax` flag (default 0.1) threaded to the sampler;
  `fmax` added to the config header (pre-change checkpoints now abort on resume
  — expected); stall counters written into `g_of_E_dZ*.json` and printed in
  the emit summary.
- `make_examples.py` 1.0.0→1.1.0, `map_accessible.py` 1.0.0→1.1.0: `--fmax`
  flag (default 0.1) replaces the hardcoded `fmax=0.05` as the BFGS target
  (flag value only — no stall/regenerate logic, per G2).

Verification (real execution, agox_v2, real GPR 1297 structs):
- `py_compile` clean on all four edited files.
- **smoke_test_2dlandau.py → PASS** (1.2.0→1.3.0, Ray-free fake GPR): main run
  visits 30 cells, 1179 accepted structures, T-dependent <dZ(T)> (4.50→2.62 Å),
  dF changes sign — physics intact. **G1(a) stall-drop check** (fmax=1e-6):
  39 stalled trials, 4 proposals dropped, no crash; m1 WARN fired for
  `--fmax < 0.02`.
- **G1(a) real-GPR run BLOCKED (environment, not code):** `main.py --fmax
  0.005` failed at Ray startup ("current node timed out during startup") because
  the user's own nested-sampling run (`main.py --n-live 8 --n-iterations 20
  --output /tmp/ns_smoke`, PID 2287212) is actively holding the Ray instance.
  Not killed (user's process). The stall-drop logic is verified Ray-free via
  the smoke test; the real-GPR G1(a) run can be re-run once that process
  finishes.
- Empirical M1 probe (`probe_inbetween_fmax.py`, 5 trials × 300 steps @ fmax
  0.1): flat side (dZ 2.5/3.0) converges 5/5; island side (3.5–5.5) stalls
  40–80% but every height keeps 1–3 passing trials, so no region empties.

Version bumps: wang_landau_2d.py 1.3.0→1.4.0; main.py 1.3.0→1.4.0;
make_examples.py 1.0.0→1.1.0; map_accessible.py 1.0.0→1.1.0;
smoke_test_2dlandau.py 1.2.0→1.3.0.
