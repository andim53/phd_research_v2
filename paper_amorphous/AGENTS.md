# AGENTS.md — paper_amorphous

Governing rules for any AI agent working in this project. Read this first.

## Project
- **Topic:** Amorphous Pt(P) via GOFEE/AGOX global optimization, with spin Hall conductivity (SHC) from FLAPW. Working title: *Amorphous Pt(P) from GOFEE/AGOX: structure, crystallinity, and spin Hall conductivity*.
- **Authors:** Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura (Mie University).
- **Layout:** `papers/paper1/` = main manuscript (RevTeX 4.2) + `supplementary/` (SPIE class). `codes/` = figure/analysis code. `analysis/` = regenerated figures/JSON. `data/` = raw AGOX/GPAW results (read-only reference). `tmp/` = FLAPW install + SHC example (read-only reference).
- **Status:** Amorphous generation complete (Pt(P), 20/30% P, cell +0/+3/+5%). SHC calculation **in progress** — paper1 has a placeholder SHC section to fill once results land.

## Operating rules
1. **Clarify before every step.** Confirm task/approach/outputs with the owner before writing/running code. Batch independent questions.
2. **Ground in the repo.** Read `README.AI.md` + relevant code before acting. Never invent files/symbols/APIs. Read-gating: read only `README.AI.md` + code unless the owner grants access to other notes.
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
- **SHC section is a placeholder** until the FLAPW SHC results exist; do not draft SHC numbers or claims before the calculation is done.

## Environment
- Local analysis/compile env: `agox_v2` (`/home/think/miniconda3/envs/agox_v2/bin/python`). Set `matplotlib.use('Agg')` before plotting (headless).
- FLAPW/SHC env: `flapw_2` conda env (see `tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW/job_genkai_mpi.sh`); runs on HPC via pjsub.
- LaTeX: no system TeX; use `~/.local/bin/tectonic` (0.17.0).
- Figure style must match `_analysist` rcParams (serif 12, ticks-in all sides, no grid, dpi 300, autolayout) and the `iteration >= 10` filter convention.
