# Supplementary Material
     v7 (2026-09-17): §S4 (iteration budget, SI-9) and §S5 (lattice constraint, SI-10) added —
     two new boron-free Fe/MgO robustness studies (CLAIMS v10). New floats: Table S4 + Figure S7
     (§S4), Table S5 + Figure S8 (§S5). Awaiting review.

     v6 (2026-09-17): no code in the section — figure captions no longer carry file paths, the two
     perturbation generators, the reference-construction routine and the 2.3 Å construction distance
     are described in words, and the data-file references are replaced by Table S1/S2/S3. No claim,
     number, table or figure changes. Awaiting review.

     v5 (2026-09-17): three passages reworded so the section carries no revision history (scientist's
     instruction): §S2's interface definition and caveats, §S3's kappa paragraph and baseline count.
     No claim, number, table or figure changes. Awaiting review.

     v4 (2026-09-17): scope note only — the paper is Fe/MgO + Fe-B/MgO (CLAIMS v9). No SI claim,
     number or figure changes; §S1 and §S3 are Fe/MgO-only by construction and §S2 is the flat-vs-
     island PDOS of Fe/MgO.

     v3 (2026-09-17): S2 (PDOS / island origin) and S3 (method-parameter sensitivity) added;
     S3 numbers purged to completed searches only.

