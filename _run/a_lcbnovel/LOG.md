# Project LOG — Novelty-LCB Fe/MgO Search (project 10)

Append-only, curated record of what the AI agent (Calyx) actually did, decisions,
and reasoning. Raw tool-call / run output is captured in `transcript.log`.

---

## 2026-08-22 — Session 1: Scaffold + repair plan + serialization validation

### Goal (user-confirmed via clarify)
Reproduce/extend `_run/7_lcbnovel_mgofe` as a clean, documented project under the
AI-Agent Project Workflow (human README + AI README + LOG + TUTORIAL). Scope:
**faithful repair** (same Fe/MgO stack, 25 Fe on fixed MgO, GPAW), heavy run to be
launched on the HPC cluster (PJM, 64-core), NOT this session. Dual logging requested.

### Discovery — run 7 and run 6 never actually ran
- Read `7_lcbnovel_mgofe/j_novel.sh.6543317.out`: crashed at **seed 3** with
  `TypeError: Could not serialize the put value <LowerConfidenceBoundCalculator>:
  cannot pickle 'sqlite3.Connection' object`. No `seed_*/` dirs exist.
- Timestamp analysis: the acquisitor fix (module-level free functions + partial) is
  present in `7_lcbnovel_mgofe/novelty_lcb/acquisitor.py` (modified 16:00) but the
  crash log is from 15:48 — **the fix landed after the failed run and was never
  re-tested on a real run.** This is the core risk in "faithful repair".
- `6_lcbnovel_benchmark/j_bench.sh.6544501.out`: crashed on the `calc`→`calculator`
  kwarg bug (Bug C); `FIX_README.md` documents the fix but no
  `benchmark_results_surface/` dir exists — also never re-run.
- **Conclusion:** neither prior project ever completed a real search. Run 7 is a
  *broken-to-be-fixed* reproduction, not a working one to copy.

### Verification of the serialization root cause
- Read `agox/models/ABC_model.py`: `GPR.__init__(database=...)` calls
  `attach_to_database(database)`, which only does `self.attach(database)` (observer
  wiring) and does **not** store `self.database`. So the GPR pickles cleanly even
  when constructed with `database=`. Confirms the DB connection only leaks through
  objects that store a DB reference — exactly the acquisitor's bound methods.

### Actions taken
1. Copied `novelty_lcb/` package (acquisitor.py, utils.py, common.py,
   benchmark_helpers.py, __init__.py) and `scripts/` builders
   (build_mgo_stack, build_fe_stack, build_heteroStruct, hetero_struct_randomize,
   plot_structure) from `7_lcbnovel_mgofe/` into `a_lcbnovel/`.
   → `REUSE the proven package` (user decision), lowest risk.
2. Wrote `main.py` — faithful to run 7's physics (A_MGO, A_FE, dist_z, supercell (5,5,1),
   kpts (1,1,1), 1 MgO layer + 1 Fe layer, kappa=2, N_iterations=100) with:
   - **serialization-safe wiring** (fixed acquisitor, positional `calculator`),
   - per-seed CLI + range, so HPC can launch one seed per job.
3. Wrote `smoke_test_serialization.py` — cheap local test (EMT, tiny Au system,
   **no GPAW**) that walks the exact crash path:
   `NoveltyLCBAcquisitor → get_acquisition_calculator() → ParallelRelaxPostprocess`.
4. Wrote `j_novel.sh` — PJM batch script (64-core, agox_v2, one seed per job,
   `SEED` env override). Fixed the run-7 env mismatch: `gpaw_env` → `agox_v2`.
5. Wrote docs: `README.md`, `README.AI.md`, `LOG.md` (this file), `TUTORIAL.md`.

### Results
- `py_compile main.py novelty_lcb/*.py scripts/*.py` → **ALL COMPILE OK** (agox_v2).
- `smoke_test_serialization.py` → **RESULT: PASS**:
  - `pickle.dumps(calc)` OK (no sqlite in graph)
  - Ray serializability report clean (0 FAIL)
  - `ParallelRelaxPostprocess(model=calc)` constructed OK
  - end-to-end 2-iteration AGOX run with EMT completed, **no** Ray serialization error.
- **Grounding:** the run-7 crash root cause is verified fixed at the code level.

### Decisions & reasoning
- **Reuse the run-7 package** rather than rewriting: it already contains the fix and
  the physics is proven; rewriting risks reintroducing Bugs A/B/C.
- **Faithful repair** (not improvement): user explicitly chose same stack, get it
  working. Downstream NS/novel-filter hooks deferred.
