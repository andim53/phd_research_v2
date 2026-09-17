# 03 — Discussion

<!-- DRAFT v1 · section 03 of the manuscript (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v1. MTJ-context citations are placeholders (UNVERIFIED) —
     to be fetched in Phase D before the LaTeX port. -->

## 3.1 Why the island is the ground state

The search finds an island ground state in every model, with the flat film sitting
0.15–0.19 eV/atom higher. The electronic-structure analysis (Supplementary Material)
indicates why. In the flat monolayer every metal atom is registry-locked directly atop an
oxygen of the MgO surface, maximising Fe–O orbital overlap and pushing the Fe d-band centre
down to −0.23 eV. That registry, however, is bought at the cost of a 3.77 % in-plane
lattice mismatch. The island relieves this strain by abandoning the registry: Fe–O contacts
drop from 25 to 9, the d-band centre rises toward bulk-like values (+0.5–0.6 eV), and the
film becomes electronically "quieter" (lower DOS at the Fermi level, weaker spin
polarisation). The energy gain of the island is therefore dominated by **strain relief and
metal cohesion**, not by any interfacial re-hybridisation benefit — the flat layer is
over-coupled to the oxide at a strain cost it cannot repay.

## 3.2 Why boron stabilises the flat film

Boron lowers the flat-state energy by ~0.04 eV/atom in both hosts, bringing the flat
configuration closer to the ground state. Two observations frame the mechanism. First,
boron does **not** bond to the MgO interface — it remains inside the metal film — so its
effect is not interfacial. Second, the effect is host-independent (Fe and Fe-Co respond
almost identically), pointing to an intrinsic, film-internal role.

**Confusion principle and amorphous formation.** The flat film can be read as the
disordered, amorphous-like configuration and the island as the ordered, crystalline-like
one. Under this reading, the stabilisation of the flat state by added elements follows the
**confusion principle** of metallic-glass formation \cite{greer1993}: the more elements in
an alloy, the harder it is for the alloy to select a viable crystal structure, and the
greater the tendency toward glass (amorphous) formation. The progression Fe → FeCo → FeCoB
increases compositional complexity, and our results show a corresponding trend: the
flat-state energy falls and flat-basin sampling rises as the film becomes more
compositionally complex, with boron the decisive addition. This is consistent with the
confusion principle acting to frustrate crystallisation and favour the flat, disordered
configuration.

We note, however, that even the most complex model (FeCoB) retains the island as its ground
state — the confusion principle stabilises the flat state but does not, in these small
model systems, fully suppress the ordered configuration. The precise origin of boron's
effect — whether it lowers the flat basin's energy or raises the island's — is not resolved
by the present data and is a natural target for the re-relaxation and further analysis.

## 3.3 Cobalt plays a minor role

Cobalt alone barely changes the flat-state energy (+0.005 eV/atom without boron, ~0 with
boron). This is notable given that CoFeB is the standard free-layer alloy in magnetic
tunnel junctions \cite{cofebmgo_mtj} % UNVERIFIED — verify before port (Phase D)
: within the present model, the wetting behaviour is set by boron, not by the Fe/Co
constitution of the host.

## 3.4 Implications for MTJ stacks

Interface flatness and boron segregation are known to govern the performance of
CoFeB/MgO magnetic tunnel junctions, in particular the perpendicular magnetic anisotropy
(PMA) and the tunnelling magnetoresistance \cite{cofebmgo_pma} % UNVERIFIED — verify before port (Phase D)
\cite{b_diffusion_mtj} % UNVERIFIED — verify before port (Phase D)
. The present results connect to this in two ways. First, they show that the flat film is
intrinsically strained and over-coupled to the oxide, so a perfectly flat CoFeB layer is
energetically penalised — a consideration for interface engineering. Second, they show that
boron acts to stabilise the flat configuration without bonding to the interface, consistent
with the picture of boron as a film-internal agent that promotes a flat, well-wetting
interface. These are trend-level, model-system conclusions; quantitative transfer to a
device stack would require the converged relaxations and a fuller treatment of the
interface.

## 3.5 Limitations

The results are qualitative/trend-level: the structures are not DFT-converged minima
(residual forces ~1–2 eV/Å), the models are single-layer slabs at Γ-point sampling, and
the flat/island split uses a chosen ΔZ threshold. The flat state is described as a
higher-energy configuration, not a proven metastable state. A full re-relaxation of
representative structures is prepared to place these conclusions on converged minima.
