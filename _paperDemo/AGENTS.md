# AGENTS.md — Governing Rules for AI Agents Working on This Project

**Project:** Impact of Boron insertion on the wetting of Fe on MgO (MTJ device relevance)
**Root:** `/home/think/Desktop/research/_paperDemo`
**Venue:** TBD (format-agnostic)
**Workflow skill:** `scientific-paper-writing` (Phase 0 → A → B → C → D → E → F → G)

## Governing workflow rules

- **Papers are drafted markdown-first, one file per section**, in `sections/`:
  `01_methods.md → 02_results.md → 03_discussion.md → 04_introduction.md → 05_conclusion.md → 06_abstract.md`.
- **Block-and-wait review gate:** after each section is drafted, STOP and hand it to the
  scientist for review. Do not draft the next section until the current one is approved.
  Do not port to LaTeX until all six sections are approved.
- **LaTeX is only the final formatting container** (`paper.tex`), produced after all
  sections are approved. Never draft directly in LaTeX.

## Citations

- Never hallucinate references. Fetch and verify BibTeX programmatically (DOI content
  negotiation / Crossref / arXiv / ADS); confirm the paper exists in 2+ sources; validate
  that the cited claim actually appears in the paper.
- Inline keys in markdown as `\cite{nameyear}` (first-author surname + year).
- `.bib` entry identifier must be **byte-for-byte identical** to the `\cite{}` key
  (`@article{nameyear, ...}`).
- Unverifiable citations: keep the key form but tag `% UNVERIFIED — verify before port`
  and log to a "pending" list in `paper_status.md`. Never invent a key.
- One master `references.bib` shared by all sections.

## Claims and numbers

- Every claim must trace to a specific source file (result JSON / `.db` / figure) — no
  unsupported statements.
- Every number in the draft must be re-verified against its raw source file before port.
- Flag any claim without evidence as `[VERIFY]`; do not write it as a result.

## Checkpoint / resume

- Always write/update `paper_status.md` before ending a session.
- A fresh session must be able to resume from `paper_status.md` alone (the file is the memory).

## Data & scope

- Raw data lives in `data/` (AGOX structure-search databases): `femgo` (Fe/MgO) and
  `febmgo` (Fe-B/MgO). This directory is large (~190 MB) and is **not** part of paper
  commits — commit only analysis scripts, the scaffold, and draft files.
- The wetting metric is derived from the structure databases (Fe/B distribution at the
  MgO interface, interface contact, lateral coverage), not from any single pre-existing value.
- The `febmgo` energy range contains relaxation artifacts / unphysical high-energy
  structures; window these out before comparing energetics.

## Commit discipline

- Commit after every change/milestone, with a descriptive message.
- Confirm with the scientist before committing on each milestone.
- Never commit the `data/` tree or other unrelated changes in the parent `research/` repo.
