# paper_status.md — paper2 (checkpoint / resume handoff)

> **paper2 = current-results fork of paper1.** Same manuscript structure (main + SI),
> but all figures are referenced **directly from `analysis/figures/`** (the regenerated,
> current-style figures) rather than the original draft PNGs. Prose matches the current
> results: 13 runs (Run 1–13), 1,180 configs, peaks 0.079/0.259, true Boltzmann density.

## Contribution (one sentence) — UNCONFIRMED
A biased-exploration active-learning (GOFEE/AGOX) framework samples a minimum-ensemble of surrogate-relaxed Fe/MgO(001) structures, from which KDE state-density + Boltzmann analysis show the island (Volmer-Weber) mode is the thermodynamic ground state and that temperature alone cannot suppress it.

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Island mode is ground state | Fig_Prog / Fig_ConDen | E_glob island; ΔZ 2.5–5.0 Å | ✅ regenerated |
| Two degeneracy peaks | Fig_ConDen | ~0.079 & ~0.259 eV/atom | ✅ regenerated |
| Flat mode ~0.18 eV/atom above island | Fig_ConDen | energy penalty | ✅ |
| Temperature raises flat-mode probability but insufficient | Fig_Boltz | 300–10000 K | ✅ |
| Ensemble = 1,180 configs (13 runs) | Fig_convStateDens | 1,180 (seeds 3–15, stop_16 excl.) | ✅ matches disk |
| Island preferred due to localized Fe 3d at Fermi level | Fig_dos | PDOS peak at E_f | ✅ (2 seeds only) |

## Citations (Phase D)
- Main: `references.bib` (from draft `apssamp.bib`). All `\cite{}` resolve; 7 `eprint` fields wrapped in `\url{}` to fix compile.
- SI: `supplementary/report.bib`. All resolve.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Ported draft verbatim into `sections/` (01_abstract … 06_ack_dataavail)
- [x] E2: main.pdf + article.pdf compile cleanly (first PDF review)
- [x] Figure regeneration (Milestone 2) — all 8 figures in `analysis/figures/`
- [x] Data-consistency report (Milestone 3) — `analysis/DATA_CONSISTENCY_REPORT.md`
- [ ] Section-by-section review gate (owner) — prose is frozen, so this is a review pass, not re-drafting
- [ ] Owner inspects regenerated figures for similarity to draft

## Open decisions / next step
- [ ] Confirm contribution framing with owner
- [ ] Owner inspects regenerated figures + emitted datasets
- NEXT: owner review of regenerated figures + datasets; then continue writing from the draft.
