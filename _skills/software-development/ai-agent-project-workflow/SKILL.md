---
name: ai-agent-project-workflow
description: "Start an AI-agent project with README/LOG/TUTORIAL/AGENTS."
version: 1.1.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [project-workflow, documentation, readme, log, tutorial, agents-md, clarify-first]
    related_skills: [plan, agox, git-commit-hygiene]
---

# AI-Agent Project Workflow

The user's standing rule for how a project must be run when an AI agent works on it.
Every new project directory should follow this. Three deliverables must coexist,
plus (once the user asks) an `AGENTS.md` that codifies the rules so future agents
read and obey them.

## When to Use

- The user starts a new project dir (e.g. `_run/<NN>_<name>/`) and asks to "start a
  project" or "set up the workflow" for it.
- Any sustained multi-step project where an AI agent will keep working across sessions.
- The user says "use the new workflow" or pastes the three-deliverables rule.

## The Core Principle

When an AI agent works on a project, **three deliverables must coexist**:

1. **README** — one for humans, one for AI agents.
2. **Log** — a continuous, append-only record of what the agent actually did.
3. **Tutorial** — instructions for how the work can be replicated.

No task is complete until all three are present and consistent with the work done.

## The Deliverables (concrete shape)

- `README.md` (human): what the project accomplishes, who it's for, how to run/use it
  at a high level, key decisions & tradeoffs (a decisions table works well).
- `README.AI.md` (agent spec): file layout, entry points & commands, dependencies &
  environment, expected inputs/outputs, error handling & edge cases, provenance.
- `LOG.md` (curated action log): append-only. Per session: Goal (user-confirmed via
  clarify), Actions taken, Results, Decisions & reasoning, Open items, Time.
