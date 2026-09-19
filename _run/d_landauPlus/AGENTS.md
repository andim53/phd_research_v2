# AGENTS.md — Governing Rules for AI Agents Working on This Project

This file is the **governing process** for any AI agent working in
`/home/think/Desktop/research/_run/d_landauPlus/`. Read it first, every time,
before doing anything. It codifies the AI-Agent Project Workflow. Complementary
to `README.AI.md` (machine spec) and `LOG.md` (action log).

---

## 1. The Core Principle

When an AI agent works on this project, a consistent record must be kept:

1. **README.AI.md** — machine spec (file layout, entry points, deps, IO, edge cases).
2. **LOG.md** — continuous, append-only record of what the agent actually did.
3. **AGENTS.md** — this file (governing rules).

No task is complete until the record is present and consistent with the work done.

## 2. Rules of Operation

1. **Clarify before every step.** Confirm task, approach, outputs with the owner
   before writing/running code. Do not assume. Batch independent clarify questions.
2. **Ground everything in the repo.** Read `README.AI.md` and the relevant code
   before acting. Never invent files/symbols/APIs. **Read-gating:** when
   investigating, read `README.AI.md` first, then the actual (relevant) code. Other
   notes (`LOG.md`, etc.) must NOT be read unless the owner gives an explicit command.
3. **Keep the record current.** After any code change, auto-update `LOG.md`
   **append-only, without reading it** — never rewrite prior entries. `README.AI.md`
   is updated only on explicit owner command.
4. **Log is append-only.** When a later decision reverses an earlier one, append a
   correction entry that says so explicitly — do not edit the old entry.
5. **Verify before claiming done.** Run compile/smoke/build and report real output.
6. **Commit after every change.** Commit each meaningful change; confirm with the
   owner on milestones. **Pathspec caveat:** this dir may contain a vestigial empty
   `.git`; git resolves to the repo toplevel `/home/think/Desktop/research` — commit
   with explicit `_run/d_landauPlus/<path>` args.
7. **Code + docs tracked; regenerable data excluded.** Follow `.gitignore` conventions
   (`*.db`, `*.xsf`, `*.png`, `*.csv`, `*.log`, `lp_output/`, `__pycache__/` are
   regenerable artifacts).
8. **Version every code file; bump on edit.** Module-level `__version__` (semver);
   bump patch on edit, minor on API/behavior change; record old→new in `LOG.md`.
9. **Ask permission before accessing other notes/projects.** Beyond `README.AI.md` +
   relevant code, ask the owner before reading/writing anything else or any other
   project directory.

## 3. Project-specific invariants

- **Environment:** local dev = `agox_v2`
  (`/home/think/miniconda3/envs/agox_v2/bin/python`); HPC heavy runs = `gpaw_env`
  pjsub (switch `conda activate` to `agox_v2` if the AGOX stack is missing).
- **The algorithm is NO-DFT.** The GPR surrogate is the only energy/force model. Do
  not introduce any GPAW/DFT evaluation into the sampling path.
- **The flat/island weight is δ-sensitive (rattle amplitude).** Before any result
  is treated as physical, the owner MUST be reminded to test multiple `--rattle`
  values (1.0, 1.5, 2.0, …) and compare the flat/island occupancy.
- **Inherent-structure caveat.** Every proposal is relaxed to a basin minimum, so
  `g(E)`, the ensemble, `Z`, `F`, `C_V` are **inherent-structure** (basin) quantities,
  not configurational. The ensemble is 1/g(E)-biased and reweightable via
  `w_i(T)=exp(-E_i/k_BT)/g(E_i)`.
- **`stop_16` is excluded by design.** The `seed_*` glob in `load_all_seeds` is
  deliberate; do not "fix" it to include `stop_*`.

## 4. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2 + ASE 3.25.0).
  Base `python3` has **no** AGOX/ASE — always use the env python.
- `GPR(..., use_ray=False)` default → single-process.
- Load relevant skills before writing code: `ai-agent-project-workflow`, `agox`,
  `agox-wang-landau`, `agox-run-code`.