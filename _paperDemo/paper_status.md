# paper_status.md — handoff / resume state

## Contribution (one sentence) — UNCONFIRMED (pending scientist review)
Boron insertion lowers the relative energy of the flat Fe wetting state on MgO, bringing
it closer to the island ground state — i.e. B promotes flat-Fe wetting character,
relevant to interface flatness in MTJ stacks.

## Target venue / format
TBD — format-agnostic (no venue selected).

## Method note
- AGOX **GOFEE** (GPR surrogate + LCB): a **biased** search seeded from a reference
  **flat** Fe layer. Filters to **iteration >= 10** (relax starts at iteration 10).
- Flatness metric: **ΔZ = z(Fe_max) − z(Fe_min)** [Å]; ΔZ≈0 = flat Fe interface.
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms**, global min = 0 eV/atom, per system.
- Flat/island basins separated by a ΔZ threshold (default 1.0 Å).

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Ground state is an island (not flat) | analysis/pes_structures.csv | global-min ΔZ = 3.65 (fe) / 3.77 (feb) Å | yes |
| B lowers flat-basin relative energy | analysis/pes_structures.csv | flat-basin min 0.1888 → 0.1493 eV/atom | yes |
| B increases flat fraction sampled | analysis/pes_structures.csv | 0.165 → 0.208 | yes |
| B does not bond to MgO | analysis/wetting_metrics.csv | B_contact_frac ≈ 0 | yes |

## Citations (Phase D)
- 0 fetched yet. Needed: MTJ stack references (PMA, B diffusion in FeB/MgO), wetting/PES references.

## Drafting progress (Phase E — markdown-first, block-and-wait)
- [ ] sections/01_methods.md  (next)
- [ ] sections/02_results.md
- [ ] sections/03_discussion.md
- [ ] sections/04_introduction.md
- [ ] sections/05_conclusion.md
- [ ] sections/06_abstract.md
- [ ] E2: port all approved sections → paper.tex

## Open decisions / next step
- [ ] SCIENTIST: confirm or revise the contribution sentence (Phase A).
- [ ] Confirm ΔZ flat-cutoff (1.0 Å) and iteration>=10 filter.
- NEXT: after Phase A confirmation → draft sections/01_methods.md, present for review.