- `transcript.log` (raw tool-call / run output): gitignored via `*.log`.
- `TUTORIAL.md`: prerequisites, reproduce each step, pitfalls, verification checklist.
- `VERSIONS.md` (version manifest — user's standing rule): one table row per source
  file with its current `__version__`, plus the bump rules. Keep it in step with the
  code; add to any project with code.
- `AGENTS.md` (governing rules — add once the user asks): codifies the workflow +
  operating rules so any future agent reads it first. The user specifically wanted
  this created so "when AI agent working on this project, it will read the file and
  work accordingly." Use filename `AGENTS.md` (the conventional agent-auto-read name).

## Operating Rules (embed these in AGENTS.md and follow them)

1. **Clarify before every step.** Confirm task, approach, and outputs with the user
   before writing/running code. Do not assume. Batch independent clarify questions
   into one call.
2. **Ground everything in the repo.** Read existing code, README.AI.md, LOG.md before
   acting. Never invent files/symbols/APIs.
3. **Keep deliverables current.** Every change to code/results updates the Log and,
   when behaviour changes, the README(s) + Tutorial.
4. **Log is append-only.** Never rewrite/delete prior entries; add new ones. When a
   later decision reverses an earlier one, append a correction entry that explicitly
   says it reverses the earlier record — do not edit the old entry.
5. **Verify before claiming done.** Run compile/smoke/build checks; report real output.
6. **Commit after every change.** Make a git commit for every meaningful change.
   Confirm with the owner first when the commit is a milestone or has side effects;
   otherwise commit promptly so Log and git history stay in step. (User's exact rule.)
7. **Code + docs tracked; regenerable data excluded.** Follow the repo `.gitignore`
   (e.g. `*.db`, `*.xsf`, `*.png`, `*.log`, output dirs are regenerable artifacts).
8. **Version every code file; bump on every edit.** Every source file carries a
   module-level `__version__ = "X.Y.Z"` (semver, baseline `1.0.0`). Any code edit
   bumps that file's patch version (minor for API/behavior changes), updates the
   `VERSIONS.md` manifest, and is recorded in `LOG.md` (old→new version). See the
   "Source-code versioning" section and `references/source-code-versioning-and-git.md`.

## User Preferences (Fe/MgO / AGOX research context)

- **Local dev/test env = `agox_v2`** (`/home/think/miniconda3/envs/agox_v2/bin/python`);
  **HPC pjsub heavy-run env = `gpaw_env`** (activated inside the batch script). Keep
  local smoke/compile on `agox_v2`, only the HPC batch run uses `gpaw_env`. Don't
  "fix" one to the other — they serve different purposes.
- **HPC launch = `pjsub j_novel.sh`** with the seed set by editing a `SEED=3` variable
  at the top of the script. Do **not** use `pjsub -x SEED=5 j_novel.sh`.
- **No verbose comment blocks in `.sh` files.** Keep batch scripts bare (PJM headers
  + env setup + command). Don't add long explanatory notes/usage comments.
- A cheap **local validation/smoke test** (lightweight system, no heavy DFT) should be
  written and run to ground repair claims in real output before the heavy run.

## Pitfalls

- **LSP/IDE import errors are misleading.** Pyright under base `python3` flags AGOX/ASE
  imports as unresolved even when the code compiles fine under `agox_v2`. Judge by the
  env python's `py_compile`, not the LSP.
- **`transcript.log` is gitignored** (`*.log`) even though the curated `LOG.md` is
  tracked. Don't expect the raw transcript in commits.
- Don't invent the deliverable filenames when the user already gave them; confirm
  scope/filename via clarify (e.g. whether AGENTS.md should be created, and what it
  covers).

## Reference Files

- `references/lcbnovel-project-example.md` — worked example: scaffolding project 10
  (Novelty-LCB Fe/MgO) end-to-end with all deliverables + AGENTS.md + commit history.
- `references/maintaining-project-layout.md` — how to evolve an existing project's
  docs when the user adds/reorganizes dirs (e.g. `_runs/`, `_analysist/`), and the
  **run-directory convention** for research projects.
- `references/benchmark-discussion.md` — writing a DISCUSSION.md from benchmark results.
- `references/source-code-versioning-and-git.md` — the **versioning convention**
  (module-level `__version__`, bump rules, `VERSIONS.md`, LOG tracking) plus git
  safety for projects nested in a parent repo and write-persistence checks.
- `references/agox-analysis-runner.md` — adding a self-contained analysis runner to
  `_analysist/` (AGOX results), scoping to supported layouts and copying only needed
  deps.

## Source-code versioning (user standing rule — summary)

Every source file carries a **module-level `__version__ = "X.Y.Z"`** (semver,
baseline `1.0.0`). **Any code change bumps that version**, and **LOG.md tracks code
versions for every change**. (Full detail in
`references/source-code-versioning-and-git.md`.)

- **Bump rule:** patch (`1.0.0 → 1.0.1`) on every edit; minor (`1.0.1 → 1.1.0`) on
  API/behavior changes.
- **On every edit:** bump the file's `__version__`, update the `VERSIONS.md` manifest
  (one row per file), and append a `LOG.md` entry recording old→new version.
- **Placement:** `__version__` goes **after** the shebang, module docstring, and any
  `from __future__ import` (putting it before `from __future__` raises
  `SyntaxError`). Keep any pre-existing function-local `__version__` untouched; add
  the module-level one (indent 0).
- **Scope:** version **source only** (root `main*.py`, `novelty_lcb/`, `scripts/`,
  test/smoke/energy_stats, `_analysist/` runner+scripts). Duplicated per-run
  snapshots under `_runs/` and `dataset/` are **not** individually versioned.

## Run-directory convention (research projects — summary)

For the Fe/MgO / AGOX research projects, concrete runs and their analysis live in two
sibling dirs separate from the project root (full detail in
`references/maintaining-project-layout.md`):

- **`_runs/<NN>_<descriptor>/`** — self-contained run dirs (job `j_*.sh` + `main*.py`
  + copies of `scripts/` and `novelty_lcb/`), each launchable in isolation. Naming =
  running index + descriptive suffix (e.g. `1_mgofe_Seed3_Iter300`, `73_novel_benchEMT`).
- **Doc policy:** HPC per-seed runs are **bare code dirs** (no per-run README/LOG/
  TUTORIAL); standalone benchmark projects (e.g. `73_novel_benchEMT`) carry the full
  doc trio inside their own dir.
- **`_analysist/`** — analysed/intermediate results (`0_analy/`, `1_result/`,
  `main_analyst.ipynb`, `main_test.ipynb`). Outputs regenerable/gitignored; `_runs/`
  code is git-tracked.

When you start a NEW heavy-run project, scaffold this `_runs/` + `_analysist/` layout
by default.

## Verification Checklist

- [ ] All three deliverables present (README human + AI, LOG, TUTORIAL) and consistent
- [ ] `AGENTS.md` (if requested) created and referenced by the project
- [ ] Clarify used before each step; user confirmed scope
- [ ] Local smoke test / compile actually run and result reported
- [ ] Changes committed per the user's rule (confirm on milestones)
- [ ] `.sh` batch script kept bare; correct env (gpaw_env) and launch (`pjsub j_novel.sh`)
- [ ] Every source file has a module-level `__version__`; `VERSIONS.md` current; `LOG.md` records old→new version for every code change
