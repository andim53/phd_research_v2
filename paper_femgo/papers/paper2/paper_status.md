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

## Current state (updated 2026-09-26, through Session 17)
- **Created** as a fork of paper1 (Session 8). Figures referenced directly from `analysis/figures/` (regenerated, current style). Only `Fig_flow` (hand-drawn schematic) is kept locally in `paper2/figures/`.
- **Prose/numbers:** match current results — 13 runs (Run 1–13), 1,180 configs, peaks 0.079/0.259, true Boltzmann density (∫ρ_B dE = 1).
- **Compiles:** `main.pdf` (983 KB) + `article.pdf` (1.16 MB) build cleanly; all citations resolve.
- **Figure style:** inherits the accepted sans-serif style + all revisions (outward ticks, s=10 no-edge YlGnBu_r scatter, lw=1.0 density lines, peak lines zorder=20 + white shadow, Fig_Prog 13 viridis colors, Fig_mgo 3-panel + rel-E cap 3.7).

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
- [x] Forked from paper1 (Session 8)
- [x] E2: main.pdf + article.pdf compile cleanly
- [x] Figures referenced from `analysis/figures/` (regenerated, current style)
- [ ] Section-by-section review gate (owner) — prose is frozen, so this is a review pass, not re-drafting
- [ ] Owner inspects the current-results figures

## Sessions 9–17 delta (added 2026-09-26)
- **Figures rewired:** Fig_env_a/b.png and Fig_sup_a/b.png (VESTA-render two-panel tables) now referenced from `analysis/figures/` in the supplementary, via the canonical `codes/vesta_writer.py` pipeline.
- **Wetting-mode work (Fig_wetModes, Fig_wetLandscape):** built for Fe/MgO vs Fe-B/MgO (owner-pooled, no LOOCV) — **not yet wired into any `.tex`**; marked future work in this paper's `CLAIMS.md`.
- **2dlandau:** moved to `codes/2dlandau/`; VERSIONS.md reconciled.

## Open decisions / next step
- [ ] Confirm contribution framing with owner
- [ ] Owner decides paper1 vs paper2 as the "live" manuscript going forward
- NEXT: owner review of paper2's figures + prose; then continue writing from the current-results version.