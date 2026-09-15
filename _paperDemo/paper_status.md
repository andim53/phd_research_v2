# paper_status.md — handoff / resume state

## Contribution (one sentence) — UNCONFIRMED (pending scientist review)
Boron insertion into the Fe deposition layer roughens the Fe film, lifts it off the
MgO interface, and shrinks its lateral footprint, while B itself does not bond to MgO —
relevant to interface flatness / B segregation in MTJ stacks.

## Target venue / format
TBD — format-agnostic (no venue selected).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| B roughens the Fe film | analysis/wetting_metrics.csv | Fe_roughness 0.989→1.103 Å, p=0.015, d=−0.87 | yes |
| B lifts Fe off the interface | analysis/wetting_metrics.csv | Fe_height_mean 3.342→3.540 Å, p=0.009, d=−0.87 | yes |
| B shrinks lateral Fe footprint | analysis/wetting_metrics.csv | fe_coverage 0.181→0.143, p=0.010, d=+0.39 | yes |
| B does not bond to MgO | analysis/wetting_metrics.csv | B_contact_frac = 0 in all 51 windowed structures | yes |
| (weak) B lowers Fe–O contact | analysis/wetting_metrics.csv | Fe_contact_frac 0.296→0.278, p=0.051 | marginal — do NOT state as strong |

## Citations (Phase D)
- 0 fetched yet. Needed: MTJ stack references (PMA, B diffusion in FeB/MgO), wetting/interface references.

## Drafting progress (Phase E — markdown-first, block-and-wait)
- [ ] sections/01_methods.md  (next)
- [ ] sections/02_results.md
- [ ] sections/03_discussion.md
- [ ] sections/04_introduction.md
- [ ] sections/05_conclusion.md
- [ ] sections/06_abstract.md
- [ ] E2: port all approved sections → paper.tex

## Open decisions / next step
- [ ] SCIENTIST: confirm or revise the contribution sentence (Phase A).
- [ ] Confirm wetting-metric operationalization is acceptable.
- NEXT: after Phase A confirmation → draft sections/01_methods.md, present for review.
