# 02 — Results

<!-- DRAFT v2 · section 02 of the manuscript (markdown-first, pre-LaTeX)
     RECONSTRUCTED 2026-09-17 under the revised core framing: Fe wetting is the subject,
     Co/B/CoB are the parameter series, and the biased search yields an EXPLORATION density
     over the flat (wetting) and island (dewetting) phases — not a thermodynamic DoS, so the
     weights are not physical. Organized by phase, not by additive.
     Grounded in CLAIMS.md v8. MT-6 is WITHDRAWN and no flat-fraction comparison appears here;
     MT-8 is claimed in §2.1; MT-4 is reported as a trend (flagged CHALLENGED in CLAIMS v3, still
     flagged in v6).
     Every number traces to analysis/pes_structures.csv or analysis/ensemble_stats.json. -->

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
with both phases populated in every model (Table 4).

**Table 4.** The two phases in each model (ΔZ ≤ 1.0 Å = flat/wetting; ΔZ > 1.0 Å = island).

| Model | Structures | Island | Flat | Global-min ΔZ (Å) | Flat-basin min dE/N (eV/atom) |
|-------|-----------|--------|------|-------------------|-------------------------------|
| Fe/MgO | 1180 | 985 | 195 | 3.65 | 0.1888 |
| Fe-B/MgO | 543 | 430 | 113 | 3.77 | 0.1493 |
| Fe-Co/MgO | 355 | 279 | 76 | 2.75 | 0.1941 |
| Fe-Co-B/MgO | 330 | 250 | 80 | 3.45 | 0.1494 |

**The island is the ground state in every model, despite the flat bias.** The lowest-energy
structure found is an island in all four models, with its global minimum at ΔZ = 2.75–3.77 Å
(Table 4, column 5) — a three-dimensional cluster rather than a flat film. This result is
*against* the direction of the bias: every search was seeded from a flat reference layer and,
in the early phases, perturbed only at small scale from it, so the flat configuration had a
systematic head start. The search nevertheless left the flat basin and converged on an island in
all four models. The flat-wetting state is therefore not an artefact of how the initial
structures were built — it is genuinely higher in energy than the island. (MT-1)

**The flat configuration is a distinct, higher-energy basin.** Taking for each model the
lowest-energy structure with ΔZ ≤ 1.0 Å isolates the flat basin's best member. In every model
it lies above the global minimum, by 0.149–0.194 eV/atom (Table 4, column 6). The flat film is
thus a separate basin of the landscape, not merely the high-ΔZ tail of a single minimum.
(MT-2)

**The branches are families, not single structures.** The ΔZ values are continuous rather
than grouped into discrete island heights: in each model the island branch spans ΔZ ≈ 1–6 Å
with a median near 2.4–3.0 Å, and the flat branch spans the whole window below 1 Å. The
low-energy members of each branch are likewise not a single repeated structure: comparing the
lowest-energy structures of each branch by their radial/angular fingerprint shows that they
form 1–4 distinct structural motifs, and that the same motif recurs across independent
searches (for Fe/MgO, the five lowest flat structures come from five different searches and
fall into two motifs, four of them in the dominant one). (MT-8)
The fingerprint is computed on the whole template-plus-film structure, so the fixed MgO
template compresses the pair distances and the motif count is a **lower bound** on the
structural diversity present; a film-resolved descriptor would be sharper. Pairwise distances
within the low-energy set of a branch are 0.37–0.71 of that branch's random-pair distance scale,
i.e. the low-energy structures are consistently more compact than the branch as a whole. The
count is also limited by how many searches contribute to the low-energy set: for Fe-Co-B the
island set within 0.02 eV/atom of the island minimum comes from a **single** search, so its
motif count is not an independent check. Detailed motif analysis is given in the Supplementary
Material.

**Experimental correspondence.** The films in this study are about **one monolayer thick on
average** — 25 metal atoms per 25 substrate sites in the 5 × 5 cell, with the boron-containing
models carrying up to three additional boron atoms — and that is the regime in which the growth
mode of Fe on MgO(001) has been characterised experimentally. At room
temperature the observed growth is three-dimensional: He-atom scattering shows **3D metal
island growth** of Fe on MgO(001), with quantified island densities, sizes and shapes,
suppressed only when the film is deposited at low temperature (140 K), where a monolayer
almost completely covers the substrate \cite{fahsold2000}; scanning tunnelling microscopy finds
that **sub-nanometre Fe grows three-dimensionally** on MgO, with island coalescence between 3.5
and 6.5 monolayers and a two-dimensional growth mode reported only above ≈6.5 monolayers
\cite{torelli2009}; and grazing-incidence small-angle X-ray scattering on five monolayers
evaporated at room temperature likewise identifies **Volmer–Weber growth** with spherical
islands \cite{reitinger2007}. A flat, continuous film is obtained instead by low-temperature
deposition \cite{fahsold2000} or by slow deposition onto a cleaved, oxygen-annealed crystal,
where the first monolayer grows pseudomorphically and layer by layer \cite{urano1988}. Our two
basins therefore map onto the two outcomes that are experimentally accessible **at this
coverage** — the flat basin onto the pseudomorphic monolayer and the island basin onto the 3D
clusters — and the energy ordering we find places the flat, wetting configuration above the
island. This is a consistency check rather than a prediction: the observed growth mode is also
set by kinetics, so the correspondence is between structural configurations, not between
energies. Because the growth mode turns two-dimensional only above ≈6.5 monolayers
\cite{torelli2009}, the comparison is specific to the monolayer regime and should not be
extrapolated to thick films.

