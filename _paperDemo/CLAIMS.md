# CLAIMS.md — FROZEN claim list (v5)

**Status: FROZEN (v5, 2026-09-17).** Supersedes v4, v3, v2 and v1.
**Project:** `_paperDemo` · **Venue:** TBD (format-agnostic)

## v5 changelog (2026-09-17)

- **New limitation added — lattice model.** Both phases are built on a **bcc** Fe lattice,
  whereas experiment reports **bct** Fe on MgO(001) below ≈10 Å (converting to bcc above)
  \cite{urano1988}. The island branch spans ΔZ ≈ 1–6 Å, i.e. inside that regime. The
  flat–island comparison is a trend within a fixed lattice model, not a prediction of absolute
  structural parameters. (Applies to MT-1 … MT-5, MT-8.)
- **New discussion-only interpretation — experimental correspondence.** The two basins are
  mapped onto the two experimentally realised growth outcomes: 3D islands at room-temperature
  deposition, suppressed only at 140 K \cite{fahsold2000}, and Volmer–Weber clusters at 5 ML
  \cite{reitinger2007}; the flat pseudomorphic monolayer obtained by slow deposition on a
  cleaved, oxygen-annealed crystal \cite{urano1988}. Framed as a **consistency check between
  structural configurations, not between energies** — the observed growth mode is also set by
  kinetics.
- **Citation status:** six Fe/MgO references fetched and verified via DOI content negotiation
  (Crossref) and added to `references.bib`: `urano1988`, `butler2001`, `yuasa2004`,
  `reitinger2007`, `fahsold2000`, `larsen2009`. **Note:** none of the first three supplied
  papers reports island formation; `urano1988` reports the opposite (layer-by-layer), and its
  role in the paper is the **Fe-atop-O registry** and the **bct result**.
- `larsen2009` supports the LCAO basis-set discussion in Methods §1.3 (LCAO is less complete
  than plane waves, affecting absolute geometric parameters).
- Everything else unchanged: MT-1 … MT-5, MT-7, MT-8 and SI-1 … SI-8 as in v3/v4; MT-6 withdrawn
  (v2); MT-4 flagged CHALLENGED (v3).

## v4 changelog (2026-09-17)

- **SI-8 ADDED (pending sign-off)** — performance of the biased exploration in finding the
  global minimum, Fe/MgO only, all iterations. The claim is centred on the **onset of
  relaxation as the pivot of the search**, not on how early or late the minimum appears.
  Source `analysis/exploration_performance.json`; figure
  `figures/exploration_performance_femgo.png`; drafted as §S1 of `sections/SI.md`.
- Nothing else changes: MT-1 … MT-5, MT-7, MT-8 and SI-1 … SI-7 are unchanged from v3; MT-6
  remains withdrawn (v2); MT-4 remains flagged CHALLENGED pending more searches (v3).
- **Not yet reflected in v4 (held for review):** the searches are still improving at
  iteration 100, so the per-model reference energies are not converged with respect to search
  length. The scientist elected to discuss this at review rather than to write it into the
  limitations now.

## v3 changelog (2026-09-17)

- **MT-8 ADDED** — the low-energy structures of each branch form a small set of *recurring
  motifs* rather than one repeated structure, and ΔZ is continuous (no discrete island
  heights). New main-text claim supporting the "map" framing; evidence from
  `analysis/ensemble_stats.json`.
- **MT-4 status: CHALLENGED — pending more searches.** Its value is unchanged, but a
  replica-resampled permutation test on the per-search flat-basin minima gives p = 0.74 at
  5 (Fe-Co) vs 4 (Fe-Co-B) searches, versus p = 0.005 for MT-3 at 13 vs 6. MT-4 is therefore
  reported in the Results as a *trend* of the same size as MT-3 until more Fe-Co / Fe-Co-B
  searches exist. The confidence rating is left as-is but flagged; it is not downgraded in v3.
- **Method & scope** now records the governing epistemic principle: the biased search returns
  an *exploration* density, not a thermodynamic density of states, so basin weights are not
  physical and only unweighted structural/energetic comparisons are used.
