# 03 — Discussion
     v6 (2026-09-18): editorial pass requested by the scientist — the bold-lead paragraphs
     ("Confusion principle and amorphous formation.", "The search-level statistic rests on 19
     searches, and it is asymmetric.") are now sub-sub headings and all mid-paragraph bold emphasis
     is removed. No number or claim changed. **APPROVAL VOIDED** by this edit (v5 was approved
     2026-09-18); re-approval pending.
     v5 (2026-09-17): re-scoped to the Fe host (CLAIMS v9) — the cobalt section is deleted (no
     sentence about the Co host anywhere), the host-independence argument and the element-count
     data bound are gone, §3.5 renumbered to §3.4 and its search-count paragraph rewritten for
     the exact test. APPROVED 2026-09-18 — the gate for the introduction is open.

<!-- DRAFT v5 · section 03 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v9 (scope: Fe/MgO + Fe-B/MgO). All \cite{} keys resolve against
     references.bib; the three MTJ placeholders were replaced by yuasa2004 (verified) when the
     CoFeB-specific assertions were dropped.
     v4 note: §3.1 mechanism rewritten (no lattice-strain relief; strain sits on the substrate). -->

## 3.1 Why the island is the ground state

The search finds an island ground state in both models, with the flat film sitting
0.19 eV/atom higher for Fe/MgO and 0.15 eV/atom higher for Fe-B/MgO. The
electronic-structure analysis (Supplementary Material)
indicates why. In the flat monolayer every metal atom is registry-locked directly atop an
oxygen of the MgO surface — the registry of the reference construction, and the one determined
experimentally for the first monolayer of Fe on MgO(001) by LEED I–V analysis \cite{urano1988}
and used in first-principles models of the Fe|MgO|Fe interface \cite{butler2001} — maximising
Fe–O orbital overlap and pushing the Fe d-band centre down to −0.23 eV. The island abandons
that registry: the number of metal atoms registered directly atop an oxygen drops from 25 (of
25) to 9 (of 25), the island's interface Fe d-band centre rises to +0.51 eV (+0.60 eV averaged
over all island Fe), and the film becomes electronically "quieter" (lower DOS at the Fermi
level, weaker spin polarisation). The island's energy gain is therefore dominated by reduced
forced interfacial coupling and restored metal cohesion: the registry-locked monolayer spends
its bonding on Fe–O contacts while forgoing the three-dimensional Fe–Fe coordination available
to a cluster, and the island reverses that trade.

It is not a lattice-strain effect. The in-plane mismatch of this interface (3.6 % of the MgO
lattice against the Fe lattice, §1.1) is carried by the substrate, which is built in that
compressed state and held fixed, not by the film; the Fe film sits at its own equilibrium lattice
constant and is not strained in-plane, so there is no film strain for the island to relieve.
The mechanism is consistent with the weak Fe–MgO coupling found in first-principles treatments
of the interface \cite{butler2001}, and with the experimental observation that a flat monolayer
requires low-temperature or slow deposition while room-temperature growth gives 3D islands at
the same one-monolayer coverage \cite{fahsold2000,torelli2009,reitinger2007}.

## 3.2 Why boron stabilises the flat film

Boron lowers the flat-state energy by 0.040 eV/atom, bringing the flat configuration closer to
the ground state. Two observations frame the mechanism. First, boron does not bond to the MgO
interface — it remains inside the metal film (a single B–O contact in one of 72 windowed Fe-B
structures) — so its effect is not interfacial. Second, the shift is not carried by one favourable
search: the Fe-B model's six per-search flat minima lie between 0.1493 and 0.2481 eV/atom, five of
them below the Fe host's median of 0.2185 eV/atom, and 94 % of resampled replicates agree in sign
(§2.2). Both observations point to an intrinsic, film-internal role for boron rather than an
interfacial or statistical one.

### Confusion principle and amorphous formation

The flat film can be read as the
disordered, amorphous-like configuration and the island as the ordered, crystalline-like
one. Under this reading, the stabilisation of the flat state by added elements follows the
confusion principle of metallic-glass formation \cite{greer1993}: the more elements in
an alloy, the harder it is for the alloy to select a viable crystal structure, and the
greater the tendency toward glass (amorphous) formation.

Our results are partly consistent with this. Adding boron lowers the flat-basin energy
(0.1888 → 0.1493 eV/atom), i.e. the added element stabilises the disordered configuration relative
to the ordered one, in the direction the principle predicts. The present models test this for a
single added metalloid and cannot decide between the competing readings of the principle — whether
it acts through the *presence of an added species* by a film-internal mechanism, or through the
*number* of species, which would require the same host with two different additions to separate. We
therefore read our result as consistent with the confusion principle acting through the added
metalloid and leave the element-count reading untested here (see §3.4).

