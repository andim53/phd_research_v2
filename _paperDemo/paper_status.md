# paper_status.md — handoff / resume state

## Contribution (one sentence) — CONFIRMED (signed off 2026-09-16)
Boron consistently lowers the relative energy of the flat metal-film wetting state on MgO
(~0.04 eV/atom) in both a pure-Fe host and a Fe-Co host, while Co alone has little effect —
i.e. B promotes flat-film wetting independently of the host metal, relevant to interface
flatness in CoFeB/MgO MTJ stacks.

**Claim list frozen:** `CLAIMS.md` **v5** (2026-09-17, FROZEN; supersedes v1–v4). v2 withdrew
MT-6; v3 added MT-8 and flagged MT-4 CHALLENGED; v4 added SI-8; v5 added the bcc/bct
lattice-model and basis-set limitations and the experimental-correspondence framing, and
recorded six newly verified Fe/MgO references. See the CLAIMS changelog.

**MTJ placeholder debt is cleared.** All three unverified placeholders (`cofebmgo_mtj`,
`cofebmgo_pma`, `b_diffusion_mtj`) were removed from §3.3/§3.4 by dropping the CoFeB-specific
assertions and citing the verified `yuasa2004` for the MTJ context. **Every `\cite{}` key in
`sections/` now resolves against `references.bib`.** If the CoFeB/PMA/boron-segregation
specifics are wanted back, genuine CoFeB references must be fetched first.

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

## Supplementary Material: Performance of the biased exploration (NEW, 2026-09-17)

Drafted as **§S1 of `sections/SI.md`** (new file). Fe/MgO only, all 13 searches, **all**
iterations (including the pre-relaxation ones the PES analysis discards).
Deliverables: `figures/exploration_performance_femgo.png`, `analysis/exploration_performance.json`
(`scripts/exploration_performance.py` v1.0.0).

Key numbers: pre-relaxation (i = 1–9) descends only 12 % of the total (0.494 → 0.435 eV/atom);
**iteration 10 (relaxation onset) is the single largest step — 49 % of the entire descent**
(0.435 → 0.250 eV/atom; per-search median drop 0.165, range 0.084–0.233); 84 % done by i = 30,
94 % by i = 50; best-known crosses 0.20 at i = 23, 0.10 at i = 29, 0.05 at i = 46, 0.02 at
i = 57, 0.005 at i = 72; **the global minimum is first found at i = 77**; only 10 / 13 searches
end within 0.05 eV/atom and 4 / 13 within 0.02 (median final best 0.040).

✅ **SIGNED OFF:** `SI-8` is frozen in **`CLAIMS.md` v5** — *"the onset of relaxation is the
pivot of the biased search: the pre-relaxation iterations provide almost no ranking
information, and roughly half the total descent occurs at the first relaxed iteration."*
A paired caveat travels with it (Fe/MgO only; quantities describe the search scheme, not any
individual structure).

**§S1 is centred on the relaxation-onset step.** Per the scientist's decision, the "how early /
how late" framing was dropped entirely — the section is organised as: pre-relaxation plateau →
the onset step (the pivot) → the long refinement sequence → disagreement between searches. The
facts are all still reported (including the global minimum first being reached at i = 77), but
they no longer carry an early/late narrative.

⚠ **Held for review (not written into CLAIMS v4):** the searches are still improving at
iteration 100, so the per-model reference energies are not converged with respect to search
length. The scientist elected to discuss this at review rather than to add it to the
limitations now.