- **Discussion-only interpretations** gains the phase-separation wording: boron changes the
  flat–island separation, and the data do not resolve whether the flat phase is stabilised or
  the island destabilised.
- MT-1 … MT-5, MT-7 and SI-1 … SI-7 are otherwise unchanged from v2 (no values, sources or
  confidence levels altered). MT-6 remains withdrawn (v2).

## v2 changelog (2026-09-17)

- **MT-6 WITHDRAWN** — "B increases the fraction of flat-basin structures sampled"
  (0.165 → 0.208; 0.214 → 0.242). Reason: the flat fraction is a *weight* of a
  **biased** exploration, not a physically interpretable population, and a cross-system
  comparison of weights additionally requires a fixed exploration operator, which does not
  hold — `data/fecomgo/main.py:75,172–175` adds a third `PermutationGenerator` to the schedule
  used by `femgo`, `febmgo` and `fecobmgo`. The flat reference also differs in kind across
  systems (pure Fe layer vs randomised Fe/Co layer vs B-decorated layer).
- MT-1 … MT-5 and MT-7 unchanged; SI-1 … SI-7 unchanged except for the note on SI-7 below.
- The withdrawn claim moves to "NOT claimed (explicitly excluded)".

This is the authoritative list of what the paper claims and does NOT claim. Drafting
(`sections/*.md`) must not introduce claims outside this list, and must not drop the
paired caveats. Numbers below are frozen to the cited source files.

---

## Contribution (one sentence)

> **Boron insertion lowers the relative energy of the flat metal-film wetting state on
> MgO by ~0.04 eV/atom in both a pure-Fe and a Fe-Co host, while Co alone has little
> effect — i.e. B promotes flat-film wetting independently of the host metal, relevant
> to interface flatness in CoFeB/MgO MTJ stacks.**

---

## Main-text claims

| ID | Claim | Exact value | Source | Confidence |
|----|-------|-------------|--------|-----------|
| **MT-1** | The lowest-energy structure found is an **island** (not flat) in all four systems | global-min ΔZ = 3.65 / 3.77 / 2.75 / 3.45 Å (Fe / Fe-B / Fe-Co / Fe-Co-B) | `analysis/pes_structures.csv` | strong |
| **MT-2** | The **flat configuration is a distinct, higher-energy basin** (not the ground state) | flat-basin min dE/N > 0 in every system (0.149–0.194 eV/atom) | `analysis/pes_structures.csv` | strong |
| **MT-3** | **B lowers the flat-state energy in the pure-Fe host** | 0.1888 → 0.1493 eV/atom (−0.040) | `analysis/pes_structures.csv` | strong (replica-resampled p = 0.005) |
| **MT-4** | **B lowers the flat-state energy in the Fe-Co host** | 0.1941 → 0.1494 eV/atom (−0.045) | `analysis/pes_structures.csv` | **CHALLENGED — pending more searches** (replica-resampled p = 0.74 at 5 vs 4 searches; reported as a trend) |
| **MT-5** | **Co alone has little effect** on the flat-state energy | 0.1888 → 0.1941 eV/atom (+0.005) | `analysis/pes_structures.csv` | strong (replica-resampled p = 0.73 — null confirmed) |
| ~~MT-6~~ | ~~B increases the fraction of flat-basin structures sampled~~ | **WITHDRAWN in v2** — see changelog | — | — |
| **MT-7** | **B does not bond to the MgO interface** (stays in the metal film) | B_contact_frac ≈ 0 in the low-energy window dE/N ≤ 0.05 eV/atom (1 of 72 Fe-B, 1 of 21 Fe-Co-B; max contact fraction 0.33 / 0.5). Window defined by `scripts/wetting_metrics.py --e-window-per-atom 0.05` | `analysis/pes_structures.csv` | strong (windowed) |
| **MT-8** | The low-energy structures of each branch form a **small set of recurring motifs** rather than one repeated structure; ΔZ is **continuous**, with no discrete island heights | Island branch spans ΔZ ≈ 1–6 Å (no quantisation); low-energy sets split into 1–3 single-linkage motifs (flat 2/2/3/2, island 2/2/3/1 per system); within-set fingerprint distance is 0.32–0.72 × the branch's random-pair scale; Fe/MgO's 5 lowest flat structures (from 5 independent searches) fall into 2 motifs, 4 in the dominant one | `analysis/ensemble_stats.json` | moderate — see paired caveat |