<!-- DRAFT v3 · supplementary document (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v9 (scope: Fe/MgO + Fe-B/MgO). Planned structure:
       S1  Performance of the biased exploration in finding the global minimum  [drafted here]
       S2  PDOS — origin of island formation (flat vs island)   [documented in experiment_log.md]
       S3  Method-parameter sensitivity (rattle / kappa / dipole) [documented in experiment_log.md]
     SI figures are flagged [SI]; SI claims are prefixed [SI] in paper_status.md.
     S1's claim is CLAIMS SI-8 (v4; signed off 2026-09-17).
     S2 drafted 2026-09-17 (CARRIES the v6 reframing: the island's gain is reduced forced
     interfacial coupling plus restored metal cohesion — NOT lattice-strain relief; the
     Fe-atop-O registry is inherited from the reference construction and is a consistency
     check, not a search prediction). Claims SI-1 … SI-4.
     S3 drafted 2026-09-17. Claims SI-5 (kappa), SI-6 (dipole), SI-7 (rattle).
     S4 drafted 2026-09-17 (v10). Claim SI-9 (iteration budget). Fe/MgO, boron-free.
     S5 drafted 2026-09-17 (v10). Claim SI-10 (lattice constraint). Fe/MgO, boron-free.
     Only completed searches (100 iterations) are used, everywhere in this paper. See CLAIMS v8:
     unfinished runs biased the original comparison, and "kappa = 1 is best" was retracted as an
     artefact of one such run sitting in the baseline. -->

## S1 Performance of the biased exploration in finding the global minimum

The main text uses only structures from iteration ≥ 10, because relaxation of candidates begins
at that iteration. Here we instead use **all** iterations of the Fe/MgO model — the model with
the largest number of independent searches (13) — to characterise how the biased exploration
progresses towards the global minimum, and to show what the discarded early iterations contain.
Energies are given as ΔE/N = (E − E_globalmin)/N relative to the lowest energy found anywhere in
the 13 searches, so the best-known energy descends to zero (Fig. S1).

**Figure S1.** Best-so-far ΔE/N against
iteration for each of the 13 searches, with the median over searches in black; (b) the lowest
energy found in each iteration (points) and the best-known energy across all searches (black
line), with the iterations at which it first crosses 0.20, 0.10, 0.05, 0.02 and 0.005 eV/atom
marked; (c) the fraction of searches whose own best-so-far has come within 0.05 and 0.02 eV/atom
of the global minimum. The vertical line in each panel marks iteration 10, where relaxation
begins.

**The onset of relaxation is the pivot of the search.** Across iterations 1–9 the best-known
energy falls only from 0.494 to 0.435 eV/atom — 0.06 eV/atom, about 12 % of the total descent of
the run. At iteration 10, the first iteration at which candidates are surrogate-relaxed, it
drops from 0.435 to 0.250 eV/atom in a single iteration: **approximately half of the entire
descent of the run (49 %) occurs at the onset of relaxation**. The per-search drop across the
onset has a median of 0.165 eV/atom and a range of 0.084–0.233 eV/atom, so the step is a
property of every search rather than of one.

**Before the onset the candidates cannot be ranked.** The structures evaluated in iterations 1–9
are unrelaxed placements, so their energy ordering reflects the starting geometry rather than any
relaxed configuration: several searches plateau after the second or third iteration and show no
further improvement for the remainder of the pre-relaxation phase. This is why the main-text
analysis discards them, and why their exclusion is not a loss of evidence.

**After the onset the descent proceeds in a long, progressively finer sequence.** The best-known
energy reaches 0.219 (i = 20), 0.078 (i = 30) and 0.030 eV/atom (i = 50) — 84 % of the total
descent complete by iteration 30 and 94 % by iteration 50 — with successive crossings of
0.20 eV/atom at i = 23, 0.10 at i = 29, 0.05 at i = 46, 0.02 at i = 57 and 0.005 at i = 72. The
global minimum is first reached at iteration 77 by one of the searches, and the searches are
still making small improvements when the run ends at iteration 100.

**The searches do not agree on the answer.** Only 10 of the 13 searches end within 0.05 eV/atom of
the global minimum, and only 4 within 0.02; the median search finishes 0.040 eV/atom above it
(per-search final values 0.000–0.086 eV/atom). A single search supplies the global minimum and a
second comes within 0.001 eV/atom of it. The final energy reached by a search therefore carries a
sizeable spread, which is why the main text compares basins across searches rather than quoting
one structure per model.

**Caveats.** The energies are single GPAW steps on surrogate-relaxed structures (residual forces
~1–2 eV/Å), so this characterises the behaviour of the *search* rather than the convergence of any
individual structure. Iteration is an AGOX counter, not a computational cost: each iteration
generates 20 candidates and evaluates a fixed number of them. The search is biased — it is seeded
from a flat reference layer — so the curve is a performance characteristic of this scheme rather
than an unbiased global-optimisation benchmark, and the quantities are specific to Fe/MgO.

## S2 Electronic-structure origin of the flat → island transition

Section 3.1 attributes the island ground state to the loss of forced interfacial coupling. Here
we test that reading directly, by comparing the **flat reference monolayer** (ΔZ = 0.000 Å) with
the **island ground state** (ΔZ = 3.652 Å) of the Fe/MgO model in the *same* projection set, so
the two are directly comparable (GPAW LCAO/dzp, PBE, kpts (12, 12, 1), 2000 points,
width 0.15 eV, Fermi-shifted). Projections are per atom: Fe-dz² (l = 2, m = 2) and O-pz
(l = 1, m = 0). d-band moments are taken over [−5, +3] eV around E_F. All numbers in this section
are those of Table S1 and Table S2.

**Figure S2.** Total DOS, Fe-dz² and O-pz for the flat monolayer (blue) and the island ground
state (red).

**Table S1.** Density-of-states metrics for the two configurations. *[SI-1, SI-2]*

| Quantity | Flat | Island | Δ (island − flat) |
|---|---|---|---|
| d-band centre (eV) | −0.2294 | +0.6013 | **+0.83 (up)** |
| d-band width (eV) | 1.4171 | 1.3139 | −0.10 (narrower) |
| Fe-dz2 integral | 31.7136 | 33.8763 | +2.16 (more filled) |
| O-pz integral | 43.8799 | 42.3738 | −1.51 (−3.4 %) |
| Spin polarisation | 5.8050 | 4.3695 | −1.44 (less magnetic) |
| DOS at E_F | 103.9621 | 78.0885 | **−25.9 (−25 %)** |

**Islanding reduces Fe–O hybridisation.** *[SI-1]* Going flat → island, the Fe d-band centre rises
by **+0.83 eV** while the O-pz integral falls by 3.4 % and the Fe-dz2 manifold becomes slightly
narrower (−0.10 eV) and more filled (+2.16). The flat monolayer is therefore the more strongly
Fe–O hybridised of the two: it mixes more O-p character and its Fe d-states sit lower, whereas the
island's d-states shift up and localise. We note explicitly that **no bulk-Fe reference was
computed**, so this shift is not calibrated against bulk Fe and no "bulk-like" comparison is made;
the claim is the direction and magnitude of the change between the two configurations, nothing
more.

**Islanding weakens the magnetic and electronic activity at E_F.** *[SI-2]* The spin polarisation
falls from 5.81 to 4.37 and the DOS at the Fermi level drops by 25 % (104.0 → 78.1). The flat
monolayer is the electronically "hotter" configuration; the island is quieter.

**Defining the interface by geometry, not by height.** The island is a buckled cluster rather than
a stack of layers, so its interface cannot be defined by a height criterion: a z-based layer split
would cut through the cluster and misassign atoms as a function of its buckling. We therefore define
the interface **geometrically**: **interface Fe := Fe with a nearest O within 2.8 Å**, i.e. Fe
actually in contact with the oxide. By this criterion the flat monolayer is 25/25 interface atoms
and the island only 9/25.

**Figure S3.** Top view of the interface, showing the metal atoms registered directly above the
substrate oxygen on the MgO(001) lattice.

**Table S2.** Site-resolved d-band metrics and the Fe-on-O registry, by geometric group. The last
two columns are the mean **nearest**-O distance and the mean in-plane offset from the nearest
substrate atom (0 = directly atop); for groups that include non-contacting Fe these are not bond
lengths. *[SI-3, SI-4]*

| Structure | Group | n | d-centre (eV) | width (eV) | ∫ | ⟨nearest d_Fe–O⟩ (Å) | ⟨offset⟩ (Å) |
|---|---|---|---|---|---|---|---|
| Flat | interface (= all) | 25 | **−0.2294** | 1.4171 | 31.7136 | 2.3000 | 0.0000 |
| Island | interface (d_Fe–O < 2.8 Å) | 9 | **+0.5106** | 1.5165 | 12.2134 | 2.3311 | 0.3722 |
| Island | non-interface | 16 | +0.6524 | 1.1815 | 21.6629 | 4.3462 | 0.4726 |
| Island | all | 25 | +0.6013 | 1.3139 | 33.8763 | 3.6208 | 0.4365 |

**The island's true interface Fe are not flat-like.** *[SI-3]* Restricting the comparison to the
9 Fe atoms genuinely in O contact does not recover the flat signature: their d-band centre is
**+0.5106 eV**, against −0.2294 eV for the flat monolayer — a difference of 0.74 eV, larger than
the spread between the island's interface (+0.5106) and non-interface (+0.6524) groups. Two
features of the model matter here. First, the two groups sit at essentially the **same nearest-O
distance** (2.3311 Å island vs 2.3000 Å flat), and that distance is the one set when the reference
film is built — a 2.3 Å interfacial separation that relaxation preserves (§1.3) — rather than an
emergent quantity, so the electronic difference **cannot** be a per-bond-length effect. Second, the flat layer's registry is
perfect (offset 0.0000 Å) and uniform, whereas the island's 9 contacts are buckled (offset
0.3722 Å) and only a third of the film. The flat monolayer's strong Fe–O coupling is therefore a
**collective** property of all 25 metal atoms being registry-locked in one plane, not a property
of an individual Fe–O bond.

