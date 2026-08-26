# Worked example — scaffolding a nested-sampling research project (b_nestedsampling)

Second end-to-end instance of the workflow (after `a_lcbnovel`). Shows how to
scaffold a NEW research project dir modeled on an existing one, and how to migrate
a legacy FLAT project dir into the workflow layout. Companion to
`lcbnovel-project-example.md`.

## The task shape
User asked to "make a project dir much like `<existing>/a_lcbnovel>`, migrate the
code/notes from `<legacy>/8_nested_sampling>`". This recurs: a new `_run/<NN>_<name>`
project that re-hosts an older, flat, non-workflow dir under the doc trio.

## Clarify before building (batch into one call)
The user's standing rule is "clarify for every step". Batch independent decisions
into a single multi-question clarify. Decisions that actually matter here:
1. **Code scope** — which files migrate (package modules + root runner + dataset
   code + a CLEAN scripts/). Offer "dedupe -Copy/_v0/checkpoint cruft" explicitly;
   the user prefers a lean scripts/ matching what the real entry points import.
2. **Dataset** — copy the full dataset incl. gitignored DBs (self-contained) vs
   code-only. This user picked self-contained.
3. **Big legacy notes file** — a 786-line `NESTED_SAMPLING_RUN.md` was the project's
   main notes. Decision: split its content into README/LOG/TUTORIAL and DROP the
   raw file (vs. keeping/archiving it). This user chose split-and-drop.
4. **Governance** — add AGENTS.md + PROMPTS.md scaffold.
5. **Sibling dirs** — scaffold `_runs/`, `_analysist/{0_analy,1_result}`,
   `_archives/`, `_tmp/` even before concrete runs exist.

## Migration recipe (flat → workflow)
- Copy only the **non-cruft** code: package modules (6 .py here), the root runner,
  the full `dataset/` (13 seed DBs, gitignored), and a **clean** `scripts/` = the
  set the entry points actually import (5 files; source had ~40 with `-Copy`,
  `_v0`, `backup`, `.ipynb_checkpoints` dupes).
- **Leave the legacy dir untouched** — copy-only migration.
- **Split the big notes file** into the trio, then delete it from the new dir.
- **Version all in-scope source** at module-level `__version__ = "1.0.0"` placed
  after the shebang/docstring/`from __future__`. Pre-existing **function-local**
  `__version__` (e.g. `0.0.1` inside scripts) are left untouched — module-level one
  added.
- Write VERSIONS.md manifest, README.md, README.AI.md, LOG.md (first entry),
  TUTORIAL.md, AGENTS.md (paths/package/skills adapted), PROMPTS.md scaffold,
  .gitignore (exclude `*.db/*.png/*.xsf/*.csv/*.log/__pycache__/_tmp/_archives`
  and the run-output dirs).
- Verify: `py_compile` every in-scope file under the env python, then run a cheap
  **smoke run** of the migrated pipeline (the user values a real end-to-end check,
  not just compile).
- Commit **scoped to the new dir** (`git add _run/b_nestedsampling/`) so unrelated
  parent-repo churn stays untouched. Confirm on the milestone.

## Job-script + environment nuance (HPC batch)
- The reference job script `a_lcbnovel/j_novel.sh` is the model: bare PJM header +
  `source ~/.bashrc; conda activate gpaw_env; module load intel impi` + the python
  line. **No verbose comment blocks** (user's standing rule).
- Locally there may be **no `gpaw_env`** — check `ls ~/miniconda3/envs/` and import
  probe both envs before deciding what the job activates. On HPC `gpaw_env` is the
  standing env; the sampling script needs the AGOX/ASE stack (which may only exist
  in `agox_v2`). Keep `gpaw_env` in the job (convention) but **document the
  `agox_v2` fallback caveat** in README.AI/TUTORIAL.
- **Literature/parameter notes belong in TUTORIAL.md, NOT in the `.sh`** — keeps
  batch scripts bare. The job may carry a one-line `echo` pointing to TUTORIAL.
- Core count: match the heavy DFT entry point (e.g. `SubprocessGPAW(ncores=24)`),
  not the sampler (which is single-process). Ask the user which to use.

## Renaming a root runner (run_nested_sampling.py → main.py)
When the user wants the root runner named `main.py`:
1. `git mv old.py main.py` (preserves history; git reports `{old => new} | 0`).
2. Fix any docstring/comment self-references to the old name.
3. **Bump the file's `__version__`** (patch for a doc-only edit) and update
   VERSIONS.md (`old.py 1.0.0` → `main.py 1.0.1`).
4. Update every current-state doc reference (README, README.AI, TUTORIAL, AGENTS).
5. **LOG.md is append-only** — do NOT rewrite historical entries that mention the
   old name; append a new correction entry recording the rename.
6. Re-verify: `py_compile main.py` + `sh -n` the job script.

## Distinguish same-named scripts
After the rename, the project has BOTH a root `main.py` (nested sampling) and a
`dataset/main.py` (AGOX search). Docs must always qualify by directory. Watch for
this collision and disambiguate in README.AI §file-layout + provenance.
