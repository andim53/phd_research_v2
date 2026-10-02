# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — CONFIRMED (owner, Session 4; reframed Session 4b/4c)
Cheap LCAO-DFT global-optimization screening — using the Steinhardt q6 crystalline-fraction as the structural descriptor — identifies amorphous minima, so the expensive all-electron DFT (FLAPW) spin-Hall step runs only on them; applied to interstitial Pt(P), it identifies 20–30 at% P as the onset of structural amorphization, with the effect saturating in concentration and modestly increasing under +3/+5% cell expansion.

> **Scope (Session 4/4b):** FLAPW SHC is the *expensive spin-Hall step* but **not part of the one-sentence contribution** for now. Contribution = cheap screening descriptor + its outputs. SHC section stays a placeholder until the calculation is done.
>
> **Experimental anchor (Session 4b):** Shashank et al. 2025 (\cite{shashank2025}) = direct experimental Pt(P) amorphous evidence (ion dose+energy route). Our 20–30 at% P is framed as the **onset regime** of the interstitial route, **not** an absolute experimental P threshold (their box-model dose→at% onset ≈ 35–66 at%).

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Current state (updated 2026-09-30, Session 4)
- **Contribution framed** and confirmed (SHC dropped from framing per owner).
- **CLAIMS.md v2 drafted** (MT-1..MT-3) — awaiting owner sign-off on the claim list.
- **CNA/RDF structural cross-check done** (`codes/emit_cna_rdf.py` v1.0.0): Steinhardt q6 crystalline fraction + partial RDF for 9 leaves (0P/20P/30P × +0/+3/+5). Results in `analysis/cna_rdf/<leaf>/cna_rdf.json`.
- **Key numbers (crystalline fraction mean):** 0P 0.85–0.91 → 20/30P 0.14–0.22 (MT-1); 20P≈30P (MT-2); cell expansion +0→+3/+5: 20P 0.212→0.170→0.157, 30P 0.223→0.137→0.152 (MT-3).
- **XRD cross-check** (`data/17_PPt/DISCUSSION.md`): integrated CI 0.81–0.83→0.35–0.38 for P loading; cell effect only ~7% (weak) → CNA is the quantitative backbone for MT-3.
- SHC pipeline built (`hpc_runs/`, Sessions 2); Run A/B not yet run on HPC.

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
- [x] Phase A.5: CLAIMS.md v2 — MT-1..MT-3 drafted + CNA/RDF backbone; **awaiting owner sign-off** (Phase B evidence mapped)
- [x] Phase B: claims mapped to CNA/RDF JSONs + XRD table
- [x] sections/03_methods.tex (drafted Session 4f — **awaiting owner review**)
- [x] sections/04_results.tex (efficiency subsection drafted Session 4i; crystallinity MT-1..MT-3 pending)
- [ ] sections/05_conclusion.tex (placeholder + efficiency note Session 4i)
- [ ] sections/02_introduction.tex
- [ ] sections/06_ack_dataavail.tex
- [ ] sections/01_abstract.tex
- [ ] E2: compile the manuscript (first PDF review)

## Open decisions / next step
- [ ] Owner reviews MT-1..MT-3 in chat and checks CLAIMS.md sign-off box → fully freeze v2.
- [ ] Commit this milestone (emit_cna_rdf.py + analysis/cna_rdf + CLAIMS v2 + LOG/VERSIONS).
- [ ] Run Run A + Run B on HPC; fill SHC placeholder when results land.
- [ ] Build figure scripts → analysis/figures (partial RDF g_PtP/g_PP as standard figure; crystalline-fraction vs cell bar/line).
- NEXT: owner sign-off on CLAIMS.md v2, then commit; then draft sections/03_methods.tex (global-optimization method, XRD + CNA/RDF crystallinity analysis).
