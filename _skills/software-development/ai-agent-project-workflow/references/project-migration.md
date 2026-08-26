# Migrating a source project into a new project dir (modeled on an existing one)

Recurring user workflow: "Make dir project, much like in <model_project>. Migrate the
codes/notes from <source_project>." Both a_lcbnovel (from 7_lcbnovel) and
b_nestedsampling (from 8_nested_sampling) were done this way. The user expects
**clarify for every step** and a decision point at each dimension below.

## The clarify dimensions (batch into one clarify call)

Ask ALL of these up front; each is a real fork that changes the scaffold:

1. **Code scope** — which code to migrate. Options: package + root runner + dataset
   code + a CLEAN scripts/ (dedupe `-Copy`/`_v0`/`backup`/`.ipynb_checkpoints` cruft);
   package + runner only; or everything verbatim (rarely wanted).
2. **Dataset / big data** — copy the full `dataset/` incl. gitignored DBs (self-
   contained) vs. migrate code only. DBs stay gitignored either way.
3. **Monolithic notes file** — the source often has one big notes md (e.g.
   NESTED_SAMPLING_RUN.md). Options: split into the README/LOG/TUTORIAL trio and DROP
   the raw file (user's pick here); split AND archive the raw under `_archives/`; or
   keep as-is.
4. **Governance** — include AGENTS.md + PROMPTS.md scaffold, AGENTS.md only, or neither.
5. **Sibling layout** — scaffold `_runs/`, `_analysist/`, `_archives/`, `_tmp/` now,
   or project root + dataset + package only.
6. **scripts/ size** — minimal set the entry script actually imports (matches the
   model project's lean scripts/) vs. full deduped tool set.
7. **Job env** — which conda env the HPC job activates. Confirm even if it seems
   obvious; the user's answer can differ from the source (e.g. keep `gpaw_env` on HPC
   even when the sampler needs the `agox_v2` AGOX stack).

## Execution sequence (after clarify)

1. Scaffold the tree (mirror the model project's dir names).
2. Copy code with `cp`, not `git mv` — the SOURCE dir is left intact as the archive
   source (copy-only migration). Verify big-data copies (e.g. DB count matches source).
3. If requested, add module-level `__version__ = "1.0.0"` to every migrated source
   file (insert after shebang/docstring/`from __future__ import`; leave pre-existing
   function-local `__version__` untouched). Update VERSIONS.md + LOG.
4. Split the monolithic notes into README/TUTORIAL/LOG (drop/archive the raw per
   decision 3). Preserve the physics notes and literature rationale into the docs.
5. Write the bare job `.sh` (no comment blocks; echo only).
6. **Verify**: `py_compile` every in-scope file under the env python; `sh -n` the job
   script; optionally a tiny smoke run of the migrated pipeline. Then commit SCOPED to
   the new dir only (the parent repo has unrelated churn — `git add <newdir>/` alone).
7. Keep the doc trio current on later edits (README/LOG/TUTORIAL/VERSIONS).

## Pitfalls

- **Source vs model confusion**: the user names a MODEL project for structure AND a
  SOURCE project for code. They are different dirs — copy code from the source, shape
  from the model.
- **DB path contract**: if the sampler hardcodes `DATASET_DIR = <project>/dataset` and
  globs `seed_*/1_db/db_*.db`, the search script must write there (see
  agox-nested-sampling `references/full_pipeline_job.md`).
- **Job env may not exist locally**: check `ls <conda>/envs/` — a standing HPC env
  (e.g. `gpaw_env`) may be absent locally while `agox_v2` has the full stack. Document
  the caveat; don't assume.
- **`git gc` warnings** (too many unreachable loose objects) are pre-existing parent-
  repo hygiene, not a failure of the scoped commit.
