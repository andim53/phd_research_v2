# LOG.md — Action Log (append-only)

## 2026-09-20 — Project scaffold (clarify-me / inspect-me approved spec)

**Goal (owner-confirmed):** initialize `d_landauPlus` — a new, no-DFT sampling
procedure for the Fe/MgO flat↔island transition on an AGOX GPR surrogate, via a
basin-hopping (inherent-structure) Wang–Landau walk initialised at the flat
reference.

**Spec provenance:** produced by a clarify-me interview and hardened through four
inspect-me passes. All findings folded: C1–C4, M1–M8, m2–m10, G1–G10. Skipped:
M4, m1 (stop_16 excluded intentionally). Δz-walk and 2D-WL ideas were proposed
and dropped in favour of a plain Markov WL walk.

**Actions taken:**
- Inspected `data/femgo` (13 seed DBs, 1333 structures Fe₂₅Mg₂₅O₂₅). Confirmed the
  flat/island split via Fe z-spread: flat = spread ≈ 0 Å (E_rel ≈ 0.30–0.67,
  metastable); island = spread ≳ 2 Å (global min). Data range 0.001–5.57 Å.
- Determined the GO run's constraint = `environment.get_constraints()` →
  `FixAtoms(substrate)` + `BoxConstraint(Fe; corner=[0,0,z_max+0.5],
  cell_z=max(spread,2.1)·4, pbc=[T,T,F])`, from `data/femgo/main.py`.
- Verified the AGOX `GPR` is a full ASE `Calculator` (energy + forces), so the
  relax path (`atoms.calc = gpr`, `ase.optimize.BFGS`) works on the real surrogate.
- Created `landau_plus/` package (adapted from `c_landausampling/wang_landau/`):
  `wang_landau_sampler.py` (LandauPlusSampler v1.0.0 — uniform-in-volume rattle,
  mandatory GPR relax with FixAtoms + BoxConstraint, flat-reference init, ensemble
  + flat/island labelling), `gpr_training.py`, `thermodynamics.py`, `utils.py`,
  `__init__.py`. All v1.0.0.
- Created `main.py` (v1.0.0) — CLI; `e-max 0.75`, `--rattle 1.5` (δ-sensitive,
  documented), `--relax-steps 100`.
- Created `smoke_test_landau_plus.py` (v1.0.0) — fake per-atom double-well GPR on a
  2-Fe motif (24/25-atom motifs give a singular BFGS Hessian; 2 atoms keep force
  full-rank). Exercises rattle/relax/accept/label/ensemble/thermodynamics.
- Created `README.AI.md`, `AGENTS.md`, `LOG.md` (the three deliverables; no
  README.md/TUTORIAL.md per owner instruction).

**Results (real execution):**
- `py_compile` on all source files: **OK**.
- `smoke_test_landau_plus.py`: **RESULT: PASS** — label (flat vs island) correct;
  relaxation lowers energy; 39/40 bins visited; T-dependent free energy (F from
  −2.84 to −2.31 eV over 100–1000 K); ensemble of 244 accepted structures with both
  `flat` and `island` labels; save() wrote `g_of_E.csv`, `ensemble.traj`,
  `ensemble.csv`.

**Decisions & reasoning:**
- Basin-hopping WL (rattle → relax → WL-accept) rather than rattle-only: this is
  the owner's explicit "generate → optimise → sample the optimised version" design,
  and yields the inherent-structure DOS.
- Flat reference init = highest-energy DB structure (the flat monolayer), so the
  walk starts at the metastable basin and descends.
- e-max = 0.75 (margin over flat top ~0.67); e-reject = default 5×e_max.
- Flat/island is a post-hoc label (Fe z-spread < 1.0 Å), NOT a sampler gate — the
  Δz-walk/2D-WL gating idea was dropped.

**Open items:**
- HPC batch script (`j_*.sh`) not yet written; production 25-Fe run not yet executed.
- The δ-dependence of the flat/island weight is untested — MUST test multiple
  `--rattle` values before trusting any physical ratio.
- `VERSIONS.md` manifest not yet created (owner asked for README.AI.md/AGENTS.md/
  LOG.md only; can add on request).

**Time:** session 2026-09-20.