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
