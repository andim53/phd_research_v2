# paper_status.md — handoff / resume state

## Contribution (one sentence) — CONFIRMED (signed off 2026-09-16)
Boron consistently lowers the relative energy of the flat metal-film wetting state on MgO
(~0.04 eV/atom) in both a pure-Fe host and a Fe-Co host, while Co alone has little effect —
i.e. B promotes flat-film wetting independently of the host metal, relevant to interface
flatness in CoFeB/MgO MTJ stacks.

**Claim list frozen:** `CLAIMS.md` **v2** (2026-09-17; supersedes v1 of 2026-09-16).
v2 withdraws MT-6 (flat-basin sampling fraction — see CLAIMS.md changelog). Do not add/drop
claims without bumping the version again.

## Target venue / format
TBD — format-agnostic (no venue selected).

## Method note
- AGOX **GOFEE** (GPR surrogate + LCB): a **biased** search seeded from a reference
  **flat** metal layer. Filters to **iteration >= 10** (relax starts at iteration 10).
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** over all metal atoms (Fe+Co) [Å].
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms**, global min = 0 eV/atom, per system.
- Flat/island basins separated by ΔZ ≤ 1.0 Å.

## Systems (4)
femgo Fe/MgO (13 replicas with data) | febmgo Fe-B/MgO (6) | fecomgo Fe-Co/MgO (5) | fecobmgo Fe-Co-B/MgO (4)
(Replica counts verified 2026-09-17 by `scripts/ensemble_analysis.py`: febmgo has 7 `seed_*`
dirs but `seed_6`'s db is EMPTY, so 6 carry data. femgo also has a `stop_16` partial run.)

## Supplementary Material: Method-parameter sensitivity
One SI study covering three method parameters of the biased-exploration scheme, all on
Fe₂₅Mg₂₅O₂₅ with a common `femgo` baseline (rattle 1.5/2.3, kappa=2, no dipole):
- **Rattle:** `param_ratt05` (1.0/1.8), `param_ratt1` (0.5/1.3)
- **Kappa (LCB):** `femgo_kappa/1_k1`, `0_k3`, `2_k4`
- **Dipole:** `femgo_dip` (`dipolelayer: xy`)

Deliverables: `figures/method_sensitivity_{rattle,kappa,dipole}.png`,
`analysis/method_sensitivity.csv`.
Status: **SUPPLEMENTARY (SI)** — validates the biased-exploration scheme; not main-text.

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Lowest-energy structure found is an island (all 4) | analysis/pes_structures.csv | ΔZ 2.75–3.77 Å at lowest energy | yes |
| Flat config is a distinct, higher-energy basin | analysis/pes_structures.csv | flat-basin dE/N > 0 (0.149–0.194) | yes |
| B lowers flat-basin energy in Fe host | analysis/pes_structures.csv | 0.1888 → 0.1493 eV/atom | yes |
| B lowers flat-basin energy in Fe-Co host | analysis/pes_structures.csv | 0.1941 → 0.1494 eV/atom | yes |
| Co alone has little effect | analysis/pes_structures.csv | 0.1888 → 0.1941 eV/atom (+0.005) | yes |
| ~~B increases flat fraction (both hosts)~~ | — | **WITHDRAWN (MT-6, CLAIMS v2)** — biased-exploration weight, and the exploration operator is not matched across systems | — |
| B does not bond to MgO | analysis/pes_structures.csv | B_contact_frac ≈ 0 | yes |
| **[SI]** Island origin: reduced Fe–O hybridization | analysis/pdos_metrics.csv | d-band centre −0.23→+0.60 eV; O-pz 43.9→42.4 | yes |
| **[SI]** Island origin: weaker magnetism/higher stability | analysis/pdos_metrics.csv | spin pol 5.81→4.37; DOS(E_F) 104→78 | yes |
| **[SI]** Island origin is strain relief, not interfacial re-hybridisation | analysis/interface_analysis.csv | island interface Fe d-centre +0.51 (not flat-like −0.23) | yes — refines the picture |
| **[SI]** Fe sits directly atop O at the interface | analysis/interface_analysis.csv | 25/25 flat, 9/9 island atop O; 0 atop Mg | yes |
| **[SI]** Rattle strength matters: reducing it degrades the search | analysis/method_sensitivity.csv | per-seed best 0.050 → 0.27–0.29 eV/atom | yes |
| **[SI]** Reduced rattle under-samples the flat basin | analysis/method_sensitivity.csv | flat fraction 0.181 → 0.030/0.015 | yes |
| **[SI]** Result robust to kappa (LCB) | analysis/method_sensitivity.csv | per-seed best 0.039–0.056 eV/atom across k=1–4 | yes |
| **[SI]** Result robust to the dipole correction | analysis/method_sensitivity.csv | per-seed best 0.050 → 0.056 eV/atom (ns) | yes (outcome-level) |

**Supplementary Material — PDOS (femgo only):** flat reference (`dos_seed_4.csv`, ΔZ=0.000)
vs island GS (`dos_seed_3.csv`, ΔZ=3.652); matched projections (Fe-dz2, O-pz), E vs E_F.
**Status: SUPPLEMENTARY (SI).** Includes the site-resolved / Fe-on-O registry subsection.
**DEFERRED:** the Fe-B PDOS comparison (`data/dos_febmgo_gs/`) — its projections (full d/p)
don't match the femgo set (dz2/pz), so it is not yet analysable side-by-side.

**NOT claimed:** that the flat state is *metastable* (needs convergence + Hessian + barrier).
The structures are **not DFT-converged** (surrogate relaxation + 1 GPAW step; residual
forces ~1–2 eV/Å) — see the relaxation caveat below and `relaxation/`.

## Relaxation caveat
- Candidates are relaxed by the **GPR surrogate** (100 steps, start_relax=10), then
  evaluated with **1 GPAW step** (`fmax=0.05, steps=1`). Residual max |F| = 1.0–2.4 eV/Å.
- "Lowest-energy"/"basin" = lowest DFT energy *found*, not a converged minimum.
- Planned fix: full DFT re-relaxation of low-force distinct structures (`relaxation/`).

## Citations (Phase D)
- 6 verified & in `references.bib`: agox2020, gofee2017, oganov2011, gpaw2014, pbe1996,
  greer1993. All `\cite{}` keys in 01_methods.md and 03_discussion.md (greer1993) resolve.
- UNVERIFIED placeholders in 03_discussion.md: cofebmgo_mtj, cofebmgo_pma, b_diffusion_mtj
  (MTJ context) — fetch before the LaTeX port.

## Drafting progress (Phase E — markdown-first, block-and-wait)
- [~] sections/01_methods.md  (APPROVED 2026-09-16; REVISED v3 2026-09-17 — needs re-approval)
      v3: §1.2 exploration schedule stated per model (Fe-Co uses a third, species-permutation
      generator); mermaid made generator-count-agnostic; "Bias" paragraph states the
      reference-layer composition per model; seed count 7 → 6. No claim changed.
- [~] sections/02_results.md  (APPROVED 2026-09-16; RECONSTRUCTED v2 2026-09-17 — needs re-approval)
      v2: reorganized by PHASE under the revised core framing —
      §2.1 the two-phase landscape (both phases populated; island is the ground state
      *despite* the flat bias → positive control, MT-1; flat is a distinct higher-energy
      basin, MT-2; branches are families of structures); §2.2 the flat (wetting) phase under
      Co/B/CoB (MT-3, MT-4, MT-5, MT-7); §2.3 the island (dewetting) phase and the
      flat–island separation; §2.4 summary.
      The withdrawn MT-6 flat-fraction comparison has been **removed**. Two [NEW]/[PENDING]
      blocks require sign-off (see below). The old section's single-lever ordering and its
      "seeded from a flat reference" remark (previously a caveat, now a positive control) are
      gone.
- [~] sections/03_discussion.md  (REVISED v3 2026-09-17 — awaiting scientist review)
      v3 changes: §3.2 confusion-principle claim restricted to the B addition (Co alone
      raises the flat energy → element count is not the driver); §3.1 unsupported
      "bulk-like" comparison removed and registry wording made precise (interface atoms
      25/25 → 9/25, d-centre +0.51/+0.60 eV); §3.2 B–MgO bound restored (1 of 72);
      §3.5 unequal-seed-count limitation added. No MT/SI claim changed.
      v3 also strikes the flat-fraction clause from §3.2 (consequence of the MT-6 withdrawal).
- [ ] sections/04_introduction.md
- [ ] sections/05_conclusion.md
- [ ] sections/06_abstract.md
- [ ] E2: port all approved sections → paper.tex

## RESOLVED: withdrawn MT-6 removed from 02_results.md (reconstructed v2)

`sections/02_results.md` was reconstructed (2026-09-17) and no longer contains the withdrawn
MT-6 flat-fraction comparison. The section is now organized by phase (see the drafting-progress
entry above) and is **awaiting re-approval**, since reconstructing an approved section voids
its approval.

**Two [NEW]/[PENDING] blocks in the reconstructed section are not yet covered by CLAIMS v2 and
need the scientist's decision:**

1. **§2.1 "The branches are families, not single structures."** Reports that ΔZ is continuous
   (island branch ΔZ ≈ 1–6 Å) and that each branch's low-energy structures form 1–3 structural
   motifs recurring across independent searches (from `analysis/ensemble_stats.json`). This is
   new evidence underpinning the "map" framing. Either approve it as main-text results content
   (requires a CLAIMS v3 claim) or move it wholly to the Supplementary Material and reduce §2.1
   to Table 1 + MT-1 + MT-2.
2. **§2.2 "[PENDING SIGN-OFF] Uncertainty of the B effect at the level of independent searches."**
   Reports the replica-resampled permutation test: Fe host +0.040 (p = 0.005, 13 vs 6),
   Fe-Co host +0.045 (**p = 0.74**, 5 vs 4), Co alone −0.005 (p = 0.73). **This challenges the
   "strong" confidence rating that CLAIMS v2 still assigns to MT-4.** Either MT-4's confidence
   is downgraded in CLAIMS v3 / the claim is reported as unresolved, or more Fe-Co and Fe-Co-B
   searches are run before MT-4 is written as a result.
3. **§2.3 [NEW] phase-separation wording.** States that B changes the flat–island separation
   without resolving whether the flat phase is stabilised or the island destabilised. This is
   already the interpretation in 03_discussion §3.2 but is not currently in CLAIMS; confirm it
   as wording, not a claim.

## RESOLVED: 01_methods.md §1.2 now states the exploration schedule per model

`sections/01_methods.md` §1.2 revised (2026-09-17, v3): the two-generator schedule is given
for Fe/MgO, Fe-B/MgO and Fe-Co-B/MgO, and a separate three-generator schedule for Fe-Co/MgO
(small-scale + large-scale + species-permutation, `num_candidates={0:[20,0,0], 10:[10,5,5],
25:[0,10,10]}`; `data/fecomgo/main.py:75,172–175`). The mermaid phase diagram was made
generator-count-agnostic and the "Bias" paragraph now states the reference-layer composition
per model (pure Fe / Fe+B / randomised Fe–Co layer ± B). Seed count corrected 7 → 6.
**Note:** the per-model generator mix is documented for completeness; it is *not* currently
listed as a limitation (the scientist elected not to add it there). It remains the reason
MT-6's cross-system density comparison was withdrawn.

## Reference PDFs (papers/)
- `papers/confusion_greer1993.pdf` — Greer, "Confusion by design," Nature 366, 303 (1993).
  Used for the confusion-principle discussion (§3.2). Citation `greer1993` in references.bib.

## Ensemble / motif investigation (2026-09-17) — see experiment_log.md for the full entry

Script: `scripts/ensemble_analysis.py` v1.0.0 → `analysis/ensemble_stats.json`,
`analysis/pes_structures_with_partial.csv`. Rebuilds `analysis/pes_structures.csv`
numerically identically (max |Δ| = 0.0; frozen 0.1888/0.1493/0.1941/0.1494 reproduced).

- **Replica counts corrected:** femgo 13 (+ `stop_16` partial run), **febmgo 6** (not 7 —
  `seed_6`'s db is empty), fecomgo 5 (`seed_4` has 1 structure), fecobmgo 4 (`seed_3` truncated).
- **Dataset-definition inconsistency:** the main text (seed_* only) uses 1180 structures /
  13 replicas / flat fraction **0.165**, while the SI baseline (`method_sensitivity.py`'s
  recursive glob, which picks up `stop_16`) uses **1207 / 14 / 0.181** for the same femgo
  baseline. The flat minimum is unaffected (0.1888). **One definition must be chosen.**
- **Flat minimum is not an accident:** every replica independently reaches the low-flat
  window (per-replica flat min: Fe 0.2185±0.021, Fe-B 0.1834±0.037, Fe-Co 0.2086±0.026,
  Fe-Co-B 0.1766±0.118), and femgo's 5 lowest flat structures (5 different replicas) cluster
  into 2 motifs with 4 replicas in the dominant one.
- **Statistical power (replica-resampled, permutation test on per-replica minima):**
  - MT-3 B in Fe host: min-of-min +0.0395, **p = 0.005** → holds.
  - MT-5 Co alone: −0.0053, **p = 0.73** → confirmed ("little effect").
  - **MT-4 B in Fe-Co host: +0.0447 but p = 0.74 → NOT resolvable** at 5 vs 4 replicas.
- **Decision needed:** whether MT-4 is reported as an unresolved trend, or more replicas are
  run for fecomgo/fecobmgo before the claim is written as a result.

## Open decisions / next step
- [x] SCIENTIST: contribution sentence approved (2026-09-16).
- [x] Claim list frozen (`CLAIMS.md` v1).
- [x] sections/01_methods.md approved (2026-09-16).
- [x] sections/02_results.md approved (2026-09-16) — **voided**: reconstructed v2 on 2026-09-17, awaiting re-approval.
- NEXT: scientist reviews `sections/03_discussion.md` (v3); on approval → draft `sections/04_introduction.md`.
- RESOLVED 2026-09-17 (review of 03 v2): the §3.2 confusion-principle sentence had claimed the
  flat energy falls along Fe → FeCo → FeCoB. It does not — Co alone raises it (MT-5). §3.2 is
  now restricted to the B addition, and the CLAIMS discussion-only entry carries the same
  bound. No MT/SI claim changed; CLAIMS v1 remains frozen.
- Open for the scientist: §3.1 no longer calls the island d-band centre "+0.5–0.6 eV, bulk-like"
  (unsupported — no bulk Fe d-centre reference exists in the repo). If the bulk comparison is
  wanted, a bulk-Fe reference calculation is needed.
- Citations: 6 verified; MTJ/PMA refs (cofebmgo_mtj, cofebmgo_pma, b_diffusion_mtj) still UNVERIFIED.
