# Renaming a research project directory (e.g. 10_lcbnovel -> a_lcbnovel)

Worked pattern (learned renaming project 10, `10_lcbnovel` -> `a_lcbnovel`) for when
the user renames the whole project dir (and/or its per-run subdirs) and expects the
repo and every internal reference to follow. Distinct from adding dirs into docs
(see `maintaining-project-layout.md`).

## When it applies

- User renames `_run/<NN>_<name>/` on disk (plain `mv`) and says "handle the rename".
- Renaming a self-contained research project that references its own name in code +
  docs + per-run copies + snapshots + memory.

## Workflow

1. **Confirm the on-disk + git state first.** A plain `mv` leaves git seeing the old
   path as deleted and the new path as untracked — that is expected, not an error.
   Run `ls -d old new`, `git status --short`, and inspect the new tree's subdirs.
2. **Clarify scope** (batch the questions): stage the rename in git? update ALL
   internal references (source, every doc, `_runs/` copies, `_analysist/1_result`
   copies, `_skills/` snapshot, memory)? one commit or several?
3. **Stage the rename so git records it as a rename** — `git add -A <old_dir> <new_dir>`
   (plus any `_skills/` if you updated it). Git detects the moved files as renames
   (R100/Rxxx); verify with `git diff --cached --name-status | grep -c '^R'`.
4. **Update the project-name string EVERYWHERE it appears** (this user's projects
   embed the project name in code paths and docs). Script a `old -> new` replace over
   text files, excluding `__pycache__`, `.git`, and regenerable/binary types
   (`.db .xsf .traj .png .pyc .out .csv .ipynb`). Walk the tree; count changed files.
   Files that typically carry the name:
   - root source: `main*.py`, `smoke_test_serialization.py`, `_analysist/run_analysis_indices.py`
   - all docs: `README.md`, `README.AI.md`, `TUTORIAL.md`, `AGENTS.md`, `LOG.md`, `VERSIONS.md`
   - `_runs/<NN>_*/` copies (each has its own `main.py`/docs) — including the
     gitignored `_analysist/1_result/<run>/` copies if the user wants full consistency
   - the `_skills/` snapshot, if the project name appears in its references
   - persistent memory (project path) — update separately via the memory tool
5. **LOG.md: append a rename entry**; the historical path strings are mechanically
   updated by the script (a path rename, not a rewrite of action history) — say so in
   the entry. Keep the append-only rule (add a new entry, don't rewrite prior ones).
6. **Verify before committing:** `py_compile` the code; run the cheap validation
   (`test_window_logic.py`); `grep -rl <oldname>` across the project text files to
   confirm zero leftovers. Then confirm the staged set is ONLY the rename + skills
   paths (see git-safety in `source-code-versioning-and-git.md`; never blanket
   `git add -A` from inside a nested project).
7. **Commit** — one combined commit (rename + content + LOG) if the user chose that.

## Pitfalls

- **`mv` ≠ git rename by itself.** Until you stage both old deletions and new
  additions, git shows the old tree "deleted" and the new one "untracked". Stage both
  paths together to get rename detection.
- **The project name is duplicated in per-run and `_analysist` copies.** Missing one
  leaves a dangling `.../10_lcbnovel` path in a copy that no longer exists. Decide via
  clarify whether the gitignored `1_result/` copies are in scope, then be consistent.
- **The `_skills/` snapshot carries the old name.** If you updated it, stage it too and
  note it in the commit.
- **LOG append-only vs mechanical string replace.** Replacing `10_lcbnovel` ->
  `a_lcbnovel` inside historical LOG text is a path rename, not a history rewrite —
  still add a NEW dated entry documenting the rename rather than editing an old one's
  meaning.
- **Verify with `py_compile` + a cheap test, not the heavy smoke test.** The smoke test
  needs the AGOX Ray pool and can fail with `ActorUnavailableError` on a low-RAM node
  for environmental reasons unrelated to the rename — judge regressions by `py_compile`
  and `test_window_logic.py` plus the rename's diff (should be ~100% similarity,
  string-only).
- **Keep the commit scoped.** The parent repo may hold unrelated pre-existing
  deletions (`nested_sampling/`, `novelty_lcb/`, ...) — leave them unstaged.
