# paper_status.md — handoff / resume state

## Contribution (one sentence) — UNCONFIRMED (pending scientist review)
Boron insertion into the Fe deposition layer roughens the Fe film and lifts it off the
MgO interface, while B itself does not bond to MgO (stays within the Fe film) — relevant
to interface flatness and B segregation in MTJ stacks.

## Target venue / format
TBD — format-agnostic (no venue selected).

## Method note
AGOX **GOFEE** global-optimization search (GPR surrogate + LCB). Structures selected by
**relative energy per atom** `dE/N = (E_i - E_globalmin)/N_atoms`, global min = 0 eV/atom,
per system, window 0.05 eV/atom.

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| B roughens the Fe film | analysis/wetting_metrics.csv | Fe_roughness 1.015→1.104 Å, p=0.015, d=−0.63 | yes |
| B lifts Fe off the interface | analysis/wetting_metrics.csv | Fe_height_mean 3.387→3.569 Å, p=0.001, d=−0.75 | yes |
| B does not bond to MgO | analysis/wetting_metrics.csv | B_contact_frac ≈ 0 (1/72 has a single B–O contact) | yes (mostly) |
| B changes lateral coverage | analysis/wetting_metrics.csv | fe_coverage 0.152→0.147, p=0.967 | NO — not supported |
| B lowers Fe–O contact | analysis/wetting_metrics.csv | Fe_contact_frac 0.284→0.272, p=0.106 | NO — not supported |

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
- [ ] Confirm wetting-metric operationalization + 0.05 eV/atom window acceptable.
- NEXT: after Phase A confirmation → draft sections/01_methods.md, present for review.