## 2.2 The flat (wetting) phase under Co, B and CoB

With the two phases established, we compare how the parameter series — Co, B and CoB added to
the Fe film — shifts the flat basin. Table 5 gives the flat-basin minimum dE/N for the four
models, arranged as a 2 × 2 design in the two additives.

**Table 5.** Flat-basin minimum dE/N (eV/atom), arranged as a 2 × 2 design in the two additives.

| Host | without B | with B | B effect |
|------|-----------|--------|----------|
| Fe | 0.1888 | 0.1493 | **−0.040** |
| Fe-Co | 0.1941 | 0.1494 | **−0.045** |

**Boron lowers the flat-state energy, in both hosts.** Adding boron lowers the flat basin's
best member by ~0.04 eV/atom in the pure-Fe host and by ~0.045 eV/atom in the Fe-Co host — the
two hosts respond almost identically. (MT-3, MT-4) The Fe-Co-host result is reported as a
**trend**: it is not yet resolved at the level of independent searches (see the uncertainty
paragraph below).

**Cobalt alone has little effect.** Adding cobalt without boron leaves the flat-basin minimum
essentially unchanged (0.1888 → 0.1941 eV/atom, +0.005), and the two boron-containing models
are indistinguishable from each other (0.1493 vs 0.1494 eV/atom). Within this model the
wetting behaviour is therefore set by boron, not by the Fe/Co constitution of the film.
(MT-5)

**Boron does not bond to the MgO interface.** Restricting to the low-energy window
(dE/N ≤ 0.05 eV/atom), only 1 of 72 Fe-B/MgO structures and 1 of 21 Fe-Co-B/MgO structures has
any boron atom within 2.6 Å of an oxygen of the substrate; the maximum boron–oxygen contact
fraction in the window is 0.33 (Fe-B) and 0.5 (Fe-Co-B). Outside the window the picture is
different — 101 of the 471 remaining Fe-B structures and 25 of the 252 remaining Fe-Co-B
structures do have a boron–oxygen contact — which is why the statement is restricted to the
low-energy window rather than made over all sampled structures. Boron therefore remains inside the
metal film rather than wetting the oxide, so its effect on the flat phase is film-internal
rather than a change in interfacial bonding. (MT-7) The window is narrow and not evenly sampled
across searches: the 21 Fe-Co-B structures in it come from only **two** searches (20 from one of
them), so this is one of the weakest-supported statements in the paper.

**Uncertainty from the choice of search.** Each model was searched from several independent
random seeds (13 / 6 / 4 / 3 completed searches for Fe / Fe-B / Fe-Co / Fe-Co-B), and structures
from one search are correlated with each other, so the independent unit is the search, not the
structure. Taking each search's own flat-basin minimum
and comparing the two sets reproduces the tabulated effects (−0.040 eV/atom for the Fe host,
−0.045 for the Fe-Co host, +0.005 for cobalt alone) and attaches a two-sided permutation-test
significance to them: **p = 0.045** for the Fe host (13 vs 6 searches), **p = 0.245** for cobalt
alone (13 vs 4), and **p = 0.092** for the Fe-Co host (4 vs 3 searches). The corresponding median
shifts are 0.035 and 0.048 eV/atom, with 93 % and 92 % of resampled replicates agreeing in sign —
i.e. the effects are not carried by a single favourable search. The Fe-host effect is therefore
significant at the 5 % level and the cobalt null stands, whereas the Fe-Co-host effect, although
of the same size, **is not resolved by the three completed Fe-Co-B searches** and is reported here
as a trend. The test is limited by its own resolution: pooling 4 and 3 searches admits only 35
distinct partitions, so no permutation test on this pair can return p < 0.029, and settling the
Fe-Co-host effect requires further completed searches of that model rather than further analysis
of these.

## 2.3 The island (dewetting) phase and the separation between phases

The same parameter series leaves the *island* phase qualitatively similar across models. In all
four models the lowest-energy structure is an island at ΔZ = 2.75–3.77 Å (Table 4), and the
island branch spans the same broad range of heights (ΔZ ≈ 1–6 Å, median 2.4–3.0 Å) whether or
not Co or B is present. Adding Co, B or CoB does not change what the dewetted state looks like;
it changes how far above it the flat, wetting state sits.

Because each model is referenced to its own lowest energy, the quantity that compares the two
phases across models is the **separation between them** — the flat-basin minimum of Table 5 —
and that separation is exactly what boron reduces. The present data do not resolve
*how* boron reduces it: a lower flat-basin energy could equally arise from stabilising the flat
phase or from destabilising the island, and distinguishing the two would require the island
phase to be referenced to an absolute (rather than per-model) energy scale, or a converged
treatment of both basins. We therefore state the effect as a change in the flat–island
separation, not as the stabilisation of either phase individually.

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
- The low-energy structures of each branch form a **small set of recurring motifs** rather
  than one repeated structure, and ΔZ is continuous — the two phases are families, and the
  energetics above are compared unweighted, since the sampled densities are biased and not
  physical (MT-8; Supplementary Material).

The mechanistic origin of these trends (electronic structure, interface registry) and the
robustness of the method to its parameters are presented in the Supplementary Material.
