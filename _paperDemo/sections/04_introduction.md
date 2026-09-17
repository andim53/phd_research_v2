# 04 — Introduction
     v5 (2026-09-18): rewritten lean and hook-style at the scientist's request — brief motivation, a
     compact "In this work, we ..." statement of what is done and found, and the closing contribution
     sentence, with the detailed method, results and discussion left to their own sections.
     "enumerate" is gone; the exact statistic is now "calculated exactly over all 27 132 possible
     reshufflings". The lower-confidence-bound and the meaning of p are kept as single clauses, not
     full derivations. No number or claim changed.
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

<!-- DRAFT v5 · section 04 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v11 (scope: Fe/MgO + Fe-B/MgO). Continuous prose, no subsections.
     Every number here is one already frozen in the approved Results: the two flat-basin minima,
     the shift between them, the island spans, the boron–oxygen window count and the exact
     search-level statistic. Nothing is introduced that is not in the frozen claim list.
     Citation keys for this section: parkin2004, djayaprawira2005, ikeda2008 (device);
     scheike2023, solano2022, ichinose2025, ghemes2024 (recent fabrication trend);
     gofee2017, hamamoto2023 (the GOFEE/LCB method choice). -->

## Introduction

MgO-based magnetic tunnel junctions reach their large magnetoresistance only when the metal film is
flat and the metal/oxide interface is well-wetting \cite{yuasa2004,parkin2004,butler2001}. A metal
film on MgO(001) does not, however, simply spread: at the monolayer coverages of a thin electrode,
room-temperature growth of Fe forms three-dimensional islands
\cite{fahsold2000,torelli2009,reitinger2007}, while a flat, pseudomorphic layer is obtained only by
slow or low-temperature deposition \cite{urano1988} — and the same islanding tendency is what modern
fabrication suppresses by growing sub-nanometre films on the barrier at cryogenic temperature
\cite{ichinose2025}. The flat film and the island are thus two competing configurations of the same
interface, and how an added element shifts their relative energies is largely open.

The question has become more pointed as fabrication has pressed on the interface itself: recent
record room-temperature magnetoresistance has been set by engineering the metal/oxide interface atom
by atom \cite{ikeda2008,scheike2023}, perpendicular junctions make the interface the source of the
required magnetic anisotropy \cite{solano2022,ichinose2025}, and both are practised through
layer-by-layer control of the stack \cite{ghemes2024}.

The composition of the film is part of the question. The electrodes of high-performance junctions are
boron-bearing and amorphous as deposited \cite{djayaprawira2005}, and added elements are understood
to favour the disordered, flat configuration over the ordered, island one — the confusion principle
of glass formation \cite{greer1993}. Whether boron actually lowers the flat film's energy relative to
the island, and by how much, is what we compute.

In this work, we compare the two configurations for a single host, Fe on MgO(001), with and without
added boron. We use a surrogate-driven global-optimisation search \cite{gofee2017,hamamoto2023} seeded
from a flat reference film, which maps both phases of the landscape and, through its acquisition rule
— the lower confidence bound, LCB = E − κσ, trading low predicted energy against uncertainty — can
escape the flat basin and reach a lower island even though it began from the flat configuration. The
two models differ only by the boron, so the comparison isolates the added element; the method, the
electronic-structure analysis and the sensitivity of the result to the search's parameters are given
in the Methods and the Supplementary Material.

We find that the island is the ground state in both models, despite the search being biased toward
the flat film, and that the flat configuration is a distinct, higher-energy basin. Adding boron lowers
the flat–island separation by 0.040 eV/atom, a 21 % reduction, at a search-level two-sided
permutation-test significance of p = 0.0444 — calculated exactly over all 27 132 possible
reshufflings of the 19 search minima — so that, if boron had no effect, a shift this large would
arise by chance in only about 4.4 % of reshufflings. Boron acts inside the film, not at the interface,
and does not displace the island as the ground state.

Boron insertion lowers the relative energy of the flat metal-film wetting state of Fe on MgO(001),
moving the flat, well-wetting configuration closer to the island ground state without displacing it —
relevant to interface flatness in MgO-based magnetic tunnel junction stacks.