**The Fe-atop-O registry is a consistency check.** *[SI-4]* Every in-contact Fe sits directly atop
an oxygen — 25/25 in the flat monolayer and 9/9 in the island — and **none** atop Mg. This is the
registry determined experimentally for the first monolayer of Fe on MgO(001) by LEED I–V analysis
\cite{urano1988} and used in first-principles models of the Fe|MgO|Fe interface \cite{butler2001},
and it is also the registry the reference layer is built with — the construction places the
substrate oxygen directly above the metal sites — so the flat film's registry follows from the
construction as much as from the physics. It is reported here as a **consistency check, not as a
prediction of the search**. What the search does add is the island's behaviour: the Fe that remain
in contact keep O as their nearest in-plane neighbour (9/9) rather than switching to Mg, so the
island reduces the *number* of Fe–O contacts (25 → 9) without abandoning their character.

**Combined picture.** The flat monolayer maximises Fe–O coupling by locking every metal atom into
one registered plane, at the cost of the three-dimensional Fe–Fe coordination available to a
cluster; the island reverses that trade, retaining strong individual Fe–O bonds for the third of
its atoms that remain in contact while restoring metal cohesion for the rest. This is the
mechanism stated in §3.1 as **reduced forced interfacial coupling plus restored metal cohesion**.
It is explicitly **not** a lattice-strain effect: the in-plane mismatch of this interface is
carried by the substrate, which is held fixed, and the metal film sits at its own equilibrium
lattice constant (§1.1, §3.4).

**Caveats.** These are single-point electronic structures on surrogate-relaxed, non-converged
geometries (residual forces ~1–2 eV/Å), and a DOS carries no total energy — the energy ordering
between the two configurations comes from the search energies, not from these curves, and a
quantitative claim would require re-relaxed geometries. The d-band moments depend on the
[−5, +3] eV window, which is a convention. The analysis is of the Fe/MgO flat and island
structures, which is the host the whole supplementary study covers; no other film composition was
recomputed. All site-resolved numbers quoted here are those of Table S2.