## Claim → evidence (Phase B)
| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Lowest-energy structure found is an island (all 4) | analysis/pes_structures.csv | ΔZ 2.75–3.77 Å at lowest energy | yes |
| Flat config is a distinct, higher-energy basin | analysis/pes_structures.csv | flat-basin dE/N > 0 (0.149–0.194) | yes |
| **B lowers flat-basin energy in Fe host** | analysis/pes_structures.csv | 0.1888 → 0.1493 eV/atom | yes — replica-resampled p = 0.005 |
| **B lowers flat-basin energy in Fe-Co host** | analysis/pes_structures.csv | 0.1941 → 0.1494 eV/atom | **CHALLENGED** — replica-resampled p = 0.74 (5 vs 4 searches); reported as a trend |
| Co alone has little effect | analysis/pes_structures.csv | 0.1888 → 0.1941 eV/atom (+0.005) | yes — replica-resampled p = 0.73 (null confirmed) |
| ~~B increases flat fraction (both hosts)~~ | — | **WITHDRAWN (MT-6, CLAIMS v2)** — biased-exploration weight, and the exploration operator is not matched across systems | — |
| B does not bond to MgO | analysis/pes_structures.csv | B_contact_frac ≈ 0 in window dE/N ≤ 0.05 eV/atom (1/72 Fe-B; 1/21 Fe-Co-B) | yes (windowed) |
| Low-energy structures of each branch form a few recurring motifs; ΔZ continuous | analysis/ensemble_stats.json | 1–3 motifs per branch; within-set distance 0.32–0.72 × random-pair scale | yes (descriptor-limited — paired caveat in CLAIMS) |
| **[SI] Signature: relaxation onset pivots the search** | analysis/exploration_performance.json | 49 % of the descent at i=10; global min at i=77; 10/13 within 0.05 eV/atom | analysis done; **SI-8 in CLAIMS v4 awaiting sign-off** |
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
- **12 verified & in `references.bib`**: agox2020, gofee2017, oganov2011, gpaw2014, pbe1996,
  greer1993, plus the six added 2026-09-17 for the Fe/MgO literature — **urano1988, butler2001,
  yuasa2004, reitinger2007, fahsold2000, larsen2009** — all verified via DOI content negotiation
  (Crossref). **Every `\cite{}` key in `sections/` resolves against `references.bib`.**
- **`yuasa2004` is verified and now cited** in §3.3 and §3.4, where it replaced the three
  CoFeB-specific placeholders (the CoFeB assertions were dropped rather than sourced).
- UNVERIFIED placeholders: **none remaining.** `cofebmgo_mtj`, `cofebmgo_pma` and
  `b_diffusion_mtj` were withdrawn from §3.3/§3.4 on 2026-09-17 and replaced by the verified
  `yuasa2004`; the CoFeB-specific assertions they supported were dropped.
- Note: the pre-existing keys `agox2020` / `gofee2017` carry year 2022 in the `.bib` (the key
  convention is surname+year, so the keys are stale) — left as-is because the sections cite them.

## Float numbering (established 2026-09-17)

All tables and figures are numbered **sequentially in order of appearance** across the drafted
section sequence (`01` → `06`), and are cited in the running text:

| Float | Location | Content |
|---|---|---|
| **Table 1** | `01_methods.md` §1.1 | the four interface models: film constitution, atom counts |
| **Table 2** | `01_methods.md` §1.2 | candidate-generation schedule, two generators (Fe/MgO, Fe-B/MgO, Fe-Co-B/MgO) |
| **Table 3** | `01_methods.md` §1.2 | candidate-generation schedule, three generators (Fe-Co/MgO) |
| **Figure 1** | `01_methods.md` §1.2 | the biased-exploration loop (mermaid workflow diagram) |
| **Table 4** | `02_results.md` §2.1 | the two phases in each model |
| **Table 5** | `02_results.md` §2.2 | flat-basin minimum dE/N, 2 × 2 additive design |
| **Figure S1** | `SI.md` §S1 | exploration-performance panels (separate `S` series) |

Caption style throughout: `**Table N.** …` / `**Figure N.** …` above tables and below figures.

⚠ **Assumption to revisit:** numbering follows the *drafting* order, in which Methods is section
01 and therefore takes the low numbers. If the final layout puts an Introduction (currently
`04`) first **and** it introduces floats of its own, every number below shifts. Cheapest fix at
port time is to renumber once, after the section order for the venue is fixed.

⚠ **Open: the main-text figures are not yet wired in.** `experiment_log.md` lists three
main-text figure files — `figures/pes_four_systems.png`, `figures/flat_state_summary.png` and
`figures/flat_vs_ground_preview.png` — but **no section currently cites any of them**, so the
main text has one figure (the Methods workflow diagram) and `02_results.md` §2.1/§2.2 describe
the two-phase landscape and the additive comparison in prose only. Wiring them in would make
them **Figure 2** (PES maps, §2.1), **Figure 3** (flat-state summary, §2.2) and possibly
**Figure 4** (side views). Awaiting the scientist's decision on which belong in the main text.

## Model geometry — strain is on the MgO, not the film (verified 2026-09-17)

