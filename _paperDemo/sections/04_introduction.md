# 04 — Introduction
     v13 (2026-09-18): one motivation sentence added before "Two structural outcomes thus compete
     ..." naming the two conventional origins of the dewetting, with no verdict (the reading stays in
     the Discussion, §3.1). Five new references (CLAIMS v12). No number or claim changed.
     **APPROVAL VOID / re-review pending.**
     **FULL-DRAFT RE-REVIEW OPENED 2026-09-18.** At the scientist's request the whole draft is
     re-opened for review — Methods, Results, Discussion, Introduction, Conclusion and Abstract
     together — ahead of adding the origin of the Volmer-Weber islanding to the Discussion.
     This entry records a review state, not an edit: no text, number, claim, table or figure
     changed and no draft version is bumped. **Every earlier approval recorded below is VOID
     for the duration of this review; each section needs re-approval.**
     v12 (2026-09-18): abbreviation pass requested by the scientist — "density-functional theory" now
     reads "density functional theory (DFT)" at its first use. No number or claim changed.
     **APPROVAL VOIDED** by this edit (v11 was approved 2026-09-18); re-approval pending.
     v11 (2026-09-18): the scientist's edit — in the reasoning paragraph, "the flat, amorphous-like
     configuration" is now simply "the flat configuration", dropping the amorphous-like label (which
     CLAIMS assigns to the Discussion as an interpretive framing). Line re-wrapped. No number or
     claim changed. **APPROVED 2026-09-18.**
     v10 (2026-09-18): a reasoning paragraph added between the Greer/boron paragraph and the
     "In this work, ..." passage, motivating the method: testing the confusion-principle question is
     not a single-calculation problem (the island is a family of many local minima, so one structure
     cannot represent it); because the question is about two phases we restrict to a deliberately
     biased exploration of those phases; and because exhaustive DFT is too costly we drive the search
     with a surrogate model. No number or claim changed; no new citation.
     v9 (2026-09-18): the scientist's edit — the confusion-principle sentence no longer carries the
     forward pointer "a reading this paper returns to in the Discussion"; the sentence now states the
     principle and applies it directly (the reading itself remains in the Discussion per CLAIMS, so
     checklist item C7 is unchanged). The paragraph was re-wrapped. No number or claim changed.
     v8 (2026-09-18): the what-we-do passage is rewritten in the example style — one achievement
     sentence ("In this work, by implementing a surrogate-driven active-learning search with a
     deliberately biased exploration strategy, we categorize the potential-energy surface ... and
     quantify how the added element shifts the relative energy of the flat mode") followed by a
     roadmap paragraph ("This paper is organized as follows. In Sec. II ... Sec. III ... Sec. IV ...
     Sec. V."). The redundant method/model/findings detail that repeated Methods §1 and Results §2 is
     removed; the detailed findings (island ground state, the 0.040 eV/atom shift, the p-value) now
     live in Results §2, and the closing contribution sentence belongs to the Conclusion. No claim or
     number removed from the frozen list; `CLAIMS.md` not bumped.
     v7 (2026-09-18): the GOFEE passage is merged into the what-we-do paragraph and trimmed — the
     method is now a single clause ("a surrogate-driven global optimisation") and the emphasis is on
     why the lower confidence bound is effective for a *biased* exploration (the search is seeded
     from the flat reference, yet the LCB keeps favouring low-energy and unsampled regions, so it can
     still reach the island). The GOFEE mechanics (surrogate-driven search, LCB acquisition, κ = 2)
     remain in Methods §1.2. No number or claim changed.
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

<!-- DRAFT v13 · section 04 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v11 (scope: Fe/MgO + Fe-B/MgO). Continuous prose, no subsections.
     As of v8 this section carries no numbers: the detailed findings (flat-basin minima, the shift,
     the p-value) live in Results §2. The motivation cites the growth/islanding literature and the
     recent fabrication trend; the achievement sentence and roadmap point to the sections. No claim
     is introduced that is not in the frozen list.
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
Two origins are conventionally assigned to such dewetting: the elastic strain energy of a
lattice-mismatched overlayer, which is the general heteroepitaxial description
\cite{mahato2012,kang2015}, and the difference in free surface energy between film and substrate,
which is the one the growth literature invokes for Fe on MgO(001), the free surface energy of Fe
being much the larger of the two and the lattice mismatch small \cite{ernult2003,dezsi2011}.
Two structural outcomes thus compete at this coverage — a flat, well-wetting film and a dewetted
island — and the growth experiments constrain their kinetics rather than their relative energies,
while interface models assume the flat geometry by construction. What is missing is a comparison of
the two configurations' energies for one and the same interface, and an answer to how that comparison
responds to a change in the film's composition.

The composition is not arbitrary. The metal electrodes of the highest-magnetoresistance MgO junctions
are boron-bearing and amorphous as deposited, which is also the condition under which the MgO barrier
grows (001)-textured \cite{djayaprawira2005}. Boron is a glass-forming addition, and added species
are in general understood to stabilise disordered configurations at the expense of crystalline ones,
in the core of the confusion principle of metallic-glass formation \cite{greer1993}. Applied to this
interface, where the flat film is the two-dimensional, disordered-like configuration and the island
the three-dimensional, ordered-like one, it suggests that boron should lower the energy of the flat
configuration relative to the island.
Whether it does so, and by how much, is a question for calculation.

Testing this idea directly is not a single-calculation question. The flat configuration is one
well-defined structure, but the ordered island it competes with is not: the
dewetted film comprises a large family of distinct structures with many local minima, so no one
geometry can represent it, and the two phases cannot be compared by relaxing a single candidate of
each. The confusion-principle question — whether an added element lowers the disordered configuration
relative to the ordered one — is therefore about the landscape as a whole, and one that is expensive
to answer, because exploring it with density functional theory (DFT) alone would require evaluating far too
many structures. Two features of the problem make it tractable. First, the question is specifically
about two phases — the flat, well-wetting film and the dewetted island — so rather than surveying
every configuration we restrict the exploration to these two targets, a deliberately biased strategy.
Second, because the search must still sample many candidates to populate both phases, we guide it with
a surrogate model, so that the expensive density-functional evaluations are spent only where they are
most informative.

In this work, by implementing a surrogate-driven active-learning search with a deliberately biased
exploration strategy \cite{gofee2017,hamamoto2023}, we categorize the potential-energy surface of Fe
on MgO(001) into its two growth modes — the flat, well-wetting film and the dewetted island — for the
same host with and without added boron, and quantify how the added element shifts the relative energy
of the flat mode.

This paper is organized as follows. In Sec. II, we present the active-learning search, the two
interface models, and the metrics used to separate the two growth modes. In Sec. III, we first
establish the two-phase landscape and the island ground state, and then report the effect of boron on
the flat–island separation. In Sec. IV, we discuss the origin of the island ground state and the role
of the added element. We summarize our work in Sec. V.
