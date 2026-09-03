# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/b_nestedsampling/`. Read it first, every time,
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

Each HPC run gets its **own self-contained directory** under `1_runs/`, so a job can
be launched and, later, understood in isolation. It carries **everything** that run
needs — job script, run script(s), and copies of `scripts/` and `nested_sampling/` —
and does **not** depend on files in the project root.

```
1_runs/
└── <NN>_<descriptor>/            # e.g. a1_mgofe_Seed3_Iter300
    ├── j_*.sh                    #   PJM batch script (one job; edit the python line)
    ├── main.py                 #   entry point(s) for that run (latest from project root)
    ├── scripts/                  #   latest slab/generator builders (self-contained)
    ├── nested_sampling/          #   latest package copy (self-contained, versioned)
    ├── README.md                 #   per-run overview, specific to that run's treatment
    ├── TUTORIAL.md               #   how to reproduce THAT run
    └── (output/ ns_output_*, generated on HPC)
```

Naming convention: **`<NN>_<descriptor>`** — a running index plus a short
descriptive suffix that captures the run's identity (e.g. `a1_mgofe_Seed3_Iter300`,
`ns1_T300_nlive500_iter5000`). This keeps runs ordered and unambiguous.

Documentation policy:
- **HPC runs** carry a **per-run `README.md` + `TUTORIAL.md`** alongside `j_*.sh` +
  `main.py` + `scripts/` + `nested_sampling/`. The README states the
  run's treatment — what differs from its sibling runs (temperature, live set,
  iterations, seed) — and the TUTORIAL reproduces **that run** in isolation. They do
  **not** carry a full per-run README.AI/LOG (the project root owns those).

**Keep run copies current.** Each run's `main.py`, `scripts/`, and
`nested_sampling/` should be kept in sync with the latest versioned copies in the
project root (`cp main.py nested_sampling/*.py scripts/*.py <run>/`
after a root change).

**NS run dirs: required `scripts` module + correct version.** For nested-sampling
runs, `nested_sampling/state_density.py` does
`from scripts.plot_structure_landscape import plot_structure_landscape`. This
resolves via the package dir on `sys.path`, so `plot_structure_landscape.py` MUST be
present at `<run>/nested_sampling/scripts/plot_structure_landscape.py` — otherwise the
run fails at import with `ModuleNotFoundError: No module named 'scripts'`.

**Use the CORRECT version.** The current `state_density.py` calls
`plot_structure_landscape(..., s=5, ...)`, so the copied `plot_structure_landscape.py`
MUST accept an `s` argument or the final landscape analysis crashes with
`TypeError: plot_structure_landscape() got an unexpected keyword argument 's'`.

- **ONLY valid source:** the reference
  `2_analysist/1_no_prior_control/nested_sampling/scripts/plot_structure_landscape.py`
  (accepts `s=25`). Always copy from here:
  `cp 2_analysist/1_no_prior_control/nested_sampling/scripts/plot_structure_landscape.py <run>/nested_sampling/scripts/`
- **DO NOT use** `dataset_boron/scripts/plot_structure_landscape.py` — it is a STALE
  version that lacks the `s=` argument and will crash the landscape analysis (this was
  the cause of the b4/b5 `TypeError`).

Everything under `1_runs/` is **tracked in git** (code + docs), subject to the same
regenerable-data exclusions.

### `2_analysist/` — analysed results

Analysed/intermediate results live in `2_analysist/`, kept separate from both the
project root and `1_runs/` so raw runs are never mixed with their analysis. Each
run's analysis gets its **own self-contained directory** under `2_analysist/`,
mirroring the `1_runs/<NN>_<descriptor>` naming, plus a shared reference run and
an archive for superseded analysis.

Current layout:
```
2_analysist/
├── 1_no_prior_control/       # shared reference run (plain Fe/MgO, no prior/window)
├── b1_.../ ... b9_.../        # per-run analysis dirs (<NN>_<descriptor>)
├── analyze_tfree_outputs.py   # analysis scripts live at the 2_analysist root
├── plot_conf_space_deltaz.py
└── _archive/                  # superseded analysis (e.g. old 0_analy/), gitignored
```

Analysis outputs are regenerable artifacts and are gitignored; only the
analysis code/scripts and per-run README/DISCUSSION docs the owner chooses to
track are tracked.
8. **Do not modify another profile's skills/plugins/cron/memories** unless the owner
   explicitly directs it.
