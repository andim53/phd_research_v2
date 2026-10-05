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

## Current state (updated 2026-10-05, Session 4ab)
- **Contribution framed and confirmed** (SHC dropped entirely from framing per owner, Session 4t).
- **CLAIMS.md v3 signed off** (MT-1..MT-4, M-1..M-1d, M-2, SI-1) — claim list frozen; manuscript must trace to it.
- **CNA/RDF structural cross-check done** (`codes/emit_cna_rdf.py` v1.1.0): Steinhardt q6 crystalline fraction + partial RDF for 9 leaves (0P/20P/30P × +0/+3/+5). Results in `analysis/cna_rdf/<leaf>/cna_rdf.json`.
- **Key numbers (crystalline fraction mean):** 0P 0.85–0.91 → 20/30P 0.14–0.22 (MT-1); 20P≈30P (MT-2); cell expansion +0→+3/+5: 20P 0.212→0.170→0.157, 30P 0.223→0.137→0.152 (MT-3).
- **XRD cross-check** (`data/17_PPt/DISCUSSION.md`): integrated CI 0.81–0.83→0.35–0.38 for P loading; cell effect only ~7% (weak) → CNA is the quantitative backbone for MT-3.
- **M-1d exploration→exploitation verified multi-seed** (61 seeds, 13 leaves): energy drop at iteration-10 LCB switch-on universal; |r| P-specific (0.7–0.9); gmin in latter half of budget. `analysis/explore_exploit/explore_exploit.json` + `fig_explore_exploit.png`.
- **Force-under-relaxation diagnostic** (NOT for the paper): P leaves are not force-converged (single-DFT-step evaluator); structural claims rest on energetics, re-check planned (Future work). `analysis/energy_vs_force/`, `analysis/force_convergence_probe.json`.
- SHC pipeline built (`hpc_runs/`, Sessions 2) but **out of scope** for this manuscript (Session 4t).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| MT-1 P amorphizes host | analysis/cna_rdf/*/cna_rdf.json | cryst.frac 0.854–0.913 → 0.137–0.223 | yes |
| MT-2 saturation 20P≈30P | analysis/cna_rdf/*/cna_rdf.json | 20P 0.157–0.212 vs 30P 0.137–0.223 (overlap) | yes |
| MT-3 cell expansion mild disorder | analysis/cna_rdf/*/cna_rdf.json | 20P 0.212→0.170→0.157; 30P 0.223→0.137→0.152 | yes |
| XRD CI supports MT-1 | data/17_PPt/DISCUSSION.md | 0.81–0.83 → 0.35–0.38 | yes |

## Citations (Phase D)
- `references.bib` populated (20 verified): `shashank2025`, `shi2025`, `yang2025`, `greer1993`, `gofee2020`, `gofee2022`, `agox2022`, `oganov2009`, `gpaw2010`, `ase2017`, `pymatgen2013`, `steinhardt1983`, `artrith2018`, `biswas2017`, `valladares2011`, `madanchi2024`, `setten2026`, `nahas2016`, `meltquench2026`, `activemlp2020`. All fetched via DOI/arXiv content negotiation. Wire into prose at the per-section review gate.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Project + paper1 scaffold (Session 1)
- [x] Phase A: contribution framing confirmed with owner (Session 4; SHC excluded)
- [x] Phase A.5: CLAIMS.md v3 — MT-1..MT-4, M-1..M-1d, M-2, SI-1 all signed off (Phase B evidence mapped)
- [x] Phase B: claims mapped to CNA/RDF JSONs + XRD table + explore/exploit JSON
- [ ] sections/03_methods.tex (placeholder — content lives in CLAIMS.md M-1..M-1d, M-2; draft prose here)
- [ ] sections/04_results.tex (placeholder — content lives in CLAIMS.md MT-1..MT-4 + M-1c; draft prose here)
- [ ] sections/05_conclusion.tex (placeholder)
- [ ] sections/02_introduction.tex (placeholder)
- [ ] sections/06_ack_dataavail.tex (placeholder)
- [ ] sections/01_abstract.tex (placeholder — draft after all sections approved)
- [ ] E2: compile the manuscript (first PDF review)

## Open decisions / next step
- [x] Owner reviewed M-1d figure + revised claim wording (Session 4ab).
- [x] Commit Session 4ab milestone (extractor, figure script, JSON, CLAIMS M-1d + Figures table, VERSIONS, LOG).
- [ ] Draft sections/03_methods.tex (global-optimization method, XRD + CNA/RDF crystallinity analysis) — block-and-wait review gate.
- [ ] Draft sections/04_results.tex (crystallinity MT-1..MT-4 + efficiency M-1c).
- [ ] SHC placeholder: **dropped from paper** (Session 4t) — no SHC section to fill.
- [ ] Build figure scripts → analysis/figures (partial RDF g_PtP/g_PP as standard figure; crystalline-fraction vs cell bar/line) — done for crystallinity 3-panel + explore/exploit; stage into papers/paper1/figures/ at compile.
- NEXT: draft sections/03_methods.tex (global-optimization method, XRD + CNA/RDF crystallinity analysis).