**Combined 2×2 statement (MT-3/4/5):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect
+0.005 (no B) — B is the dominant lever, Co is not.
**Note:** MT-6 (flat-basin sampling fraction) is withdrawn in v2. The flat-basin *fraction*
may still be reported as a descriptive attribute of the sampled database, but not as a
physical result and not as a cross-system comparison.

**Paired caveat for MT-8 (must travel with the claim).** The motif test uses the AGOX global
`Fingerprint` (radial + angular distribution functions) computed on the whole template + film
structure. Because the 50-atom MgO template is identical across structures, it dominates the
descriptor and compresses all pair distances, so the reported motif counts are a *lower bound*
on the structural diversity present — the descriptor cannot resolve differences finer than the
distances it reports. A film-resolved descriptor (or a species-aware RMSD) would be sharper.
The claim must therefore be stated as "a small set of recurring motifs", not as an exact
number of distinct structures.

---

## Supplementary-material claims

| ID | Claim | Exact value | Source | Confidence |
|----|-------|-------------|--------|-----------|
| **SI-1** | Islanding **reduces Fe–O hybridisation** | d-band centre −0.229 → +0.601 eV; O-pz ∫ 43.88 → 42.37 | `analysis/pdos_metrics.csv` | strong |
| **SI-2** | Islanding **weakens magnetism and lowers DOS(E_F)** | spin pol 5.81 → 4.37; DOS(E_F) 104.0 → 78.1 | `analysis/pdos_metrics.csv` | moderate |
| **SI-3** | The island's **true interface Fe are NOT flat-like** → island origin is **strain relief**, not interfacial re-hybridisation | island interface d-centre +0.51 eV vs flat −0.23 eV (despite ~equal d_Fe-O, 2.33 vs 2.30 Å) | `analysis/interface_analysis.csv` | moderate |
| **SI-4** | **Fe sits directly atop O** at the interface | 25/25 (flat) and 9/9 (island) atop O; 0 atop Mg (flat offset 0.000 Å) | `analysis/interface_analysis.csv` | strong (structural) |
| **SI-5** | The result is **robust to the LCB kappa** | per-seed best 0.039–0.056 eV/atom across kappa ∈ {1,2,3,4} | `analysis/method_sensitivity.csv` | strong |
| **SI-6** | The result is **robust to the dipole correction** | per-seed best 0.050 → 0.056 eV/atom (within seed spread) | `analysis/method_sensitivity.csv` | weak (outcome-level only) |
| **SI-7** | **Reducing the rattle strength degrades the search ~5×** and under-samples the flat basin | per-seed best 0.050 → 0.27–0.29 eV/atom; flat fraction 0.181 → 0.030/0.015 | `analysis/method_sensitivity.csv` | strong |
| **SI-8** *(pending sign-off, v4)* | **The onset of relaxation is the pivot of the biased search**: the pre-relaxation iterations provide almost no ranking information, and roughly half the total descent occurs at the first relaxed iteration | best-known ΔE/N: 0.494 (i=1) → 0.435 (i=9; 12 % of the descent) → **0.250 (i=10; 49 %)**; per-search drop across the onset median 0.165 (range 0.084–0.233) eV/atom; 84 % of the descent by i=30, 94 % by i=50; global minimum first reached at i=77; 10 of 13 searches end within 0.05 eV/atom of it, 4 within 0.02 | `analysis/exploration_performance.json` | strong (Fe/MgO only) |

**Paired caveat for SI-8 (must travel with the claim).** Fe/MgO only, and the quantities are
properties of the *search scheme*, not of any individual structure: the energies are single GPAW
steps on surrogate-relaxed candidates (residual forces ~1–2 eV/Å), the search is biased (seeded
from a flat reference layer), and iteration is an AGOX counter rather than a computational cost.

