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

## Session 3 — 2026-09-20 (Fig_Prog Run renumbering)
**Goal (user-confirmed via clarify):** relabel Fig_Prog from on-disk seeds (3–15) to independent runs (Run 1–13), and update the paper's Fig_Prog mention to reference Run 1.

**Actions taken:**
1. `emit_datasets.py`: renumber on-disk seeds 3–15 → Run 1–13 in Fig_Prog.json (run_map).
2. `draw_energy_progression.py` (1.1.0→1.2.0): label lines by the JSON key (Run N) instead of "Seed N".
3. Re-emitted Fig_Prog.json (keys Run 1..13) + regenerated Fig_Prog.png.
4. Manuscript: Fig_Prog caption → "13 independent runs (Run 1–13)"; results prose "Seed 0" → "Run 1".
5. Recompiled main.pdf — builds cleanly.

**Results:** Fig_Prog legend now shows Run 1–13; paper text references Run 1.

**Open items:**
- [ ] Commit Session 3.
- [ ] NOTE: Fig_convStateDens caption + convergence prose still use "seed 0 / seeds 0 and 1 / seeds 0 to 2" — flagged, not changed (different figure's discussion).

## Session 3 (cont.) — 2026-09-20 (Fig_convStateDens Run renumbering)
**Actions taken:**
6. `emit_datasets.py`: renumber Fig_convStateDens curves to Run 1 / Runs 1-2 / ... / Runs 1-13.
7. `draw_state_density_conv.py` (1.1.0→1.2.0): label curves by Run N.
8. Re-emitted Fig_convStateDens.json + regenerated PNG.
9. Manuscript: Fig_convStateDens caption "seed 0"→"Run 1"; convergence prose "seeds 0 and 1 / seeds 0 to 2"→"Runs 1 and 2 / Runs 1 to 3".
10. Recompiled main.pdf — builds cleanly.

**Results:** Fig_convStateDens now uses Run 1..13 labels; paper text consistent.

## Session 4 — 2026-09-20 (KDE smearing trial + revert)
**Goal (user-confirmed via clarify):** trial tight KDE smearing (bw=0.05, matching the amorphous 0_lcb system) on the state-density/Boltzmann figures; inspect the change; then revert to original and state the smearing parameter in Methods.

**Actions taken:**
1. Found the amorphous system's KDE parameter: `_run/0_lcb/2_analysist/11_bTa/7_fxg_0b/analysis_indices/stage2_landscape.json` → `data.params.kde_bw = 0.05`.
2. Applied `KDE_BW=0.05` to all state-density KDEs in emit_datasets.py (Fig_ConDen, Fig_Boltz, Fig_convStateDens, Fig_mgo); re-emitted + regenerated.
3. Inspected: tight KDE split the island basin into 3 peaks (0.054, 0.088, 0.259) — island basin is broad/bimodal (raw histogram 49→90→61 across 0.03–0.12, Δz mean ~3.4 Å). Flat peak unchanged.
4. **Reverted** KDE_BW to None (Scott's rule) per owner decision — figures back to 2 peaks (0.079, 0.259).
5. Added the KDE smearing parameter to Methods (03_methods.tex): Scott's rule h = M^{-1/5} σ.
6. Recompiled main.pdf — builds cleanly.

**Results:** Figures reverted to original wide smearing (2 peaks). Methods now states the KDE bandwidth (Scott's rule).

**Decisions:** Tight KDE (bw=0.05) revealed the island basin is broad/bimodal, but reverted to original per owner. The smearing parameter is documented in Methods.

**Open items:**
- [ ] Commit Session 4.

## Session 5 — 2026-09-20 (figure style trial — sans-serif)
**Goal (user-confirmed via clarify):** test the owner's sans-serif matplotlib rcParams on all figures; owner reviews and accepts/rejects.

**Actions taken:**
1. Overwrote CUSTOM_RC_PARAMS in common.py with the owner's style: font sans-serif (Helvetica/Arial/DejaVu Sans), size 11, ticks-in, top/right ticks, legend.frameon=True edgecolor black. Kept autolayout + dpi 300 for headless output. Recorded the old _analysist serif style as OLD_SOURCE_STYLE for easy revert.
2. Bumped common.py 1.1.0→1.2.0.
3. Regenerated ALL 8 figures (Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_mgo, Fig_env, Fig_sup) — verified valid.

**Result:** figures in analysis/figures/ now use the sans-serif style, pending owner review.

**Decision:** TRIAL — revert via OLD_SOURCE_STYLE if rejected.

## Session 6 — 2026-09-20 (accept style; remove inner ticks; cap rel-E at 0.7 eV/atom)
**Goal (owner):** accept the sans-serif style; remove inner (top/right) ticks; cap the relative-energy axis at 0.7 eV/atom.

**Actions taken:**
1. ACCEPTED the sans-serif style (common.py 1.2.0→1.3.0).
2. Removed inner ticks: dropped xtick.top / ytick.right from CUSTOM_RC_PARAMS.
3. Capped relative-energy axis at 0.7 eV/atom in Fig_ConDen (y), Fig_Boltz (x), Fig_convStateDens (y), Fig_mgo (y).
4. Bumped draw script versions (landscape/boltzmann/si_mgo→1.2.0, state_density_conv→1.3.0).
5. Regenerated all 8 figures.

**Result:** figures show accepted style, no inner ticks, rel-E axis ≤ 0.7 eV/atom.

**Decision:** style ACCEPTED (no longer a trial).

## Session 7 — 2026-09-21 (figure revision batch)
**Goal (user-confirmed via clarify):** 6 figure changes.

**Actions taken:**
1. common.py 1.4.0: tick direction in→out (outward ticks).
2. Fig_ConDen + Fig_mgo scatter: s=5→10, edgecolors black→none (color gradient readable).
3. State-density/Boltzmann/conv line widths: lw 1.5→1.0 (match axis).
4. Fig_Prog: 13 runs now use 13 distinct viridis colors, single solid linestyle (was 4 colors × 4 styles repeating).
5. Fig_mgo: rel-energy axis cap 0.7→3.7 eV/atom.
6. Fig_mgo: added 3rd panel (c) temperature-dependent Boltzmann probability (data emitted in emit_datasets.py 1.2.0); SI caption updated to describe (c) as Boltzmann distribution.
7. Regenerated all 8 figures; recompiled SI (article.pdf).

**Result:** figures updated per spec; SI compiles.

**Decision:** PCA scatter s=10 edgecolors='none'; Fig_Prog viridis 13 colors solid; Fig_mgo cap 3.7.

## Session 7b — 2026-09-21 (fix Fig_mgo state-density KDE cutoff)
**Issue (owner):** Fig_mgo state-density KDE looked cut off in relative energy.
**Diagnosis:** emit_datasets.py used the shared E_LIMIT (-0.1, 1.6) for the mgo KDE grid, but the Fig_mgo axis cap was raised to 3.7 — so the density curve terminated at 1.6, well below the axis edge.
**Fix:** emit_mgo now uses a dedicated grid to 3.7 (mgo_e_max), so the density curve reaches the axis edge (density ~0.013 at 3.7). emit_datasets.py 1.2.0→1.3.0.
**Result:** Fig_mgo state density no longer truncated; regenerated + committed.

## Session 7c — 2026-09-21 (PCA scatter colormap: visible on white)
**Issue (owner):** PuBu colormap was hard to see against the white background (light flat points vanished).
**Fix:** switched PCA Δz scatter cmap PuBu→YlGnBu_r (dark blue at low Δz, light yellow at high Δz) in Fig_ConDen + Fig_mgo. draw_landscape.py 1.3.0→1.4.0, draw_si_mgo.py 1.3.0→1.4.0.
**Result:** flat points now visible on white; both figures regenerated.

## Session 7d — 2026-09-21 (peak dashed lines: pop over data)
**Issue (owner):** island/flat dashed lines in Fig_Boltz + Fig_ConDen were hard to see behind the data lines/curves.
**Fix:** raised peak lines to zorder=20 (outermost) and added a white withStroke shadow (lw 3.5) — same effect as the text labels. draw_landscape.py 1.4.0→1.5.0, draw_boltzmann.py 1.3.0→1.4.0.
**Result:** peak lines now pop clearly over the graphs; both figures regenerated.

## Session 7e — 2026-09-21 (Boltzmann: peak-normalized -> true density ∫P dE=1)
**Goal (owner):** change Fig_Boltz definition from peak-normalized probability to a true Boltzmann density.
**Fix:** emitter (emit_datasets.py 1.3.0→1.4.0) uses np.trapz over the dense grid for Z (continuous ∫=1 density) instead of sum+/max(); applied to Fig_Boltz and Fig_mgo panel (c). draw_boltzmann.py 1.4.0→1.5.0 and draw_si_mgo.py 1.4.0→1.5.0: ylabel -> "Boltzmann density rho_B(E) (1/eV)", dynamic ylim.
**Text:** Fig_Boltz caption + results prose -> Boltzmann density with ∫dE=1; SI Fig_mgo(c) caption updated.
**Result:** every T-density trapezoid-integrates to 1.0; curves comparable across T. Both PDFs recompile.
