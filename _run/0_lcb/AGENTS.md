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
- **Prompts** — `PROMPTS.md`: future-work prompt log, numbered `#1`, `#2`, `#3`, ...
  (newest last). `PROMPTS.md` is **editable only when the owner grants
  permission**; it may hold the owner's pending task prompts (including the container
  brief telling the agent to improve a prompt, or to **run** a task). When the owner
  drops a prompt in for the agent to execute, treat it as an ordinary owner command:
  clarify first, then perform the task per these rules.
- **Instructions** — `INSTRUCTION.md`: owner-side how-to playbook. Holds
  self-contained, second-person, line-by-line guides that let the OWNER do the
  work by hand that the agent would otherwise do. Append-only; blocks are headed
  `INSTR #N — <short title>` + date, **newest first** (see Rule 11).

## 3. Rules of Operation

1. **Clarify before every step.** Confirm the intended task, approach, and outputs
   with the project owner before writing or running code. Do not assume. Batch
   independent clarify questions into one call.
2. **Ground everything in the repo.** Read the relevant existing code and the
   `README.AI.md` spec before acting. Never invent files, symbols, or APIs
   not already present or explicitly requested.
   **When investigating the project, read only from `README.AI.md` first, then
   the actual (relevant) code. All other notes — `README.md`, `TUTORIAL.md`,
   `LOG.md`, `VERSIONS.md`, `PROMPTS.md`, `QNA.md`, `DISCUSSION.md`, etc. — must
   NOT be read unless the project owner gives an explicit command. If the agent
   thinks reading another note is necessary, it may ask the owner for
   permission, which the owner may grant if they also think it is necessary
   (permission covers READING only, not modifying the note).**
3. **Keep the deliverables current.** After making any change within the code,
   auto-update the Log (`LOG.md`) and version notes (`VERSIONS.md`), **append-only
   and without reading them** — never rewrite existing entries. All **other**
   notes (`README.md`, `README.AI.md`, `TUTORIAL.md`, `PROMPTS.md`,
   `DISCUSSION.md`, `QNA.md`, etc.) are updated **only on explicit owner command**
   (e.g. "update the README.AI.md", "update the TUTORIAL.md").
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
10. **Ask permission before accessing other notes or other projects.** When it is
    necessary to read, access, or modify any other note (anything beyond
    `README.AI.md` and the relevant code) or any other project directory (inside
    or outside this project), ask the owner for explicit permission first. Never
    proceed on an assumed approval.
11. **`INSTRUCTION.md` is an append-only, owner-facing how-to.** On the owner's
    explicit request to *prepare an instruction* for a task (and after clarifying
    the task/approach when needed), the agent **prepends** a new self-contained
    block **at the top of the instructions list** in `INSTRUCTION.md` (newest
    first) — it does **not** read-and-rewrite or replace prior blocks. The
    agent's job is to instruct the owner, not to perform the task itself. Each
    block is written in the **second person** ("you run …", "edit `file.py:LINE`
    …") and includes the exact commands (with the correct env python), the
    precise edit location(s) and how to edit, how to run the smoke/verification
    step, and the expected output / how to verify. Blocks are headed
    `INSTR #N — <short title>` + date; the next `N` is the highest existing
    header number + 1 (determined by a targeted header lookup). Do **not** append
    one automatically for every executed task — only on request. Track and commit
    each prepend under the explicit `_run/0_lcb` pathspec, and add a `LOG.md`
    entry for it.

## 3a. Project-specific conventions

- **`2_analysist/17_PPt/` is the incorporated Pt–P run tree.** It predates this
  scaffold and is **kept as-is, not reorganized**. The canonical scripts live in
  `17_PPt/scripts/` and each family's `main.py`; per-run copies are snapshots.
- **`run_analysis_indices.py` is the project-agnostic analysis runner** (v2.1.0),
  adapted from `a_lcbnovel`'s Fe/MgO runner. It analyses any of the interstitial
  families under `2_analysist/` (`11_bTa`, `15_bPt`, `16_bW`, `17_PPt`) by pointing
  `--dataset` at one leaf dir (holding `seed_*/1_db/db_*.db`) and `--outdir` at its
  output. Dep: `2_analysist/scripts/plot_structure_landscape.py`.
- **`1_runs/`** — future self-contained run dirs (`<NN>_<descriptor>/`: job `j_*.sh`
  + `main*.py` + `scripts/`), each launchable in isolation. Heavy HPC runs go here,
  not in the project root.
- **Every analysis dir ships a `DISCUSSION.md`** stating the exact running command +
  parameters and discussing results grounded in the actual numbers.
- **New analysis code must be written in two steps.** When adding or extending any
  analysis that computes quantities an AI is expected to read or plot, structure it
  so that: **Step 1** — a data/emitter function computes the results and writes a
  **self-describing JSON** whose payload embeds enough context for a downstream AI
  to interpret it *standalone* (no working tree): provenance (dataset/family,
  origin), units, the exact method/formula used, a per-field legend
  (`description`), plus the raw arrays it will plot (e.g. an energy grid + the
  plotted curve); **Step 2** — a *separate* plot/reader function **reads that JSON
  and draws the graph from it** (JSON = single source of truth). Follow the existing
  Stage-3 pattern (`_probability_data` emits → `_plot_probability_from_data` reads;
  `--from-json` replots without any DB reload). Prefer this over a function that
  computes and plots from in-memory arrays alone, so figures always reflect the
  persisted, self-describing data. Applies to all **new** analysis code; existing
  functions are not force-refactored unless the task touches them.

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
