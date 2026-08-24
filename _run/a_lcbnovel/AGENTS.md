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
2. **Ground everything in the repo.** Read the relevant existing code, the
   `README.AI.md` spec, and `LOG.md` before acting. Never invent files, symbols, or
   APIs that are not already present or explicitly requested.
3. **Keep the deliverables current.** Every task that changes code or produces
   results must update the Log, and, when behaviour changes, the README(s) and
   Tutorial. Do not leave the docs describing a state the code no longer matches.
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

## 3a. Run directories: `_runs/` and `_analysist/`

Heavy runs and their analysis live in two sibling directories, separate from the
project-root code/docs.

### `_runs/` — self-contained run directories

Each HPC run (or benchmark) gets its **own self-contained directory** under
`_runs/`, so a job can be launched and, later, understood in isolation. It carries
**everything** that run needs — job script, main script(s), and copies of `scripts/`
and `novelty_lcb/` — and does **not** depend on files in the project root.

```
_runs/
├── <NN>_<descriptor>/            # e.g. 1_mgofe_Seed3_Iter300
│   ├── j_*.sh                    #   PJM batch script (one seed/job; edit SEED=, N_ITERATIONS=)
│   ├── main*.py                  #   entry point(s) for that run
│   ├── scripts/                  #   copied slab/generator builders (self-contained)
│   ├── novelty_lcb/              #   copied package (self-contained)
│   └── (output/ seed_<N>/ db files, generated on HPC)
└── <NN>_<descriptor>/            # full benchmark projects may add the doc trio
    ├── README.md / README.AI.md / LOG.md / TUTORIAL.md / AGENTS.md
    ├── j_*.sh / main*.py
    ├── scripts/ / novelty_lcb/
    └── benchmark_results/ (regenerable)
```

Naming convention: **`<NN>_<descriptor>`** — a running two-digit index plus a
short descriptive suffix that captures the run's identity (e.g.
`4_mgofe_Seed3_Iter900`, `73_novel_benchEMT`). This keeps runs ordered and
unambiguous.

Documentation policy:
- **HPC per-seed Fe/MgO runs** (one seed per job, e.g. `1_mgofe_Seed3_Iter300`)
  are **bare code dirs**: `j_*.sh` + `main.py` + `scripts/` + `novelty_lcb/` and
  their regenerable outputs. They do **not** get a per-run README/LOG/TUTORIAL.
- **Standalone benchmark projects** (e.g. `73_novel_benchEMT`) are full projects
  and carry the **complete doc trio** (README + README.AI + LOG + TUTORIAL, and an
  AGENTS.md if the owner asks) inside their own dir.

Everything under `_runs/` is **tracked in git** (code + docs), subject to the same
regenerable-data exclusions.

### `_analysist/` — analysed results

Analysed/intermediate results live in `_analysist/`, kept separate from both the
project root and `_runs/` so raw runs are never mixed with their analysis.

Expected layout (matching the repo-root `.gitignore`):
```
_analysist/
├── 0_analy/               # intermediate analysis / staging
├── 1_result/              # final analysed results
├── main_analyst.ipynb     # analysis notebook (gitignored if large)
└── main_test.ipynb        # scratch/testing notebook (gitignored)
```

Analysis outputs are regenerable artifacts and are gitignored; only the
analysis code/notebooks the owner chooses to track are tracked.
8. **Do not modify another profile's skills/plugins/cron/memories** unless the owner
   explicitly directs it.

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
