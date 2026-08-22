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
   plot_structure) from `7_lcbnovel_mgofe/` into `10_lcbnovel/`.
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
2. Make the initial git commit for the whole `10_lcbnovel` scaffold.

Confirmed: the rule reads "commit after every change, but confirm with the owner first
when it's a milestone or has side effects"; the initial commit is ONE commit for the
whole scaffold (code + docs + AGENTS.md), message
`10_lcbnovel: Novelty-LCB Fe/MgO scaffold (repair of run 7) + governing AGENTS.md`.

### Actions taken
- Edited `AGENTS.md`: replaced the old "Do not commit without asking" rule with a
  new "Commit after every change" rule (confirm with owner for milestones/side
  effects), and renumbered the following rules.
- (This file) appended this Session 1c entry.
- Staged and committed the whole `10_lcbnovel/` directory as one commit.

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
