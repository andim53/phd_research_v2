# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — UNCONFIRMED
A GOFEE/AGOX global-optimization search generates amorphous Pt(P) (P interstitials in fcc Pt 3×3×3) across cell expansions, whose structure and crystallinity are characterized, and whose spin Hall conductivity is computed via FLAPW.

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Current state (updated 2026-09-21, Session 1)
- **Project scaffolded** mirroring `paper_femgo`: AGENTS.md, README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, .gitignore, `papers/paper1/` (main.tex + sections/ + figures/ + references.bib + supplementary/), `codes/`, `analysis/`.
- **Paper1 scaffolded** with empty section stubs (01_abstract … 06_ack_dataavail). No prose yet.
- **SHC section is a placeholder** — the FLAPW SHC calculation is in progress; no SHC numbers/claims until results land.
- **Data audited:** Pt–P cell families `0_plus5cell` (+5%), `1_plus0cell` (+0%), `2_plus3cell` (+3%); `3_plus10cell` (+10%) **excluded**. `main.py` `SCALE_CELL=1.05` stale for +0/+3.

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| *(none frozen yet)* | | | |

## Citations (Phase D)
- `references.bib` empty (no prose yet). Populate per-section at the review gate.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Project + paper1 scaffold (Session 1)
- [ ] Phase A: confirm contribution framing with owner
- [ ] Phase A.5: freeze CLAIMS.md
- [ ] Phase B: map claims to results
- [ ] sections/03_methods.tex (draft first)
- [ ] sections/04_results.tex (incl. SHC placeholder → fill when results land)
- [ ] sections/05_conclusion.tex
- [ ] sections/02_introduction.tex
- [ ] sections/06_ack_dataavail.tex
- [ ] sections/01_abstract.tex
- [ ] E2: compile the manuscript (first PDF review)

## Open decisions / next step
- [ ] Confirm contribution framing with owner (Phase A)
- [ ] Decide which structures feed the SHC calculation (best-so-far vs representative set vs crystalline reference)
- [ ] Run the SHC calculation (in progress) and fill the placeholder section
- [ ] Write `codes/` figure/analysis scripts and produce `analysis/` outputs
- NEXT: confirm contribution framing with owner, then draft Methods (03_methods.tex).
