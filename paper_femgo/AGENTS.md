# AGENTS.md — paper_femgo

Governing rules for any AI agent working in this project. Read this first.

## Project
- **Topic:** Machine Learning-Based Partition Function Sampling: Application to Fe on MgO(001) Growth.
- **Authors:** Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura (Mie University).
- **Layout:** `papers/paper1/` = main manuscript (RevTeX 4.2) + `supplementary/` (SPIE class). `codes/` = figure-regeneration code. `analysis/` = regenerated figures/JSON. `data/` = raw AGOX/GPAW results (read-only reference).
- **Draft provenance:** finished draft ported from `tmp/draft_paper/` (zips). Prose preserved verbatim; only structure split into `sections/`.

## Operating rules
1. **Clarify before every step.** Confirm task/approach/outputs with the owner before writing/running code. Batch independent questions.
2. **Ground in the repo.** Read `README.md` + relevant code before acting. Never invent files/symbols/APIs. Read-gating: read only `README.md` + code unless the owner grants access to other notes.
3. **Keep deliverables current.** After any code change, append to `LOG.md` and update `VERSIONS.md` (append-only, never rewrite). Other notes updated only on explicit owner command.
4. **Log is append-only.** Never rewrite/delete prior entries; append corrections that explicitly reverse earlier records.
5. **Verify before claiming done.** Run compile/smoke checks; report real output.
6. **Commit after every change.** Commit per milestone; confirm with owner on milestones.
7. **Code + docs tracked; regenerable data excluded.** Follow repo `.gitignore` (`*.db`, `*.png`, `*.log`, `*.pdf` are regenerable artifacts).
8. **Version every code file; bump on every edit.** Module-level `__version__`; bump patch on edit, minor on behavior change; update `VERSIONS.md` + `LOG.md`.
9. **Ask permission before accessing other notes/projects.**

## Paper-writing rules (scientific-paper-writing skill)
- **LaTeX-native, one `.tex` per section** in `papers/paper1/sections/`; `main.tex` `\input`s them. Block-and-wait review gate between sections.
- **Checkpoint/resume:** always update `papers/paper1/paper_status.md` before ending a session; a fresh session reads it first.
- **Citations:** never hallucinate; fetch/verify programmatically; mark `[CITATION NEEDED]`. `\cite{key}` must match `.bib` key byte-for-byte.
- **Claims:** every number traces to a source file; figures/results come from `analysis/` by reference. `CLAIMS.md` freezes the claim list; drafting must not introduce claims outside it.
- **Reuse rule:** produce paper-needed graphs in `codes/`/`analysis/`, then reference them; do not duplicate.
- **Numbers stay as drafted.** The manuscript's stated numbers (e.g. "seeds 0–13, 1,207 configs") are NOT to be silently changed; discrepancies vs on-disk data are flagged in a report, not edited into the prose.

## Environment
- Local analysis/compile env: `agox_v2` (`/home/think/miniconda3/envs/agox_v2/bin/python`). Set `matplotlib.use('Agg')` before plotting (headless).
- LaTeX: no system TeX; use `~/.local/bin/tectonic` (0.17.0).
- Figure style must match `_analysist` rcParams (serif 12, ticks-in all sides, no grid, dpi 300, autolayout) and the `iteration >= 10` filter convention.
