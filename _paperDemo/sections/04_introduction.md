# 04 — Introduction
     v1 (2026-09-18): first draft, written after Methods, Results and Discussion were approved. It
     closes on the frozen contribution sentence of the claim list, with the quoted energy shift and
     the significance value left to the Results. Three device-side references were added for this
     section and verified by DOI content negotiation. No Co host is discussed and the device material
     is referred to generically.

<!-- DRAFT v1 · section 04 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v11 (scope: Fe/MgO + Fe-B/MgO). Continuous prose, no subsections.
     Every number here is one already frozen in the approved Results: the two flat-basin minima,
     the shift between them, the island spans, the boron–oxygen window count and the exact
     search-level statistic. Nothing is introduced that is not in the frozen claim list.
     Citation keys added for this section: parkin2004, djayaprawira2005, ikeda2008. -->

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
\cite{urano1988}. Two structural outcomes thus compete at this coverage — a flat, well-wetting film
and a dewetted island — and the growth experiments constrain their kinetics rather than their
relative energies, while interface models assume the flat geometry by construction. What is missing
is a comparison of the two configurations' energies for one and the same interface, and an answer to
how that comparison responds to a change in the film's composition.

The composition is not arbitrary. The metal electrodes of the highest-magnetoresistance MgO junctions
are boron-bearing and amorphous as deposited, which is also the condition under which the MgO barrier
grows (001)-textured \cite{djayaprawira2005}. Boron is a glass-forming addition, and added species
are in general understood to stabilise disordered configurations at the expense of crystalline ones,
in the spirit of the confusion principle of metallic-glass formation \cite{greer1993} — a reading
this paper returns to in the Discussion. Applied to this interface, where the flat film is the
two-dimensional, disordered-like configuration and the island the three-dimensional, ordered-like
one, it suggests that boron should lower the energy of the flat configuration relative to the island.
Whether it does so, and by how much, is a question for calculation.

We address it by comparing the energies of the two configurations for a single host, with and without
an added metalloid. The two models are a single Fe layer on a single MgO(001) layer, about one
monolayer thick — 25 metal atoms on a 5 × 5 substrate cell — built on the computed Fe lattice
constant with the substrate compressed to match it; the second model differs only by three boron
atoms in the film, so that the comparison isolates the added species. Each model is sampled with a
surrogate-driven global optimisation search \cite{agox2020,gofee2017} that is deliberately seeded
from a flat reference film, so that the flat basin is populated from the outset and any lower-lying
basin the search finds is populated alongside it, and each model is run from a number of independent
random seeds. The landscape that results is read as a map of the two phases — film flatness against
relative energy — and the electronic-structure origin of what the search finds, together with the
sensitivity of the result to the search's method parameters and to the lattice constraint, is
reported in the Supplementary Material. The structures compared are not converged minima, and the
comparison is a trend obtained within a fixed lattice model; the bounds this places on the
interpretation are set out with the methods.

Both models answer the question of which configuration is preferred in the same way. The
lowest-energy structure found is an island in each, with a vertical span of about 3.7 Å — a result
that runs against the direction of the search's bias, since every search began from a flat reference
film and was perturbed only at small scale from it in its early iterations. The flat film is
nevertheless a distinct basin of the landscape rather than the high-span tail of a single minimum,
lying 0.1888 eV/atom above the island for Fe/MgO and 0.1493 eV/atom above it for Fe-B/MgO. Adding
boron therefore lowers the relative energy of the flat, wetting configuration by 0.040 eV/atom, a
21 % reduction of the flat–island separation, with a search-level two-sided test over the 19
independent searches giving p = 0.0444 — an exact enumeration of all 27 132 partitions of the pooled
search minima, whose resolution floor is p = 3.7 × 10⁻⁵. The effect is not interfacial: within the
low-energy window, only one of the 72 boron-containing structures has a boron–oxygen contact, so
boron acts inside the metal film. What boron does not do is displace the island as the ground state:
the ordered, three-dimensional configuration remains the more stable of the two in both models.

Boron insertion lowers the relative energy of the flat metal-film wetting state of Fe on MgO(001),
moving the flat, well-wetting configuration closer to the island ground state without displacing it —
relevant to interface flatness in MgO-based magnetic tunnel junction stacks.
