# paper_status.md — paper1 (checkpoint / resume handoff)

## Contribution (one sentence) — UNCONFIRMED
A GOFEE/AGOX global-optimization search generates amorphous Pt(P) (P interstitials in fcc Pt 3×3×3) across cell expansions, whose structure and crystallinity are characterized, and whose spin Hall conductivity is computed via FLAPW.

## Target venue / format
- Main: APS RevTeX 4.2 (`revtex4-2`, `aps` class), preprint option. Compiles with tectonic.
- SI: SPIE class (`spieman.cls` + `spiejour.bst`).
- Venue template swap deferred to submission (Phase G).

## Current state (updated 2026-09-21, Session 2)
- **Project scaffolded** mirroring `paper_femgo`: AGENTS.md, README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, .gitignore, `papers/paper1/` (main.tex + sections/ + figures/ + references.bib + supplementary/), `codes/`, `analysis/`.
- **Paper1 scaffolded** with empty section stubs (01_abstract … 06_ack_dataavail). No prose yet.
- **SHC pipeline built (`hpc_runs/`, Session 2 spec-driver)**: Run A (novelty+force filter + DFT re-opt → `opt_novel_<leaf>.traj` ×4), Run B (FLAPW SHC), 0%-P reference traj, dose↔at% helper, XRD benchmark adapter. Build-validated locally (filter ran on all 4 leaves; reference traj + XRD probe + SHC parse tested); FLAPW/GPAW run only on HPC.
- **SHC section is a placeholder** — no SHC numbers/claims until Run B results land.
- **Data audited:** Pt–P cell families `0_plus5cell` (+5%), `1_plus0cell` (+0%), `2_plus3cell` (+3%); `3_plus10cell` (+10%) **excluded**. `main.py` `SCALE_CELL=1.05` stale for +0/+3.

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| *(none frozen yet)* | | | |

## Citations (Phase D)
- `references.bib` empty (no prose yet). Populate per-section at the review gate.

## Drafting progress (Phase E — LaTeX-native, block-and-wait)
- [x] Project + paper1 scaffold (Session 1)
- [ ] Phase A: confirm contribution framing with owner
- [ ] Phase A.5: freeze CLAIMS.md
- [ ] Phase B: map claims to results
- [ ] sections/03_methods.tex (draft first)
- [ ] sections/04_results.tex (incl. SHC placeholder → fill when results land)
- [ ] sections/05_conclusion.tex
- [ ] sections/02_introduction.tex
- [ ] sections/06_ack_dataavail.tex
- [ ] sections/01_abstract.tex
- [ ] E2: compile the manuscript (first PDF review)

## Open decisions / next step
- [ ] Confirm contribution framing with owner (Phase A)
- [x] Decide which structures feed the SHC: **3 distinct novel+low-force amorphous minima
      per leaf (4 leaves) via `hpc_runs/select_reopt/filter_select.py`, DFT re-opted →
      `opt_novel_<leaf>.traj` ×4; + 0%-P +0-cell crystalline reference traj** (decided
      Session 2).
- [ ] Run the SHC calculation on HPC (Run B: `hpc_runs/shc/`, 4 + 1 pjsub) and fill the
      placeholder section; confirm xoptics SHC parse fields (spec G7).
- [ ] Run Run A on HPC for real DFT re-opt.
- [ ] XRD benchmark vs reference (existing `_run/0_lcb` pipeline) — simulated XRD of
      selected minima vs Shashank 2025 (I220/I111 0.33→3.14).
- [ ] Write `codes/` figure/analysis scripts and produce `analysis/` outputs.
- NEXT: submit Run A + Run B on HPC; then draft Methods (03_methods.tex).