## S3 Method-parameter sensitivity of the biased exploration

The search used here is a custom, biased scheme — GOFEE (a GPR surrogate with an LCB acquisition
function) seeded from a flat Fe reference layer, with a heterostructure-aware randomiser and a
rattle generator supplying the perturbation. Here we vary **three method parameters** on the same
Fe25Mg25O25 system and ask whether the method's conclusions survive the choice: is the island
still the ground state, how far does a single search reach, and is the flat/island basin picture
preserved. The baseline for every family is the plain Fe/MgO run (rattle 1.5/2.3, kappa = 2, no
dipole correction). Energies are per-seed best ΔE/N relative to the lowest energy found in any of
these runs, −436.909 eV.

**Only completed searches are used.** Several of the searches in this study were **stopped early**,
and they are excluded everywhere in this paper. A short search has had less time to descend, so its
per-seed best is systematically worse — every such search in this set is a severe outlier
(0.23–0.35 eV/atom, against ~0.03–0.09 for completed searches) — and because searches that stopped
early are not distributed evenly across the settings they would distort the comparison between
them. The same criterion is applied without exception throughout the analysis, and it is decided
from the **iteration count recorded for each search, not from how a search is labelled**: a
search that looks complete can have stopped early. The baseline quoted in Table S3 therefore
consists of **13 completed searches** — one further search of that family stopped early — which is
the replica count used in the main text.

**Table S3.** Method-parameter sensitivity; completed searches only (100 iterations). *[SI-5, SI-6,
SI-7]*

| Family | Setting | Searches | per-seed best (eV/atom) | Flat fraction | Diversity |
|---|---|---|---|---|---|
| rattle | baseline (1.5 / 2.3) | 13 | **0.03683 ± 0.02575** | 0.165 | 2.22 |
| rattle | reduced-0.5 (1.0 / 1.8) | 2 | **0.26073 ± 0.06804** | 0.023 | 3.74 |
| rattle | reduced-1.0 (0.5 / 1.3) | 4 | **0.25583 ± 0.13287** | 0.017 | 4.33 |
| kappa | kappa = 2 (baseline) | 13 | 0.03683 ± 0.02575 | 0.165 | 2.22 |
| kappa | kappa = 1 | 16 | 0.03947 ± 0.02371 | 0.182 | 2.36 |
| kappa | kappa = 3 | 10 | 0.03509 ± 0.02182 | 0.149 | 2.65 |
| kappa | kappa = 4 | 9 | 0.03209 ± 0.01872 | 0.132 | 2.68 |
| dipole | no dipole (baseline) | 13 | 0.03683 ± 0.02575 | 0.165 | 2.22 |
| dipole | dipole xy | 11 | 0.03770 ± 0.02436 | 0.158 | 2.67 |

**Figure S4.** Convergence, per-seed best, basin sampling and diversity for the rattle-strength
family (four panels).

**Figure S5.** The same four panels for the kappa family.

**Figure S6.** The same four panels for the dipole family.

**Reducing the rattle strength degrades the search by about 7×.** *[SI-7]* Cutting the two
perturbation amplitudes roughly in half raises the per-seed best
from **0.0368 to 0.2607 / 0.2558 eV/atom** — a factor of **7.1 and 7.0** — and the flat-basin
fraction collapses from **0.165 to 0.023 / 0.017**. Reducing the perturbation is therefore not a
cheaper equivalent of the baseline: the rattle is what makes the search escape the initial region
and reach the low-energy basin at all, and less of it leaves the search sampling almost exclusively
the island side. **The magnitude here is weakly determined** — these two arms retain only 2 and
4 completed searches — so the factor should be read as "about an order of magnitude", not as a
calibrated ratio. The direction is not in doubt: every arm
of the sweep is worse than the baseline, and the flat basin is under-sampled by an order of
magnitude in the flat fraction.

