# 04 — Introduction
     v6 (2026-09-18): reverted to the full, step-by-step story (the v1–v4 style, addressing recent
     advances), per the scientist's preference, keeping the two refinements from v5: "enumerate" is
     replaced by "calculated" throughout (the exact statistic is "calculated over all 27 132 possible
     reshufflings"), and the what-we-do passage opens with "In this work, we ...". No number or claim
     changed.
     v5 (2026-09-18): rewritten lean and hook-style at the scientist's request — brief motivation, a
     compact "In this work, we ..." statement of what is done and found, and the closing contribution
     sentence, with the detailed method, results and discussion left to their own sections.
     SUPERSEDED by v6 (the scientist preferred the fuller story).
     v4 (2026-09-18): the significance statement now explains what p is, in plain terms — each of the
     19 searches contributes its own lowest flat-state energy, p = 0.0444 is the fraction of random
     reshufflings of those values into two groups of 13 and 6 that would reproduce a shift as large
     by chance alone, and the test is an exact enumeration (27 132 reshufflings, resolution floor
     p = 3.7 × 10⁻⁵). No number changed.
     v3 (2026-09-18): the phase-controlled design is now stated as a core methodological reason
     (the dewetted family is a continuous set, not a single structure, so exhaustive enumeration is
     not the goal), and the choice of GOFEE is justified in the introduction through its
     lower-confidence-bound property — LCB(r) = E(r) − κσ(r) balances exploitation against
     exploration and so guides the search toward the global minimum even when it is seeded from a
     flat reference film. New reference: hamamoto2023. No claim or number changed.
     v2 (2026-09-18): four recent MTJ-fabrication references added (scheike2023, solano2022,
     ichinose2025, ghemes2024) with a new paragraph on the recent fabrication trend; the
     metal-on-MgO islanding difficulty is now also anchored to modern device-scale growth
     (ichinose2025). No claim or number changed.
     v1 (2026-09-18): first draft, written after Methods, Results and Discussion were approved. It
     closes on the frozen contribution sentence of the claim list, with the quoted energy shift and
     the significance value left to the Results. No Co host is discussed and the device material is
     referred to generically.

<!-- DRAFT v6 · section 04 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v11 (scope: Fe/MgO + Fe-B/MgO). Continuous prose, no subsections.
     Every number here is one already frozen in the approved Results: the two flat-basin minima,
     the shift between them, the island spans, the boron–oxygen window count and the exact
     search-level statistic. Nothing is introduced that is not in the frozen claim list.
     Citation keys for this section: parkin2004, djayaprawira2005, ikeda2008 (device);
     scheike2023, solano2022, ichinose2025, ghemes2024 (recent fabrication trend);
     gofee2017, hamamoto2023 (the GOFEE/LCB method choice). -->

## Introduction

MgO-based magnetic tunnel junctions reach very large tunnel magnetoresistance at room temperature
when the barrier is crystalline and the metal electrodes are matched to it in-plane
\cite{yuasa2004,parkin2004}. The transport calculations that account for the effect were carried out
for an ideal Fe|MgO|Fe(001) interface, in which a flat metal layer sits directly above the substrate
oxygen \cite{butler2001}. Achieving those values in practice is a question of realising that
interface closely enough: the high magnetoresistance is obtained when the barrier is (001)-oriented
and the metal film flat and continuous \cite{yuasa2004}, and the barrier's orientation and stress
relaxation are themselves sensitive to how the metal is deposited and annealed
\cite{djayaprawira2005,ikeda2008}. The structural quality of the metal/oxide interface is therefore
part of the specification of the device rather than an incidental detail.

Two recent trends in junction fabrication have only sharpened that point. The first is the push on
the tunnel magnetoresistance itself: after a decade of stagnation at the 604 % reported in 2008 for
junctions with boron-alloy electrodes \cite{ikeda2008}, epitaxial junctions now reach a record 631 %
at room temperature (1143 % at 10 K), and the gain comes explicitly from the interface — from tuning
the crystallographic orientation and the oxygen content of the MgO barrier through ultrathin metal
insertions at the metal/oxide boundary \cite{scheike2023}. The second is the move to perpendicularly
magnetised junctions for dense, non-volatile memory, in which the metal/oxide interface is itself a
functional layer: the Fe/MgO interface carries a large perpendicular surface anisotropy, whose
strength is traced to the hybridisation of interfacial iron and oxygen states \cite{solano2022}, and
sub-nanometre metal films grown on the barrier are engineered for the perpendicular anisotropy and
the low magnetic damping that low-power switching requires \cite{ichinose2025}. Both trends converge
on the same requirement — a metal film that is flat, epitaxial and well-wetting on the crystalline
barrier — and, in practice, on layer-by-layer control of the roughness and thickness of each film in
the stack \cite{ghemes2024}.

The flat, lattice-matched film assumed in such interface models is not, however, the configuration
that a metal film necessarily adopts when it is deposited on MgO(001). At the monolayer coverages
relevant to a thin electrode, growth experiments find the film dewetting into three-dimensional
islands: He-atom scattering records three-dimensional island growth of Fe on MgO(001) at room
temperature, suppressed only when the film is deposited at 140 K \cite{fahsold2000}; scanning
tunnelling microscopy combined with X-ray magnetic circular dichroism finds sub-nanometre Fe growing
three-dimensionally, with a two-dimensional growth mode reported only above about 6.5 monolayers
\cite{torelli2009}; and grazing-incidence small-angle X-ray scattering on five monolayers likewise
identifies Volmer–Weber growth with spherical islands \cite{reitinger2007}. A flat, pseudomorphic
monolayer is obtained instead by slow deposition onto a cleaved, oxygen-annealed crystal
\cite{urano1988}. The islanding tendency survives even into the most controlled modern fabrication:
grain-to-grain epitaxial growth of a sub-nanometre ferromagnetic layer on a polycrystalline MgO(001)
barrier on 300 mm wafers must be performed at cryogenic temperature (100 K), because room-temperature
deposition lets the metal nucleate as islands and break the film's continuity \cite{ichinose2025}.
Two structural outcomes thus compete at this coverage — a flat, well-wetting film and a dewetted
island — and the growth experiments constrain their kinetics rather than their relative energies,
while interface models assume the flat geometry by construction. What is missing is a comparison of
the two configurations' energies for one and the same interface, and an answer to how that comparison
responds to a change in the film's composition.

The composition is not arbitrary. The metal electrodes of the highest-magnetoresistance MgO junctions
are boron-bearing and amorphous as deposited, which is also the condition under which the MgO barrier
grows (001)-textured \cite{djayaprawira2005}. Boron is a glass-forming addition, and added species
are in general understood to stabilise disordered configurations at the expense of crystalline ones,
in the spirit of the confusion principle of metallic-glass formation \cite{greer1993} — a reading
this paper returns to in the Discussion. Applied to this interface, where the flat film is the
two-dimensional, disordered-like configuration and the island the three-dimensional, ordered-like
one, it suggests that boron should lower the energy of the flat configuration relative to the island.
Whether it does so, and by how much, is a question for calculation.

In this work, we address it by comparing the energies of the two configurations for a single host,
with and without an added metalloid. The phase-controlled design follows from the nature of the two
configurations themselves. The flat film is a single, well-defined geometry, but the dewetted family
is not a single structure: it spans a continuous range of cluster sizes and heights rather than one
low-energy geometry, so an exhaustive calculation of its potential-energy surface is not the goal. We
therefore do not attempt one; instead the search is designed to resolve the two phases that the
wetting question is about — the flat, well-wetting film and the dewetted island — and to compare
their relative energies under a controlled change of composition.

We realise this with GOFEE, global optimisation with first-principles energy expressions
\cite{gofee2017}, a surrogate-driven global search in which a Gaussian-process model of the energy
landscape, trained on the fly from single-point DFT energies, decides which candidate structures are
worth evaluating with the full calculation \cite{hamamoto2023}. The selection rule is the lower
confidence bound, LCB(r) = E(r) − κσ(r): a candidate r is chosen by minimising its predicted energy
E(r) penalised by its predicted uncertainty σ(r), with κ a fixed constant (κ = 2 here). The two
terms pull in opposite directions — E(r) favours regions already found to be low in energy, while
the −κσ(r) term favours regions not yet sampled — so the bound keeps probing the uncertain parts of
the landscape even after a low basin has been located. That is what lets the search be seeded from a
flat reference film and still reach the island: the flat basin is populated from the outset, but the
acquisition continues to explore the territory where a genuinely lower configuration may lie, so the
search is guided toward the global minimum rather than confined to the reference configuration. Each
model is run from a number of independent random seeds.

The two models are a single Fe layer on a single MgO(001) layer, about one monolayer thick — 25 metal
atoms on a 5 × 5 substrate cell — built on the computed Fe lattice constant with the substrate
compressed to match it; the second model differs only by three boron atoms in the film, so that the
comparison isolates the added species. The sampled landscape is read as a map of the two phases —
film flatness against relative energy — and the electronic-structure origin of what the search finds,
together with the sensitivity of the result to the search's method parameters and to the lattice
constraint, is reported in the Supplementary Material. The structures compared are not converged
minima, and the comparison is a trend obtained within a fixed lattice model; the bounds this places on
the interpretation are set out with the methods.

Both models answer the question of which configuration is preferred in the same way. The
lowest-energy structure found is an island in each, with a vertical span of about 3.7 Å — a result
that runs against the direction of the search's bias, since every search began from a flat reference
film and was perturbed only at small scale from it in its early iterations. The flat film is
nevertheless a distinct basin of the landscape rather than the high-span tail of a single minimum,
lying 0.1888 eV/atom above the island for Fe/MgO and 0.1493 eV/atom above it for Fe-B/MgO. Adding
boron therefore lowers the relative energy of the flat, wetting configuration by 0.040 eV/atom, a
21 % reduction of the flat–island separation. A search-level two-sided permutation test quantifies
the confidence in this shift. Each of the 19 independent searches contributes its own lowest
flat-state energy — 13 from the boron-free model and 6 from the boron-containing one — and the test
asks how often a random reshuffling of those 19 values into two groups of 13 and 6 would, by chance
alone, produce a shift at least as large as the one observed. The answer is p = 0.0444: if boron had
no effect, a shift this large would still appear by chance in about 4.4 % of reshufflings. The test
is exact, calculated over all 27 132 possible reshufflings rather than sampled, so it is significant
at the 5 % level and its resolution floor is p = 3.7 × 10⁻⁵ — the conclusion is not an artefact of
too few searches. The effect is not interfacial: within the low-energy window, only one of the 72
boron-containing structures has a boron–oxygen contact, so boron acts inside the metal film. What
boron does not do is displace the island as the ground state: the ordered, three-dimensional
configuration remains the more stable of the two in both models.

Boron insertion lowers the relative energy of the flat metal-film wetting state of Fe on MgO(001),
moving the flat, well-wetting configuration closer to the island ground state without displacing it —
relevant to interface flatness in MgO-based magnetic tunnel junction stacks.
