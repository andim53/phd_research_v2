# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/0_lcb/`. Read it first, every time, before doing
anything. It codifies the AI-Agent Project Workflow the project owner set down. It
is complementary to, not a replacement for, `README.AI.md` (the machine spec) and
`LOG.md` (the action log).

---

## 1. The Core Principle

When an AI agent works on this project, **three deliverables must coexist**:

1. **README** — one for humans, one for AI agents
2. **Log** — a continuous record of what the AI actually did
3. **Tutorial** — instructions for how the work can be replicated

No task is complete until all three are present and consistent with the work done.

## 2. The Deliverables

- **README for humans** — `README.md`: plain-language overview (what/for-who/how),
  key decisions & tradeoffs, status.
- **README for AI agents** — `README.AI.md`: structured spec (layout, entry points,
  commands, deps, inputs/outputs, error handling & edge cases, provenance).
- **Log** — `LOG.md`: curated, append-only action log. Raw tool/run output goes in
  `transcript.log` (gitignored via `*.log`).
- **Tutorial** — `TUTORIAL.md`: prerequisites, reproduce steps, pitfalls,
  verification checklist.
- **Versions** — `VERSIONS.md`: one table row per source file with its
  `__version__`, plus the bump rules.
- **Prompts** — `PROMPTS.md`: future-work prompt log with a single shared
  `## Grammar notes` section.

## 3. Rules of Operation

1. **Clarify before every step.** Confirm the intended task, approach, and outputs
   with the project owner before writing or running code. Do not assume. Batch
   independent clarify questions into one call.
2. **Ground everything in the repo.** Read the relevant existing code,
   `README.AI.md`, and `LOG.md` before acting. Never invent files, symbols, or APIs
   not already present or explicitly requested.
3. **Keep the deliverables current.** Every task that changes code or produces
   results must update the Log and, when behaviour changes, the README(s) and
   Tutorial. Do not leave the docs describing a state the code no longer matches.
4. **Log is append-only.** Never rewrite or delete prior Log entries; add new ones.
   When a later decision reverses an earlier one, append a correction entry that
   explicitly says it reverses the earlier record — do not edit the old entry.
5. **Verify before claiming done.** Run the relevant checks (compile, smoke test,
   build) and report what real execution returned. Do not fabricate results.
6. **Commit after every change.** Make a git commit for every meaningful change.
   Confirm with the owner first when the commit is a milestone or has side effects;
   otherwise commit promptly so Log and git history stay in step.
7. **Code + docs tracked; regenerable data excluded.** Follow the repo `.gitignore`
   conventions (`*.db`, `*.xsf`, `*.png`, `*.log`, output dirs are regenerable
   artifacts).
8. **Version every code file; bump on every edit.** Every source file carries a
   module-level `__version__ = "X.Y.Z"`. Any code edit bumps patch (minor on
   API/behavior change), updates `VERSIONS.md`, and records old→new in `LOG.md`.
9. **Do not modify another profile's skills/plugins/cron/memories.**

## 3a. Project-specific conventions

- **`_analysist/17_PPt/` is the incorporated Pt–P run tree.** It predates this
  scaffold and is **kept as-is, not reorganized**. The canonical scripts live in
  `17_PPt/scripts/` and each family's `main.py`; per-run copies are snapshots.
- **`run_analysis_indices.py` is an annotated Fe/MgO copy** from `a_lcbnovel`. It
  must be **retargeted to Pt–P (`17_PPt`)** before being used for analysis. Do not
  run it on `17_PPt` as-is.
- **`_runs/`** — future self-contained run dirs (`<NN>_<descriptor>/`: job `j_*.sh`
  + `main*.py` + `scripts/`), each launchable in isolation. Heavy HPC runs go here,
  not in the project root.
- **Every analysis dir ships a `DISCUSSION.md`** stating the exact running command +
  parameters and discussing results grounded in the actual numbers.

## 4. Environment (invariant)

- **Local dev/test:** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE + GPAW). Base `python3` has no AGOX/ASE/GPAW.
- **HPC pjsub runs:** `gpaw_env` (activated inside the batch script). Launch via
  `pjsub j_*.sh` with the seed/concentration set by editing the script variable —
  **never `pjsub -x`**. Keep `.sh` scripts bare (PJM headers + env setup + command).

## 5. Relationship to the wider repo

- `_run/0_lcb/` is **not its own git repo**; it lives inside
  `/home/think/Desktop/research` (the parent repo). Always stage **explicit
  pathspecs** for `0_lcb` (e.g. `git add _run/0_lcb/...`), never blanket `git add -A`
  or `git commit -a` from inside the project (those stage the whole parent repo,
  including unrelated files).
- Verify the staged set before committing (`git diff --cached --stat`); if unrelated
  files were accidentally staged, restore them with a scoped pathspec.
