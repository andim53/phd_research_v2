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

---

## Session 2026-08-30 (2) — Add swap (permutation) move for multi-species systems

**Goal (user-confirmed via clarify):** Edit the Wang–Landau sampler so that
systems with ≥2 atom species can perform a permutation (swap) move, controlled by
a flag for swapping times per iteration, modeled on the reference
`_archive/_analysist/1_result/66_MgOFe_20B/scripts/global_permutation_generator.py`.

**Clarify decisions (all user-confirmed):**
1. **Scope:** swap positions of two atoms of DIFFERENT species within the mobile
   (perturb) set only — substrate stays fixed (matches the reference's
   'active atoms' scope).
2. **Integration:** swap is an ALTERNATIVE move — each MC step chooses swap vs
   rattle by a probability flag (`--swap-prob`, default 0 = off); a swap move
   performs a random `1..N` position swaps.
3. **Single swap action:** exchange positions AND rattle the two swapped atoms a
   little (mirrors the reference's swap + rattle_strength).
4. **Single-species behaviour:** disable swap automatically with a warning when
   only one mobile species is present (so the plain Fe/MgO `dataset` still runs).

**Actions taken:**
- `wang_landau_sampler.py` (1.0.0 → 1.1.0): added `swap_prob`/`max_swaps`/
  `swap_rattle` params; `_swap_species` detection + `swap_available` guard;
  `_propose_swap()` (random `1..max_swaps` swaps, picks two distinct mobile
  species, swaps their positions, rattles them by `swap_rattle`);
  `_propose_move()` (chooses swap vs rattle by `swap_prob`); move counters
  (`n_swap_moves`/`n_rattle_moves`); `run()` now uses `_propose_move()` and
  prints move counts.
- `main.py` (1.0.0 → 1.1.0): added `--swap-prob`, `--max-swaps`, `--swap-rattle`
  CLI flags and wired them into `WangLandauSampler(...)`.
- `smoke_test_wang_landau.py` (1.0.0 → 1.1.0): refactored `main()` to call
  `test_single_species()` + new `test_two_species_swap()` (2-species toy with
  swap_prob=0.5 must produce swap moves; single-species with swap_prob>0 must
  fall back to all-rattle).
- Docs: updated `VERSIONS.md`, `README.md` (CLI table, usage example, decisions
  table, Concepts note), `README.AI.md` (CLI table, error-handling #7),
  `TUTORIAL.md` (Step 4b).

**Results (real output):**
- Compile: `$PY -m py_compile main.py wang_landau/*.py smoke_test_wang_landau.py`
  → OK.
- 2-species toy: `swap_prob=0.5` → 1000 swap / 1000 rattle moves (50/50 as
  expected); full 3000-step run → 1495 swap / 1505 rattle.
- Single-species toy with `swap_prob=0.5` → 0 swap / 1000 rattle (graceful
  no-op, no crash).
- `smoke_test_wang_landau.py` → `[SMOKE] RESULT: PASS` (both single-species and
  swap tests).

**Decisions & reasoning:**
- Kept the swap purely positional (exchange two atoms' positions, then rattle
  them) rather than pulling in the AGOX Candidate/Environment confinement +
  steric machinery — our sampler works on plain `ase.Atoms` + GPR and has no
  Environment. The reference's confinement/steric checks have no analogue here,
  so the swap is geometric + the WL acceptance handles physicality.
- `max_swaps` semantics = random `1..max` per swap move, exactly the reference's
  `num_swaps = randint(max_number_of_swaps) + 1`.
- Debugged a numpy list-indexing bug: `trial.get_chemical_symbols()` returns a
  list, which can't be fancy-indexed by an int array — fixed with
  `np.array(...)`.

**Open items:**
- Run the swap move on the real boron dataset (HPC) once a boron run is launched
  (`--perturb-symbols Fe,B --swap-prob ...`).

**Time:** ~2026-08-30 20:50–21:10 (JST).

---

## Session 2026-08-30 (3) — Scaffold run dirs `_runs/c1` and `_runs/c2`

**Goal (user-confirmed via clarify):** Create two self-contained run dirs under
`_runs/`: c1 uses the plain Fe/MgO `dataset`, c2 uses the B3-doped
`dataset_boron3`.

**Clarify decisions (all user-confirmed):**
1. **Naming:** `_runs/c1_mgofe_N40_Emax04` and `_runs/c2_boron3_N40_Emax04`
   (`<NN>_<descriptor>` convention).
2. **Params:** default for both — `--n-bins 40 --e-max 0.40 --mc-steps 20000000
   --small-step 0.05 --large-step 0.40 --temperatures 100..1000`.
3. **Swap:** c2 (boron3) enables the swap move — `--perturb-symbols Fe,B
   --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05`. c1 (Fe/MgO) uses
   `--perturb-symbols Fe` with no swap (single mobile species).
4. **Launch:** scaffold only (batch scripts + per-run README/TUTORIAL + code +
   dataset copies), ready to launch later — do NOT `pjsub`.

**Actions taken:**
- Created `_runs/c1_mgofe_N40_Emax04/` and `_runs/c2_boron3_N40_Emax04/`.
- Copied `main.py` (v1.1.0) + `wang_landau/` package into each (self-contained).
- Copied the datasets self-contained: `dataset/` (13 DBs, Fe/MgO) into c1,
  `dataset_boron3/` (7 DBs, B3Fe25Mg25O25) into c2. Removed embedded `.git`
  gitlinks.
- Wrote `j_c1_mgofe_N40_Emax04.sh` (dataset, Fe, no swap) and
  `j_c2_boron3_N40_Emax04.sh` (dataset_boron3, Fe,B, swap) — bare PJM scripts
  (`gpaw_env`, 24 cores).
- Wrote per-run `README.md` + `TUTORIAL.md` for each run dir.

**Results (real output):**
- Both run dirs compile standalone:
  `$PY -m py_compile <run>/main.py <run>/wang_landau/*.py` → OK (v1.1.0).
- c2 dataset confirmed B3Fe25Mg25O25 / 78 atoms.
- Git staging: 91 files (code + docs + `latt_log.md`); regenerable data
  (`.db/.xsf/.png/.csv/.out`) correctly excluded by `.gitignore`.

**Open items:**
- Launch the runs on HPC when ready: `pjsub
  _runs/c1_mgofe_N40_Emax04/j_c1_mgofe_N40_Emax04.sh` and `pjsub
  _runs/c2_boron3_N40_Emax04/j_c2_boron3_N40_Emax04.sh`.

**Time:** ~2026-08-30 21:15–21:30 (JST).

---

## Session 2026-08-31 — c1 sweep job (mc-steps 10k/30k/50k)

**Goal (user-confirmed via clarify):** Make a new job script in
`_runs/c1_mgofe_N40_Emax04/` that runs the SAME parameters as
`j_c1_mgofe_N40_Emax04.sh` but as an MC-steps sweep (10000 / 30000 / 50000),
each saved to its own separate output dir.

**Clarify decisions (all user-confirmed):**
1. One job script running all three `--mc-steps` values sequentially in ONE PJM job.
2. All params identical to the c1 baseline (--n-bins 40 --e-max 0.40 --small-step
   0.05 --large-step 0.40 --perturb-symbols Fe --temperatures 100,200,300,500,1000
   --rng 42); only --mc-steps and --output differ.
3. Output dirs: `wl_output_c1_sweep_10000`, `wl_output_c1_sweep_30000`,
   `wl_output_c1_sweep_50000`.
4. Job script name: `j_c1_mgofe_N40_Emax04_sweep.sh`.

**Actions taken:**
- Created `_runs/c1_mgofe_N40_Emax04/j_c1_mgofe_N40_Emax04_sweep.sh` (bare PJM,
  gpaw_env, 24 cores; three sequential `python ./main.py` calls).
- Updated the run-dir `README.md` and `TUTORIAL.md` to document the sweep job.

**Results (real output):**
- `main.py --help` confirms all sweep args (--mc-steps, --output, --dataset,
  --n-bins, --e-max, --small-step, --large-step, --perturb-symbols,
  --temperatures, --rng) are valid in this run's main.py (v1.1.0).

**Open items:**
- Launch `pjsub _runs/c1_mgofe_N40_Emax04/j_c1_mgofe_N40_Emax04_sweep.sh` on HPC
  when ready.

**Time:** ~2026-08-31 (JST).

---

## Session 2026-08-31 (2) — c2 sweep job (mc-steps 10k/30k/50k)

**Goal:** Mirror the c1 sweep for the c2 run (B3-doped) — a new job script in
`_runs/c2_boron3_N40_Emax04/` running the SAME parameters as
`j_c2_boron3_N40_Emax04.sh` but as an MC-steps sweep (10000 / 30000 / 50000),
each to its own output dir.

**Clarify:** Not needed — "do the same for c2" is unambiguous (mirror the c1
sweep, including the swap flags).

**Actions taken:**
- Created `_runs/c2_boron3_N40_Emax04/j_c2_boron3_N40_Emax04_sweep.sh` (bare PJM,
  gpaw_env, 24 cores; three sequential `python ./main.py` calls, all params
  identical to the c2 baseline incl. swap: --dataset dataset_boron3 --n-bins 40
  --e-max 0.40 --small-step 0.05 --large-step 0.40 --perturb-symbols Fe,B
  --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 --temperatures
  100,200,300,500,1000 --rng 42).
- Outputs: `wl_output_c2_sweep_10000`, `wl_output_c2_sweep_30000`,
  `wl_output_c2_sweep_50000`.
- Updated the run-dir `README.md` and `TUTORIAL.md` to document the sweep job.

**Results (real output):** job script created; docs updated. (Not launched.)

**Open items:**
- Launch `pjsub _runs/c2_boron3_N40_Emax04/j_c2_boron3_N40_Emax04_sweep.sh` on HPC
  when ready.

**Time:** ~2026-08-31 (JST).

---

## Session 2026-08-31 (3) — Analyze Wang-Landau HPC outputs (c1, c2) + fix g(E) PNG bug

**Goal (user-confirmed via clarify):** Write a tool to extract the necessary data
for each `wl_output_*` (per-iteration state density + process/convergence
metrics) for both c1 and c2, and plot the state density from each iteration.

**Clarify decisions (all user-confirmed):**
1. Fix the matplotlib math-text bug (the HPC PNGs failed) AND build the analysis
   tool.
2. Single analysis script in `_analysist/` auto-discovering all `wl_output_*`
   dirs for c1 and c2, extracting per-output data + convergence metrics, plotting
   the state density per system.
3. One state-density figure per system (c1: mc1000 + 3 sweeps = 4 curves; c2: 3
   sweeps).

**Actions taken:**
- **Bug fix:** `main.py` g(E) x-label `r"$(E - E_{\\mathrm{min}})/N$"` had a
  double backslash (`\\mathrm`) → matplotlib mathtext `ParseSyntaxException`,
  crashing the HPC `g_of_E.png` write. Fixed to single `\mathrm` in all 5 copies
  (root, `_runs/c1`, `_runs/c2`, `_analysist/c1`, `_analysist/c2`). Verified the
  label renders.
- **New tool:** `_analysist/analyze_wl_outputs.py` (v1.0.0) auto-discovers
  `wl_output_*`, reads `g_of_E.csv`/`thermodynamics.csv`/`heat_capacity.csv` and
  parses per-run segments from the job `.out` logs (init rel E, stages, final
  ln_f, rattle/swap moves, 1/t status, visited-bin trajectory). Writes
  `wl_analysis_summary.csv` + `state_density_c1.png` + `state_density_c2.png`.
- **DISCUSSION.md** in `_analysist/` documenting the findings.

**Results (real output):** tool runs; figures `state_density_c1.png` (2100x1350)
and `state_density_c2.png` (2100x1350) + summary CSV produced. Key findings
(recorded in DISCUSSION.md):
- The HPC g_of_E.png failed due to the `\\mathrm` math-text bug (CSVs survived).
- Physics: the WL walker is **stuck at the top bin** — c1 init rel E = 0.675
  eV/atom (> e_max 0.40 → top bin), c2 init rel E = 159.9996 eV/atom (unphysical
  GPR extrapolation). c1 reaches 20/40 bins only at 30k+ steps; c2 stays 1/40.
  Stages advance trivially (walker keeps visiting the top bin), so **visited-bin
  count** is the honest convergence metric.
- Thermodynamics Z/F from these runs are not meaningful (delta/partial g(E)).

**Open items:**
- Fix `initialize()` to start inside the tracked window / reject unphysical init
  rel E, and re-run the sweeps.
- Note: user edited `_runs/c1`/`_runs/c2` job scripts to 64 cores and reverted
  the sweep README/TUTORIAL sections; those edits left untouched.

**Time:** ~2026-08-31 (JST).
