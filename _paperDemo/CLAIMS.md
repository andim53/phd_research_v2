# CLAIMS.md — FROZEN claim list (v1)

**Status: FROZEN — awaiting scientist sign-off (Phase A gate).**
**Date frozen:** 2026-09-16 · **Project:** `_paperDemo` · **Venue:** TBD (format-agnostic)

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
| **MT-6** | **B increases the fraction of flat-basin structures sampled** | 0.165 → 0.208 (Fe host); 0.214 → 0.242 (Fe-Co host) | `analysis/pes_structures.csv` | moderate |
| **MT-7** | **B does not bond to the MgO interface** (stays in the metal film) | B_contact_frac ≈ 0 (1 of 72 windowed structures has a single B–O contact) | `analysis/pes_structures.csv` | strong |

**Combined 2×2 statement (MT-3/4/5):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect
+0.005 (no B) — B is the dominant lever, Co is not.

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

---

## NOT claimed (explicitly excluded)

| Excluded claim | Why |
|----------------|-----|
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
- **Greer confusion principle** \cite{greer1993}: the Fe → FeCo → FeCoB progression
  (increasing compositional complexity) is claimed to *explain the trend* of flat-state
  stabilisation — more elements frustrate crystallisation and favour the flat/disordered
  configuration. Honest bound retained: even FeCoB keeps the island as ground state, so the
  principle stabilises but does not fully suppress the ordered configuration in these models.

## Sign-off

- [x] **MT-1 … MT-7 approved** (main text) — scientist (2026-09-16)
- [x] **SI-1 … SI-7 approved** (supplementary) — scientist (2026-09-16)
- [x] **Exclusions confirmed** — scientist (2026-09-16)
- [x] Contribution sentence approved (2026-09-16)

**Status: SIGNED OFF (2026-09-16).** This list is frozen for drafting. Any new result or
claim requires an explicit update to this file (bump to v2) before it enters a section.
