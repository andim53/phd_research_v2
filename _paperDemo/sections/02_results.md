# 02 — Results
     v5 (2026-09-18): the two main-text figures are now cited and captioned — Figure 2 (the sampled
     two-phase landscape, §2.1) and Figure 3 (the flat-basin comparison, §2.2). No claim, number or
     table changed. APPROVED 2026-09-18.
     v4 (2026-09-17): re-scoped to the Fe host (CLAIMS v9). All Co/CoB results, the 2 x 2 design
     and the MT-4/MT-5 paragraphs are out of the paper; the p-value is now the exact 0.0444 of
     CLAIMS v9 §4; Tables 4-5 became Tables 3-4. TO BE RE-APPROVED — no prior approval survives.

<!-- DRAFT v5 · section 02 of the manuscript (markdown-first, pre-LaTeX)
     Fe/MgO and Fe-B/MgO only (CLAIMS v9). The biased search yields an EXPLORATION density over
     the flat (wetting) and island (dewetting) phases — not a thermodynamic DoS, so the weights
     are not physical. Organized by phase, not by additive.
     MT-6 is WITHDRAWN and no flat-fraction comparison appears here; MT-8 is claimed in §2.1;
     MT-4/MT-5 are ARCHIVED with the Co host and no longer appear.
     Every number traces to analysis/pes_structures.csv or analysis/ensemble_stats.json. -->

## 2.1 The two-phase landscape of the metal film on MgO

Our target is the wetting of the metal film on MgO(001). The property that distinguishes a
wetting from a dewetting film is its flatness, measured by the vertical span of the film,
ΔZ = z(metal)_max − z(metal)_min over the film's metal atoms (Fe); ΔZ ≈ 0 is a flat, wetting
film and large ΔZ a three-dimensional island. We therefore designed the search to return a
**map of this two-phase landscape**: a GOFEE global optimisation (Methods §1.2) **seeded from a
flat reference layer**, so that the flat basin is populated from the outset and any
lower-lying basin the search finds is populated alongside it. The result is a sampled
distribution over ΔZ and energy — an *exploration* density, not a thermodynamic density of
states. Because the sampling is deliberately biased, we use it only for unweighted structural
and energetic comparisons; the number of structures in a basin is a descriptive attribute of
the sampled database, not a physical population.

Across the two models the search returns 1723 structures spanning ΔZ from 0.001 to 5.57 Å,
with both phases populated in each (Table 3). Fig. 2 draws that landscape: every structure is
placed at its own vertical span and at its energy above the model's lowest, so the figure is the map
the search was designed to produce rather than a selection of representative structures. The points
form a continuous band that descends from the flat window into an island minimum near ΔZ = 3.7 Å in
both models, and the two panels share one energy scale, so a given height means the same relative
energy in either.

**Table 3.** The two phases in each model (ΔZ ≤ 1.0 Å = flat/wetting; ΔZ > 1.0 Å = island).

| Model | Structures | Island | Flat | Global-min ΔZ (Å) | Flat-basin min dE/N (eV/atom) |
|-------|-----------|--------|------|-------------------|-------------------------------|
| Fe/MgO | 1180 | 985 | 195 | 3.65 | 0.1888 |
| Fe-B/MgO | 543 | 430 | 113 | 3.77 | 0.1493 |

**Figure 2.** The sampled two-phase landscape of the metal film on MgO. Each point is one structure
from the Fe/MgO (left) and Fe-B/MgO (right) searches, plotted as its relative energy dE/N above the
model's own lowest energy against the vertical span of the film, ΔZ. The shaded band is the flat
window (ΔZ ≤ 1.0 Å); the star marks the model's lowest-energy structure and the diamond the best
member of its flat basin. Both panels use the same energy scale.

