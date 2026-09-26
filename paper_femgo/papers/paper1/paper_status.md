# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — UNCONFIRMED
A biased-exploration active-learning (GOFEE/AGOX) framework samples a minimum-ensemble of surrogate-relaxed Fe/MgO(001) structures, from which KDE state-density + Boltzmann analysis show the island (Volmer-Weber) mode is the thermodynamic ground state and that temperature alone cannot suppress it.

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Current state (updated 2026-09-26, through Session 17)
- **Manuscript:** ported verbatim into `sections/` (01_abstract … 06_ack_dataavail). Numbers corrected to current results: **13 runs (Run 1–13), 1,180 configs**, peaks **0.079 / 0.259 eV/atom**, `stop_16` excluded. `main.pdf` + `article.pdf` compile cleanly, all citations resolve.
- **Figures:** paper1 uses the **original draft PNGs** (in `paper1/figures/`) — it preserves draft provenance. The *regenerated/current-style* figures live in `analysis/figures/` and are used by **paper2**.
- **Figure style:** sans-serif rcParams ACCEPTED (common.py 1.4.0); ticks outward; no inner ticks; PCA scatter s=10 edgecolors=none, YlGnBu_r cmap; density line lw=1.0; peak lines zorder=20 + white shadow; Fig_Prog 13 viridis colors; Fig_mgo 3-panel + rel-E cap 3.7.
- **Boltzmann:** Fig_Boltz / Fig_mgo(c) use a **true Boltzmann density** (∫ρ_B dE = 1), not peak-normalized.
- **Data-consistency:** `analysis/DATA_CONSISTENCY_REPORT.md` — ensemble + peak mismatches RESOLVED; DOS limited to 2 seeds; finite-size data in `data/femgo_3x3` / `femgo_4x4`.
- **paper2:** created as a current-results fork (figures from `analysis/figures/`).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Island mode is ground state | Fig_Prog / Fig_ConDen | E_glob island; ΔZ 2.5–5.0 Å | ✅ |
| Two degeneracy peaks | Fig_ConDen | ~0.079 & ~0.259 eV/atom | ✅ |
| Flat mode ~0.18 eV/atom above island | Fig_ConDen | energy penalty | ✅ |
| Temperature raises flat-mode probability but insufficient | Fig_Boltz | 300–10000 K, ∫ρ_B dE=1 | ✅ |
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
- [x] Figure style accepted + all figure revisions (Session 5–7)
- [x] Boltzmann density (∫ρ_B dE = 1) (Session 7e)
- [ ] Section-by-section review gate (owner) — prose is frozen, so this is a review pass, not re-drafting
- [ ] Owner decides whether paper1 stays on draft figures or moves to regenerated (`analysis/figures/`)

## Sessions 9–17 delta (added 2026-09-26)
- **Boltzmann/texture:** true Boltzmann density (∫ρ_B dE=1) agreed; framed black legend boxes applied to Fig_Boltz/Fig_mgo/Fig_dos/Fig_Prog/Fig_convStateDens.
- **Wetting-mode work (Fig_wetModes, Fig_wetLandscape):** Fe/MgO vs Fe-B/MgO comparison figures built (LOOCV removed per owner; pooled) — **not yet in any `.tex`**, tracked as future work in `paper2/CLAIMS.md`.
- **VESTA canonical writer:** `codes/vesta_writer.py` (2.0.0) is now the single canonical writer; emitters refactored. Darker ~0.95× color preset is the default.
- **Fig S1 / S2:** Fig_env .vesta + PNG panels (Fig_env_a/b.png) and Fig_sup PNG panels (Fig_sup_a/b.png) rendered via canonical writer; both supplementary figures are now 2-column line-less tables. Old `Fig_env.png`/`Fig_sup.png` superseded.
- **2dlandau:** code moved to `codes/2dlandau/` (Session beyond this paper's main figures); `VERSIONS.md` paths reconciled along with the following fixes (inspect-this C1/M1/M2 fold, 2026-09-26).

## Open decisions / next step
- [ ] Confirm contribution framing with owner
- [ ] Owner decides paper1 vs paper2 as the "live" manuscript going forward
- NEXT: owner review of the two papers; then continue writing from the current-results version.