9. **Ask permission before accessing other notes or other projects.** When it is
   necessary to read, access, or modify any other note (anything beyond
   `README.AI.md` and the relevant code) or any other project directory (inside
   or outside this project), ask the owner for explicit permission first. Never
   proceed on an assumed approval.

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

## 3c. Temperature-free (tfree) analysis task template

When the owner asks to **"analyze tfree"** for a run (or to reproduce the b6/b9 analysis for a
temperature-free NS run), follow this template. Invoke the `agox-tfree-analysis` skill
(discoverable by name) for the full step-by-step procedure.

**Clarify before beginning (per standing rule).** At minimum confirm:
1. **Which ns_output dir** — a run dir may hold several `ns_output_*` outputs (e.g. b6 has
   `ns_output_tfree_walk_emax04` and `ns_output_tfree_walk_emax04_01Perturb`). Default to the one
   documented in that run's `README.md`; ask if ambiguous.
2. **Output placement + naming** — follow the b6/b9 pattern:
   `<run_dir>/analysis_<ns_output_name>/` (the analysis dir name mirrors the ns_output dir name).
3. **Extras** — replicate the b9 output exactly (9 PNGs + DISCUSSION.md, skip the delta-Z
   landscape) unless the run has posterior `.xsf` and the owner wants `conf_space_deltaz.png` too.
4. **Commit** — confirm scope (per the flat `2_analysist/` `.gitignore`: PNGs gitignored; a
   `DISCUSSION.md` is now trackable).

**Procedure (once clarified):**
```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/b_nestedsampling/2_analysist
$PY analyze_tfree_outputs.py \
    --data <run_dir>/<ns_output_name> \
    --outdir <run_dir>/analysis_<ns_output_name> \
    --n-atoms 75
```
- Uses `2_analysist/analyze_tfree_outputs.py` (numpy + matplotlib only, no AGOX).
- Produces the **9 standard PNGs** + a printed textual summary (samples convergence, weighted
  `g(E)` histogram, cumulative Z sanity check, live histogram, `Z`/`log Z`/`F`, heat capacity,
  configurational state density, `Z`-consistency, combined summary).
- **Write a `DISCUSSION.md`** in the output dir mirroring the b6/b9 structure (run/data/script
  header; sampling & energy window; weighted histogram; live set; thermodynamics; C_V; sanity;
  interpretation & caveats; next steps) — grounded in the real numbers the analyzer printed.
  **The DISCUSSION.md MUST include an "Analysis reproduction (command used)" block right after
  the Script line** with the exact analyzer command + parameters for that run (full python path +
  `--data <run>/<ns_output_name> --outdir <run>/analysis_<ns_output_name> --n-atoms 75`) and a
  one-line explanation of each parameter, so the analysis is reproducible.
- **Skip `conf_space_deltaz.png`** unless the run has `posterior_*.xsf` (a `--no-posterior-xsf`
  run cannot produce it — say so in the DISCUSSION).
- **Log** the session in `LOG.md` (append-only); **commit** the trackable parts (LOG.md + the
  DISCUSSION.md) after confirming scope.

**Deliverables check:** 9 PNGs + `DISCUSSION.md` in `<run_dir>/analysis_<ns_output_name>/`,
LOG.md updated, committed per scope.

---

## 4. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0 +
  Ray). Base `python3` has **no** AGOX/ASE — always use the env python.
- Heavy runs target the HPC cluster (PJM batch, 64-core). `j_nestedsampling.sh`
  activates `gpaw_env` (standing convention) — **caveat:** the sampling script needs
  the AGOX/ASE stack from `agox_v2`; switch the `conda activate` line if the HPC job
  fails on AGOX imports.
- `GPR(..., use_ray=False)` → single-process; scale out by submitting many
  independent jobs, not MPI-parallelising one invocation.
- Load relevant skills before writing code: `ai-agent-project-workflow`,
  `agox-nested-sampling`, `agox`, `simulation-analysis`, `agox-run-code`.

---

## 5. Relationship to Existing Systems

This workflow generalizes the `ai-agent-reminder-system` pattern — extending it from
reminders to full project execution. Project-specific state, provenance, and
references are in `README.AI.md`; the running record of what has been done is in
`LOG.md`.
