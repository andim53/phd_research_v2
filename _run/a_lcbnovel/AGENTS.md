# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/a_lcbnovel/`. Read it first, every time, before
doing anything. It codifies the AI-Agent Project Workflow that the project owner set
down. It is complementary to, not a replacement for, `README.AI.md` (the machine
spec) and `LOG.md` (the action log).

---

## 1. The Core Principle

When an AI agent works on this project, **three deliverables must coexist**:

1. **README** — one for humans, one for AI agents
2. **Log** — a continuous record of what the AI actually did
3. **Tutorial** — instructions for how the work can be replicated

No task is complete until all three are present and consistent with the work done.

---

## 2. The Three Deliverables

### 2.1 README for Humans
A plain-language overview of:
- What the project accomplishes
- Who it's for
- How to run/use it at a high level
- Key decisions and tradeoffs made

In this project that file is `README.md`.

### 2.2 README for AI Agents
A structured, machine-readable specification including:
- File structure layout
- Entry points and commands
- Dependencies and environment setup
- Expected inputs/outputs
- Error handling and edge cases

In this project that file is `README.AI.md`.

### 2.3 Log of AI Actions
An append-only record of:
- Every tool call and its result
- Files created, modified, or deleted
- Decisions made and the reasoning behind them
- Errors encountered and how they were resolved
- Time spent per major action

In this project:
- `LOG.md` — curated, append-only action log (the primary log).
- `transcript.log` — raw tool-call / run-output transcript.

### 2.4 Tutorial
Step-by-step instructions covering:
- Prerequisites and setup
- How to reproduce each major step
- Common pitfalls and how to avoid them
- Verification steps to confirm success

In this project that file is `TUTORIAL.md`.

---

## 3. Rules of Operation

1. **Clarify before every step.** Confirm the intended task, approach, and outputs
   with the project owner before writing or running code. Do not assume.
2. **Ground everything in the repo.** Read the relevant existing code and the
   `README.AI.md` spec before acting. Never invent files, symbols, or
   APIs that are not already present or explicitly requested.
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
5. **Verify before claiming done.** Run the relevant checks (compile, smoke test,
   build) and report what real execution returned. Do not fabricate results.
6. **Commit after every change.** Make a git commit for every meaningful change to
   the project. Confirm with the owner first when the commit is a milestone or has
   side effects (e.g. a large set of changes, a release point, or anything that might
   affect other work). Otherwise, commit promptly after each change so the Log and
   the git history stay in step.
7. **Code + docs tracked; regenerable data excluded.** Follow the repo's `.gitignore`
   conventions (output dirs, `*.db`, `*.xsf`, `*.png`, logs are regenerable artifacts).

## 3a. Run directories: `1_runs/` and `2_analysist/`

Heavy runs and their analysis live in two sibling directories, separate from the
project-root code/docs.

### `1_runs/` — self-contained run directories

Each HPC run (or benchmark) gets its **own self-contained directory** under
`1_runs/`, so a job can be launched and, later, understood in isolation. It carries
**everything** that run needs — job script, main script(s), and copies of `scripts/`
and `novelty_lcb/` — and does **not** depend on files in the project root.

```
1_runs/
├── <NN>_<descriptor>/            # e.g. a1_mgofe_Seed3_Iter300
│   ├── j_*.sh                    #   PJM batch script (one seed/job; edit SEED=, N_ITERATIONS=)
│   ├── main*.py                  #   entry point(s) for that run (latest from project root)
│   ├── scripts/                  #   latest slab/generator builders (self-contained)
│   ├── novelty_lcb/              #   latest package copy (self-contained, versioned)
│   ├── README.md                 #   per-run overview, specific to that run's treatment
│   ├── TUTORIAL.md               #   how to reproduce THAT run
│   └── (output/ seed_<N>/ db files, generated on HPC)
└── <NN>_<descriptor>/            # full benchmark projects add the doc trio
    ├── README.md / README.AI.md / LOG.md / TUTORIAL.md / AGENTS.md
    ├── j_*.sh / main*.py
    ├── scripts/ / novelty_lcb/
    └── benchmark_results/ (regenerable)
```

Naming convention: **`<NN>_<descriptor>`** — a running two-digit index plus a
short descriptive suffix that captures the run's identity (e.g.
`a1_mgofe_Seed3_Iter300`, `73_novel_benchEMT`). This keeps runs ordered and
unambiguous.

Documentation policy:
- **HPC per-seed Fe/MgO runs** (one seed per job, e.g. `a1_mgofe_Seed3_Iter300`)
  carry a **per-run `README.md` + `TUTORIAL.md`** alongside `j_*.sh` + `main.py` +
  `scripts/` + `novelty_lcb/`. The README states the run's treatment — what differs
  from its sibling runs (seed, iteration budget) — and the TUTORIAL reproduces **that
  run** in isolation. They do **not** carry a full per-run README.AI/LOG (the project
  root owns those).
- **Standalone benchmark projects** (e.g. `73_novel_benchEMT`) are full projects
  and carry the **complete doc trio** (README + README.AI + LOG + TUTORIAL, and an
  AGENTS.md if the owner asks) inside their own dir.

**Keep run copies current.** Each per-seed run's `main.py`, `scripts/`, and
`novelty_lcb/` should be kept in sync with the latest versioned copies in the project
root (`cp main.py novelty_lcb/*.py scripts/*.py <run>/` after a root change).

Everything under `1_runs/` is **tracked in git** (code + docs), subject to the same
regenerable-data exclusions.

