# Worked example: scaffolding project 10 (Novelty-LCB Fe/MgO)

This is the concrete, validated example of the AI-Agent Project Workflow applied
end-to-end. Reuse the shapes here when starting a new `_run/<NN>_<name>/` project.

## The user's prompt (verbatim intent)

"start a project in this dir ... Use this instruction" + pasted the three-deliverables
rule (README human + AI, LOG, TUTORIAL). Later: "write another file ... that will act
as a rule. Later, when AI agent working on this project, it will read the file and
work accordingly." → this is the AGENTS.md ask. Then: "Include a git commit ... add in
the AGENTS.md to also include git commit. The commit must be done for every changes."

## Deliverables produced (all under project root)

- `README.md` — human overview: what/for-who/how, decisions & tradeoffs table, status.
- `README.AI.md` — agent spec: layout, entry points & commands table, dependencies,
  inputs/outputs, error handling & edge cases, provenance.
- `LOG.md` — append-only; one section per session with Goal / Actions / Results /
  Decisions / Open items / Time. Raw transcript lives separately.
- `transcript.log` — raw tool-call + run output. **Gitignored** via `*.log`.
- `TUTORIAL.md` — prerequisites, numbered reproduce steps, pitfalls, verification
  checklist.
- `AGENTS.md` — governing rules; the file future agents read first. Added on the
  user's explicit ask, filename confirmed via clarify (standard agent-auto-read name).

## The AGENTS.md content pattern

Mirror the user's rule back into AGENTS.md as sections: Core Principle (three
deliverables coexist), the three deliverables (each mapped to the project's real
files), Rules of Operation, Environment (invariant), Relationship to existing systems.
Rules of Operation that were validated in this session and belong in every AGENTS.md:
1 clarify-before-every-step, 2 ground-in-repo, 3 keep-deliverables-current,
4 append-only-log, 5 verify-before-claiming-done, 6 commit-after-every-change
(confirm with owner on milestones), 7 code+docs-tracked-data-excluded.

## Key session mechanics

- **Clarify before every step**: each milestone started with a batched clarify call
  (goal, system, reuse, log-format; then filename/scope/link for AGENTS.md; then
  commit-rule + initial-commit shape; then seed/env/docs for the .sh edit). The user
  repeatedly asked "Clarify for every step" — never skip this.
- **Commit rule evolution**: AGENTS.md originally said "do not commit without asking";
  the user later wanted "commit after every change" (with milestone confirmation).
  When a rule is replaced, the OLD entry stays in the append-only LOG and a NEW
  correction entry is appended that explicitly says it reverses the earlier record.
- **`.sh` batch scripts**: keep bare — PJM headers + env setup + command. No long
  comment/usage blocks (user explicitly asked to remove them). Seed set via a
  hand-edited `SEED=3` variable; run as `pjsub j_novel.sh` (NOT `pjsub -x SEED=5`).
- **Env split (research context)**: local dev/test = `agox_v2`; HPC pjsub heavy run =
  `gpaw_env`. The user corrected an earlier decision that had switched the batch script
  to `agox_v2` — the HPC batch script must use `gpaw_env`.

## Git history pattern

- One initial commit for the whole scaffold (all code + docs + AGENTS.md), descriptive
  message: `10_lcbnovel: Novelty-LCB Fe/MgO scaffold (repair of run 7) + governing AGENTS.md`.
- Follow-up commits per change batch (e.g. env/pjsub correction): 5 files, one commit.
- Confirm with owner on milestone-size commits; commit promptly otherwise.

## Verification

- `py_compile` under the env python for all .py (LSP/Pyright flags are noise — see
  SKILL.md Pitfalls).
- A cheap local smoke test (lightweight system, no heavy DFT) validates repair claims
  with real output before the heavy HPC run.
- `git status --short` clean after committing; `git log -1 --stat` to confirm.
