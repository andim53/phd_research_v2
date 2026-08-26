# Migrating an existing flat project dir into the structured layout

When the user says "make a new project dir much like `<model>/a_lcbnovel>` and
migrate the code/notes from `<old flat dir>`", the task is NOT "start fresh" and
NOT "rename a dir". It is **re-homing** an existing, often-messy project into the
structured README/LOG/TUTORIAL/VERSIONS/AGENTS layout. Worked example: migrated
`_run/8_nested_sampling` → `_run/b_nestedsampling`.

## Sequence that worked

1. **Read the model dir's layout** (`a_lcbnovel/`): note the root doc files
   (README, README.AI, LOG, TUTORIAL, VERSIONS, AGENTS, PROMPTS, .gitignore) and
   the sibling dirs (`_runs/`, `_analysist/{0_analy,1_result}`, `_archives/`,
   `_tmp/`). Also read the parent repo `.gitignore` to know what is already
   excluded globally.
2. **Inspect the source dir fully** before clarifying — package modules, root
   runner, dataset layout, a big notes file, a messy `scripts/`. Know what's
   cruft (`-Copy`, `_v0`, `_backup`, `.ipynb_checkpoints`, `__pycache__`) vs
   canonical.
3. **Clarify (batch into one call) the genuine decision points.** For this class
   the recurring ones are:
   - code scope (package + runner + dataset code + a *clean* scripts/, vs
     verbatim including cruft);
   - whether to copy the heavy gitignored data (e.g. seed DBs) so the new dir is
     self-contained, or code-only;
   - how to handle a large monolithic notes file (split into the doc trio + drop
     the raw file, vs keep/archive it);
   - whether to include AGENTS.md + an empty PROMPTS.md scaffold;
   - whether to scaffold `_runs/`/`_analysist/`/`_archives/`/`_tmp/` now even with
     no concrete runs yet;
   - which `scripts/` to keep (minimal = only what `main.py` actually imports,
     matching the model's lean `scripts/`);
   - which conda env the HPC batch script activates (see env caveat below).
4. **Copy-only migration** — never move/delete the source. Leave
   `_run/8_nested_sampling/` intact. `cp`/`cp -r` into the new dir.
5. **Split a monolithic notes file** (e.g. a 786-line NESTED_SAMPLING_RUN.md) into
   README.md (overview + decisions) + TUTORIAL.md (reproduce + pitfalls) + LOG.md
   (first session entry), then **drop the raw file** from the new copy (user's
   explicit choice). Keep per-file citations of what came from where.
6. **Add `__version__ = "1.0.0"`** to every migrated source file — do it
   programmatically (see below) and update `VERSIONS.md`. Files duplicated under
   `dataset/` and `_runs/` are NOT individually versioned.
7. **Verify** with `py_compile` under the env python (`agox_v2`), then — if the
   user agrees — run the cheap local smoke test in the new dir to prove the
   migrated pipeline works end-to-end before any HPC run. Report real output.
8. **Commit scoped to the new dir only.** `git add _run/<newname>/` — the parent
   repo has unrelated churn, so never `git add -A`. Verify with `git add -n` (dry
   run) that only code+docs (no *.db/*.png/*.xsf/pycache) are staged. Commit at
   each milestone (scaffold commit, then a follow-up for the smoke-run LOG entry).

## `__version__` insertion (migration gotcha)

Modules with `from __future__ import annotations` need the version AFTER the
shebang + docstring + the `from __future__` line (putting it before raises
`SyntaxError`). Scripts with no `from __future__` get it at the very top. Do it in
one programmatic pass (read lines → find last `from __future__` line → insert
`__version__` after it with blank-line separation → write back), then
`grep -rn "__version__"` to confirm every file got it exactly once. **Preserve
pre-existing function-local `__version__`** (e.g. `0.0.1` inside a function) —
the module-level `1.0.0` is added alongside; both are legit per the versioning
convention.

## Env caveat for HPC batch scripts of migrated research code

Standing convention is `conda activate gpaw_env` in HPC `j_*.sh`, but a
nested-sampling / AGOX-GPR script needs the AGOX+ASE stack which lives in
`agox_v2`. Keep the batch script bare and activate `gpaw_env` (user's choice to
keep convention), but **document the caveat** in README.AI.md + TUTORIAL.md: if
the HPC job fails on AGOX imports, switch `conda activate gpaw_env` →
`conda activate agox_v2`. Always state this explicitly; never silently "fix" one
env to the other.

## Pitfalls

- A conda plugin error report can appear in the captured process stream of a run
  and look alarming, yet be **non-fatal side-process noise** — the Python
  pipeline can still exit 0 and produce all outputs. Judge success by the
  pipeline's exit code + outputs, not by stray stderr text. (`CONDA_NO_PLUGINS=true`
  suppresses the plugin noise.)
- `git gc` warnings ("too many unreachable loose objects", stale `gc.log`) are
  pre-existing parent-repo hygiene, not a failure of your scoped commit.
- Keep a fresh `git status --short -- <newname>/` and `git add -n` check before
  committing so regenerable artifacts never sneak in.
