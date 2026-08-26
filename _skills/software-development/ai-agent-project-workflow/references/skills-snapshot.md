# Snapshotting research skills into a project `_skills/` dir

Worked pattern (learned maintaining project 10, `10_lcbnovel`) for when the user
asks to "copy all the skills used in my research into this dir" — i.e. vendor the
Hermes skills that a research project depends on into the project itself, so the
project is self-contained and reproducible without the live skill store.

## When it applies

- User asks for a copy/snapshot of skills into a project dir (e.g.
  `/home/think/Desktop/research/_skills/`).
- User wants a project to carry its own copy of the skills used to build/run it.

## Workflow

1. **Survey the source first.** The live skill store is `~/.hermes/skills/`
   (category subdirs: `research/`, `mlops/`, `software-development/`, ...). List
   each category's skill dirs (each has a `SKILL.md` plus optional
   `references/`, `templates/`, `scripts/`). Also read `.usage.json` if you need
   to decide which skills are actually used (it stores `use_count` per skill
   name).
2. **Clarify scope & structure before copying** (per the workflow). Confirm:
   - **Which skills** count as "used in research" (this user chose: the full
     `research/` category + `mlops/agox-gpr-analysis` +
     `software-development/ai-agent-project-workflow`).
   - **Structure/depth** (this user chose: copy each skill as its FULL directory,
     preserving category subdirs `research/`, `mlops/`, `software-development/` —
     not flattening, not SKILL.md-only).
   - **Snapshot vs metadata** (this user chose: one-time snapshot + a small
     `README.md` documenting date/source/layout).
3. **Copy with `cp -r`, preserving the category tree.** e.g.
   `cp -r ~/.hermes/skills/research _skills/` plus the specific extra skills into
   their category subdirs. Do NOT copy dotfiles/metadata (`.usage.json`,
   `.curator_ledger.jsonl`, `__pycache__`) — they are not part of the skills.
4. **Handle a pre-existing target.** If `_skills/` already has old *flat* snapshots
   (e.g. an old `agox-skill/`, `gpaw-skill/` without category subdirs) that the new
   categorized copy supersedes: confirm with the user, then archive them out of the
   way (e.g. move to `_skills_archive_flat_<date>/`), and add that archive dir to
   the repo `.gitignore` so it is NOT committed. Git often detects the old flat dir
   → new category dir as a clean **rename** (R100) when the content matches.
5. **Write a `_skills/README.md`** documenting the snapshot date, source, count,
   and layout, plus where any superseded flat copies were archived.
6. **Verify the copy** before committing: compare per-dir file counts source vs
   dest (`find <dir> -type f | wc -l`), confirm no hidden dotfiles came along, and
   confirm each SKILL.md is present.
7. **Commit the snapshot; gitignore the archive.** Stage explicit paths (`git add
   .gitignore _skills/`), never blanket `git add -A` from inside a nested project
   (stages the whole parent repo — see `source-code-versioning-and-git.md`).
   Confirm only the intended paths are staged before committing.

## Pitfalls

- **`git add -A` from a nested project stages the whole parent repo.** The
  `_run/<NN>_<name>` projects live inside `/home/think/Desktop/research` (one repo).
  Stage explicit pathspecs only. Leave unrelated pre-existing changes (e.g. other
  projects' deletions) untouched — do not stage or commit them.
- **Old flat snapshots are superseded, not a conflict.** When the new categorized
  copy includes the same skill (old `agox-skill/` → new `research/agox/`), archive
  the flat one and gitignore it rather than committing both.
- **One-time snapshot, not auto-synced.** Note in the README that the copy is a
  point-in-time snapshot; a later update to `~/.hermes/skills/` requires re-copying.
- **Don't copy the skill store's metadata files** (usage/curator ledger, backups) —
  only the skill dirs themselves.