**The kappa parameter changes nothing measurable.** *[SI-5]* All four settings land within
**0.0321–0.0395 eV/atom** — a total span of 0.0074 eV/atom, far inside the standard deviations
(0.019–0.026) — so the method's conclusions are **robust to the acquisition parameter**, and in
particular **no value of kappa can be identified as better than another** from these runs. This
warrants stating explicitly, because a ranking of the settings is easy to produce accidentally: the
per-seed best varies strongly from search to search, so a family that happens to hold one
under-sampled search moves its mean enough to change the apparent order while the completed searches
are indistinguishable. There is a small,
monotone trend in the flat-basin fraction — 0.182, 0.165, 0.149 and 0.132 for kappa = 1, 2, 3 and 4
— i.e. more exploration relative to exploitation samples slightly less of the flat basin, but the
effect is within the same order as the seed-to-seed spread.

**The dipole correction does not change the outcome.** *[SI-6]* The per-seed best moves from
0.03683 ± 0.02575 to 0.03770 ± 0.02436 eV/atom, a difference of 0.0009 eV/atom — an order of
magnitude smaller than the standard deviation. **Caveat:** these are two *separate* searches, so the difference
mixes the correction with sampling noise. This is an outcome-level comparison only; isolating the
dipole energy shift would require recomputing the *same* structures with and without the
correction, which was not done.

**Caveats for the whole study.** Search counts are unequal (13 / 2 / 4 for rattle, 13 / 16 / 10 / 9
for kappa, 13 / 11 for dipole), and the exclusion of searches that stopped early is disclosed above.
The rattle sweep explores only *lower* rattle — there is no higher-rattle arm, so this is not a
maximum and the baseline should not be read as an optimum. "Diversity" (the mean pairwise
structural-fingerprint distance between sampled structures) is **inversely correlated with
convergence** — a better-converged population is more concentrated — so it is not interpreted as
exploration breadth. One run family also contains a small set of structures of a different
composition, written by the run's own bookkeeping; those are excluded from every number here, as is
any structure outside the target composition.


## S4 The result does not depend on the search budget

The main text reports the Fe/MgO model at a **100-iteration budget**. To test whether the
*comparison* the paper makes — the island being
the ground state and the flat basin sitting above it — survives a longer search, the **same
calculation** was run to 200, 400 and 600 iterations: the run script is identical to the main-text
one except for the number of iterations, and the reference layer, the two perturbation generators and
the acquisition parameter are unchanged. 6, 7 and 4 searches completed at 200, 400 and 600 iterations
respectively.

**Method.** The primary evidence is a **per-run truncation**: each search is cut at a budget *k*
(100, then its own full budget) and the flat/island quantities recomputed, so the 100-iteration and
full-budget numbers come from the *same trajectory* and need no cross-run normalisation. The
flat/island split is ΔZ ≤ 1.0 Å and only iterations ≥ 10 are used, as in the main text. Each arm is
tested against its own budget, and searches that stopped early are excluded.

