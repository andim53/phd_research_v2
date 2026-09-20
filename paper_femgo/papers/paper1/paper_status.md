# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — UNCONFIRMED
A biased-exploration active-learning (GOFEE/AGOX) framework samples a minimum-ensemble of surrogate-relaxed Fe/MgO(001) structures, from which KDE state-density + Boltzmann analysis show the island (Volmer-Weber) mode is the thermodynamic ground state and that temperature alone cannot suppress it.

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Island mode is ground state | Fig_Prog / Fig_ConDen | E_glob island; ΔZ 2.5–5.0 Å | pending |
| Two degeneracy peaks | Fig_ConDen | ~0.074 & ~0.255 eV/atom | pending |
| Flat mode ~0.18 eV/atom above island | Fig_ConDen | energy penalty | pending |
| Temperature raises flat-mode probability but insufficient | Fig_Boltz | 300–10000 K | pending |
| Ensemble = 1,207 configs (seeds 0–13) | Fig_convStateDens | 1,207 (draft number) | **MISMATCH** (disk: 1,180) |
| Island preferred due to localized Fe 3d at Fermi level | Fig_dos | PDOS peak at E_f | pending |

## Citations (Phase D)
- Main: `references.bib` (from draft `apssamp.bib`). All `\cite{}` resolve; 7 `eprint` fields wrapped in `\url{}` to fix compile.
- SI: `supplementary/report.bib`. All resolve.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Ported draft verbatim into `sections/` (01_abstract … 06_ack_dataavail)
- [x] E2: main.pdf + article.pdf compile cleanly (first PDF review)
- [ ] Section-by-section review gate (owner) — prose is frozen, so this is a review pass, not re-drafting
- [ ] Figure regeneration (Milestone 2) + owner inspection for similarity
- [ ] Data-consistency report (Milestone 3)

## Open decisions / next step
- [ ] Confirm contribution framing with owner
- [ ] Confirm whether to keep "1,207 / seeds 0–13" or update to disk reality (currently: keep as drafted, flag in report)
- NEXT: Milestone 2 — write & run figure-regeneration code in `codes/`.