**Note on SI-7 (v2):** SI-7 still uses the flat fraction, and deliberately so. Unlike
withdrawn MT-6, it compares **one system against itself under a changed method parameter**
(rattle strength), where the sampling density is precisely the intended diagnostic — "does a
weaker perturbation still find the flat basin?". It is not a cross-system population
comparison, so the operator-matching failure that invalidates MT-6 does not apply. SI-7
remains a *method-quality* claim on Fe/MgO only.

---

## NOT claimed (explicitly excluded)

| Excluded claim | Why |
|----------------|-----|
| **B increases the fraction of flat-basin structures sampled** (withdrawn MT-6, v2) | Not a physical result: the flat fraction is a *weight* of a **biased** exploration. Cross-system comparison additionally requires a fixed exploration operator, which does not hold — Fe-Co alone uses a three-generator schedule including a `PermutationGenerator` (`data/fecomgo/main.py:75,172–175`), and the flat reference differs in kind across systems. Reportable only as a descriptive attribute of the sampled database. |
| The flat state is **"metastable"** | Not established — needs converged relaxation + Hessian + a barrier. Use "higher-energy flat basin". |
| B **lowers the Fe–O contact fraction** | Not significant under the per-atom window (p=0.106). |
| B **shrinks the lateral Fe coverage** | Dropped out under the per-atom window (p=0.967); was only significant under the loose absolute window. |
| The **Fe-B PDOS comparison** | Deferred — the Fe-B PDOS uses full d/p projections, mismatched with the femgo dz2/pz set. |
| **Quantitative energy ordering** beyond ~trend level | Structures are not DFT-converged (see limitations). |
| The dipole comparison as **isolating** the dipole energy shift | The two runs are separate searches; outcome-level only. |

---

## Method & scope (fixed)

- Search: AGOX **GOFEE** (GPR surrogate + LCB), a **biased** exploration seeded from a
  reference **flat** metal layer; only **iteration ≥ 10** used.
- **Epistemic status of the sampled data (v3).** The search returns an ***exploration*
  density, not a thermodynamic density of states**. The sampling is deliberately biased
  (seeded from a flat reference, with a phase-dependent generator mix), so the number of
  structures in a basin is **not** a physical population or weight. Only **unweighted**
  structural and energetic comparisons are admissible; basin counts may be reported as
  descriptive attributes of the sampled database only.
- **The island being the ground state despite the flat bias is a positive control** (MT-1):
  every search started from a flat reference layer and was perturbed only at small scale in
  the early phases, yet converged on an island in all four models.
- Metrics: **ΔZ** = z(metal_max) − z(metal_min) over Fe+Co [Å]; **dE/N** = (E − E_globalmin)/N
  [eV/atom] per system, global min = 0; flat/island split at ΔZ ≤ 1.0 Å.
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (main search).
- Systems: Fe/MgO, Fe-B/MgO, Fe-Co/MgO, Fe-Co-B/MgO.

## Limitations (must appear with the claims)

- **Structures are NOT DFT-converged** — surrogate relaxation + **1 GPAW step**; residual
  forces ~1–2 eV/Å. "Lowest energy"/"basin" = lowest DFT energy *found*.
- Unequal seed counts across systems (13 / 7 / 5 / 4) and across parameter settings.
- **Lattice model (v5):** both phases are built on a **bcc** Fe lattice, but experiment reports
  **bct** Fe on MgO(001) below ≈10 Å \cite{urano1988}; the island branch (ΔZ ≈ 1–6 Å) lies in
  that regime. The comparison is a trend within a fixed lattice model.
- **Basis-set completeness (v5):** LCAO basis sets are less complete than plane waves
  \cite{larsen2009}, which shifts absolute geometric parameters (e.g. the computed Fe–O
  separation, 2.30–2.33 Å, sits at the upper end of the experimental/calculated 2.0–2.3 Å
  range \cite{urano1988,butler2001}). Quantities are compared at fixed settings.
- ΔZ ≤ 1.0 Å flat cutoff is a chosen threshold.
- kpts = (1,1,1), single-layer slabs → qualitative/trend-level.

