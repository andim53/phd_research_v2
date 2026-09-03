# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/c_landausampling/`. Read it first, every time,
before doing anything. It codifies the AI-Agent Project Workflow that the project
owner set down. It is complementary to, not a replacement for, `README.AI.md` (the
machine spec) and `LOG.md` (the action log).

---

## 1. The Core Principle

When an AI agent works on this project, **three deliverables must coexist**:

1. **README** — one for humans, one for AI agents
2. **Log** — a continuous record of what the AI actually did
3. **Tutorial** — instructions for how the work can be replicated

No task is complete until all three are present and consistent with the work done.

---

## 2. The Three Deliverables

- `README.md` — human overview: what the project does, who it's for, how to run
  it, key decisions & tradeoffs.
- `README.AI.md` — machine spec: file layout, entry points & commands,
  dependencies & environment, inputs/outputs, error handling.
- `LOG.md` — curated, append-only action log (the primary log). `transcript.log`
  holds raw tool-call/run output (gitignored via `*.log`).
- `TUTORIAL.md` — step-by-step reproduction + pitfalls + verification.
- `VERSIONS.md` — version manifest (one row per source file's `__version__`).
- `PROMPTS.md` — prompt log + grammar concept system (§3b below).
- `AGENTS.md` — this file (governing rules).

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
6. **Commit after every change.** Make a git commit for every meaningful change.
   Confirm with the owner first when the commit is a milestone or has side effects;
   otherwise commit promptly so the Log and git history stay in step.
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

## 3a. Run directories: `1_runs/` and `2_analysist/`

Heavy runs and their analysis live in two sibling directories, separate from the
project-root code/docs.

### `1_runs/` — self-contained run directories

Each HPC run gets its **own self-contained directory** under `1_runs/`, carrying
everything that run needs — job script, run script(s), and copies of `scripts/`
and `wang_landau/` — and does **not** depend on files in the project root.

```
1_runs/
└── <NN>_<descriptor>/            # e.g. c1_mgofe_N40_Emax04_Iter2e7
    ├── j_*.sh                    #   PJM batch script
    ├── main.py                   #   entry point (latest from project root)
    ├── scripts/                  #   latest builders (self-contained)
    ├── wang_landau/              #   latest package copy (self-contained, versioned)
    ├── README.md                 #   per-run overview
    ├── TUTORIAL.md               #   how to reproduce THAT run
    └── (output/ wl_output_*, generated on HPC)
```

Naming convention: **`<NN>_<descriptor>`** — running index + descriptive suffix
(e.g. `c1_mgofe_N40_Emax04_Iter2e7`, `c2_boron3_N40`). HPC runs carry a per-run
`README.md` + `TUTORIAL.md`; they do **not** carry a full per-run README.AI/LOG
(the project root owns those).

**Keep run copies current.** Each run's `main.py`, `scripts/`, and `wang_landau/`
should be kept in sync with the latest versioned copies in the project root.

Everything under `1_runs/` is **tracked in git** (code + docs), subject to the
regenerable-data exclusions.

### `2_analysist/` — analysed results

Analysed/intermediate results live in `2_analysist/`, one self-contained dir per
run mirroring `1_runs/<NN>_<descriptor>`, plus root-level analysis scripts and an
archived `_archive/`. Analysis outputs are regenerable artifacts (gitignored);
only the analysis code/scripts and per-run docs the owner chooses to track are
tracked.

---

## 3b. PROMPTS.md — the prompt log + grammar concept system

`PROMPTS.md` is the project's **prompt log**: every prompt the owner adds for
future work, each marked with a **flag code** and cleaned into a consistent
grammar. It is a deliverable the agent must keep current alongside
README/LOG/TUTORIAL.

**`PROMPTS.md` is editable only when the owner grants permission.** It may hold the
owner's pending task prompts (including the container brief telling the agent to
improve a prompt, or to **run** a task). When the owner drops a prompt in for the
agent to execute, treat it as an ordinary owner command: clarify first, then perform
the task per these rules.

- **Flag heading.** Every prompt gets `# FLAG: <code>` where `<code>` is derived
  from the local timestamp as **`YYYYMMDD_HHMM`** (e.g. `20260830_2030`). Newer
  prompts sit **above** older ones.
- **Two grammar blocks** under each flag: `## Original (before grammar fix)` and
  `## Fixed grammar (after)`.
- **One shared `## Grammar notes` section** covering the whole file — do **not**
  create a new notes section per prompt. Grammar fixes are folded into the single
  existing `## Grammar notes` section as **generalized concepts** (each with the
  concrete instances from the flagged prompts underneath).

### Agent duties
- When the owner adds a prompt (or one is dropped in with an empty flag), assign
  its flag code from the local time, fix the grammar into the "after" block, and
  **fold the fixes into the existing Grammar notes** (adding a new concept only if
  the mistake is genuinely new).
- Keep the new prompt **above** older ones.
- Treat `PROMPTS.md` as a tracked deliverable.

---

## 4. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE
  3.25.0 + Ray). Base `python3` has **no** AGOX/ASE — always use the env python.
- Heavy runs target the HPC cluster (PJM batch). `j_wanglandau.sh` activates
  `gpaw_env` (standing convention) — **caveat:** the sampling script needs the
  AGOX/ASE stack from `agox_v2`; switch the `conda activate` line if the HPC job
  fails on AGOX imports.
- `GPR(..., use_ray=False)` default → single-process; scale out by submitting many
  independent jobs, not MPI-parallelising one invocation.
- Load relevant skills before writing code: `ai-agent-project-workflow`,
  `agox-nested-sampling`, `agox`, `simulation-analysis`, `agox-run-code`.

---

## 5. Relationship to Existing Systems

This project generalizes the AI-Agent Project Workflow to Wang–Landau sampling of
`g(E)` over an AGOX GPR surrogate. It is the algorithm-sibling of
`_run/b_nestedsampling` (same problem, nested sampling). Project-specific state,
provenance, and references are in `README.AI.md`; the running record of what has
been done is in `LOG.md`.
