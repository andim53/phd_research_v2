# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — CONFIRMED (owner, Session 4; reframed Session 4b/4c)
Cheap LCAO-DFT global-optimization screening — using the Steinhardt q6 crystalline-fraction as the structural descriptor — identifies amorphous minima, so the expensive all-electron DFT (FLAPW) spin-Hall step runs only on them; applied to interstitial Pt(P), it identifies 20–30 at% P as the onset of structural amorphization, with the effect saturating in concentration and modestly increasing under +3/+5% cell expansion.

> **Scope (Session 4t):** **FLAPW SHC is dropped entirely from the paper** — the contribution is the cheap, reference-dependent screening → structural verification pipeline. No SHC claims are made. (The `hpc_runs/` SHC pipeline exists but is out of scope for this manuscript.)
>
> **Experimental anchor (Session 4b):** Shashank et al. 2025 (\cite{shashank2025}) = direct experimental Pt(P) amorphous evidence (ion dose+energy route). Our 20–30 at% P is framed as the **onset regime** of the interstitial route, **not** an absolute experimental P threshold (their box-model dose→at% onset ≈ 35–66 at%).

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Current state (updated 2026-10-05, Session 4at)
- **Contribution framed and confirmed** (SHC dropped entirely from framing per owner, Session 4t).
- **CLAIMS.md v7 signed off** (MT-1..MT-6, M-1..M-1d, M-2) — claim list frozen; manuscript must trace to it. **v7 (Session 4bn): adds MT-6 — comparative validation against Shashank et al. 2025** (our 20–30 at% P onset consistent with their converted ~36 at% P onset; box-model dose→at% conversion, Table 1 + `fig_crystallinity_vs_concentration.png`). **v6 (Session 4at): crystalline-fraction energy cap tightened 0.3 → 0.1 eV/atom** (per owner), matching the XRD lowest-window convention. **SI-1 dropped (Session 4bc):** the Ta/W polymorphism demonstration is removed from the SI; the polymorphic-host reference-choice point stays in the main text (M-3, MT-5) as a design statement, with the 5 Ta/W refs still cited in Methods.
- **CNA/RDF structural cross-check done** (`codes/emit_cna_rdf.py` v1.1.0): Steinhardt q6 crystalline fraction + partial RDF for 9 leaves (0P/20P/30P × +0/+3/+5). Results in `analysis/cna_rdf/<leaf>/cna_rdf.json` — **canonical data now at e_max=0.1 eV/atom**.
- **Key numbers (crystalline fraction mean, e_max=0.1):** 0P 0.99 → 20/30P 0.09–0.18 (MT-1); 20P≈30P (MT-2); cell expansion +0→+3/+5: 20P 0.184→0.137→0.094, 30P 0.176→0.098→0.098 (MT-3).
- **XRD cross-check** (`data/17_PPt/DISCUSSION.md`): integrated CI 0.81–0.83→0.35–0.38 for P loading; cell effect only ~7% (weak) → CNA is the quantitative backbone for MT-3.
- **M-1d exploration→exploitation verified multi-seed** (60 seeds, 12 leaves; 4×4 leaf excluded): energy drop at iteration-10 LCB switch-on universal; |r| P-specific (0.7–0.9); gmin in latter half of budget. `analysis/explore_exploit/explore_exploit.json` + `fig_explore_exploit.png`.
- **R-1e surrogate performance (Fig 3) tightened to 0.1 eV/atom** (Session 4au): MAE/GPR σ now reported at the single 0–0.1 eV/atom window (bar chart, one bar per leaf grouped by P loading); multi-window "error grows with distance" trend dropped. `analysis/surrogate_perf/surrogate_perf.json` (e_max=0.1) + `fig_surrogate_perf.png` (v3.0.0).
- **Force-under-relaxation diagnostic** (NOT for the paper): P leaves are not force-converged (single-DFT-step evaluator); structural claims rest on energetics, re-check planned (Future work). `analysis/energy_vs_force/`, `analysis/force_convergence_probe.json`.
- SHC pipeline built (`hpc_runs/`, Sessions 2) but **out of scope** for this manuscript (Session 4t).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| MT-1 P amorphizes host | analysis/cna_rdf/*/cna_rdf.json | cryst.frac 0.99 → 0.09–0.18 (e_max=0.1) | yes |
| MT-2 saturation 20P≈30P | analysis/cna_rdf/*/cna_rdf.json | 20P 0.094–0.184 vs 30P 0.098–0.176 (overlap) | yes |
| MT-3 cell expansion mild disorder | analysis/cna_rdf/*/cna_rdf.json | 20P 0.184→0.137→0.094; 30P 0.176→0.098→0.098 | yes |
| XRD CI supports MT-1 | data/17_PPt/DISCUSSION.md | 0.81–0.83 → 0.35–0.38 | yes |

## Citations (Phase D)
- `references.bib` populated (29 verified): `shashank2025`, `shi2025`, `yang2025`, `greer1993`, `gofee2020`, `gofee2022`, `agox2022`, `oganov2009`, `gpaw2010`, `ase2017`, `pymatgen2013`, `steinhardt1983`, `artrith2018`, `biswas2017`, `valladares2011`, `madanchi2024`, `setten2026`, `nahas2016`, `meltquench2026`, `activemlp2020` (20 main) + `colin2017`, `kozhukhovska2026`, `barmak2017`, `liubarmak2016`, `chattaraj2020` (5 polymorphic-host refs, cited in Methods) + **`fritz2018`, `liao2019`, `turek2019`, `yoon2025` (Session 4bq: Introduction SHC-motivation + cost + amorphous heavy-metal examples + power-consumption factor)**. All fetched via DOI/arXiv content negotiation. Wire into prose at the per-section review gate.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Project + paper1 scaffold (Session 1)
- [x] Phase A: contribution framing confirmed with owner (Session 4; SHC excluded)
- [x] Phase A.5: CLAIMS.md v3 — MT-1..MT-4, M-1..M-1d, M-2, SI-1 all signed off (Phase B evidence mapped)
- [x] Phase B: claims mapped to CNA/RDF JSONs + XRD table + explore/exploit JSON
- [x] sections/03_methods.tex (DRAFTED Session 4ao — traces M-1, M-1b, M-2, M-3; 19 cites all resolve; compiles clean; **Session 4ap: de-code-like'd prose, added iteration-timeline figure Fig. 1; Session 4aq: M-1c/M-1d/M-1e moved to Results**) — **awaiting owner review**
- [x] sections/04_results.tex (DRAFTED Session 4aq — traces R-1c, R-1d, R-1e; **Session 4ar: crystallinity MT-1..MT-4 drafted + Fig. 2; Session 4as: XRD cross-check figure Fig. 3; Session 4bn: MT-6 comparative-validation subsection + Table 1 + Fig. 6**) — **APPROVED (Session 4bd)**
- [x] sections/05_conclusion.tex (DRAFTED Session 4bd — mirrors contribution sentence; no new claims; MT-6 validation sentence added Session 4bp) — **APPROVED (Session 4bq)**
- [x] sections/02_introduction.tex (DRAFTED Session 4bq — motivation: SHC + cost + amorphous examples; power-consumption factor; reference-anchored approach; femgo-style closing + roadmap; **APPROVED (Session 4bq)**)
- [x] sections/06_ack_dataavail.tex (DRAFTED Session 4bq — acknowledgments: JSPS KAKENHI 25K07225, CSpnRN Osaka U, MEXT X-NICS Tohoku U, Kyushu U + ISSP U Tokyo facilities; data availability placeholder) — **awaiting owner review**
- [ ] sections/01_abstract.tex (placeholder — draft after all sections approved)
- [ ] E2: compile the manuscript (first PDF review)

## Open decisions / next step
- [x] Owner reviewed M-1d figure + revised claim wording (Session 4ab).
- [x] Commit Session 4ab milestone (extractor, figure script, JSON, CLAIMS M-1d + Figures table, VERSIONS, LOG).
- [x] Draft sections/03_methods.tex (global-optimization method, XRD + CNA/RDF crystallinity analysis) — **DRAFTED Session 4ao, awaiting owner review (block-and-wait gate).**
- [x] Draft sections/04_results.tex (crystallinity MT-1..MT-4 + efficiency R-1c) — **DONE Session 4ar** (crystallinity drafted; efficiency R-1c drafted Session 4aq). **APPROVED Session 4bd.**
- [x] Draft sections/05_conclusion.tex — **DONE Session 4bd** (mirrors contribution sentence; no new claims). **APPROVED Session 4bq.**
- [x] Draft sections/02_introduction.tex — **DONE Session 4bq** (motivation SHC/cost/amorphous examples + power-consumption factor + reference-anchored approach + femgo-style closing/roadmap). **APPROVED Session 4bq.**
- [x] Draft sections/06_ack_dataavail.tex — **DONE Session 4bq** (acknowledgments: JSPS KAKENHI 25K07225, CSpnRN Osaka U, MEXT X-NICS Tohoku U, Kyushu U/ISSP U Tokyo facilities; data availability placeholder). **Awaiting owner review.**
- [ ] SHC placeholder: **dropped from paper** (Session 4t) — no SHC section to fill.
- [ ] Build figure scripts → analysis/figures (partial RDF g_PtP/g_PP as standard figure; crystalline-fraction vs cell bar/line) — done for crystallinity 3-panel + explore/exploit + iteration-timeline (Fig. 1); stage into papers/paper1/figures/ at compile.
- NEXT: owner approves 06_ack_dataavail.tex; then draft 01_abstract.tex, then E2 first-PDF review.
