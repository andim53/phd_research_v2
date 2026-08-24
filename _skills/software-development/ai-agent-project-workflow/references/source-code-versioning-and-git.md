# Source-code versioning + git safety (research projects)

Two durable conventions/gotchas learned maintaining project a_lcbnovel. Both apply
to the user's `_run/<NN>_<name>` research projects.

## 1. Source-code versioning convention (user-established standing rule)

The user requires that **every code file carry a version param**, that **any code
change bumps that version**, and that **LOG.md tracks code versions for every change**.
Adopt this on every research project by default.

Scheme (confirmed with the user):
- **Per-file, module-level** `__version__ = "X.Y.Z"` (semver). Baseline `1.0.0`.
- **Patch bump** (`1.0.0 → 1.0.1`) on every code edit; **minor bump**
  (`1.0.1 → 1.1.0`) on API/behavior changes.
- Add a project-level **`VERSIONS.md`** manifest: one table row per file with its
  current version, plus the bump rules.
- **On every edit:** bump the file's `__version__`, update `VERSIONS.md`, and append
  a `LOG.md` entry recording old→new version for the file(s).

Placement rules:
- `__version__` goes **after** the shebang, the module docstring, and **after any
  `from __future__ import`** line. Inserting it before a `from __future__` import
  raises `SyntaxError: from __future__ imports must occur at the beginning of the
  file` — a silent-but-deadly placement bug when scripting the insertion.
- Keep function-local `__version__` variables that already exist in a file untouched;
  add the module-level one (indent 0). Don't conflate the two.

Scope decision: version **source only** (root `main*.py`, `novelty_lcb/`, `scripts/`,
test/smoke/energy_stats, `_analysist/` runner+scripts). Duplicated per-run snapshots
under `_runs/<NN>.../` and `dataset/` are **not** individually versioned — they are
self-contained copies; bump the source and sync a copy only if that run needs it.

## 2. Git safety: project dirs nested inside a parent repo

The `_run/<NN>_<name>` project is usually **not its own git repo** — it lives inside
`/home/think/Desktop/research` (the parent repo). Consequences:

- `git rev-parse --show-toplevel` returns the **parent**, not the project. `git add -A`
  (or `git commit -a`) run from inside the project stages **the whole parent repo**,
  including unrelated/other-project files and pre-existing staged deletions of other
  projects. **Always stage explicit pathspecs for the project dir**, never blanket
  `git add -A`.
- The **parent `.gitignore`'s path rules do not reach a nested project dir**. E.g. the
  parent ignores `_analysist/0_analy/` at its own level, but a nested
  `_run/a_lcbnovel/_analysist/0_analy/` still shows as untracked. Add a **project-level
  `.gitignore`** (with its own `_analysist/0_analy/`, `_analysist/1_result/`,
  `*.db/*.png/*.traj/*.xsf/*.csv/*.out`) so regenerable outputs stay out of the commit.
- **Before committing, verify the staged set** (`git diff --cached --stat`) contains
  only the intended project files and nothing from siblings.
- **If you accidentally staged unrelated deletions**, restore with a scoped pathspec:
  `git restore --source=HEAD --staged --worktree -- _analysist/` from the parent root
  (a path like `_analysist/` matches only the top-level one, not nested `_run/...`).

Note: gitignored dirs (e.g. a parent's `_analysist/0_analy/`, `1_result/`, notebooks)
that vanish from disk cannot be restored from git — only tracked files can.

## 3. Verify file writes actually persisted

When editing many files programmatically, don't trust the write's return value alone —
**read the file back with a real tool** (`read_file` / `terminal grep`) to confirm the
edit landed. In this session a batch of programmatic writes reported success but did
not persist to the real tree (grep of the actual files showed 0 matches), silently
leaving files untagged. Ground truth = `git diff` / reading the real file, not the
writer's `verified` flag.