Verified from the construction code and from the stored structures (not inferred from the text):

- **The simulation cell takes the DFT-optimised Fe lattice constant.** `data/femgo/seed_3`'s
  first candidate has cell in-plane = **14.35 Å = 5 × 2.870**.
- **The MgO is the strained component.** Its O–O in-plane nearest-neighbour distance is
  **2.870 Å**, against the bulk value `a_MgO/√2 = 2.9783 Å` → **3.6 % in-plane compression of
  the MgO**. (The familiar "3.77 %" is the same 0.108 Å difference expressed *relative to the
  Fe* value.)
- `build_mgo_stack` (`data/femgo/scripts/build_mgo_stack.py:33`) places the substrate oxygen
  **directly above an Fe site**, so the epitaxy is built by matching MgO onto Fe, and the
  Fe-atop-O registry is **inherited from the construction**.
- The substrate is then held fixed in that compressed state; only the film relaxes. **The Fe
  film sits at its own equilibrium lattice constant and is not strained in-plane.**
- The interfacial separation is the build parameter `dist_fe2o = 2.3 Å` (the `build_mgo_stack`
  default; `main.py` does not override it), preserved by relaxation: **2.300 Å** (flat),
  **2.331 Å** (island). It is a construction parameter, not a computed quantity.

**Decided:**

- ✅ **Description fixed (2026-09-17):** `01_methods.md` §1.1 now states the strain direction
  and §1.3 now states the Fe–O separation is a construction parameter.
- ⏸ **Mechanism wording HELD at the scientist's request.** Dropping "strain relief" for
  *reduced forced interfacial coupling + restored metal cohesion*, the SI-4 registry
  reframing, the inverse-convention limitation and the possible inverted re-run are all
  recorded in **`CLAIMS.md` → "PENDING v6"** and are **not** yet applied to `03_discussion.md`
  §3.1 or to SI-3/SI-4.
- **No numbers change.** The structures were always built this way; ΔZ, dE/N, flat-basin
  minima, registry counts and d-band centres are unaffected. This is a re-description, not a
  recomputation.

## Literature verification — Fe/MgO experiment (2026-09-17)

Three PDFs added by the scientist (`papers/mgofe_{urano1988,butler2001,yuasa2004}.pdf`); the
Urano scan had no text layer and was OCR'd (tesseract; install recorded in the session log).

| Reference | What it actually reports | Relation to our results |
|---|---|---|
| **Urano & Kanaji 1988** (JPSJ 57, 3403; LEED I–V + AES) | Fe on MgO(001) **grows layer by layer**, pseudomorphic at 1 ML, Fe **just above O at ~2.0 Å**; **bct → bcc at ≈10 Å** | **No islanding** — the opposite. Supports our **Fe-atop-O registry** (SI-4) and supplies the **bct limitation** |
| **Butler et al. 2001** (PRB 63, 054416; first-principles TMR) | Fe atop O per LEED; Fe–O **2.169 Å** (calc) / 2.0 Å (LEED) / 2.3 Å (earlier FLAPW); **~3.5 % mismatch**; *"only weak interactions"* between Fe and MgO | Supports the **registry** and **weak coupling**; not a growth-mode paper |
| **Yuasa et al. 2004** (Nat. Mater. 3, 868; MBE MTJ) | Giant TMR; **flatness** of epitaxial Fe is the quality criterion; RT top-Fe growth gives higher dislocation density than 200 °C | Neither islanding nor a structural validation — motivates the flat-interface requirement |
| **Fahsold et al. 2000** (PRB 61, 8475; He-atom scattering) — *added by us* | **3D metal island growth** of Fe on MgO(001) at room temperature, **suppressed only at 140 K** where a monolayer almost covers the substrate | **The genuine islanding validation**, and it is at ≈1 ML coverage |
| **Reitinger et al. 2007** (JAP 102, 034310; GISAXS) — *added by us* | **Volmer–Weber growth** at RT on **five** monolayers, spherical superparamagnetic islands | Second islanding reference; note the coverage is **5 ML**, not 1 ML |

