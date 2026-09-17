# 03 — Discussion

<!-- DRAFT v3 · section 03 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v5. All \cite{} keys resolve against references.bib; the three
     MTJ placeholders were replaced by yuasa2004 (verified) when the CoFeB-specific
     assertions were dropped. -->

## 3.1 Why the island is the ground state

The search finds an island ground state in every model, with the flat film sitting
0.15–0.19 eV/atom higher. The electronic-structure analysis (Supplementary Material)
indicates why. In the flat monolayer every metal atom is registry-locked directly atop an
oxygen of the MgO surface — the registry determined experimentally for the first monolayer of
Fe on MgO(001) by LEED I–V analysis \cite{urano1988} and used in first-principles models of the
Fe|MgO|Fe interface \cite{butler2001} — maximising Fe–O orbital overlap and pushing the Fe
d-band centre down to −0.23 eV. That registry, however, is bought at the cost of a 3.77 % in-plane
lattice mismatch. The island relieves this strain by abandoning the registry: the number
of metal atoms registered directly atop an oxygen drops from 25 (of 25) to 9 (of 25), the
island's interface Fe d-band centre rises to +0.51 eV (+0.60 eV averaged over all island
Fe), and the film becomes electronically "quieter" (lower DOS at the Fermi level, weaker
spin polarisation). The energy gain of the island is therefore dominated by **strain
relief** — metal atoms leave the strained registry rather than deepen it — and not by any
interfacial re-hybridisation benefit; the flat layer is over-coupled to the oxide at a
strain cost it cannot repay. This is consistent with the weak Fe–MgO coupling found in
first-principles treatments of the interface \cite{butler2001}, and with the experimental
observation that a flat monolayer requires low-temperature or slow deposition while room-
temperature growth gives 3D islands \cite{fahsold2000,reitinger2007}.

## 3.2 Why boron stabilises the flat film

Boron lowers the flat-state energy by ~0.04 eV/atom in both hosts, bringing the flat
configuration closer to the ground state. Two observations frame the mechanism. First,
boron does **not** bond to the MgO interface — it remains inside the metal film (a single
B–O contact in one of 72 windowed Fe-B structures) — so its effect is not interfacial.
Second, the effect is host-independent (Fe and Fe-Co respond almost identically), pointing
to an intrinsic, film-internal role.

**Confusion principle and amorphous formation.** The flat film can be read as the
disordered, amorphous-like configuration and the island as the ordered, crystalline-like
one. Under this reading, the stabilisation of the flat state by added elements follows the
**confusion principle** of metallic-glass formation \cite{greer1993}: the more elements in
an alloy, the harder it is for the alloy to select a viable crystal structure, and the
greater the tendency toward glass (amorphous) formation.

Our results are partly consistent with this. Adding boron lowers the flat-basin energy in
both hosts (Fe 0.1888 → Fe-B 0.1493 eV/atom; Fe-Co 0.1941 → Fe-Co-B 0.1494 eV/atom). They do
not, however, support compositional complexity *per se* as the driver. Adding Co alone leaves
the flat basin slightly *higher* in energy (0.1888 → 0.1941 eV/atom; §3.3), and the two
two-element systems differ far more from each other (Fe-B vs Fe-Co, 0.045 eV/atom) than
Fe-Co does from the three-element Fe-Co-B (0.003 eV/atom). Within these models the flat,
disordered configuration is therefore stabilised by the presence of boron, not by the
number of elements — consistent with the confusion principle acting through the added
metalloid, but not with a simple complexity-counting reading of it.

We note, however, that even the boron-containing models retain the island as their ground
state — the confusion principle stabilises the flat state but does not, in these small
model systems, fully suppress the ordered configuration. The precise origin of boron's
effect — whether it lowers the flat basin's energy or raises the island's — is not resolved
by the present data and is a natural target for the re-relaxation and further analysis.

## 3.3 Cobalt plays a minor role

Cobalt alone barely changes the flat-state energy (+0.005 eV/atom without boron, ~0 with
boron). The practical relevance is that the metal film in an MgO-based magnetic tunnel junction
must be a flat, coherently matched layer for the tunnelling magnetoresistance to reach its high
values \cite{yuasa2004}: within the present model, the wetting behaviour is set by boron, not by
the Fe/Co constitution of the host.

## 3.4 Implications for MTJ stacks

The performance of MgO-based magnetic tunnel junctions rests on the structural quality of the
metal/oxide interface. The giant tunnel magnetoresistance of single-crystal Fe/MgO/Fe junctions
arises from coherent spin-polarised tunnelling across a lattice-matched interface, with the
residual mismatch accommodated by interfacial dislocations and the growth conditions chosen to
minimise them \cite{yuasa2004}. The present results connect to this in two ways. First, they
show that the flat film is intrinsically strained and over-coupled to the oxide, so a perfectly
flat metal layer is energetically penalised — a consideration for interface engineering in the
CoFeB/MgO stack used in devices. Second, they show that boron acts to stabilise the flat
configuration without bonding to the interface, consistent with the picture of boron as a
film-internal agent that promotes a flat, well-wetting interface. These are trend-level,
model-system conclusions; quantitative transfer to a device stack would require the converged
relaxations and a fuller treatment of the interface.

## 3.5 Limitations

The results are qualitative/trend-level: the structures are not DFT-converged minima
(residual forces ~1–2 eV/Å), the models are single-layer slabs at Γ-point sampling, and
the flat/island split uses a chosen ΔZ threshold. The four systems also have unequal seed
counts (13 / 7 / 5 / 4 for Fe / Fe-B / Fe-Co / Fe-Co-B), so their sampling fractions are
compared only as trends, not as like-for-like populations. The flat state is described as a
higher-energy configuration, not a proven metastable state. A full re-relaxation of
representative structures is necessary to place these conclusions on converged minima.