We note, however, that the boron-containing film retains the island as its ground state — the
confusion principle stabilises the flat state but does not, in this small model system, fully
suppress the ordered configuration. The precise origin of boron's effect — whether it lowers the
flat basin's energy or raises the island's — is not resolved by the present data and is a natural
target for the re-relaxation and further analysis.

## 3.3 Implications for MTJ stacks

The performance of MgO-based magnetic tunnel junctions rests on the structural quality of the
metal/oxide interface. The giant tunnel magnetoresistance of single-crystal Fe/MgO/Fe junctions
arises from coherent spin-polarised tunnelling across a lattice-matched interface, with the
residual mismatch accommodated by interfacial dislocations and the growth conditions chosen to
minimise them \cite{yuasa2004}. The present results connect to this in two ways. First, they
show that a perfectly flat, registry-locked metal layer maximises Fe–O bonding at the expense of
metal coordination and is therefore energetically penalised relative to a clustered film — a
consideration for interface engineering in MgO-based tunnel junctions, whose barrier must stay
flat and coherently matched for the tunnelling magnetoresistance to reach its high values
\cite{yuasa2004}. Second, they show that boron acts to stabilise the flat configuration without
bonding to the interface, consistent with the picture of boron as a film-internal agent that
promotes a flat, well-wetting interface.
These are trend-level, model-system conclusions; quantitative transfer to a device stack would
require the converged relaxations and a fuller treatment of the interface.

## 3.4 Limitations

One scope bound follows from the design rather than from the methods. The paper compares a single
host with and without one added element, boron. Nothing here separates the effect of *boron* from
the effect of *an added element as such*; that would need a second chemically different addition in
the same host, which is not analysed (the element-count reading of the confusion principle is
therefore untested — §3.2). What the design does exclude is a trivial explanation from the
construction: the two models share the lattice constant, substrate, reference-layer geometry and
candidate-generation schedule, and differ only by the boron (§1.6).

The results are qualitative/trend-level: the structures are not DFT-converged minima
(residual forces ~1–2 eV/Å), the models are single-layer slabs at Γ-point sampling, and
the flat/island split uses a chosen ΔZ threshold. The two models also have unequal seed
counts (13 completed searches for Fe/MgO against 6 for Fe-B/MgO) and their atom counts differ
(75 and 78), so sampling fractions are compared only as trends, not as like-for-like populations.
The flat state is described as a
higher-energy configuration, not a proven metastable state. A full re-relaxation of
representative structures is necessary to place these conclusions on converged minima.

Two features of the model itself bound the interpretation. First, the strain convention is the
inverse of the experimental stack: here the in-plane lattice is the Fe lattice constant and the
MgO substrate is the compressed component, held fixed, whereas in a real junction the bulk
MgO imposes its lattice on a thin Fe film, which absorbs the mismatch as in-plane strain and
relieves it through interfacial dislocations \cite{yuasa2004}. The film in this work is therefore
unstrained, and this model does not represent the strained-film situation. Second, both phases are
built on a body-centred-cubic Fe lattice, while the experimentally reported structure of ultrathin
Fe on MgO(001) is body-centred tetragonal below about 10 Å \cite{urano1988}; the island branch
(ΔZ ≈ 1–5.6 Å) lies in that regime (§1.6). The flat–island comparison is therefore a trend obtained
within one fixed lattice model, and extending it to thicker, experimentally strained films would
require a different construction.

### The search-level statistic rests on 19 searches, and it is asymmetric

The comparison pools
13 completed searches of the Fe/MgO model against 6 of the Fe-B/MgO model. The permutation test
enumerates all 27 132 partitions of that pool, so its resolution floor is p = 3.7 × 10⁻⁵ and the
reported p = 0.0444 is not limited by the number of searches; it would, however, tighten with more
completed Fe-B/MgO searches, since the smaller group sets the width of the null. Two further
bounds follow from the same asymmetry. The boron-free interface statement (§2.2) is measured on the
72 Fe-B/MgO structures inside the low-energy window, which come from four of the six searches —
so its effective number of independent observations is closer to four than to 72 — and the Fe-B/MgO
motif counts (§2.1) rest on two (flat) and three (island) searches against five and four for
Fe/MgO. Statements resting on those sets are correspondingly weaker evidence than the flat-basin
energies of Table 4, which use every search of both models.