**Consequence for the paper:** the three supplied papers cannot be cited for island formation.
The islanding support comes from `fahsold2000` (RT, ≈1 ML) and `reitinger2007` (RT, 5 ML); the
flat/wetting basin corresponds to the pseudomorphic monolayer obtained by slow deposition
(`urano1988`) or by low-temperature deposition (`fahsold2000`). This is framed as a
**correspondence between structural configurations, not between energies** (CLAIMS v5,
discussion-only), because the experimental growth mode is also kinetically controlled.

**Convergence of the literature:** RT deposition → 3D islands; 2D layer-by-layer requires low
temperature (140 K) or slow deposition on a specially prepared crystal. Urano's layer-by-layer
result at RT is therefore the outlier in the literature, not ours.

## Drafting progress (Phase E — markdown-first, block-and-wait)
- [~] sections/01_methods.md  (APPROVED as revised earlier 2026-09-17; **REVISED again
      2026-09-17 — needs re-approval**) — §1.1 now states the strain direction (cell = Fe
      lattice constant; MgO compressed 3.6 % relative to bulk; substrate frozen compressed;
      film unstrained), §1.3 now states that the Fe–O separation is a construction parameter
      rather than a computed quantity, and the three tables plus the workflow diagram are now
      numbered floats cited in the text (Tables 1–3, Figure 1).
      Earlier v3: §1.2 exploration schedule stated per model (Fe-Co uses a third,
      species-permutation generator); mermaid made generator-count-agnostic; "Bias"
      paragraph states the reference-layer composition per model; seed count 7 → 6.
- [~] sections/02_results.md  (APPROVED 2026-09-16; RECONSTRUCTED v2 2026-09-17 — needs re-approval)
      v2: reorganized by PHASE under the revised core framing —
      §2.1 the two-phase landscape (both phases populated; island is the ground state
      *despite* the flat bias → positive control, MT-1; flat is a distinct higher-energy
      basin, MT-2; branches are families of structures); §2.2 the flat (wetting) phase under
      Co/B/CoB (MT-3, MT-4, MT-5, MT-7); §2.3 the island (dewetting) phase and the
      flat–island separation; §2.4 summary.
      The withdrawn MT-6 flat-fraction comparison has been **removed**. The three items first
      flagged inline were resolved in CLAIMS v3 (MT-8 added; MT-4 flagged as a trend; §2.3
      wording recorded) — see below. The old section's single-lever ordering and its
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

## RESOLVED: reconstructed 02_results.md, sign-off items closed via CLAIMS v3

`sections/02_results.md` was reconstructed (2026-09-17) and no longer contains the withdrawn
MT-6 flat-fraction comparison. It is organized by phase and is **awaiting re-approval**, since
reconstructing an approved section voids its approval.

The three items that were flagged inline in the first reconstruction have all been resolved by
the scientist and are now in `CLAIMS.md` v3 — the inline `[PENDING SIGN-OFF]` markers have been
removed from the section:

1. **§2.1 "The branches are families, not single structures"** → kept in the main text as
   **MT-8**, with a paired caveat (the global template+film fingerprint compresses distances,
   so the motif count is a *lower bound*).
2. **§2.2 uncertainty paragraph** → retitled "Uncertainty from the choice of search"; **MT-4 is
   now flagged CHALLENGED — pending more searches** and is reported in the Results as a trend.
   Its confidence rating is deliberately *not* downgraded yet: the intent is to settle it with
   more Fe-Co / Fe-Co-B searches.
3. **§2.3 phase-separation wording** → added to CLAIMS' *Discussion-only interpretations*.

**Open follow-up:** running additional Fe-Co and Fe-Co-B searches is the agreed way to resolve
MT-4. Until then it stays a trend.

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
- [x] Claim list frozen (`CLAIMS.md` — now **v5, FROZEN** 2026-09-17).
- [x] sections/01_methods.md approved (2026-09-16) — revised twice; **APPROVED as revised 2026-09-17**.
- [ ] **OPEN — full texts of the two islanding references.** `fahsold2000` (PRB 61, 8475) and
      `reitinger2007` (JAP 102, 034310) are cited from their **verified abstracts only**; both
      are closed access (Semantic Scholar `openAccessPdf.status = CLOSED`) and no institutional
      copy was reachable, so the cited statements have not been checked against the full papers.
      The Urano PDF carries a *"Downloaded from journals.jps.jp by 三重大学"* watermark, i.e. the
      scientist has institutional access — placing these two PDFs in `papers/` would close this.
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