### `2_analysist/` — analysed results

Analysed/intermediate results live in `2_analysist/`, kept separate from both the
project root and `1_runs/` so raw runs are never mixed with their analysis.

Expected layout (matching the repo-root `.gitignore`):
```
2_analysist/
├── 0_analy/               # intermediate analysis / staging
├── 1_result/              # final analysed results
├── main_analyst.ipynb     # analysis notebook (gitignored if large)
└── main_test.ipynb        # scratch/testing notebook (gitignored)
```

Analysis outputs are regenerable artifacts and are gitignored; only the
analysis code/notebooks the owner chooses to track are tracked.

### Per-run analysis convention

Each concrete run's analysis is produced by a self-contained runner in
`2_analysist/` — the **multi-seed** runner `run_analysis_indices.py` (71/72, loads all
`seed_*/1_db/db_*.db` from a `--dataset` dir) and the **single-seed** runner
`run_analysis_a_runs.py` (per-seed a-runs, e.g. `a1_mgofe_Seed3_Iter300/output`).
Analysis outputs go to a per-run dir `<run>/analysis_indices/` or
`<run>/analysis_a_runs/` (progression plot + window `.xsf`, `conf_space.png`,
`binding_probability_vs_temperature.png`).

**Every analysis dir must ship a `DISCUSSION.md`** (mirroring the b_nestedsampling
convention) that:
- states the **exact running command + parameters** in a `## Running script` section
  (the full `python <runner>.py --dataset ... --outdir ... [flags]` line), so the
  analysis is reproducible and traceable to its generating invocation; and
- discusses the results grounded in the actual numbers.

CLI for both runners: `--dataset --outdir --e-max --normalize-density --start-iter`.
Analysis outputs (PNG/xsf) are gitignored (regenerable); the runners + `scripts/` and
any DISCUSSION.md the owner chooses to track are tracked.
8. **Do not modify another profile's skills/plugins/cron/memories** unless the owner
   explicitly directs it.
9. **Ask permission before accessing other notes or other projects.** When it is
   necessary to read, access, or modify any other note (anything beyond
   `README.AI.md` and the relevant code) or any other project directory (inside
   or outside this project), ask the owner for explicit permission first. Never
   proceed on an assumed approval.

---

## 3b. PROMPTS.md — the prompt log + grammar concept system

`PROMPTS.md` is the project's **prompt log**: every prompt the owner adds for future
work, each marked with a **flag code** and cleaned into a consistent grammar. It is a
deliverable the agent must keep current alongside README/LOG/TUTORIAL.

### Format of each prompt entry

- **Flag heading.** Every prompt gets a first-level heading `# FLAG: <code>` above it,
  where `<code>` is derived from the local timestamp as **`YYYYMMDD_HHMM`**
  (year, month, day, hour, **minute** — e.g. `20260826_1437`). Newer prompts sit
  **above** older ones.
- **Two grammar blocks** under each flag:
  - `## Original (before grammar fix)` — the owner's raw text, preserved verbatim.
  - `## Fixed grammar (after)` — the same prompt with the grammar corrected.
- **One shared `## Grammar notes` section** covering the whole file (see below) — do
  **not** create a new notes section per prompt.

### The grammar notes are concept-based, not per-prompt

When a prompt is added, its grammar fixes are folded into the **single existing**
`## Grammar notes` section. Notes are organized as **generalized concepts** (each with
the concrete instances from the flagged prompts underneath), so recurring mistakes are
named once and recognized across prompts. The current concepts are:

1. **Incomplete clauses** — an instruction missing its verb, object, or noun (e.g.
   "Make for kappa 3, 4, and 5" → add the object "Make runs ..."; "Make a new 1_runs"
   → add the noun "directory").
2. **Redundant / near-duplicate words** — stacked words with the same meaning (e.g.
   "kappa number" → "kappa value"; "system and setup" → pick one or define both).
3. **Vague / ambiguous value listing** — values that read as a range or start point
   rather than a fixed set (e.g. "NOVELTY_WEIGHT, starting from 2.0, 3.0, 4.0" →
   "NOVELTY_WEIGHT values: 2.0, 3.0, and 4.0").
4. **Non-idiomatic phrasing** — unnatural preposition/filler around common actions
   (e.g. "Clarify for every step" → "Clarify each step").
5. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token (e.g. a path broken inside "research"); keep them on one line and in
   backticks.

### Agent duties

- When the owner adds a prompt (or one is dropped in with an empty flag), assign its
  flag code from the local time, fix the grammar into the "after" block, and **fold the
  fixes into the existing Grammar notes** (adding a new concept only if the mistake is
  genuinely new, otherwise reusing/strengthening an existing one).
- Keep the new prompt **above** older ones.
- Treat `PROMPTS.md` as a tracked deliverable: update it when prompted, and keep its
  grammar notes consistent with what is actually in the prompts.

---

## 4. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0 +
  GPAW). Base `python3` has **no** AGOX/ASE/GPAW — always use the env python.
- Heavy Fe/MgO GPAW runs target the HPC cluster (PJM batch, 64-core); one seed per job.
- Load relevant skills before writing AGOX code: `agox`, `agox-run-code`,
  `agox-novel-filter`, `agox-nested-sampling`, `simulation-analysis`.

---

## 5. Relationship to Existing Systems

This workflow generalizes the `ai-agent-reminder-system` pattern — extending it from
reminders to full project execution. Project-specific state, provenance, and
references are in `README.AI.md`; the running record of what has been done is in
`LOG.md`.
