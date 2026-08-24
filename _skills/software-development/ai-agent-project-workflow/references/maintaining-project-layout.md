# Maintaining / evolving a project's docs and layout

Worked pattern (learned maintaining project 10, `a_lcbnovel`) for when the user adds
or reorganizes directories/config inside an existing AI-Agent project and asks you to
"introduce" them into the docs. This is a recurring task distinct from green-field
scaffolding.

## When it applies

- User drops new dirs/files into a project (e.g. `_runs/`, `_analysist/`) and says
  "edit the md note, tutorials, and AGENTS note" / "introduce X into the docs".
- The project already follows the three-deliverables + AGENTS.md workflow, so the docs
  must be kept consistent with the new layout.

## Workflow

1. **Survey the actual layout first.** Read the md note(s), and inspect the new dirs
   with `search_files`/`ls`/`git status` BEFORE editing. Note real details that the docs
   must match: existing subdir names, whether `main*.py`/`scripts/`/`novelty_lcb/` are
   copied per-dir or shared, any `.gitignore` entries that already reference the new
   layout (a strong signal of the intended structure — e.g. repo-root `.gitignore`
   already listed `_analysist/0_analy/`, `_analysist/1_result/`, `main_analyst.ipynb`).
2. **Clarify scope before editing** (per the workflow). Ask which files, plus any
   conventions to lock in (naming scheme, doc policy per dir type). Batch the questions
   in one call.
3. **Edit ALL the docs, not just one.** Keep the deliverables consistent with the new
   layout and with each other:
   - `README.md` (human) — a "Run directories" section + a how-to-use callout pointing
     at the new layout, a decisions-table row, a Status checkbox.
   - `README.AI.md` (agent spec) — the file-layout tree and an explanatory note.
   - `TUTORIAL.md` — the launch/usage steps rewritten to the new layout, plus pitfalls
     and a verification-checklist item.
   - `AGENTS.md` — the governing rule describing the new layout/convention.
   - `LOG.md` — append a dated entry (Goal / Clarify / Actions / Results / Decisions /
     Open items / Time), never edit prior entries.
4. **Ground every path/name in what you actually saw.** Don't invent subdirectory names;
   reuse the ones already present and those the `.gitignore` anticipates.
5. **Handle clarify timeouts:** if a clarify call times out with partial/empty answers,
   take the recommended default for the unanswered ones, and record them in the LOG's
   clarify section as "defaults taken (question unanswered)". Move on; surface the
   assumption rather than re-asking.
6. **Commit** the doc changes together with any repo-mutating step (e.g. a rename) so
   history stays clean; confirm on milestones.

## Pitfalls

- **Trailing space in a dir name** — a run dir was created as `_runs/3_..._Iter700 `
  (trailing space). This is a path/script hazard. Fix with `git mv "old " "new"` (this
  renames all tracked files with history); then add a pitfall note telling future
  agents to keep dir names space-free. Never rely on an unquoted path with the space.
- **Don't make unrequested renames** — but a clear typo like a trailing space is worth
  fixing via `git mv` (confirm with the user first if unsure).
- **Docs drift** — a new layout that is documented in only one of the four docs (or
  not in LOG.md) violates the "deliverables must be consistent" rule. Update the full
  set.

## Run-directory convention (this user's research projects)

For the Fe/MgO / AGOX research projects, heavy runs and their analysis live in two
sibling dirs separate from the project root:

- **`_runs/<NN>_<descriptor>/`** — self-contained run dirs (job `j_*.sh` + `main*.py`
  + copies of `scripts/` and `novelty_lcb/`), so each HPC run is launchable in
  isolation. Naming = running index + descriptive suffix (e.g.
  `1_mgofe_Seed3_Iter300`, `73_novel_benchEMT`).
- **Doc policy:** HPC per-seed runs are **bare code dirs** (no per-run README/LOG/
  TUTORIAL); standalone benchmark projects (e.g. `73_novel_benchEMT`) carry the full
  doc trio inside their own dir.
- **`_analysist/`** — analysed/intermediate results, kept separate from `_runs/`.
  Expected layout: `0_analy/` (staging), `1_result/` (final), `main_analyst.ipynb` /
  `main_test.ipynb` (notebooks). Outputs are regenerable/gitignored; `_runs/` code is
  git-tracked.
