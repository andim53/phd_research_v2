# 02 — Results

<!-- DRAFT v2 · section 02 of the manuscript (markdown-first, pre-LaTeX)
     RECONSTRUCTED 2026-09-17 under the revised core framing: Fe wetting is the subject,
     Co/B/CoB are the parameter series, and the biased search yields an EXPLORATION density
     over the flat (wetting) and island (dewetting) phases — not a thermodynamic DoS, so the
     weights are not physical. Organized by phase, not by additive.
     Grounded in CLAIMS.md v2. MT-6 is WITHDRAWN and no flat-fraction comparison appears here.
     Every number traces to analysis/pes_structures.csv or analysis/ensemble_stats.json.
     [NEW]/[PENDING] markers flag content that is not yet covered by CLAIMS v2 and needs
     scientist sign-off before this section is re-approved. -->

## 2.1 The two-phase landscape of the metal film on MgO

Our target is the wetting of the metal film on MgO(001). The property that distinguishes a
wetting from a dewetting film is its flatness, measured by the vertical span of the film,
ΔZ = z(metal)_max − z(metal)_min over all film atoms (Fe and Co); ΔZ ≈ 0 is a flat, wetting
film and large ΔZ a three-dimensional island. We therefore designed the search to return a
**map of this two-phase landscape**: a GOFEE global optimisation (Methods §1.2) **seeded from a
flat reference layer**, so that the flat basin is populated from the outset and any
lower-lying basin the search finds is populated alongside it. The result is a sampled
distribution over ΔZ and energy — an *exploration* density, not a thermodynamic density of
states. Because the sampling is deliberately biased, we use it only for unweighted structural
and energetic comparisons; the number of structures in a basin is a descriptive attribute of
the sampled database, not a physical population.

Across the four models the search returns 2408 structures spanning ΔZ from 0.001 to 6.10 Å,
with both phases populated in every model (Table 1).

**Table 1 — the two phases in each model** (ΔZ ≤ 1.0 Å = flat/wetting; ΔZ > 1.0 Å = island).

| Model | Structures | Island | Flat | Global-min ΔZ (Å) | Flat-basin min dE/N (eV/atom) |
|-------|-----------|--------|------|-------------------|-------------------------------|
| Fe/MgO | 1180 | 985 | 195 | 3.65 | 0.1888 |
| Fe-B/MgO | 543 | 430 | 113 | 3.77 | 0.1493 |
| Fe-Co/MgO | 355 | 279 | 76 | 2.75 | 0.1941 |
| Fe-Co-B/MgO | 330 | 250 | 80 | 3.45 | 0.1494 |

**The island is the ground state in every model, despite the flat bias.** The lowest-energy
structure found is an island in all four models, with its global minimum at ΔZ = 2.75–3.77 Å
(Table 1, column 5) — a three-dimensional cluster rather than a flat film. This result is
*against* the direction of the bias: every search was seeded from a flat reference layer and,
in the early phases, perturbed only at small scale from it, so the flat configuration had a
systematic head start. The search nevertheless left the flat basin and converged on an island in
all four models. The flat-wetting state is therefore not an artefact of how the initial
structures were built — it is genuinely higher in energy than the island. (MT-1)

**The flat configuration is a distinct, higher-energy basin.** Taking for each model the
lowest-energy structure with ΔZ ≤ 1.0 Å isolates the flat basin's best member. In every model
it lies above the global minimum, by 0.149–0.194 eV/atom (Table 1, column 6). The flat film is
thus a separate basin of the landscape, not merely the high-ΔZ tail of a single minimum.
(MT-2)

**The branches are families, not single structures.** [NEW] The ΔZ values are continuous rather
than grouped into discrete island heights: in each model the island branch spans ΔZ ≈ 1–6 Å
with a median near 2.4–3.0 Å, and the flat branch spans the whole window below 1 Å. The
low-energy members of each branch are likewise not a single repeated structure: comparing the
lowest-energy structures of each branch by their radial/angular fingerprint shows that they
form 1–3 distinct structural motifs, and that the same motif recurs across independent
searches (for Fe/MgO, the five lowest flat structures come from five different seeds and fall
into two motifs, four of them in the dominant one). Detailed motif analysis is given in the
Supplementary Material. [END NEW]

## 2.2 The flat (wetting) phase under Co, B and CoB

With the two phases established, we compare how the parameter series — Co, B and CoB added to
the Fe film — shifts the flat basin. Table 2 gives the flat-basin minimum dE/N for the four
models, arranged as a 2 × 2 design in the two additives.

**Table 2 — flat-basin minimum dE/N (eV/atom).**

