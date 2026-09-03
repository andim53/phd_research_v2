# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/0_pdos/`. Read it first, every time, before
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
   conventions (output dirs, `*.db`, `*.xsf`, `*.png`, `*.csv`, logs are regenerable
   artifacts).
8. **Do not modify another profile's skills/plugins/cron/memories** unless the owner
   explicitly directs it.
9. **Ask permission before accessing other notes or other projects.** When it is
   necessary to read, access, or modify any other note (anything beyond
   `README.AI.md` and the relevant code) or any other project directory (inside
   or outside this project), ask the owner for explicit permission first. Never
   proceed on an assumed approval.

---

## 3a. Run directories: `1_runs/` and `_results/`

Heavy runs and their analysis live in two sibling directories, separate from the
project-root code/docs.

### `1_runs/` — self-contained run directories

Each HPC PDOS run gets its **own self-contained directory** under `1_runs/`, so a
job can be launched and, later, understood in isolation. It carries **everything**
that run needs — job script, `main.py`, and the structure file(s) — and does **not**
depend on files in the project root.

```
1_runs/
└── <NN>_<descriptor>/            # e.g. 1_pdos_boron3_gs
    ├── main.py                   #   entry point (GPAW LCAO DOS/PDOS)
    ├── job_dos.sh                #   PJM batch script (gpaw_env, 24 cores)
    ├── <struct>.traj             #   the structure file(s) to analyse
    ├── README.md                 #   per-run overview
    └── TUTORIAL.md               #   how to reproduce THAT run
```

Naming convention: **`<NN>_<descriptor>`** — a running two-digit index plus a
short descriptive suffix (e.g. `1_pdos_boron3_gs`).

Everything under `1_runs/` is **tracked in git** (code + docs), subject to the same
regenerable-data exclusions.

### `_results/` — completed runs + analysis

Completed runs and their analysis live in `_results/`, kept separate from the
project root so finished work is not mixed with active development. Analysis is
produced by `_results/analyze_dos.py`, which reads `dos_seed_{seed}.csv` files.
Regenerable outputs (`*.png`, `*.csv`, `.traj`, `.xsf`) are gitignored; the runner
`analyze_dos.py` and any docs the owner chooses to track are tracked.

---

## 3b. PROMPTS.md — the prompt log

`PROMPTS.md` is the project's **prompt log**: every prompt the owner adds for future
work, numbered simply `#1`, `#2`, `#3`, ... (newest last). It is a deliverable the
agent must keep current alongside README/LOG/TUTORIAL.

**`PROMPTS.md` is editable only when the owner grants permission.** It may hold the
owner's pending task prompts (including the container brief telling the agent to
improve a prompt, or to **run** a task). When the owner drops a prompt in for the
agent to execute, treat it as an ordinary owner command: clarify first, then perform
the task per these rules.

### Agent duties

- When the owner adds a prompt, append it as the next number (`#1`, `#2`, ...).
- Treat `PROMPTS.md` as a tracked deliverable: update it when prompted.

---

## 4. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0 +
  GPAW 25.7.0). Base `python3` has **no** AGOX/ASE/GPAW — always use the env python.
- Heavy GPAW DOS/PDOS runs target the HPC cluster (PJM batch, `gpaw_env`, 24 cores).
  Launch via plain `pjsub job_dos.sh` — never `pjsub -x`.
- Load relevant skills before writing GPAW/PDOS code: `gpaw`,
  `dos-pdos-analysis`, `agox`.
- `dataset_boron3/` is a **read-only input** (AGOX search data for FeB/MgO). Do not
  modify it.

---

## 5. Relationship to Existing Systems

This workflow generalizes the `ai-agent-reminder-system` pattern — extending it from
reminders to full project execution. Project-specific state, provenance, and
references are in `README.AI.md`; the running record of what has been done is in
`LOG.md`.
