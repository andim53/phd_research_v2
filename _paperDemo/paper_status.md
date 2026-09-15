# paper_status.md — handoff / resume state

## Contribution (one sentence) — UNCONFIRMED (pending scientist review)
Boron consistently lowers the relative energy of the flat metal-film wetting state on MgO
(~0.04 eV/atom) in both a pure-Fe host and a Fe-Co host, while Co alone has little effect —
i.e. B promotes flat-film wetting independently of the host metal, relevant to interface
flatness in CoFeB/MgO MTJ stacks.

## Target venue / format
TBD — format-agnostic (no venue selected).

## Method note
- AGOX **GOFEE** (GPR surrogate + LCB): a **biased** search seeded from a reference
  **flat** metal layer. Filters to **iteration >= 10** (relax starts at iteration 10).
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** over all metal atoms (Fe+Co) [Å].
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms**, global min = 0 eV/atom, per system.
- Flat/island basins separated by ΔZ ≤ 1.0 Å.

## Systems (4)
femgo Fe/MgO (13 seeds) | febmgo Fe-B/MgO (7) | fecomgo Fe-Co/MgO (5) | fecobmgo Fe-Co-B/MgO (4)

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Ground state is an island (all 4) | analysis/pes_structures.csv | global-min ΔZ 2.75–3.77 Å | yes |
| B lowers flat-state energy in Fe host | analysis/pes_structures.csv | 0.1888 → 0.1493 eV/atom | yes |
| B lowers flat-state energy in Fe-Co host | analysis/pes_structures.csv | 0.1941 → 0.1494 eV/atom | yes |
| Co alone has little effect | analysis/pes_structures.csv | 0.1888 → 0.1941 eV/atom (+0.005) | yes |
| B increases flat fraction (both hosts) | analysis/pes_structures.csv | 0.165→0.208; 0.214→0.242 | yes |
| B does not bond to MgO | analysis/pes_structures.csv | B_contact_frac ≈ 0 | yes |

## Citations (Phase D)
- 0 fetched yet. Needed: CoFeB/MgO MTJ references (PMA, B diffusion, interface flatness),
  wetting/PES references.

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
