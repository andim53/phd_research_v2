# AGENTS.md — Governing Rules for AI Agents Working on This Project

**Project:** Effect of Boron insertion on metal-film wetting on MgO — pure-Fe vs Fe-Co
hosts (MTJ / CoFeB relevance)
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

- Raw data lives in `data/` (AGOX/**GOFEE** structure-search databases), four systems:
  `femgo` (Fe/MgO), `febmgo` (Fe-B/MgO), `fecomgo` (Fe-Co/MgO), `fecobmgo` (Fe-Co-B/MgO).
  This directory is large (~190 MB) and is **not** part of paper commits — commit only
  analysis scripts, the scaffold, and draft files.
- The runs are GOFEE (GPR surrogate + LCB): a **biased** exploration seeded from a
  reference **flat** metal layer. Only structures with **iteration >= 10** are used
  (relaxation starts at iteration 10).
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** over all metal film atoms (Fe+Co)
  [Å]; ΔZ ≈ 0 = flat film (wet), ΔZ large = island (dewet).
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms** [eV/atom], global min = 0,
  computed per system over the iteration>=10 set. Flat/island basins split at ΔZ ≤ 1.0 Å.
- The `febmgo` / `fecobmgo` energy ranges contain relaxation artifacts / unphysical
  high-energy structures; the iteration filter + per-system global-min normalization
  window these out.
- Co systems have fewer seeds (fecomgo 5, fecobmgo 4) than the Fe systems (femgo 13,
  febmgo 7) — note this when reporting uncertainty.

## Commit discipline

- Commit after every change/milestone, with a descriptive message.
- Confirm with the scientist before committing on each milestone.
- Never commit the `data/` tree or other unrelated changes in the parent `research/` repo.