- **One seed per PJM job**: the sampler/pool is effectively per-seed; scale-out by
  array submission (matches the run-8 multiseed guide's "many independent jobs").

### Open items / next steps
- [ ] Calibrate the Novelty-LCB energy window from a short standard-LCB run
      (target = band centre, ΔE ≈ 0.5–1.0 eV). Placeholder `0.0 / 1.0` is a TODO.
- [ ] Launch the heavy Fe/MgO search on HPC (pjsub, one seed per job).
- [ ] After calibration + runs: downstream analysis (nested sampling / novel filter).

### Time
Recon + scaffold + validation ≈ 25 min.

---

## 2026-08-22 — Session 1b: Add governing rule file (AGENTS.md)

### Goal (user-confirmed via clarify)
Write a persistent rule file in this project that any AI agent will read and work
according to. User provided the AI-Agent Project Workflow as the governing process.
Confirmed: filename **AGENTS.md**; scope = the workflow rule only (README human +
AI, LOG, TUTORIAL); it **references** (does not replace) `README.AI.md` and `LOG.md`.

### Actions taken
- Created `AGENTS.md` — governing rules for AI agents:
  - Core principle: three deliverables must coexist (README human + AI, Log, Tutorial).
  - Sections for each deliverable, mapped to this project's actual files
    (`README.md`, `README.AI.md`, `LOG.md` + `transcript.log`, `TUTORIAL.md`).
  - Rules of operation: clarify-before-every-step, ground in repo, keep deliverables
    current, append-only log, verify before claiming done, code/docs tracked vs
    regenerable data, no commit without asking.
  - Invariant environment block + skill pointers.
  - Relationship to `ai-agent-reminder-system`.

### Results
- `AGENTS.md` written (3.9 KB). Verified on disk.

### Decisions & reasoning
- **AGENTS.md** is the conventional filename AI agents auto-read, so a future agent
  will discover the rules without being told.
- Kept it as the *governing process* and left `README.AI.md` as the *machine spec*
  and `LOG.md` as the *action log* — three complementary, single-purpose files
  rather than one monolithic rule dump (user's explicit choice).

### Open items / next steps
- Unchanged from Session 1: calibrate energy window, then launch heavy HPC search.

### Time
~5 min.

---

## 2026-08-22 — Session 1c: Git commit rule + initial commit

### Goal (user-confirmed via clarify)
1. Add a git-commit rule to `AGENTS.md`: commit after every change.
2. Make the initial git commit for the whole `a_lcbnovel` scaffold.

Confirmed: the rule reads "commit after every change, but confirm with the owner first
when it's a milestone or has side effects"; the initial commit is ONE commit for the
whole scaffold (code + docs + AGENTS.md), message
`a_lcbnovel: Novelty-LCB Fe/MgO scaffold (repair of run 7) + governing AGENTS.md`.

### Actions taken
- Edited `AGENTS.md`: replaced the old "Do not commit without asking" rule with a
  new "Commit after every change" rule (confirm with owner for milestones/side
  effects), and renumbered the following rules.
- (This file) appended this Session 1c entry.
- Staged and committed the whole `a_lcbnovel/` directory as one commit.

### Results
- `AGENTS.md` now mandates committing every change.
- Initial commit created (see `git log -1`).

### Decisions & reasoning
- **One commit for the whole scaffold** (user's choice): the scaffold is a single
  coherent deliverable, so splitting code/docs would add noise without value.
- **Keep asking on milestones**: a blanket auto-commit could bury a large or
  side-effecting change without review; confirming at milestones keeps the owner in
  control while still ensuring routine changes are committed promptly.

### Open items / next steps
- Unchanged: calibrate energy window, then launch heavy HPC search.

### Time
~5 min.

---

## 2026-08-22 — Session 1d: Correction — HPC env + pjsub usage

### Goal (user correction)
1. Use **`gpaw_env`** for the HPC pjsub heavy run (not `agox_v2`).
2. Use **`pjsub j_novel.sh`** only — do **not** use `pjsub -x SEED=5 j_novel.sh`.
3. Remove the explanatory comment block from `j_novel.sh` (no long notes in the script).

Note: this **reverses** a decision recorded in Session 1 (which switched the batch
script to `agox_v2` and added a comment about the env mismatch). This entry is the
current, correct behaviour.

### Actions taken
- Rewrote `j_novel.sh`: no top comment block; `conda activate gpaw_env`; seed set by
  editing `SEED=3` at the top (hand-edited, run as `pjsub j_novel.sh`); `N_ITERATIONS=100`.
- Updated `README.md`: usage + decisions-table compute row (`gpaw_env`, `pjsub j_novel.sh`,
  seed via editing `SEED=`).
- Updated `README.AI.md`: pjsub usage + dependencies (local `agox_v2` vs HPC `gpaw_env`).
- Updated `TUTORIAL.md`: Step 4 (pjsub + seed editing + gpaw_env), pitfall #4 (env split),
  prerequisites (HPC uses `gpaw_env`).
- `AGENTS.md`: local env note unchanged (correct — agox_v2 is the local dev/test env).

### Results
- All docs now consistent: local dev/test = `agox_v2`; HPC pjsub = `gpaw_env`;
  launch via `pjsub j_novel.sh` with seed hand-edited in the script.

### Decisions & reasoning
- Keep the **local** smoke test / compile on `agox_v2` (that's this machine's env);
  only the **HPC** batch run uses `gpaw_env`. The two serve different purposes.
- Follow the owner's preference: no `-x` flag, no verbose comment block in `.sh`.

### Open items / next steps
- Unchanged: calibrate energy window, then launch heavy HPC search.

### Time
~10 min.

---

## 2026-08-22 — Session 1e: Explain Novelty-LCB method in README.md

### Goal (user request)
Owner added a Note block in `README.md` asking three conceptual questions about the
method: (1) what Novelty(x) is and whether it uses the 720-dim descriptor or PCA,
(2) what σ(x) is and how it is computed, (3) how a candidate is picked from a(x) and
how this compares to regular LCB in GOFEE. Owner asked to replace the Note with an
explanation. Confirmed via clarify: replace the Note block with a proper
"How the Novelty-LCB works" section in README.md, concise-but-complete, grounded in code.

### Actions taken
- Replaced the raw Note block (lines 18-23) in `README.md` with a new
  "## How the Novelty-LCB works" section answering all three questions, each citing
  the relevant code path in `novelty_lcb/acquisitor.py`:
  - Q1: Novelty(x) = min Euclidean distance in descriptor space; computed with the
    FULL 720-dim Fingerprint (no PCA); `descriptor.get_features(cand).ravel()` +
    `np.linalg.norm(db_feats - cand_feat, axis=1)`; empty DB => novelty 0.
  - Q2: σ(x) = GPR predictive std from `model.predict_energy_and_uncertainty`; kernel
    posterior uncertainty vs training points in 720-dim space.
  - Q3: AGOX sorts ascending, so code returns `-a(x)`; largest true a(x) picked first;
    out-of-window => +inf never selected; candidates pre-relaxed on LCB surface
    `E - kappa*sigma` (novelty has no force), then evaluated by GPAW.
  - Comparison: regular LCB = `mu - kappa*sigma` minimized (energy-exploit/explore);
    Novelty-LCB = `sigma + lambda*Novelty` maximized inside an energy window
    (diversity-focused); both share the LCB relaxation surface + GPR/Fingerprint stack.

### Results
- README.md now has a self-contained, code-grounded explanation of the method.
- Verified the section reads correctly and the Note block is gone.

### Decisions & reasoning
- Grounded every claim in the actual `acquisitor.py` implementation (not generic
  descriptions) so the README stays truthful and traceable to the code.
- Kept it in README.md (owner's choice) so a human reader gets the explanation in
  context without jumping to a separate doc.

### Open items / next steps
- Unchanged: calibrate energy window, then launch heavy HPC search.

### Time
~10 min.

---

## 2026-08-22 — Session 1f: Explain KMeansSampler in README.md

### Goal (user request)
Owner added a Note in `README.md` (after Q2) asking how the KMeansSampler is actually
used in the script, whether there is an energy criterion, and how the number of
clusters is decided. Confirmed via clarify: add a new subsection right after Q2 inside
the "How the Novelty-LCB works" section, concise-but-complete with key code lines.

### Actions taken
- Read AGOX source `samplers/kmeans.py` + `main.py` wiring to ground the answer.
- Replaced the Note block with a new "### How the KMeansSampler is used" subsection:
  - Role: diversity-preserving down-selection BETWEEN the collector and the acquisitor,
    over already-evaluated (relaxed + DFT-scored) structures, not raw candidates.
  - In main.py: `KMeansSampler(descriptor, database, sample_size=SAMPLE_SIZE)` (SAMPLE_SIZE=20).
  - Mechanism: sklearn KMeans on 720-dim features; keep lowest-energy member per cluster.
  - Energy criterion: `max_energy=5` eV filter (KMeansEnergyFilter) + lowest-energy per cluster.
  - Number of clusters: automatic, `n_clusters = 1 + min(sample_size-1, floor(N/5))`,
    capped at sample_size; grows with DB size. No manual cluster count.

### Results
- README.md now explains the KMeansSampler, grounded in the actual AGOX source.
- Note block removed; new subsection inserted in the right place (after Q2, before Q3).

### Decisions & reasoning
- Grounded all claims in `agox/samplers/kmeans.py` and `main.py` so the README is
  truthful and traceable.
- Matched the existing Q1/Q2/Q3 style and placement (owner's choice).

### Open items / next steps
- Unchanged: calibrate energy window, then launch heavy HPC search.

### Time
~10 min.

---

## 2026-08-22 — Session 1g: Assessment for local-minimum sampling in README.md

### Goal (user request)
Owner added a Note in `README.md` (inside the KMeansSampler section) asking, in the
context of **local-minimum sampling**: what "5 eV above the lowest-energy structure"
means and how it affects the database; whether the current Novelty-LCB works for
local-minimum sampling; what is wrong / right / improvable. Confirmed via clarify:
replace the Note with an in-place subsection and give a **deep dive** (full worked
analysis of the local-minimum vs global-search mismatch, with references to the
`_run/8_nested_sampling` and `_run/9_novelFilter` downstream tools).

### Actions taken
- Replaced the Note block with a new "### Assessment for local-minimum sampling"
  subsection inside the KMeansSampler section covering:
  - DB effect of max_energy=5 filter: does NOT delete from DB; only gates which
    structures are eligible for sampling (excludes >5 eV above running lowest).
  - Fit of Novelty-LCB: partly — the novelty term aids basin diversity.
  - What is right: diversity, KMeans one-rep-per-basin, downstream tools
    (9_novelFilter dedup + 8_nested_sampling) already provide local-minimum stats.
  - What is wrong/limited: global-search heuristic not a minima sampler; uncalibrated
    window; novelty saturates as DB grows; DB not a clean minima set; novelty vs raw DB
    (near-duplicates) not vs a representative set.
  - Improvements: calibrate window; compare novelty against deduplicated set; separate
    "discover basins" (AGOX) from "weight basins" (NS/novel-filter); optional basin
    bookkeeping at acquisition time.

### Results
- README.md now has a grounded assessment for local-minimum sampling, referencing the
  sibling `_run/8` and `_run/9` pipelines.
- Note block removed; subsection placed in the right spot.

### Decisions & reasoning
- Deep-dive chosen by owner; grounded in `agox/samplers/kmeans.py`, `main.py`, and the
  actual downstream tools so the critique is concrete, not generic.
- Framed the recommended workflow as AGOX-to-discover + novel-filter/nested-sampling
  to-weight, matching the division of labour across this project's sibling runs.

### Open items / next steps
- Unchanged: calibrate energy window, then launch heavy HPC search.

### Time
~10 min.

---

## 2026-08-22 — Session 1h: Calibrate energy window from LCB-only dataset

### Goal (user request)
Owner added a Note in `README.md` (inside the local-minimum assessment): they added a
previous LCB-only run of the same system at `./dataset`, and asked how to decide
`target_energy` from it. Confirmed via clarify: recommend **band-centre strategy**
(target ≈ −411.6 eV, ΔE ≈ 25 eV, broad low-selectivity) and apply it to BOTH the
README assessment and main.py.

### Actions taken
- Inspected `./dataset` (13 seeds 3-15 + stop_16/trash). Wrote a temp energy-stats
  script, ran it under `agox_v2`:
  - 1297 structures, Mg25O25Fe25 (75 atoms), composition uniform.
  - E_min −436.91, E_max −386.29, mean −424.17, median −428.93.
  - p1..p99 ≈ [−436.8, −391.6]; band centre ≈ −411.6 eV.
- Updated `main.py`: `NOVELTY_TARGET_ENERGY = −411.6`, `NOVELTY_DELTA_E = 25.0`
  (was placeholder 0.0 / 1.0), with a comment citing the dataset source.
- Updated `README.md` assessment: point #2 rewritten ("window is on absolute energy"),
  added "How to set target_energy (from the LCB-only dataset)" with the stats + the
  chosen window; updated "What can be improved"; updated decisions-table Energy-window
  row; updated Status (calibration done; HPC launch still open).
- Updated `TUTORIAL.md` Step 5 to reflect calibration is done from the dataset.
- Updated `README.AI.md` pitfall #3 (absolute-energy window, calibrated values).
- Kept the energy-stats helper as a permanent utility `energy_stats.py` (used to
  re-verify calibration); removed the temp underscore script.

### Results
- Energy window calibrated and written into main.py; all docs consistent.
- Verified `main.py` compiles (py_compile OK).

### Decisions & reasoning
- **Band-centre, wide ΔE (25 eV)** chosen by owner: non-restrictive window so novelty
  + uncertainty drive the search; covers ~all of p1..p99. (Narrow low-band option
  documented for stricter local-minimum targeting.)
- Kept the window definition fact (absolute E, not relative) explicit — this is the
  key reason target_energy must be a real energy, not 0.

### Open items / next steps
- [ ] Launch the heavy Fe/MgO search on HPC (pjsub j_novel.sh) — still the main pending
      science step.
- [ ] (Optional) verify `_run/8_nested_sampling` / `_run/9_novelFilter` integration
      with this project's DB output.

### Time
~15 min.

---

## 2026-08-22 — Session 1i: Add energy_stats.py tutorial to TUTORIAL.md

### Goal (user request)
Include a tutorial for `energy_stats.py` in `TUTORIAL.md`. Confirmed via clarify: add
a dedicated subsection inside Step 5 ("Using energy_stats.py") with the exact run
command, expected output, and how to interpret the numbers to set the window.

### Actions taken
- Added "### Using `energy_stats.py`" subsection inside Step 5:
  - Purpose of the script (reads ./dataset DBs, prints energy distribution).
  - Exact run command (`/home/think/miniconda3/envs/agox_v2/bin/python energy_stats.py`).
  - Expected output block (the actual 1297-structure stats: min/max/mean/median +
    p1..p99).
  - How to set the window: broad (target ≈ −411.6, ΔE = 25) vs narrow low-energy
    (target ≈ p25 −432, ΔE ≈ 3); write into main.py; re-run on dataset/system change.
- Fixed stale TUTORIAL pitfall #3 (was "Uncalibrated window placeholder 0.0/1.0") to
  reflect the calibrated absolute-energy window.

### Results
- TUTORIAL.md now documents energy_stats.py end-to-end.
- Pitfall #3 consistent with the calibrated values.

### Decisions & reasoning
- Kept the tutorial inside Step 5 (owner's choice) so the calibration + its verification
  tool live together.
- Included the actual expected output so a reader can confirm a correct run at a glance.

### Open items / next steps
- Unchanged: launch heavy HPC search; (optional) verify downstream integration.

### Time
~5 min.

---

## 2026-08-22 — Session 1j: Explain 'target_energy = 0' in README.md

### Goal (user request)
Owner added a Note in `README.md` (after the calibration block) asking what happens
if the energy window is set to 0 — does it search around energy 0? Confirmed via
clarify: replace the Note in-place with a concise "What if target_energy = 0?"
subsection (absolute-energy point, code behaviour with E vs 0, physical meaning of 0).

### Actions taken
- Replaced the Note with a "### What if `target_energy = 0`?" subsection:
  - The window [target - dE, target + dE] is compared against the GPR's ABSOLUTE
    predicted total energy E (code tests E < lo or E > hi).
  - Fe/MgO total energies are ~-400 eV (band [-436.9, -386.3], never near 0).
  - With target=0, dE=1.0 the window [-1, +1] excludes every candidate (+inf in
    sorting space) -> the search stalls.
  - Wider dE (e.g. 400) would overlap the band but is roundabout.
  - 0-eV only makes sense for RELATIVE energies; this acquisitor uses absolute total
    energy, so target_energy must be a real band energy (hence the calibration).

### Results
- README.md now explains the target_energy=0 pitfall, grounded in the code's
  absolute-energy window logic.

### Decisions & reasoning
- Grounded in the acquisitor's actual comparison (absolute predicted E) so the
  warning is precise, not generic.
- Kept it concise and placed in the calibration context (owner's choice).

### Open items / next steps
- Unchanged: launch heavy HPC search; (optional) verify downstream integration.

### Time
~5 min.

---

## 2026-08-22 — Session 1k: Explain 'continue from previous DB' in README.md

### Goal (user request)
Owner added a Note in `README.md` asking whether AGOX checks/continues from a
previous DB on re-run. Confirmed via clarify: replace the Note in-place with a
concise "Does AGOX continue from a previous database?" subsection.

### Actions taken
- Read AGOX source `databases/database.py` to ground the answer:
  - `__init__(initialize=False, call_initialize=True)` default; `os.remove` only if
    `initialize=True`.
  - `_initialize()` checks if the `structures` table exists; does not recreate if
    present; `_init_storage()` loads existing rows into memory.
- Replaced the Note with a subsection answering "yes, it continues", explaining:
  - initialize=False => existing DB not deleted on open.
  - _initialize restores stored candidates (novelty vs get_all_candidates).
  - Implications: re-run same seed resumes/extends the DB; to restart fresh you must
    delete the db file (or use a new path) — AGOX won't clear it by default.

### Results
- README.md now explains the resume-from-existing-DB behavior, grounded in database.py.

### Decisions & reasoning
- Grounded in the actual AGOX Database.__init__/_initialize source so the answer is
  precise (resume vs restart semantics).
- Kept it concise and in place (owner's choice).

### Open items / next steps
- Unchanged: launch heavy HPC search; (optional) verify downstream integration.

### Time
~5 min.

---

## 2026-08-22 — Session 1l: Auto global-minimum energy window (remove regular-LCB-first step)

### Goal (user request)
Previously the Novelty-LCB window needed a manually-set `target_energy`, requiring a
regular-LCB run first to calibrate the band. User asked to make a parameter so the
target energy is **automatically the global minimum** of the current DB, with control
over how much energy ABOVE that minimum to search.

### Confirmed design (via clarify)
- **Backward compatible:** add `energy_above_min` param; when set, use auto global-min
  mode; when `None`, fall back to centered `target_energy ± delta_E`.
- **Cap only the top:** window = `(-inf, E_min + X]`; allow E < E_min so a new lower
  minimum can still be found.
- **Live global min:** recomputed from the current DB each acquisition round.
- **One parameter:** `energy_above_min` (X, eV above the live min).

### Actions taken (code)
- `novelty_lcb/acquisitor.py`:
  - `__init__`: added `energy_above_min: Optional[float] = None`; `target_energy` now
    defaults to `None` (backward compatible). Updated docstring.
  - Added `_global_min_energy()` helper — live lowest finite DFT energy in the DB.
  - `calculate_acquisition_function`: window logic now branches:
    auto mode (`(-inf, E_min+X]`, no cap when DB empty), centered mode
    (`target ± delta_E`), or no constraint. `in_window` meta-info updated.
- `main.py`: replaced `NOVELTY_TARGET_ENERGY`/`NOVELTY_DELTA_E` with
  `NOVELTY_ENERGY_ABOVE_MIN = 5.0`; acquisitor wired with `energy_above_min=...`.

### Validation
- `py_compile` main.py + novelty_lcb/*.py: OK.
- Added `test_window_logic.py` (isolated, no Ray/AGOX): 8/8 PASS
  (auto cap, allow-below-min, empty-DB no-cap, live E_min tracking, centered
  backward-compat, no-constraint).
- NOTE: `smoke_test_serialization.py` could not complete this session — it fails on
  the documented Ray `ActorUnavailableError` under node memory pressure (1.1 GB free,
  swap full). This is environmental, not caused by this change; the isolated window
  test validates the code change directly.

### Decisions & reasoning
- Backward compatible + additive keeps the proven centered mode available while making
  the new auto mode the default path (removes the two-step regular-LCB-first cost).
- Cap-only-top is the right semantics for "search X eV above the global minimum": it
  still lets the search improve the global minimum.

### Open items / next steps
- Re-run `smoke_test_serialization.py` when the node has free memory (verify the full
  AGOX path still constructs).
- Launch the heavy Fe/MgO search on HPC (pjsub j_novel.sh) with the auto window.

### Time
~25 min.

---

## 2026-08-22 — Session 1m: Per-atom energy window mode (energy_above_min in eV/atom)

### Goal (user request)
Add a parameter to use energy **per atom** for the energy-above-global-min window,
so choosing the window height is easy on the scale of 1-2 eV/atom.

### Confirmed design (via clarify)
- **Boolean flag** `per_atom` (default False) — backward compatible; total-eV stays
  default.
- **Strict per-atom**: divide BOTH the candidate predicted E and the global min E_min
  by N, then compare `E/N <= E_min/N + X`.
- **Full scope**: acquisitor.py + main.py + docs + per-atom test cases + commit.

### Actions taken (code)
- `novelty_lcb/acquisitor.py`:
  - `__init__`: added `per_atom: bool = False`; updated docstring.
  - Added `_n_atoms()` helper (atom count from DB candidates; falls back to 1).
  - Window logic: when `energy_above_min` set and `per_atom=True`, compare
    `(E/N) <= (E_min/N) + X` (X in eV/atom); otherwise total-eV as before.
- `main.py`: added `NOVELTY_ENERGY_PER_ATOM = True` (default on for this project) and
  set `NOVELTY_ENERGY_ABOVE_MIN = 1.0` eV/atom; wired `per_atom=NOVELTY_ENERGY_PER_ATOM`.

### Validation
- `py_compile` main.py + novelty_lcb/acquisitor.py: OK.
- `test_window_logic.py` now 16/16 PASS, incl. per-atom cases:
  - `_n_atoms` returns 75 from DB.
  - per-atom cap: E/N above cap excluded, E/N below cap included, below-global-min allowed.
  - equivalence: per_atom X (1.0 eV/atom) == total X (75 eV) give identical accept/reject
    for fixed N — confirms the math.
- `smoke_test_serialization.py` still cannot run this session (Ray ActorUnavailableError,
  node memory pressure — environmental).

### Decisions & reasoning
- Per-atom makes the window size-independent (0.5-2 eV/atom), which is easier to reason
  about and transferable across system sizes.
- Default flipped to per_atom=True for this project (fixed 75-atom composition), with a
  clear per-atom value (1.0 eV/atom). Total-eV mode remains available.
- For fixed N, per-atom and total modes are mathematically equivalent (verified by the
  equivalence test), so enabling per_atom by default changes only the unit of X.

### Open items / next steps
- Re-run `smoke_test_serialization.py` when memory frees.
- Launch the heavy Fe/MgO search on HPC with the per-atom auto window.

### Time
~20 min.

---

## 2026-08-22 — Session 1n: Add main_benchmark.py (Ni8/Au EMT, regular vs Novelty-LCB auto window)

### Goal (user request)
Create `main_benchmark.py` comparing regular LCB vs Novelty-LCB (with the new auto
global-minimum window) on the Ni8 / Au(4,4,2) fcc100 surface using EMT.

### Confirmed design (via clarify)
- Shape: same as run 6 — SEED_LIST=[41,101,201,301,401], N_ITERATIONS=30, per-seed db,
  aggregate + plots.
- Metrics: reuse run 6 verbatim (distinct configs, best E, energy range, duplicates,
  discovery curves, stats, plots).
- Contrast: same seeds + full stack, only the acquisitor differs.
- Package: import the local `novelty_lcb` (has energy_above_min/per_atom).
- Novelty window: `energy_above_min = 0.1` eV/atom, `per_atom=True`
  (40-atom Au+Ni cell -> cap 4 eV above global min). Outputs to `benchmark_results/`.

### Actions taken
- Wrote `main_benchmark.py` modeled on `_run/6_lcbnovel_benchmark/run.py`:
  - build_system/build_stack (regular vs novelty), get_distinct_configurations,
    run_single, compute_discovery_curve, aggregate + stats + JSON + plots.
  - Novelty-LCB wired with `energy_above_min=NOVELTY_ENERGY_ABOVE_MIN`,
    `per_atom=NOVELTY_ENERGY_PER_ATOM`.
  - Added `USE_RAY = False` config for the GPR (avoid per-CPU Ray actors).
- `py_compile` OK.
- Smoke: build_stack for both acquisitors reaches the parallel pool — but a full run
  cannot complete on this node (memory pressure -> Ray ActorUnavailableError, because
  ParallelCollector/ParallelRelaxPostprocess use Ray pools). This is environmental and
  inherent to AGOX Parallel components; the benchmark is intended to run on the HPC
  cluster (64-core, ample RAM). USE_RAY + a JSON NOTE document this.

### Validation
- Compile OK.
- Window logic for the auto global-min per-atom path is already covered by
  `test_window_logic.py` (16/16 PASS).
- Full benchmark execution deferred to a node with enough RAM (HPC).

### Decisions & reasoning
- Reused run-6 metrics/structure to keep the comparison directly comparable.
- Chose 0.1 eV/atom for a meaningful 4 eV cap on the 40-atom cell (documented).
- USE_RAY=False reduces actor count but does not fully remove Ray (parallel components
  need the pool); note added that the benchmark needs adequate RAM.

### Open items / next steps
- Run `main_benchmark.py` on the HPC cluster (or a RAM-rich node).
- (Optional) add a benchmark_results/ entry to .gitignore (PNG/JSON are regenerable).
- Launch the heavy Fe/MgO search with the per-atom auto window.

### Time
~20 min.

---

## 2026-08-22 — Session 1o: Add job.sh (HPC batch for the EMT benchmark)

### Goal (user request)
Prepare an HPC batch script for `main_benchmark.py`.

### Confirmed design (via clarify)
- **Name:** `job.sh` at a_lcbnovel root, same PJM style as `j_novel.sh`.
- **Env:** `gpaw_env` (user's choice). NOTE: benchmark uses EMT+AGOX (no GPAW); the
  script documents the assumption that the HPC's gpaw_env has AGOX/ASE/EMT. On this
  machine there is no `gpaw_env` (only agox, agox_v2, flapw-build, pymat_xrd), so the
  script targets the HPC.
- **Structure:** single job, all seeds x 2 acquisitors, N_ITERATIONS=30 (fast EMT).
- **Cores:** 64 (same as j_novel.sh). Elapse 02:00:00.

### Actions taken
- Wrote `job.sh` (PJM batch): 64-core, gpaw_env, `OMP_NUM_THREADS=1 python
  ./main_benchmark.py`, echo of start/end times. Comment notes the AGOX env assumption
  and fallback to agox_v2 if gpaw_env lacks AGOX.

### Validation
- No HPC submission possible from this node. Script follows the same structure as the
  working `j_novel.sh`. Shell syntax is simple (no executable to compile).

### Decisions & reasoning
- Kept gpaw_env per user choice, with a clear comment documenting the AGOX assumption
  (the benchmark needs AGOX/EMT, not GPAW).
- Single job (all seeds) because EMT is fast; 64 cores for the AGOX parallel pool.

### Open items / next steps
- Submit `pjsub job.sh` on HPC to run the benchmark.
- Launch the heavy Fe/MgO search (j_novel.sh) with the per-atom auto window.

### Time
~5 min.

---

## 2026-08-22 — Session 1p: Document the benchmark in README/TUTORIAL/README.AI

### Goal (user request)
Add a note about the EMT benchmark (`main_benchmark.py` + `job.sh`) to the README and
TUTORIAL. Confirmed via clarify:
- README.md: benchmark item in "How to use it" + a decisions-table row.
- TUTORIAL.md: new top-level "Step 6 — EMT benchmark (optional)"; analysis step
  renumbered to Step 7.
- README.AI.md: mention in layout + entry points + a pitfall (consistency).
- Include the RAM/Ray caveat (benchmark needs a RAM-rich node / HPC for the AGOX pool).

### Actions taken
- README.md: added benchmark commands to "How to use it" (local + `pjsub job.sh`) and
  a "Benchmark" decisions-table row.
- TUTORIAL.md: added Step 6 (EMT benchmark) with commands, metrics, the auto-window
  values (0.1 eV/atom, 40-atom cell -> ~4 eV), and a RAM/Ray caveat; renumbered the
  downstream-analysis step to Step 7.
- README.AI.md: added `main_benchmark.py`, `test_window_logic.py`, `energy_stats.py`,
  `job.sh`, `benchmark_results/` to the file layout; benchmark commands to entry
  points; pitfall #6 (benchmark needs RAM for the Ray pool).

### Results
- Benchmark now documented consistently across README.md, TUTORIAL.md, README.AI.md.
- No stale step references in README (analysis already referenced without a step number).

### Decisions & reasoning
- Kept the note concise and placed near the existing usage/steps so it reads in context.
- Renumbered the analysis step to Step 7 to keep the tutorial sequential.

### Open items / next steps
- Submit `pjsub job.sh` on HPC to run the benchmark.
- Launch the heavy Fe/MgO search (j_novel.sh).

### Time
~10 min.

---

## 2026-08-22 — Session 1q: Rename job.sh -> j_benchmark.sh

### Goal (user request)
Rename the benchmark batch script from `job.sh` to `j_benchmark.sh`.

### Actions taken
- `git mv job.sh j_benchmark.sh` (preserves history).
- Updated the script's internal header comment (`pjsub j_benchmark.sh`).
- Updated all live-doc references:
  - README.md: `pjsub j_benchmark.sh` + decisions-table row.
  - TUTORIAL.md: `pjsub j_benchmark.sh`.
  - README.AI.md: file-layout line, entry-point command, pitfall #6.
  - LOG.md historical entries keep the old name `job.sh` (append-only — this entry
    records the rename).

### Results
- No `job.sh` remains in live docs; `j_benchmark.sh` is the sole benchmark batch script.
- git detects the rename (R).

### Decisions & reasoning
- Kept LOG.md history unchanged (append-only rule); documented the rename here.
- Used `git mv` so the file's history is preserved.

### Open items / next steps
- Submit `pjsub j_benchmark.sh` on HPC to run the benchmark.
- Launch the heavy Fe/MgO search (j_novel.sh).

### Time
~5 min.

---

## 2026-08-22 — Session 1r: Add kappa x novelty_weight sweep benchmark

### Goal (user request)
Create a new benchmark (new .py + .sh) studying the impact of kappa and novelty_weight,
on the same system as main_benchmark.py (Ni8/Au(4,4,2) fcc100, EMT).

### Confirmed design (via clarify)
- Sweep: full grid kappa in [0.5,1.0,2.0,4.0] x novelty_weight in [0.0,0.5,1.0,1.5,2.0]
  = 20 combos, Novelty-LCB only.
- 1 seed per combo (seed 41), N_ITERATIONS=30.
- Metrics: distinct configs, best E, duplicates, discovery curves + heatmaps/curves
  vs kappa & novelty_weight.

### Actions taken
- Wrote `main_benchmark_sweep.py`:
  - Reuses main_benchmark.py helpers (build_system, build_stack, run_single,
    compute_discovery_curve) so the system is identical.
  - run_combo() overrides mb.KAPPA / mb.NOVELTY_WEIGHT / window / OUTDIR, runs one
    Novelty-LCB search, restores originals (try/finally).
  - Outputs to benchmark_results/sweep_kappa_lambda/: sweep_results.json,
    sweep_heatmaps.png (3 heatmaps), sweep_curves.png (per-kappa lines), 
    sweep_discovery.png (all discovery curves).
  - 1 fixed seed per combo.
- Wrote `j_benchmark_sweep.sh` (PJM batch, gpaw_env, 64-core, elapse 02:00:00).

### Validation
- py_compile OK.
- Import sanity: 20 combos, correct grid, reuses main_benchmark helpers, OUTDIR correct.
- Full execution deferred to HPC (needs the AGOX Ray pool; same RAM caveat as
  main_benchmark).

### Decisions & reasoning
- Reused main_benchmark helpers for identical system/metrics (minimal duplication).
- Grid sweep (not one-at-a-time) to see kappa/lambda interactions.
- 1 seed per combo for speed (20 combos).

### Open items / next steps
- Submit `pjsub j_benchmark_sweep.sh` on HPC to run the sweep.
- (Docs) optionally add the sweep to README/README.AI/TUTORIAL.
- Launch the heavy Fe/MgO search (j_novel.sh).

### Time
~20 min.

---

## 2026-08-22 — Session 1s: Document the sweep benchmark in README/README.AI/TUTORIAL

### Goal (user request)
Add a note about the kappa x novelty_weight sweep benchmark to the README and TUTORIAL.
Confirmed via clarify:
- README.md: sweep item in "How to use it" (step 5) + a decisions-table row.
- TUTORIAL.md: sub-block within Step 6 (after the main benchmark).
- README.AI.md: file-layout + entry-point commands (consistency).

### Actions taken
- README.md: added step 5 (sweep commands, local + `pjsub j_benchmark_sweep.sh`) and a
  "Sweep benchmark" decisions-table row.
- TUTORIAL.md: added "### Kappa x novelty_weight sweep (optional)" inside Step 6 with
  the grid, commands, outputs, and a RAM/Ray caveat.
- README.AI.md: added `main_benchmark_sweep.py` + `j_benchmark_sweep.sh` to the file
  layout and the entry-point command block.

### Results
- Sweep benchmark now documented consistently across README.md, TUTORIAL.md, README.AI.md.

### Decisions & reasoning
- Kept the sweep as a sub-block of Step 6 (not a new top-level step) so the two
  benchmarks live together (owner's choice).
- Matched the existing benchmark note style.

### Open items / next steps
- Submit `pjsub j_benchmark_sweep.sh` on HPC to run the sweep.
- Launch the heavy Fe/MgO search (j_novel.sh).

### Time
~10 min.

---

## 2026-08-25 — Session: Introduce `_runs/` and `_analysist/` into the docs

### Goal (user request)
User added `_runs/` (self-contained run dirs for HPC runs + benchmarks) and
`_analysist/` (analysed results) to the project. Asked Calyx to introduce these two
dirs into the project note (README.md), the tutorials (TUTORIAL.md), and the AGENTS
note (AGENTS.md), clarifying each step.

### Clarify (confirmed)
- Run naming: `<NN>_<descriptor>` (running index + descriptive suffix, e.g.
  `4_mgofe_Seed3_Iter900`, `73_novel_benchEMT`).
- Run-doc policy: HPC per-seed Fe/MgO runs are **bare code dirs** (j_*.sh + main.py +
  scripts/ + novelty_lcb/ + regenerable output, no per-run docs); standalone
  benchmarks (e.g. 73_novel_benchEMT) carry the full doc trio in their own dir.
- Trailing-space run dir `3_mgofe_Seed3_Iter700 ` → **rename** via git mv (drop the
  space), update git tracking.
- Defaults taken for the two unanswered questions: edit all four docs (README.md,
  README.AI.md, TUTORIAL.md, AGENTS.md) for consistency; document the expected
  `_analysist/` layout (0_analy/, 1_result/, main_analyst.ipynb, main_test.ipynb).

### Actions taken
1. `git mv` renamed `_runs/3_mgofe_Seed3_Iter700 ` → `_runs/3_mgofe_Seed3_Iter700`
   (all 13 tracked files; removes the trailing-space path hazard).
2. AGENTS.md: added §3a "Run directories: `_runs/` and `_analysist/`" — layout
   diagram, `<NN>_<descriptor>` naming, bare-vs-full run-doc policy, git-tracking
   rule, and expected `_analysist/` layout.
3. README.AI.md: added `_runs/` (with the 4 existing dirs annotated) and
   `_analysist/` to the file-layout tree + a §2a "`_runs/` and `_analysist/`" note.
4. README.md: added a "Where heavy runs actually live" callout under How-to-use, a
   new "Run directories: `_runs/` and `_analysist/`" section, a decisions-table row
   ("Run organization"), and a Status checkbox.
5. TUTORIAL.md: rewrote Step 4 (launch) to `cd` into `_runs/<NN>_<descriptor>/` and
   `pjsub` its own job script; added Step 4b (analysed results → `_analysist/`);
   added a pointer from Step 6 to `_runs/73_novel_benchEMT`; added pitfalls 7
   (trailing-space run-dir names) and 8 (keep run dirs self-contained); added a
   verification-checklist item.

### Results
- All four docs now consistently describe the `_runs/` / `_analysist/` organisation,
  the naming convention, and the bare-vs-full run-doc policy.
- Trailing-space run dir renamed cleanly via git mv.

### Decisions & reasoning
- Docs kept consistent across the trio + AGENTS.md (the workflow requires all three
  deliverables to agree with the code layout).
- Run-dir naming documented as `<NN>_<descriptor>` so new runs are ordered and
  unambiguous; matched the existing `1/2/3_...` and `73_novel_benchEMT` examples.
- `_analysist/` layout mirrors what the repo-root `.gitignore` already anticipates
  (0_analy/, 1_result/, main_analyst.ipynb, main_test.ipynb).

### Open items / next steps
- (User) add new run dirs under `_runs/` as new HPC runs are launched.
- Submit `pjsub j_benchmark_sweep.sh` on HPC to run the sweep.
- Launch the heavy Fe/MgO search (j_novel.sh).

### Time
~20 min.

---

## 2026-08-25 — Session: Analysis runner for Fe/MgO heavy runs (idx 71, 72) in _analysist

### Goal (user request)
User added results (71-74) to `_analysist/1_result/` and asked Calyx to make an
analysis code like the sibling `/home/think/Desktop/research/_analysist/run_analysis_indices.py`,
copy the necessary py dependencies into `_analysist/` for easy calling, and clarify
each step.

### Clarify (confirmed)
- **Scope:** support indices 71 & 72 only (the Fe/MgO heavy runs), which match the
  reference `seed_*/1_db` layout. Benchmarks 73/74 use a flat `benchmark_results/`
  layout (no `seed_*` dirs) that `process_database` cannot consume; excluded.
- **Deps:** copy only the 3 needed modules into `_analysist/scripts/` —
  `process_database.py`, `plot_structure_landscape.py`, `calculate_relative_energy.py`.
- **Name:** keep `run_analysis_indices.py` (mirror the sibling).
- **DB root:** map idx 71 -> `71_novel_runEWindow/output`, idx 72 ->
  `72_novel_AutoGlob_1eVperAtomAboveGlob/output` (each holds `seed_3/1_db/db_3.db`).
- **Git:** add a project `.gitignore` (ignore `_analysist/0_analy/`,
  `_analysist/1_result/`, `*.db/*.png/*.traj/*.xsf/*.csv/*.out`) and commit only
  code+docs. Update README/README.AI/TUTORIAL. Commit now.

### Actions taken
1. Copied the 3 dependency modules into `_analysist/scripts/`.
2. Wrote `_analysist/run_analysis_indices.py` — mirrors the sibling runner (3-stage
   pipeline: ① `process_database`, ② PCA landscape, ③ Boltzmann probability), scoped
   to GROUPS `novel_lcb_femgo: [71, 72]` with `FOLDER_MAP` pointing each index at its
   `output/` DB root. Added a `--idx` single-index shorthand. Corrected the docstring
   env/paths to this machine (`/home/think/miniconda3/envs/agox_v2`).
3. Verified end-to-end under `agox_v2`: ran idx 71 and idx 72 — all 3 stages
   completed, producing `0_analy/idx_{71,72}/` (`traj_<N>.traj`, `data_<N>.csv`,
   `progression_*.png`, `2_im/conf_space.png`,
   `2_im/binding_probability_vs_temperature.png`). `py_compile` clean.
4. Found the project is part of the **parent** repo (`/home/think/Desktop/research`),
   whose `.gitignore` `_analysist/0_analy/` rules target the parent's `_analysist`,
   not this nested one — so nested `_analysist/0_analy` + `1_result` (and `.traj`)
   were leaking as untracked. Added project-level `.gitignore` to exclude them +
   regenerable types. Verified only `run_analysis_indices.py` + `scripts/*` remain
   trackable under `_analysist`.
5. Updated docs: README.md (`_analysist` section + run instructions), README.AI.md
   (file-layout tree + §2a note + entry-point command), TUTORIAL.md (new Step 4c with
   the git-note about the nested `.gitignore`).

### Results
- `_analysist/run_analysis_indices.py` + `_analysist/scripts/{process_database,
  plot_structure_landscape, calculate_relative_energy}.py` created and verified (idx
  71, 72 both ran clean, real outputs produced).
- Git: analysis code is the only trackable content under `_analysist`; outputs and
  results are gitignored via the new project `.gitignore`.

### Decisions & reasoning
- Scoped to 71/72 because the reference pipeline's stage-1 (`process_database`) needs
  a `seed_*/1_db` layout; the flat benchmark dirs 73/74 don't fit and already have
  their own analysis. (Earlier clarify also confirmed 71/72 only.)
- Kept the runner self-contained (local `scripts/` deps only) so it is callable in
  place without touching the parent `_analysist`.
- Added `--idx` shorthand for convenience; kept all sibling CLI flags (`--e-max`,
  `--normalize-density`, `--skip-probability`, `--indices`).
- Project `.gitignore` added because the parent's `_analysist` rules don't reach this
  nested dir; only code+docs are tracked per the workflow.

### Open items / next steps
- Interpret the produced landscape/probability figures for runs 71 (energy-window)
  vs 72 (auto-global-min) — e.g. how the energy-window mode shapes the explored basin
  distribution vs the auto-global-min mode.
- (Optional) extend the runner to the benchmark dirs (73/74) if a flat-DB stage-1
  aggregator is wanted later.

### Time
~25 min.

---

## 2026-08-25 — Session: Add source-code versioning (__version__) across the project

### Goal (user request)
"Edit the project a_lcbnovel. For all the code, include a version param. Any
changes into the code will also update the code version. The LOG md file will also
track the codes version for every changes. Clarify for every changes."

### Clarify (confirmed)
- **Scope:** version the **source code only** — root `main*.py`, `novelty_lcb/`,
  `scripts/`, test/smoke/energy_stats, and `_analysist/` runner+scripts (20 files).
  Duplicated snapshots under `_runs/1|2|3|73` and `dataset/` are **not** individually
  versioned.
- **Scheme:** per-file module-level `__version__ = "X.Y.Z"` (semver), baseline 1.0.0.
- **Bump:** patch on every edit, minor for API/behavior changes; `LOG.md` records each
  file's old→new version.
- **Manifest:** add a project-level `VERSIONS.md` table listing every file's current
  version.
- **Initial pass:** set all in-scope files to `1.0.0` now and log it.

### Actions taken
1. Surveyed tracked `.py` files (~90) and confirmed the in-scope source set (20 files).
2. Added a module-level `__version__ = "1.0.0"` to each of the 20 in-scope files,
   placed after the shebang/module docstring and **after any `from __future__`
   import** (4 files: `novelty_lcb/{acquisitor,benchmark_helpers,common,utils}.py`).
   Note: `scripts/build_*_stack.py`, `hetero_struct_randomize.py`, `plot_structure.py`
   and `_analysist/scripts/calculate_relative_energy.py` already had a
   **function-local** `__version__` (0.0.1 / 0.2) in HEAD — left those as-is and added
   a proper module-level `1.0.0`.
3. Verified: all 20 compile (`py_compile` OK); `smoke_test_serialization.py` and
   `test_window_logic.py` still PASS (no runtime regression).
4. Created `VERSIONS.md` manifest (single-source table of all 20 files → 1.0.0, plus
   versioning rules and the out-of-scope note).
5. Documented the convention: README.md (versioning note), README.AI.md (§2b +
   VERSIONS.md in the file-layout tree), TUTORIAL.md (pitfall 9 + verification item).

### Results — Code versions (initial baseline, all 1.0.0)
The following files now carry `__version__ = "1.0.0"`:
`main.py`, `main_benchmark.py`, `main_benchmark_sweep.py`, `energy_stats.py`,
`smoke_test_serialization.py`, `test_window_logic.py`,
`novelty_lcb/__init__.py`, `novelty_lcb/acquisitor.py`,
`novelty_lcb/benchmark_helpers.py`, `novelty_lcb/common.py`, `novelty_lcb/utils.py`,
`scripts/build_fe_stack.py`, `scripts/build_heteroStruct.py`,
`scripts/build_mgo_stack.py`, `scripts/hetero_struct_randomize.py`,
`scripts/plot_structure.py`, `_analysist/run_analysis_indices.py`,
`_analysist/scripts/calculate_relative_energy.py`,
`_analysist/scripts/plot_structure_landscape.py`,
`_analysist/scripts/process_database.py`.
(Initial baseline — no prior module-level version to diff against.)

### Decisions & reasoning
- Module-level `__version__` (semver) so each file self-describes its version and can
  be read/imported programmatically; placed after `from __future__` to keep valid
  Python.
- Kept function-local legacy `__version__` markers untouched (they are internal to a
  function, not the module version).
- Scope limited to source (not the duplicated `_runs/`/`dataset/` snapshots) per the
  confirmed decision, to avoid a huge mechanical churn on self-contained copies.
- `VERSIONS.md` added as the single-source manifest so future edits update one table.

### Open items / next steps
- (Process) from now on, any code edit bumps the file's `__version__` (patch; minor
  for API/behavior), updates `VERSIONS.md`, and is recorded in `LOG.md`.
- (User) launch heavy Fe/MgO searches; run the 73/74 benchmarks on HPC.

### Time
~30 min.

---

## 2026-08-25 — Session: Rename project dir 10_lcbnovel -> a_lcbnovel

### Goal (user request)
User renamed the project dir on disk: `/home/think/Desktop/research/_run/10_lcbnovel`
-> `_run/a_lcbnovel`, and the per-seed run dirs under `_runs/`:
`1_mgofe_Seed3_Iter300` -> `a1_...`, `2_mgofe_Seed3_Iter500` -> `a2_...`,
`3_mgofe_Seed3_Iter700` -> `a3_...`. Asked Calyx to handle the rename (clarify each step).

### Clarify (confirmed)
- **Git rename:** stage the rename so git records it as a rename (add deletions + new dir), commit cleanly.
- **Content:** update ALL internal `10_lcbnovel` -> `a_lcbnovel` references across the
  whole project (README/README.AI/TUTORIAL/AGENTS/LOG/VERSIONS + code + `_runs/` +
  `_analysist/` copies), including the gitignored `1_result/` copies.
- **Skills:** update the `_skills/` snapshot references too.
- **Memory:** update my persistent memory note.
- **Commit:** one commit (rename + content updates + LOG entry).

### Actions taken
1. Verified the on-disk rename and git state (old paths deleted, `a_lcbnovel/` untracked).
2. Ran a scripted `10_lcbnovel` -> `a_lcbnovel` replacement across the project source
   (18 files: main.py, smoke_test, AGENTS/README/README.AI/TUTORIAL/LOG/VERSIONS,
   _analysist/run_analysis_indices.py, _runs/a{1,2,3}_*/main.py, _runs/73 docs).
3. Ran the replacement across the gitignored `_analysist/1_result/` copies
   (21 files: 71/72/73/74 docs + code), per the confirmed scope.
4. Ran the replacement across the `_skills/` snapshot (12 files).
5. Updated persistent memory (project path -> _run/a_lcbnovel).
6. Verified no remaining `10_lcbnovel` text references in the project.
7. Appending this LOG entry (with the historical LOG path references updated per the
   confirmed scope — a mechanical path rename, not a rewrite of action history).

### Results
- Rename staged in git as a rename; internal references consistent across project,
  `_analysist` copies, `_skills` snapshot, and memory.

### Decisions & reasoning
- Updated ALL references (not just root docs) so paths in `_runs/` and `_analysist`
  copies don't dangle to a non-existent `10_lcbnovel`.
- Also updated the gitignored `1_result/` copies and `_skills/` snapshot so the whole
  tree is consistent; the `_skills` copy is a snapshot, refreshed here to match.
- One combined commit (rename + content) per the user's choice; LOG append-only rule
  preserved (added a new entry; historical entries' path strings updated).

### Open items / next steps
- (User) launch heavy Fe/MgO searches; run the 73/74 benchmarks on HPC.
- (Optional) refresh the `_skills/` snapshot if any live skill is edited later.

### Time
~20 min.


---

## 2026-08-26 — Session: Per-run README+TUTORIAL + latest-code sync under _runs/

### Goal (user request, confirmed via clarify)
Each `_runs/` dir is self-contained: carries the LATEST versioned package dirs
(`novelty_lcb/`, `scripts/`) from the project root, plus a per-run `README.md` +
`TUTORIAL.md` specific to that run's treatment. Update governance docs (AGENTS,
README.AI, TUTORIAL) and the `agox-novelty-lcb` skill to match.

### Clarify (confirmed)
- **Scope:** a1/a2/a3 per-seed runs get README+TUTORIAL; 73_novel_benchEMT only has
  its packages refreshed (already has full docs).
- **Docs per run:** `README.md` + `TUTORIAL.md` only (not README.AI/LOG — project root
  owns those).
- **Package sync:** copy latest root `novelty_lcb/` + `scripts/` (versioned) into all
  four run dirs; also sync latest root `main.py` into a1/a2/a3 (user chose "update with
  versioning").
- **Per-run doc content:** specific to the treatment — i.e. what differs from the
  sibling runs (seed, N_ITERATIONS).
- **AGENTS.md:** update policy from "bare code dirs, no per-run docs" to "each per-seed
  run carries README+TUTORIAL"; sync README.AI.md layout + root TUTORIAL.
- **Skills:** fix stale `10_lcbnovel` → `a_lcbnovel` refs in `agox-novelty-lcb` and
  refresh the `_skills/` snapshot.

### Actions taken
1. Synced latest versioned `main.py`, `novelty_lcb/`, `scripts/` from project root →
   `_runs/a1_mgofe_Seed3_Iter300/`, `a2_...Iter500/`, `a3_...Iter700/`; refreshed
   `_runs/73_novel_benchEMT/{novelty_lcb,scripts}/`. Verified byte-identical to root
   (all copies now carry `__version__`).
2. Wrote per-run `README.md` + `TUTORIAL.md` for a1/a2/a3, each specific to its
   treatment (seed=3, N_ITERATIONS=300/500/700) with a sibling-difference table.
3. Updated `AGENTS.md`: per-run README+TUTORIAL policy + "keep run copies current"
   sync rule + `_runs/` layout tree.
4. Updated `README.AI.md` §2a layout and root `TUTORIAL.md` pitfall #8.
5. Fixed stale `10_lcbnovel` → `a_lcbnovel` refs in `agox-novelty-lcb` skill
   (SKILL.md + references/auto-window-and-test.md + kappa-lambda-sweep.md) and synced
   the `_skills/research/agox-novelty-lcb/` snapshot.

### Results
- All run-dir code copies match the latest project root (main.py, novelty_lcb/, scripts/).
- Per-run README+TUTORIAL present in a1/a2/a3; 73 packages refreshed.
- Governance docs (AGENTS, README.AI, TUTORIAL) and skill/snapshot consistent.

### Decisions & reasoning
- Per-seed runs remain lightweight (README+TUTORIAL, no README.AI/LOG) so HPC run dirs
  stay focused; the project root remains the single owner of the full doc spec.
- Per-run README/TUTORIAL are specific to the treatment (the iteration budget), since
  main.py is byte-identical across a1/a2/a3 — the docs differentiate the runs by their
  actual differing variable.

### Open items / next steps
- (User) launch heavy Fe/MgO searches (a1/a2/a3 on HPC); run the 73/74 benchmarks.

### Time
~25 min.