| Host | without B | with B | B effect |
|------|-----------|--------|----------|
| Fe | 0.1888 | 0.1493 | **−0.040** |
| Fe-Co | 0.1941 | 0.1494 | **−0.045** |

**Boron lowers the flat-state energy, in both hosts.** Adding boron lowers the flat basin's
best member by ~0.04 eV/atom in the pure-Fe host and by ~0.045 eV/atom in the Fe-Co host — the
two hosts respond almost identically. (MT-3, MT-4)

**Cobalt alone has little effect.** Adding cobalt without boron leaves the flat-basin minimum
essentially unchanged (0.1888 → 0.1941 eV/atom, +0.005), and the two boron-containing models
are indistinguishable from each other (0.1493 vs 0.1494 eV/atom). Within this model the
wetting behaviour is therefore set by boron, not by the Fe/Co constitution of the film.
(MT-5)

**Boron does not bond to the MgO interface.** Restricting to the low-energy window
(dE/N ≤ 0.05 eV/atom), only 1 of 72 Fe-B/MgO structures and 1 of 21 Fe-Co-B/MgO structures has
any boron atom within 2.6 Å of an oxygen of the substrate; the maximum boron–oxygen contact
fraction in the window is 0.33 (Fe-B) and 0.5 (Fe-Co-B). Boron therefore remains inside the
metal film rather than wetting the oxide, so its effect on the flat phase is film-internal
rather than a change in interfacial bonding. (MT-7)

**[PENDING SIGN-OFF] Uncertainty of the B effect at the level of independent searches.**
Each model was searched from several independent random seeds (13 / 6 / 5 / 4 for Fe / Fe-B /
Fe-Co / Fe-Co-B), and structures from one search are correlated with each other, so the
independent unit is the search, not the structure. Taking each search's own flat-basin minimum
and comparing the two sets reproduces the tabulated effects (−0.040 eV/atom for the Fe host,
−0.045 for the Fe-Co host, +0.005 for cobalt alone) and attaches a permutation-test
significance to them: **p = 0.005** for the Fe host (13 vs 6 searches) and **p = 0.73** for
cobalt alone (13 vs 5), but **p = 0.74** for the Fe-Co host (5 vs 4 searches). The
corresponding median shifts are 0.035 and 0.032 eV/atom — i.e. not carried by a single
favourable search. The Fe-host effect and the cobalt null are therefore robust to the choice of
search, whereas the Fe-Co-host effect, although of the same size, **is not resolved by the four
searches currently available for Fe-Co-B**. [END PENDING]

## 2.3 The island (dewetting) phase and the separation between phases

The same parameter series leaves the *island* phase qualitatively similar across models. In all
four models the lowest-energy structure is an island at ΔZ = 2.75–3.77 Å (Table 1), and the
island branch spans the same broad range of heights (ΔZ ≈ 1–6 Å, median 2.4–3.0 Å) whether or
not Co or B is present. Adding Co, B or CoB does not change what the dewetted state looks like;
it changes how far above it the flat, wetting state sits.

Because each model is referenced to its own lowest energy, the quantity that compares the two
phases across models is the **separation between them** — the flat-basin minimum of Table 2 —
and that separation is exactly what boron reduces. [NEW] The present data do not resolve
*how* boron reduces it: a lower flat-basin energy could equally arise from stabilising the flat
phase or from destabilising the island, and distinguishing the two would require the island
phase to be referenced to an absolute (rather than per-model) energy scale, or a converged
treatment of both basins. We therefore state the effect as a change in the flat–island
separation, not as the stabilisation of either phase individually. [END NEW]

## 2.4 Summary of the results

- The biased GOFEE search, seeded from a flat reference, maps both the flat (wetting) and
  island (dewetting) phases in all four models, over ΔZ = 0–6 Å.
- **The island is the ground state in every model** (ΔZ = 2.75–3.77 Å), even though the search
  was biased toward the flat configuration — the flat bias did not manufacture the result.
- **The flat configuration is a distinct, higher-energy basin**, 0.149–0.194 eV/atom above the
  island in every model.
- Across the parameter series, **boron lowers the flat–island separation by ~0.04 eV/atom,
  equally in a pure-Fe and an Fe-Co host**, while **cobalt alone does not**.
- **Boron does not bond to the MgO interface** — it stays within the film, so its effect on the
  flat phase is film-internal.
- [NEW] Both branches are families of structures rather than single configurations; the
  energetics above are compared unweighted, since the sampled densities are biased and not
  physical (Supplementary Material).

The mechanistic origin of these trends (electronic structure, interface registry) and the
robustness of the method to its parameters are presented in the Supplementary Material.