**The island is the ground state in both models, despite the flat bias.** The lowest-energy
structure found is an island in each model, with its global minimum at ΔZ = 3.65 Å (Fe/MgO) and
3.77 Å (Fe-B/MgO) (Table 3, column 5) — a three-dimensional cluster rather than a flat film. This
result is *against* the direction of the bias: every search was seeded from a flat reference layer
and, in the early phases, perturbed only at small scale from it, so the flat configuration had a
systematic head start. The search nevertheless left the flat basin and converged on an island in
both models. The flat-wetting state is therefore not an artefact of how the initial structures
were built — it is genuinely higher in energy than the island. (MT-1)

**The flat configuration is a distinct, higher-energy basin.** Taking for each model the
lowest-energy structure with ΔZ ≤ 1.0 Å isolates the flat basin's best member. In both models it
lies above the global minimum — by 0.1888 eV/atom for Fe/MgO and 0.1493 eV/atom for Fe-B/MgO
(Table 3, column 6). The flat film is thus a separate basin of the landscape, not merely the
high-ΔZ tail of a single minimum. (MT-2)

**The branches are families, not single structures.** The ΔZ values are continuous rather
than grouped into discrete island heights: in each model the island branch spans ΔZ ≈ 1–5.6 Å
with a median of 3.02 Å (Fe/MgO) and 2.58 Å (Fe-B/MgO), and the flat branch spans the whole
window below 1 Å. The low-energy members of each branch are likewise not a single repeated
structure: comparing the lowest-energy structures of each branch by their radial/angular
fingerprint shows that each branch's low-energy set splits into **two** distinct structural
motifs, and that a motif recurs across independent searches — for Fe/MgO, the five lowest flat
structures come from five different searches and fall into two motifs, four of them in the
dominant one. (MT-8)
The fingerprint is computed on the whole template-plus-film structure, so the fixed MgO
template compresses the pair distances and the motif count is a **lower bound** on the
structural diversity present; a film-resolved descriptor would be sharper. Pairwise distances
within the low-energy set of a branch are 0.41–0.44 of that branch's random-pair distance scale,
i.e. the low-energy structures are consistently more compact than the branch as a whole. The
count is also limited by how many searches contribute to the low-energy set: the Fe-B/MgO flat
set within 0.02 eV/atom of its minimum comes from two searches and its island set from three, so
those counts rest on fewer independent searches than the corresponding Fe/MgO numbers (five and
four).

**Experimental correspondence.** The films in this study are about **one monolayer thick on
average** — 25 metal atoms per 25 substrate sites in the 5 × 5 cell, the boron-containing film
carrying three additional boron atoms — and that is the regime in which the growth
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

## 2.2 The flat (wetting) phase with and without boron

With the two phases established, we compare how adding boron to the Fe film shifts the flat basin.
Table 4 gives the flat-basin minimum dE/N for the two models, i.e. the same host with and without
the metalloid, and Fig. 3 places the two values side by side with the change between them
marked.

**Table 4.** Flat-basin minimum dE/N (eV/atom) for the same Fe host with and without boron.

| Film | Flat-basin min dE/N (eV/atom) | B effect |
|------|-------------------------------|----------|
| Fe | 0.1888 | — |
| Fe-B | 0.1493 | **−0.040** |

**Figure 3.** Flat-basin minimum relative energy for the same Fe host with and without boron. A bar
is the lowest energy found among the structures of the flat window (ΔZ ≤ 1.0 Å), in eV/atom above
the model's own lowest energy, and the bracket gives the shift produced by boron.

**Boron lowers the flat-state energy.** Adding boron lowers the flat basin's best member by
0.040 eV/atom — from 0.1888 to 0.1493 eV/atom — a 21 % reduction of the flat–island separation.
(MT-3) The effect is measured across 13 independent Fe/MgO searches and 6 independent Fe-B/MgO
searches; its search-level significance is given in the uncertainty paragraph below.

