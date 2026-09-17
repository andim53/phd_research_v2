# CLAIMS.md — FROZEN claim list (v2)

**Status: FROZEN (v2, 2026-09-17).** Supersedes v1 (signed off 2026-09-16).
**Project:** `_paperDemo` · **Venue:** TBD (format-agnostic)

## v2 changelog (2026-09-17)

- **MT-6 WITHDRAWN** — "B increases the fraction of flat-basin structures sampled"
  (0.165 → 0.208; 0.214 → 0.242). Reason: the flat fraction is a *weight* of a
  **biased** exploration, not a physically interpretable population. The sampling density
  can only be compared across systems if the exploration operator is held fixed, and it is
  not: `data/fecomgo/main.py` uses a three-generator schedule
  (`num_candidates={0:[20,0,0], 10:[10,5,5], 25:[0,10,10]}`, adding a `PermutationGenerator`,
  lines 172–175), whereas `femgo`, `febmgo` and `fecobmgo` use two generators
  (`{0:[20,0], 10:[10,10], 25:[0,20]}`). The flat reference itself also differs in kind
  across systems (pure Fe layer vs randomised Fe/Co layer vs B-decorated layer). The claim is
  therefore not sound as a *physical* result and has been removed rather than restated.
- MT-1 … MT-5 and MT-7 are **unchanged** from v1 (no values, sources or confidence levels
  altered). SI-1 … SI-7 are unchanged except for the note on SI-7 below.
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
| **MT-3** | **B lowers the flat-state energy in the pure-Fe host** | 0.1888 → 0.1493 eV/atom (−0.040) | `analysis/pes_structures.csv` | strong |
| **MT-4** | **B lowers the flat-state energy in the Fe-Co host** | 0.1941 → 0.1494 eV/atom (−0.045) | `analysis/pes_structures.csv` | strong |
| **MT-5** | **Co alone has little effect** on the flat-state energy | 0.1888 → 0.1941 eV/atom (+0.005) | `analysis/pes_structures.csv` | strong |
| ~~MT-6~~ | ~~B increases the fraction of flat-basin structures sampled~~ | **WITHDRAWN in v2** — see changelog | — | — |
| **MT-7** | **B does not bond to the MgO interface** (stays in the metal film) | B_contact_frac ≈ 0 (1 of 72 windowed structures has a single B–O contact) | `analysis/pes_structures.csv` | strong |

**Combined 2×2 statement (MT-3/4/5):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect
+0.005 (no B) — B is the dominant lever, Co is not.
**Note:** MT-6 (flat-basin sampling fraction) is withdrawn in v2. The flat-basin *fraction*
may still be reported as a descriptive attribute of the sampled database, but not as a
physical result and not as a cross-system comparison.

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
- Metrics: **ΔZ** = z(metal_max) − z(metal_min) over Fe+Co [Å]; **dE/N** = (E − E_globalmin)/N
  [eV/atom] per system, global min = 0; flat/island split at ΔZ ≤ 1.0 Å.
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (main search).
- Systems: Fe/MgO, Fe-B/MgO, Fe-Co/MgO, Fe-Co-B/MgO.

## Limitations (must appear with the claims)

- **Structures are NOT DFT-converged** — surrogate relaxation + **1 GPAW step**; residual
  forces ~1–2 eV/Å. "Lowest energy"/"basin" = lowest DFT energy *found*.
- Unequal seed counts across systems (13 / 7 / 5 / 4) and across parameter settings.
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

## Sign-off

- [x] **MT-1 … MT-5, MT-7 approved** (main text) — scientist (2026-09-16)
- [x] **SI-1 … SI-7 approved** (supplementary) — scientist (2026-09-16)
- [x] **Exclusions confirmed** — scientist (2026-09-16)
- [x] Contribution sentence approved (2026-09-16)
- [x] **MT-6 withdrawn and moved to the excluded list** (v2, 2026-09-17) — scientist

**Status: FROZEN (v2, 2026-09-17).** This list is frozen for drafting. Any new result or
claim requires an explicit update to this file before it enters a section.
**Version history:** v1 (2026-09-16) initial frozen list · v2 (2026-09-17) MT-6 withdrawn.
