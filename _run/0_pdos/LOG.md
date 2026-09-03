# LOG.md — Action Log for _run/0_pdos (PDOS calculations)

Append-only record of what an AI agent did in this project. Never rewrite or
delete prior entries; add new ones at the bottom. Timestamps are local (JST).

---

## Session 1 — Project scaffolding (2026-09-01)

### Goal (user-confirmed)
Initialize the PDOS-calculation project in `_run/0_pdos` following the
AI-Agent Project Workflow: full deliverable set + AGENTS.md + VERSIONS.md.

### Actions taken
1. Surveyed the existing directory state:
   - `_results/` (10_dos, 32_dos, 37_dos, analyze_dos.py) — completed DOS/PDOS runs.
   - `1_runs/1_pdos_boron3_gs/` — a prepared but uncommitted PDOS run for the
     FeB/MgO global ground state (main.py, job_dos.sh, gs_boron3.traj,
     README.md, TUTORIAL.md).
   - `dataset_boron3/` — AGOX search data (seed_0..6 DBs).
2. Confirmed no project docs existed (no README/LOG/TUTORIAL/AGENTS/VERSIONS).
3. Verified git context: repo root is `research/`, branch `main`, `_run/0_pdos`
   is currently untracked (`??`). `.gitignore` excludes `*.db`, `*.csv`, `*.xsf`,
   `*.png`, `*.log`, `*.traj`-type regenerable artifacts and `__pycache__/`.
4. Clarify call to confirm scope/AGENTS.md/content/commit — timed out with no
   answers; proceeded with the documented recommended defaults (full workflow
   set, create AGENTS.md, document existing baseline, commit once done).
5. Created the six deliverable files:
   - `README.md` — human overview, layout, key systems, decisions table, status.
   - `README.AI.md` — machine spec (env, layout, entry points, code pattern,
     output schema, ground-state extraction, error handling).
   - `LOG.md` — this file.
   - `TUTORIAL.md` — reproduction steps.
   - `VERSIONS.md` — version manifest.
   - `AGENTS.md` — governing rules for AI agents.

### Results
All six deliverable files created and consistent with the existing project
state (results, runs, dataset_boron3).

### Decisions & reasoning
- Created the **full** workflow set because the user's standing rule lists
  README(+AI) + LOG + TUTORIAL + AGENTS + VERSIONS as the standard scaffold for
  a new project dir.
- Documented the **existing baseline** (including the uncommitted
  `1_pdos_boron3_gs` run) so README/LOG reflect reality, per rule 3.
- The `1_pdos_boron3_gs` run was prepared in an earlier session (not this one);
  this session only documents it.

### Open items
- Launch `1_runs/1_pdos_boron3_gs` on HPC (`pjsub job_dos.sh`) — not yet done.
- `dataset_boron3/seed_6` db is empty; confirm whether that is expected.

### Time
Scaffolding session, ~15 min.

## 2026-09-04 00:13 JST

- AGENTS.md: PROMPTS.md editable only on owner permission; may hold owner task prompts to run (dropped-in prompts = ordinary owner command).
