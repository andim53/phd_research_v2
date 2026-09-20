# LOG.md — paper_femgo (append-only)

## Session 1 — 2026-09-20 (initialization)
**Goal (user-confirmed via clarify):** Initialize `scientific-paper-writing` on `paper_femgo`, port the finished draft from `tmp/draft_paper/`, regenerate all figures in the `_analysist` style, and audit data consistency.

**Actions taken:**
1. Scoped the task: read the finished draft (`apssamp.tex` main + `article.tex` SI), the `_analysist` reference figure code, and the data dirs.
2. Audited data: `data/femgo/` = seeds 3–15 (13 seeds, 1,297 raw / 1,180 under iter≥10), `stop_16` truncated (36), `mgofe/` = seeds 0–5 (seed_5 truncated at 26), DOS = 2 seeds.
3. Clarified 4 decisions with the owner (seed handling, layout, figure scope, doc scaffold) → spec approved.
4. Created project scaffold: `papers/paper1/` (main.tex + sections/ + figures/ + references.bib + supplementary/), `codes/`, `analysis/`.
5. Ported draft verbatim: split `apssamp.tex` into `sections/01_abstract … 06_ack_dataavail.tex`; copied figures + SI (article.tex, report.bib, spieman.cls, spiejour.bst).
6. Fixed figure filename mismatches (`fig_Boltz.png`→`Fig_Boltz.png`; removed stray `Fig_sup.png` from main figures).
7. Fixed 7 `eprint` fields in `references.bib` that carried raw PDF URLs with `_` (wrapped in `\url{}`) — these broke LaTeX compile.
8. Compiled both manuscripts with tectonic: `main.pdf` (14 pp) and `article.pdf` (SI) both build cleanly, all citations resolve.
9. Wrote doc scaffold: AGENTS.md, README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, paper_status.md, CLAIMS.md.

**Results:** Manuscript + SI compile cleanly; project scaffold in place; figure code pending (Milestone 2).

**Decisions & reasoning:**
- Full skill layout (`papers/paper1/` with per-section `.tex`) per owner choice.
- Manuscript numbers kept as drafted; discrepancies flagged in report only (owner choice).
- Fig_flow schematic excluded from regeneration (hand-drawn).

**Open items:**
- [ ] Milestone 2: write & run figure-regeneration code (Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_env, Fig_sup, Fig_mgo).
- [ ] Milestone 3: data-consistency report.
- [ ] Commit Milestone 1.

**Time:** 2026-09-20 ~19:30–19:45 JST

## Session 1 (cont.) — 2026-09-20 (Milestone 2: figure regeneration)
**Actions taken:**
10. Wrote `codes/common.py` (shared rcParams + AGOX data loading, iter≥10 filter) + 8 figure scripts.
11. Ran all 8 scripts under `agox_v2`; all produced PNGs in `analysis/figures/`.
12. Fixed Fig_sup source: `42_amorph_seed_3x3` was a BTa54 system (wrong); corrected to `18_..._repSeedDat101` (Fe9Mg9O9, 3×3) + `20_..._4x4` (Fe16Mg16O16, 4×4).

**Results:** Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_mgo, Fig_env, Fig_sup all regenerate. Landscape peaks at 0.079/0.259 eV/atom (vs paper's 0.074/0.255 — KDE bandwidth difference, flagged in report). Fig_sup Δz: 3×3=3.60 Å, 4×4=5.51 Å (matches ~1 Å/area trend).

**Decisions:** Fig_sup finite-size data lives in sibling `_analysist/1_result/` (not `paper_femgo/data/`).

**Open items:**
- [ ] Milestone 3: data-consistency report.
- [ ] Commit Milestone 2.

## Session 1 (cont.) — 2026-09-20 (Milestone 3: data-consistency report)
**Actions taken:**
13. Wrote `analysis/DATA_CONSISTENCY_REPORT.md` flagging all manuscript-vs-data mismatches.

**Results:** Report documents: (1) ensemble 1,207/14-seeds vs disk 1,180/13-seeds; (2) peak positions 0.074/0.255 vs 0.079/0.259; (3) DOS limited to 2 seeds; (4) mgofe seed_5 truncated; (5) finite-size data lives in sibling _analysist/1_result (not paper_femgo/data); (6) Fig_sup source corrected (42_amorph is BTa54, not Fe/MgO).

**Open items:**
- [ ] Commit Milestone 3.
- [ ] Owner review: confirm contribution framing, decide on ensemble-number reconciliation.

## Session 2 — 2026-09-20 (rewrite + emit→plot + finite-size data)
**Goal (user-confirmed via clarify):** (1) rewrite manuscript to 13 runs / 1,180 configs, exclude stop_16, update peaks to 0.079/0.259; (2) emit→plot refactor (CSV/JSON before plotting); (3) copy finite-size data into paper_femgo/data as femgo_3x3 / femgo_4x4.

**Actions taken:**
1. Copied finite-size data: `_analysist/1_result/18_..._repSeedDat101` → `data/femgo_3x3` (Fe9Mg9O9), `20_..._4x4` → `data/femgo_4x4` (Fe16Mg16O16). Updated `draw_si_supercell.py` to read from these local paths.
2. Added emit→plot to `common.py` (emit_combined_csv, emit_figure_json) + new `emit_datasets.py` generating 4 combined CSVs + 6 per-figure JSONs.
3. Refactored 6 data-driven draw scripts to read from the emitted JSONs (Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_mgo). Structure figs (Fig_env, Fig_sup) stay data-driven.
4. Rewrote manuscript: 14→13 runs, 1,207→1,180 configs, peaks 0.074/0.255→0.079/0.259 (prose + all captions + Data Availability). stop_16 excluded.
5. Recompiled main.pdf + article.pdf — both build cleanly.

**Results:** datasets in `analysis/` (dataset_femgo.csv 1,180; dataset_mgofe.csv 472; dataset_femgo_3x3.csv 268; dataset_femgo_4x4.csv 1,799; + 6 JSONs). All 8 figures regenerate from emitted data. Manuscript numbers now match disk.

**Decisions:** seed range written as "13 independent runs" (no explicit range, per owner). Peak positions updated to regenerated KDE values.

**Open items:**
- [ ] Commit Session 2.
- [ ] Owner inspects regenerated figures + datasets.