---

## Discussion-only interpretations (not results claims)

These are interpretive framings permitted in the Discussion; they do **not** add results
claims to MT/SI and do not change the frozen list.

- **Flat ↔ amorphous, island ↔ crystalline mapping.** The flat film is read as the
  disordered/amorphous-like configuration and the island as the ordered/crystalline-like
  one.
- **Greer confusion principle** \cite{greer1993}: the flat/disordered configuration is
  claimed to be stabilised by added elements, in the spirit of the confusion principle
  (more elements frustrate crystallisation and favour the disordered configuration).
  **Data bound (added 2026-09-17; Discussion-only wording, no MT/SI claim changed):** the
  supported driver is the *presence of boron*, not the element count. Adding Co alone
  raises the flat-basin energy (MT-5, 0.1888 → 0.1941 eV/atom), and the two two-element
  systems differ more from each other (Fe-B 0.1493 vs Fe-Co 0.1941) than Fe-Co does from
  three-element Fe-Co-B (0.1494). The principle is retained as acting through the added
  metalloid, not through complexity counting. Honest bound retained: even the boron-bearing
  models keep the island as ground state, so the principle stabilises but does not fully
  suppress the ordered configuration in these models.
- **Phase-separation wording (added 2026-09-17, v3).** Boron is described as changing the
  **flat–island separation**, not as stabilising the flat phase or destabilising the island
  individually. Because each model is referenced to its own lowest energy, a reduced
  separation is consistent with either. Resolving it would require an absolute (cross-system)
  energy reference and/or a converged treatment of both basins. Permitted in Results §2.3 and
  Discussion §3.2; it is wording, not a results claim.
- **Experimental correspondence (added 2026-09-17, v5).** The flat and island basins are mapped
  onto the two growth outcomes reported for Fe on MgO(001): room-temperature deposition gives
  3D islands (suppressed only at 140 K) \cite{fahsold2000} and Volmer–Weber clusters at 5 ML
  \cite{reitinger2007}, whereas a flat pseudomorphic monolayer is obtained by slow deposition on
  a cleaved, oxygen-annealed crystal \cite{urano1988}. **Scope bound (must travel with it):**
  this is a correspondence between *structural configurations*, not between energies — the
  experimental growth mode is also governed by kinetics, so the experiment neither confirms nor
  refutes the calculated energy ordering.

## Sign-off

- [x] **MT-1 … MT-5, MT-7 approved** (main text) — scientist (2026-09-16)
- [x] **SI-1 … SI-7 approved** (supplementary) — scientist (2026-09-16)
- [x] **Exclusions confirmed** — scientist (2026-09-16)
- [x] Contribution sentence approved (2026-09-16)
- [x] **MT-6 withdrawn and moved to the excluded list** (v2, 2026-09-17) — scientist
- [x] **MT-8 added** (main text, v3, 2026-09-17) — scientist
- [x] **MT-4 flagged CHALLENGED, to be reported as a trend pending more Fe-Co searches**
      (v3, 2026-09-17) — scientist
- [x] **Method & scope: exploration-density principle + positive-control framing** (v3,
      2026-09-17) — scientist
- [x] **Discussion-only: phase-separation wording** (v3, 2026-09-17) — scientist
- [x] **SI-8: performance of the biased exploration** (v4, 2026-09-17) — scientist
- [x] **v5: bcc/bct lattice-model limitation, basis-set limitation, experimental-correspondence
      framing, six verified Fe/MgO references** (2026-09-17) — scientist

**Status: FROZEN (v5, 2026-09-17).** This list is frozen for drafting. Any new result or claim
requires an explicit update to this file before it enters a section.
**Version history:** v1 (2026-09-16) initial frozen list · v2 (2026-09-17) MT-6 withdrawn ·
v3 (2026-09-17) MT-8 added, MT-4 flagged challenged, exploration-density principle ·
v4 (2026-09-17) SI-8 added · v5 (2026-09-17) lattice-model + basis-set limitations,
experimental-correspondence framing, six verified Fe/MgO references.
