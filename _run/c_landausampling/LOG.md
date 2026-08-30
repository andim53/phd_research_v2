# LOG — Project c_landausampling (append-only)

Curated, append-only record of agent actions. Append new entries; never rewrite or
delete prior ones. Per session: Goal (user-confirmed via clarify), Actions, Results,
Decisions & reasoning, Open items, Time.

---

## Session 2026-08-30 — Project creation (Wang–Landau density of states)

**Goal (user-confirmed via clarify):** Create a new project dir at
`/home/think/Desktop/research/_run/c_landausampling`, structured like
`_run/b_nestedsampling` (README human+AI, LOG, TUTORIAL, VERSIONS, AGENTS,
PROMPTS, `.gitignore`, plus `_runs/`, `_analysist/`, `_archives/`, `_tmp/`), and
implement a **Wang–Landau** sampling that computes the density of states `g(E)`
using a Python + AGOX GPR surrogate (like b), with the Fortran toy
`_tmp/main_wanglandau_1d.f` as the algorithmic reference.

**Clarify decisions (all user-confirmed):**
1. **Scope:** scaffold the FULL project now — docs trio + AGENTS/VERSIONS/PROMPTS
   + `.gitignore` + `_runs/_analysist/_archives/_tmp` layout + Wang–Landau code
   (`main.py` + `wang_landau` package + `j_wanglandau.sh`) + local smoke test +
   git commit.
2. **Target:** real run on the AGOX GPR surrogate of the dataset; keep the 1D
   Fortran toy as an algorithmic reference in `_tmp/`.
3. **Datasets:** support all three (`dataset`, `dataset_boron3`, `dataset_boron`);
   default = `dataset`.
4. **Data wiring:** copy ALL three full dataset dirs into the project for a
   self-contained layout (~300M regenerable data; DBs/xsf gitignored).

**Actions taken:**
- Loaded `ai-agent-project-workflow`, `agox-nested-sampling`, `agox-run-code`
  skills; inspected `b_nestedsampling` deliverables (README/README.AI/AGENTS/
  VERSIONS/.gitignore/LOG/TUTORIAL/PROMPTS), the `nested_sampling` package, and
  `_tmp/main_wanglandau_1d.f`.
- Scaffolded `c_landausampling/{wang_landau,_runs,_analysist,_archives,_tmp}`.
- Wrote the `wang_landau/` package:
  - `wang_landau_sampler.py` (v1.0.0) — `WangLandauSampler`: flat-histogram
    density of states over relative energy per atom bins, small/large rattle
    moves on mobile atoms, Wang–Landau acceptance `ln r < ln g(cur) − ln g(trial)`,
    standard `f→√f` refinement then 1/t algorithm (Belardinelli & Pereyra 2007).
  - `gpr_training.py` (v1.0.0) — `load_all_seeds`, `build_gpr`, `validate_gpr`.
  - `thermodynamics.py` (v1.0.0) — `g_of_E_to_thermodynamics`,
    `heat_capacity_from_thermo` (normalises g(E) to unit integral; Z, F, C_V).
  - `utils.py` (v1.0.0) — `K_B`, `shift_energies`, `_logsumexp`.
  - `__init__.py` (v1.0.0) — package re-exports.
- Wrote `main.py` (v1.0.0): CLI runner (load dataset → train GPR → WangLandau
  → thermodynamics + g(E) plot), with `--dataset` selector for all three datasets.
- Wrote `smoke_test_wang_landau.py` (v1.0.0): cheap local validation of the real
  sampler on a **fake 1-atom double-well GPR** (no DFT/heavy training).
- Wrote `j_wanglandau.sh` (bare PJM script, `gpaw_env`, 24 cores).
- Copied `dataset/`, `dataset_boron3/`, `dataset_boron/` from `b_nestedsampling`
  (self-contained); removed the embedded `dataset_boron3/scripts/.git` gitlink.
- Wrote `.gitignore`, `README.md`, `README.AI.md`, `TUTORIAL.md`, `VERSIONS.md`,
  `AGENTS.md`, `PROMPTS.md`.

**Results (real output):**
- Compile: `$PY -m py_compile main.py wang_landau/*.py smoke_test_wang_landau.py`
  → OK.
- Smoke test: `$PY smoke_test_wang_landau.py` → `[SMOKE] RESULT: PASS`; 39/40 bins
  visited, 4 stages, 1/t switch reached, T-dependent `F` (≈ −0.13 eV at 100 K →
  ≈ +1.07 eV at 1000 K). Confirmed the thermodynamics module is correct (a spread
  g(E) gives T-dependent F; a delta-like g(E) gives constant F — expected).
- Real-GPR run (`--dataset dataset`, agox_v2, local): verified end-to-end wiring —
  loaded 1297 structures (13 DBs, Fe25Mg25O25/75 atoms, E −436.91…−386.29 eV),
  trained the 720-dim Fingerprint GPR (neg. log marginal likelihood 876.35;
  validation deltas ≈ 0.02–0.10 eV), initialized the WL walker (rel E 0.675 eV/atom,
  bin 39 of [0, 0.40]), and reached the first flatness stage. **Note:** each WL step
  calls `predict_energy` (cython Fingerprint feature ~ per-step bottleneck); 5000
  steps took ~190 s locally, so the full 20M-step run is intended for the HPC job
  (`j_wanglandau.sh`), not local verification.

**Decisions & reasoning:**
- Ported the Fortran 1D algorithm to structures+energy bins rather than a scalar
  coordinate; kept the standard→1/t refinement exactly.
- `g(E)` normalised to unit integral (WL gives g up to a constant); only the
  additive constant is arbitrary, so relative quantities and C_V are robust.
- Default `--e-max 0.40` eV/atom (island at 0, spans past the flat/barrier
  region), matching the Fortran's "island → barrier+margin" window.

**Open items:**
- Confirm the full real run completes and produces `g_of_E.*`,
  `thermodynamics.csv`, `heat_capacity.csv`.
- Future: per-run dirs under `_runs/` and analysis under `_analysist/` as runs
  are launched.

**Post-scaffold fix (main.py 1.0.0 → 1.0.1):** `--start-from-top` used
`action="store_true"` with `default=True`, so the documented
`--no-start-from-top` would not actually disable it. Switched to
`argparse.BooleanOptionalAction` so both forms work. Updated `VERSIONS.md`.

**Time:** ~2026-08-30 20:20–20:40 (JST).