**Table S4.** Flat-basin minimum ΔE/N (eV/atom), pooled per arm at each budget (the main-text
definition: relative to the arm's own global minimum). The main-text model is the 100-iteration
reference.

| Budget | completed searches | k = 100 | k = 200 | k = 400 | k = 600 |
|---|---|---|---|---|---|
| 200 iterations | 6 | 0.1901 | 0.1901 | — | — |
| 400 iterations | 7 | 0.1624 | 0.1645 | 0.1662 | — |
| 600 iterations | 4 | 0.1807 | 0.1932 | 0.1966 | 0.1978 |
| main text (13 searches, 100 it) | 13 | **0.1888** | | | |

**Figure S7.** (a) the absolute ground-state energy of each search against the budget, showing that
the search is still improving in absolute terms; (b) the flat–island separation of each search
against the budget, showing that it does not shrink; (c) the per-search change in the flat-basin
minimum from 100 iterations to the full budget.

**The island remains the ground state at every budget.** In all 17 searches the lowest-energy
structure is an island at both the 100-iteration cut and the full budget. *(MT-1)*

**The flat–island separation does not shrink with a longer search.** Per run, the separation is
unchanged in 5 of the 17 searches and larger in the other 12 — it never decreases — by a median of
**+0.0104 eV/atom** (range 0 to **+0.0268**). Pooled per arm it rises from 0.1901 to 0.1901 (200
iterations), 0.1624 to 0.1662 (400) and 0.1807 to 0.1978 eV/atom (600). A longer search therefore
does not bring the flat basin closer to the ground state; if anything it leaves it relatively higher.
*(SI-9)*

**The absolute minimum is not converged at 100 iterations.** 12 of the 17 searches find a lower
island with more budget, by a median of **0.0013 eV/atom** (range 0 to 0.0071). It is the
*comparison* that is budget-insensitive, not the absolute energy — which is why the main text reports
separations at a stated budget rather than converged absolute values.

**The flat basin is a smaller fraction of the sampled set at longer budgets** (0.165 at 100
iterations falling to 0.05–0.11 at 600). This is descriptive: longer searches keep finding better
islands, so the flat basin occupies a smaller share of the sampled structures. As everywhere in this
paper, the fraction is a sampling weight of a biased exploration, not a population.

**Cross-check.** The 13 main-text searches, read through this analysis, reproduce the pooled
flat-basin minimum **0.1888 eV/atom** exactly, so the two analyses agree on the reference value.

**Scope bound.** All runs here are the boron-free Fe/MgO model, so this study bounds the structural
result (MT-1, MT-2) and the flat–island separation. The boron effect (MT-3) was not re-run at a
longer budget, and no such data exist.

## S5 The result does not depend on which phase sets the in-plane lattice

The main-text model takes the **Fe lattice constant** for the simulation cell, so the substrate
carries the in-plane mismatch (compressed 3.6 % against its bulk value) and the film is unstrained —
the inverse of the experimental stack, where bulk MgO imposes its lattice on a thin film. To test
whether the structural result depends on this choice, the cell is swept from Fe-matched to
MgO-matched, *a* = *a*_Fe + *f*·(*a*_MgO/√2 − *a*_Fe), with both the film and the substrate built on
that cell. At *f* = 0.25 the substrate is compressed
2.83 % and the film stretched 0.98 %; at *f* = 0.75, −0.94 % and +2.94 %; at *f* = 1.00 the substrate
sits at the **experimental MgO lattice constant** (4.212 Å as used) and the film is stretched
3.92 % — the convention of the experimental stack. 10, 10 and 5 searches completed at *f* = 0.25,
0.75 and 1.00. The paper's own Fe/MgO model (13 searches, cell = a_Fe) is the Fe-matched reference.

**Table S5.** The constraint, the strains it puts on each phase, and the flat-basin minimum
(pooled, relative to each arm's own global minimum).

| *f* | cell a (Å) | substrate strain | film strain | searches | flat-basin min ΔE/N (eV/atom) | island ground state |
|---|---|---|---|---|---|---|
| 0 (main text) | 2.87019 | −3.63 % | 0.00 % | 13 | **0.1888** | yes |
| 0.25 | 2.89408 | −2.83 % | +0.98 % | 10 | 0.1932 | yes |
| 0.75 | 2.95025 | −0.94 % | +2.94 % | 10 | 0.1982 | yes |
| 1.00 | 2.97833 | 0.00 % | +3.92 % | 5 | 0.1907 | yes |

**Figure S8.** (a) the flat-basin minimum against the constraint, pooled per arm with the individual
searches overlaid; (b) the ΔZ distributions of each arm; (c) the search-to-search spread within each
arm.

**The island is the ground state under every constraint.** In all 25 searches, at every value of
*f*, the lowest-energy structure is an island. *(MT-1)*

**The flat-basin minimum is flat against the constraint.** Pooled, it is 0.1932 (*f* = 0.25), 0.1982
(*f* = 0.75) and 0.1907 eV/atom (*f* = 1.00), against 0.1888 eV/atom for the Fe-matched main-text
model — a total spread of **0.0094 eV/atom** across the whole sweep. The search-to-search scatter
within an arm is 0.017–0.031 eV/atom, i.e. 2–3× the entire sweep effect, so no dependence on the
constraint is resolvable. For scale, the constraint moves the separation by about a quarter of the
boron effect (0.040 eV/atom). *(SI-10)*

**The physically inverted strain case is therefore calculated for this model.** The far end of the
sweep places the substrate at the experimental MgO lattice constant and stretches the film — the
convention of the experimental stack — and the result is unchanged. What is *not* covered is the
boron-containing model, and the substrate is a single layer, so it is the constraint that is
inverted, not the full experimental geometry.

**Caveats.** All runs are the boron-free Fe/MgO model, so this bounds the structural result (MT-1,
MT-2) and the strain-convention limitation, not the boron effect (MT-3). The *f* = 0 and *f* = 0.5
arms of the sweep are outside the paper's scope, and the sweep's Fe lattice constant (2.866 Å)
differs from the main text's (2.87019 Å) by 0.15 %, so the Fe-matched reference is the paper's own
model rather than a sweep arm. Absolute energies are not comparable across arms (the cells differ);
only the separation within an arm is meaningful.

