# LOG — Project b_nestedsampling (append-only)

Curated, append-only record of agent actions. Append new entries; never rewrite or
delete prior ones. Per session: Goal (user-confirmed via clarify), Actions, Results,
Decisions & reasoning, Open items, Time.

---

## Session 2026-08-26 — Project creation & migration from `_run/8_nested_sampling`

**Goal (user-confirmed via clarify):** Create a new nested-sampling project dir at
`/home/think/Desktop/research/_run/b_nestedsampling`, structured like
`/home/think/Desktop/research/_run/a_lcbnovel` (README human+AI, LOG, TUTORIAL,
VERSIONS, AGENTS, PROMPTS, `.gitignore`, plus `_runs/`, `_analysist/`, `_archives/`,
`_tmp/`), and migrate the code/notes from `_run/8_nested_sampling`.

**Clarify decisions (all user-confirmed):**
1. Code scope: package (6 modules) + `run_nested_sampling.py` + dataset code + a
   CLEAN `scripts/` (dedupe `-Copy`/`_v0`/checkpoint cruft).
2. Dataset: copy the full `dataset/` dir including the (gitignored) seed DBs →
   self-contained.
3. `NESTED_SAMPLING_RUN.md` (786 lines): split into the README/LOG/TUTORIAL trio,
   drop the raw file.
4. Governance: add `AGENTS.md` + an empty `PROMPTS.md` scaffold.
5. Layout: scaffold `_runs/`, `_analysist/`, `_archives/`, `_tmp/`.
6. Scripts: keep only the 5 scripts `dataset/main.py` actually imports
   (`build_mgo_stack`, `build_fe_stack`, `build_heteroStruct`,
   `hetero_struct_randomize`, `plot_structure`).
7. `j_nestedsampling.sh` activates `gpaw_env` (standing HPC convention; AGOX caveat
   flagged in docs).

**Actions taken:**
- Loaded `ai-agent-project-workflow` + `agox-nested-sampling` skills; inspected
  both `8_nested_sampling` and the `a_lcbnovel` model layout.
- Scaffolded `b_nestedsampling/{nested_sampling,scripts,_runs,_analysist/{0_analy,1_result},_archives,_tmp}`.
- Copied the `nested_sampling/` package (6 modules), `run_nested_sampling.py`, the
  full `dataset/` (13 seed DBs verified), and the 5 clean scripts.
- Created `j_nestedsampling.sh` (bare PJM script; `gpaw_env`; `use_ray=False`
  params preserved from source `job.sh`).
- Added module-level `__version__ = "1.0.0"` to all 12 in-scope source files
  (left pre-existing function-local `0.0.1` in `scripts/*.py` untouched).
- Split `NESTED_SAMPLING_RUN.md` into `README.md` / `TUTORIAL.md` (+ LOG here),
  then **deleted the raw file** from the migrated copy.
- Wrote `README.md`, `README.AI.md`, `TUTORIAL.md`, `VERSIONS.md`, `AGENTS.md`,
  `PROMPTS.md`, `.gitignore`, `transcript.log`.

**Results / verification:**
- 13/13 seed DBs copied; package + runner + scripts in place.
- `__version__ = "1.0.0"` present in all 12 files (grep-verified).
- `py_compile` check of all in-scope source under `agox_v2` (see below).
- Source `_run/8_nested_sampling/` left **intact** (copy-only migration).

**Decisions & reasoning:**
- `gpaw_env` for the HPC job keeps the standing convention; the AGOX/agox_v2
  requirement is documented as a caveat in README.AI.md + TUTORIAL.md (matching the
  source notes' warning).
- `_archives/` added to `.gitignore` (archived artifacts are regenerable/reference).

**Open items:**
- No concrete `_runs/` run yet — scaffolded empty, ready for a future run.
- A full/smoke production run has **not** been re-executed in the new dir (only
  compile-check); the dataset + code are migrated, so a smoke run can confirm
  end-to-end.

**Time:** 2026-08-26 ~20:00–20:15 JST.