**Boron does not bond to the MgO interface.** Restricting to the low-energy window
(dE/N ≤ 0.05 eV/atom), only 1 of the 72 Fe-B/MgO structures in that window has any boron atom
within 2.6 Å of an oxygen of the substrate; the maximum boron–oxygen contact fraction in the
window is 0.33. Outside the window the picture is different — 101 of the 471 remaining Fe-B/MgO
structures do have a boron–oxygen contact — which is why the statement is restricted to the
low-energy window rather than made over all sampled structures. Boron therefore remains inside the
metal film rather than wetting the oxide, so its effect on the flat phase is film-internal
rather than a change in interfacial bonding. (MT-7)

**Uncertainty from the choice of search.** Each model was searched from several independent
random seeds (13 completed searches for Fe/MgO, 6 for Fe-B/MgO), and structures from one search
are correlated with each other, so the independent unit is the search, not the structure. Taking
each search's own flat-basin minimum, the per-search minimum falls from 0.2171 eV/atom without
boron to 0.1882 eV/atom with it on average (medians 0.2185 and 0.1834), a **median** shift of
0.0351 eV/atom with 94 % of resampled replicates agreeing in sign — the effect is not carried by a
single favourable search, and the best-structure difference of Table 4 (−0.040 eV/atom) is the
extreme of the same distribution rather than a lone outlier. A two-sided permutation test over the
19 searches gives **p = 0.0444**, significant at the 5 % level. The test is an **exact enumeration
of all 27 132 partitions** of the pooled search minima, so this value is exact for the data and its
resolution floor is p = 3.7 × 10⁻⁵ — more than three orders of magnitude below the value reported,
i.e. the conclusion is not an artefact of too few searches.

## 2.3 The island (dewetting) phase and the separation between phases

Adding boron leaves the *island* phase qualitatively similar. In both models the lowest-energy
structure is an island — at ΔZ = 3.65 Å (Fe/MgO) and 3.77 Å (Fe-B/MgO) (Table 3) — and the island
branch spans the same broad range of heights in both (ΔZ ≈ 1–5.6 Å, median 3.02 Å without boron and
2.58 Å with it). Boron does not change what the dewetted state looks like; it changes how far above
it the flat, wetting state sits.

Because each model is referenced to its own lowest energy, the quantity that compares the two
phases is the **separation between them** — the flat-basin minimum of Table 4 — and that separation
is what boron reduces. The present data do not resolve *how* boron reduces it: a lower flat-basin
energy could equally arise from stabilising the flat phase or from destabilising the island, and
distinguishing the two would require the island phase to be referenced to an absolute (rather than
per-model) energy scale, or a converged treatment of both basins. We therefore state the effect as
a change in the flat–island separation, not as the stabilisation of either phase individually.

## 2.4 Summary of the results

- The biased GOFEE search, seeded from a flat reference, maps both the flat (wetting) and
  island (dewetting) phases in both models, over ΔZ = 0.001–5.57 Å.
- **The island is the ground state in both models** (ΔZ = 3.65 and 3.77 Å), even though the search
  was biased toward the flat configuration — the flat bias did not manufacture the result.
- **The flat configuration is a distinct, higher-energy basin**, 0.1888 eV/atom above the island
  for Fe/MgO and 0.1493 eV/atom for Fe-B/MgO — in both cases a separate basin, not the high-ΔZ
  tail of a single minimum.
- **Boron lowers the flat–island separation by 0.040 eV/atom** (13 vs 6 completed searches,
  exact two-sided permutation p = 0.0444).
- **Boron does not bond to the MgO interface** — it stays within the film, so its effect on the
  flat phase is film-internal.
- The low-energy structures of each branch form a **small set of recurring motifs** rather
  than one repeated structure, and ΔZ is continuous — the two phases are families, and the
  energetics above are compared unweighted, since the sampled densities are biased and not
  physical (MT-8).

The mechanistic origin of these trends (electronic structure, interface registry) and the
robustness of the method to its parameters are presented in the Supplementary Material.
