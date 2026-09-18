# Supplementary Material
     **FULL-DRAFT RE-REVIEW OPENED 2026-09-18.** At the scientist's request the whole draft is
     re-opened for review — Methods, Results, Discussion, Introduction, Conclusion and Abstract
     together — ahead of adding the origin of the Volmer-Weber islanding to the Discussion.
     This entry records a review state, not an edit: no text, number, claim, table or figure
     changed and no draft version is bumped. **Every earlier approval recorded below is VOID
     for the duration of this review; each section needs re-approval.**
     v13 (2026-09-18): claim tags removed from the section text — the inline [SI-1]…[SI-7] and
     (SI-9)/(SI-10)/(SI-11)/(MT-1) markers and the *[SI-x]* tags in the table captions. They are
     internal traceability to CLAIMS.md and should not reach the reader. No number, claim, table or
     figure changed. **APPROVAL VOIDED** (v10 was approved 2026-09-18); re-approval pending.
     v12 (2026-09-18): abbreviation pass requested by the scientist — GPAW/LCAO/PBE (§S2), DOS
     (Fig. S2 caption), LEED (§S2) and GOFEE/GPR/LCB (§S3) now carry their long name at first use in
     this document. No number, claim, table or figure changed. **APPROVAL VOIDED** (v10 was approved
     2026-09-18); re-approval pending.
     v11 (2026-09-18): editorial pass requested by the scientist — the bold-lead paragraphs are now
     sub-sub headings and all mid-paragraph bold emphasis is removed (same treatment as the main
     text). No number, claim, table or figure changed. **APPROVAL VOIDED** by this edit (v10 was
     approved 2026-09-18); re-approval pending.
     v10 (2026-09-18): all caveats removed from the section text at the scientist's instruction
     ("for now, remove all the caveats ... I will later review"), preserved in CLAIMS.md paired
     caveats and Limitations and in paper_status.md. Removed from §S1–§S6: the "Caveats." blocks
     (S1, S2, S3, S5, S6), the no-bulk-Fe note (S2), the weakly-determined-magnitude and
     accidental-ranking notes (S3), the unequal-counts/diversity/different-composition block (S3),
     the not-converged-absolute-minimum and not-a-population notes and the Scope bound (S4), the
     not-covered-boron / single-layer and the strain-convention caveats (S5), and the SI-11
     "indicative rather than settled" caveat (S6). No number or claim changed. **APPROVED
     2026-09-18.**
     v9 (2026-09-18): the SI-6 caveat in §S3 (dipole) is removed at the scientist's decision, after
     verification that the dipole and baseline runs share the same system and the same randomization
     seed (see paper_status.md → OPEN). The runs are seed-matched: the earliest structures are
     identical (matched dipole shift ~0.0013 eV/atom, consistent with the reported 0.0009), but the
     correction changes the energies that train the surrogate, so the two searches diverge into
     different structures after the first ~10 iterations; the comparison is therefore outcome-level.
     The caveat's "two separate searches" framing was dropped per the scientist; the recorded finding
     remains available if a reviewer pushes on it. No number or claim changed. Awaiting review.
     v8 (2026-09-17): §S6 (the inverted stack, MgO on Fe) added as a QUALIFIED finding (SI-11,
     CLAIMS v11) — a ground-state comparison: the inverted stack's ground state is a flat MgO film,
     the opposite of Fe-on-MgO, but the searches do not converge at the 100-iteration budget, so the
     comparison is indicative rather than settled. New floats: Table S6 + Figure S9 (§S6). Awaiting
     review.

     v7 (2026-09-17): §S4 (iteration budget, SI-9) and §S5 (lattice constraint, SI-10) added —
     two new boron-free Fe/MgO robustness studies (CLAIMS v10). New floats: Table S4 + Figure S7
     (§S4), Table S5 + Figure S8 (§S5).

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

<!-- DRAFT v13 · supplementary document (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v11 (scope: Fe/MgO + Fe-B/MgO). Planned structure:
       S1  Performance of the biased exploration in finding the global minimum  [drafted here]
       S2  PDOS — origin of island formation (flat vs island)   [drafted here]
       S3  Method-parameter sensitivity (rattle / kappa / dipole) [drafted here]
       S4  Iteration budget — does the comparison survive a longer search?  [drafted here, v10]
       S5  Lattice constraint — which phase sets the in-plane lattice?  [drafted here, v10]
       S6  The inverted stack (MgO on Fe) — ground-state comparison, QUALIFIED  [drafted here, v11]
     SI figures are flagged [SI]; SI claims are prefixed [SI] in paper_status.md.
     S1's claim is CLAIMS SI-8 (v4; signed off 2026-09-17).
     S2 drafted 2026-09-17 (CARRIES the v6 reframing: the island's gain is reduced forced
     interfacial coupling plus restored metal cohesion — NOT lattice-strain relief; the
     Fe-atop-O registry is inherited from the reference construction and is a consistency
     check, not a search prediction). Claims SI-1 … SI-4.
     S3 drafted 2026-09-17. Claims SI-5 (kappa), SI-6 (dipole), SI-7 (rattle).
     S4 drafted 2026-09-17 (v10). Claim SI-9 (iteration budget). Fe/MgO, boron-free.
     S5 drafted 2026-09-17 (v10). Claim SI-10 (lattice constraint). Fe/MgO, boron-free.
     S6 drafted 2026-09-17 (v11). Claim SI-11 — QUALIFIED/weak, a ground-state comparison: the
     inverted stack (MgO film on Fe substrate) has a flat MgO film as its ground state, the opposite
     of Fe-on-MgO whose ground state is an island, but the searches do not converge at the
     100-iteration budget. Boron-free.
     Only completed searches (100 iterations) are used, everywhere in this paper. See CLAIMS v8:
     unfinished runs biased the original comparison, and "kappa = 1 is best" was retracted as an
     artefact of one such run sitting in the baseline. -->

## S1 Performance of the biased exploration in finding the global minimum

The main text uses only structures from iteration ≥ 10, because relaxation of candidates begins
at that iteration. Here we instead use all iterations of the Fe/MgO model — the model with
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

### The onset of relaxation is the pivot of the search

Across iterations 1–9 the best-known
energy falls only from 0.494 to 0.435 eV/atom — 0.06 eV/atom, about 12 % of the total descent of
the run. At iteration 10, the first iteration at which candidates are surrogate-relaxed, it
drops from 0.435 to 0.250 eV/atom in a single iteration: approximately half of the entire
descent of the run (49 %) occurs at the onset of relaxation. The per-search drop across the
onset has a median of 0.165 eV/atom and a range of 0.084–0.233 eV/atom, so the step is a
property of every search rather than of one.

### Before the onset the candidates cannot be ranked

The structures evaluated in iterations 1–9
are unrelaxed placements, so their energy ordering reflects the starting geometry rather than any
relaxed configuration: several searches plateau after the second or third iteration and show no
further improvement for the remainder of the pre-relaxation phase. This is why the main-text
analysis discards them, and why their exclusion is not a loss of evidence.

### After the onset the descent proceeds in a long, progressively finer sequence

The best-known
energy reaches 0.219 (i = 20), 0.078 (i = 30) and 0.030 eV/atom (i = 50) — 84 % of the total
descent complete by iteration 30 and 94 % by iteration 50 — with successive crossings of
0.20 eV/atom at i = 23, 0.10 at i = 29, 0.05 at i = 46, 0.02 at i = 57 and 0.005 at i = 72. The
global minimum is first reached at iteration 77 by one of the searches, and the searches are
still making small improvements when the run ends at iteration 100.

### The searches do not agree on the answer

Only 10 of the 13 searches end within 0.05 eV/atom of
the global minimum, and only 4 within 0.02; the median search finishes 0.040 eV/atom above it
(per-search final values 0.000–0.086 eV/atom). A single search supplies the global minimum and a
second comes within 0.001 eV/atom of it. The final energy reached by a search therefore carries a
sizeable spread, which is why the main text compares basins across searches rather than quoting
one structure per model.

## S2 Electronic-structure origin of the flat → island transition

Section 3.1 attributes the island ground state to the loss of forced interfacial coupling. Here
we test that reading directly, by comparing the flat reference monolayer (ΔZ = 0.000 Å) with
the island ground state (ΔZ = 3.652 Å) of the Fe/MgO model in the *same* projection set, so
the two are directly comparable (GPAW, linear combination of atomic orbitals (LCAO) with a
double-zeta polarised basis, the Perdew–Burke–Ernzerhof (PBE) functional, kpts (12, 12, 1), 2000 points,
width 0.15 eV, Fermi-shifted). Projections are per atom: Fe-dz² (l = 2, m = 2) and O-pz
(l = 1, m = 0). d-band moments are taken over [−5, +3] eV around E_F. All numbers in this section
are those of Table S1 and Table S2.

**Figure S2.** Total density of states (DOS), Fe-dz² and O-pz for the flat monolayer (blue) and the island ground
state (red).

**Table S1.** Density-of-states metrics for the two configurations.

| Quantity | Flat | Island | Δ (island − flat) |
|---|---|---|---|
| d-band centre (eV) | −0.2294 | +0.6013 | **+0.83 (up)** |
| d-band width (eV) | 1.4171 | 1.3139 | −0.10 (narrower) |
| Fe-dz2 integral | 31.7136 | 33.8763 | +2.16 (more filled) |
| O-pz integral | 43.8799 | 42.3738 | −1.51 (−3.4 %) |
| Spin polarisation | 5.8050 | 4.3695 | −1.44 (less magnetic) |
| DOS at E_F | 103.9621 | 78.0885 | **−25.9 (−25 %)** |

### Islanding reduces Fe–O hybridisation

Going flat → island, the Fe d-band centre rises
by +0.83 eV while the O-pz integral falls by 3.4 % and the Fe-dz2 manifold becomes slightly
narrower (−0.10 eV) and more filled (+2.16). The flat monolayer is therefore the more strongly
Fe–O hybridised of the two: it mixes more O-p character and its Fe d-states sit lower, whereas the
island's d-states shift up and localise.

### Islanding weakens the magnetic and electronic activity at E_F

The spin polarisation
falls from 5.81 to 4.37 and the DOS at the Fermi level drops by 25 % (104.0 → 78.1). The flat
monolayer is the electronically "hotter" configuration; the island is quieter.

### Defining the interface by geometry, not by height

The island is a buckled cluster rather than
a stack of layers, so its interface cannot be defined by a height criterion: a z-based layer split
would cut through the cluster and misassign atoms as a function of its buckling. We therefore define
the interface geometrically: interface Fe := Fe with a nearest O within 2.8 Å, i.e. Fe
actually in contact with the oxide. By this criterion the flat monolayer is 25/25 interface atoms
and the island only 9/25.

**Figure S3.** Top view of the interface, showing the metal atoms registered directly above the
substrate oxygen on the MgO(001) lattice.

**Table S2.** Site-resolved d-band metrics and the Fe-on-O registry, by geometric group. The last
two columns are the mean nearest-O distance and the mean in-plane offset from the nearest
substrate atom (0 = directly atop); for groups that include non-contacting Fe these are not bond
lengths.

| Structure | Group | n | d-centre (eV) | width (eV) | ∫ | ⟨nearest d_Fe–O⟩ (Å) | ⟨offset⟩ (Å) |
|---|---|---|---|---|---|---|---|
| Flat | interface (= all) | 25 | **−0.2294** | 1.4171 | 31.7136 | 2.3000 | 0.0000 |
| Island | interface (d_Fe–O < 2.8 Å) | 9 | **+0.5106** | 1.5165 | 12.2134 | 2.3311 | 0.3722 |
| Island | non-interface | 16 | +0.6524 | 1.1815 | 21.6629 | 4.3462 | 0.4726 |
| Island | all | 25 | +0.6013 | 1.3139 | 33.8763 | 3.6208 | 0.4365 |

### The island's true interface Fe are not flat-like

Restricting the comparison to the
9 Fe atoms genuinely in O contact does not recover the flat signature: their d-band centre is
+0.5106 eV, against −0.2294 eV for the flat monolayer — a difference of 0.74 eV, larger than
the spread between the island's interface (+0.5106) and non-interface (+0.6524) groups. Two
features of the model matter here. First, the two groups sit at essentially the same nearest-O
distance (2.3311 Å island vs 2.3000 Å flat), and that distance is the one set when the reference
film is built — a 2.3 Å interfacial separation that relaxation preserves (§1.3) — rather than an
emergent quantity, so the electronic difference cannot be a per-bond-length effect. Second, the flat layer's registry is
perfect (offset 0.0000 Å) and uniform, whereas the island's 9 contacts are buckled (offset
0.3722 Å) and only a third of the film. The flat monolayer's strong Fe–O coupling is therefore a
collective property of all 25 metal atoms being registry-locked in one plane, not a property
of an individual Fe–O bond.

### The Fe-atop-O registry is a consistency check

Every in-contact Fe sits directly atop
an oxygen — 25/25 in the flat monolayer and 9/9 in the island — and none atop Mg. This is the
registry determined experimentally for the first monolayer of Fe on MgO(001) by low-energy
electron diffraction (LEED) I–V analysis
\cite{urano1988} and used in first-principles models of the Fe|MgO|Fe interface \cite{butler2001},
and it is also the registry the reference layer is built with — the construction places the
substrate oxygen directly above the metal sites — so the flat film's registry follows from the
construction as much as from the physics. It is reported here as a consistency check, not as a
prediction of the search. What the search does add is the island's behaviour: the Fe that remain
in contact keep O as their nearest in-plane neighbour (9/9) rather than switching to Mg, so the
island reduces the *number* of Fe–O contacts (25 → 9) without abandoning their character.

### Combined picture

The flat monolayer maximises Fe–O coupling by locking every metal atom into
one registered plane, at the cost of the three-dimensional Fe–Fe coordination available to a
cluster; the island reverses that trade, retaining strong individual Fe–O bonds for the third of
its atoms that remain in contact while restoring metal cohesion for the rest. This is the
mechanism stated in §3.1 as reduced forced interfacial coupling plus restored metal cohesion.
It is explicitly not a lattice-strain effect: the in-plane mismatch of this interface is
carried by the substrate, which is held fixed, and the metal film sits at its own equilibrium
lattice constant (§1.1, §3.4).

## S3 Method-parameter sensitivity of the biased exploration

The search used here is a custom, biased scheme — global optimisation with first-principles energy
expressions (GOFEE), a Gaussian-process regression (GPR) surrogate with a lower confidence bound
(LCB) acquisition function, seeded from a flat Fe reference layer, with a heterostructure-aware
randomiser and a rattle generator supplying the perturbation. Here we vary three method parameters on the same
Fe25Mg25O25 system and ask whether the method's conclusions survive the choice: is the island
still the ground state, how far does a single search reach, and is the flat/island basin picture
preserved. The baseline for every family is the plain Fe/MgO run (rattle 1.5/2.3, kappa = 2, no
dipole correction). Energies are per-seed best ΔE/N relative to the lowest energy found in any of
these runs, −436.909 eV.

### Only completed searches are used

Several of the searches in this study were stopped early,
and they are excluded everywhere in this paper. A short search has had less time to descend, so its
per-seed best is systematically worse — every such search in this set is a severe outlier
(0.23–0.35 eV/atom, against ~0.03–0.09 for completed searches) — and because searches that stopped
early are not distributed evenly across the settings they would distort the comparison between
them. The same criterion is applied without exception throughout the analysis, and it is decided
from the iteration count recorded for each search, not from how a search is labelled: a
search that looks complete can have stopped early. The baseline quoted in Table S3 therefore
consists of 13 completed searches — one further search of that family stopped early — which is
the replica count used in the main text.

**Table S3.** Method-parameter sensitivity; completed searches only (100 iterations).

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

### Reducing the rattle strength degrades the search by about 7×

Cutting the two
perturbation amplitudes roughly in half raises the per-seed best
from 0.0368 to 0.2607 / 0.2558 eV/atom — a factor of 7.1 and 7.0 — and the flat-basin
fraction collapses from 0.165 to 0.023 / 0.017. Reducing the perturbation is therefore not a
cheaper equivalent of the baseline: the rattle is what makes the search escape the initial region
and reach the low-energy basin at all, and less of it leaves the search sampling almost exclusively
the island side. The direction is not in doubt: every arm
of the sweep is worse than the baseline, and the flat basin is under-sampled by an order of
magnitude in the flat fraction.

### The kappa parameter changes nothing measurable

All four settings land within
0.0321–0.0395 eV/atom — a total span of 0.0074 eV/atom, far inside the standard deviations
(0.019–0.026) — so the method's conclusions are robust to the acquisition parameter, and in
in particular no value of kappa can be identified as better than another from these runs. There is a small,
monotone trend in the flat-basin fraction — 0.182, 0.165, 0.149 and 0.132 for kappa = 1, 2, 3 and 4
— i.e. more exploration relative to exploitation samples slightly less of the flat basin, but the
effect is within the same order as the seed-to-seed spread.

### The dipole correction does not change the outcome

The per-seed best moves from
0.03683 ± 0.02575 to 0.03770 ± 0.02436 eV/atom, a difference of 0.0009 eV/atom — an order of
magnitude smaller than the standard deviation.

## S4 The result does not depend on the search budget

The main text reports the Fe/MgO model at a 100-iteration budget. To test whether the
*comparison* the paper makes — the island being
the ground state and the flat basin sitting above it — survives a longer search, the same
calculation was run to 200, 400 and 600 iterations: the run script is identical to the main-text
one except for the number of iterations, and the reference layer, the two perturbation generators and
the acquisition parameter are unchanged. 6, 7 and 4 searches completed at 200, 400 and 600 iterations
respectively.

### Method

The primary evidence is a per-run truncation: each search is cut at a budget *k*
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

### The island remains the ground state at every budget

In all 17 searches the lowest-energy
structure is an island at both the 100-iteration cut and the full budget.

### The flat–island separation does not shrink with a longer search

Per run, the separation is
unchanged in 5 of the 17 searches and larger in the other 12 — it never decreases — by a median of
+0.0104 eV/atom (range 0 to +0.0268). Pooled per arm it rises from 0.1901 to 0.1901 (200
iterations), 0.1624 to 0.1662 (400) and 0.1807 to 0.1978 eV/atom (600). A longer search therefore
does not bring the flat basin closer to the ground state; if anything it leaves it relatively higher.


The flat basin is a smaller fraction of the sampled set at longer budgets (0.165 at 100
iterations falling to 0.05–0.11 at 600). Longer searches keep finding better islands, so the flat
basin occupies a smaller share of the sampled structures.

### Cross-check

The 13 main-text searches, read through this analysis, reproduce the pooled
flat-basin minimum 0.1888 eV/atom exactly, so the two analyses agree on the reference value.

## S5 The result does not depend on which phase sets the in-plane lattice

The main-text model takes the Fe lattice constant for the simulation cell, so the substrate
carries the in-plane mismatch (compressed 3.6 % against its bulk value) and the film is unstrained —
the inverse of the experimental stack, where bulk MgO imposes its lattice on a thin film. To test
whether the structural result depends on this choice, the cell is swept from Fe-matched to
MgO-matched, *a* = *a*_Fe + *f*·(*a*_MgO/√2 − *a*_Fe), with both the film and the substrate built on
that cell. The two endpoints are the experimental lattice constants of the two bulk phases: bcc
α-Fe, *a* = 2.866 Å \cite{pietrokowsky1966}, and rocksalt MgO, *a* = 4.2112 Å \cite{swanson1953}
(4.212 Å as used in the inputs). At *f* = 0.25 the substrate is compressed
2.83 % and the film stretched 0.98 %; at *f* = 0.75, −0.94 % and +2.94 %; at *f* = 1.00 the substrate
sits at the experimental MgO lattice constant and the film is stretched
3.92 % — the convention of the experimental stack. 10, 10 and 5 searches completed at *f* = 0.25,
0.75 and 1.00. The paper's own Fe/MgO model (13 searches, cell = a_Fe) is the Fe-matched reference;
it uses the *computed* Fe lattice constant (2.87019 Å) rather than the experimental 2.866 Å, so the
sweep's f = 0 endpoint is a reference, not identical to the main-text model.

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

### The island is the ground state under every constraint

In all 25 searches, at every value of
*f*, the lowest-energy structure is an island.

### The flat-basin minimum is flat against the constraint

Pooled, it is 0.1932 (*f* = 0.25), 0.1982
(*f* = 0.75) and 0.1907 eV/atom (*f* = 1.00), against 0.1888 eV/atom for the Fe-matched main-text
model — a total spread of 0.0094 eV/atom across the whole sweep. The search-to-search scatter
within an arm is 0.017–0.031 eV/atom, i.e. 2–3× the entire sweep effect, so no dependence on the
constraint is resolvable. For scale, the constraint moves the separation by about a quarter of the
boron effect (0.040 eV/atom).

### The physically inverted strain case is therefore calculated for this model

The far end of the
sweep places the substrate at the experimental MgO lattice constant and stretches the film — the
convention of the experimental stack — and the result is unchanged.

## S6 The inverted stack: a ground-state comparison (an MgO film on an Fe substrate)

The main text studies Fe deposited on MgO, and its ground state is an island. Here we ask whether the
wetting of the deposited layer is symmetric — whether a film behaves the same way when it is the
oxide that is deposited. The comparison is made at the ground state of each stack: an MgO film
on an Fe substrate, against the Fe-on-MgO result of the main text. The inverted stack uses the same
system and scheme (Fe25Mg25O25, 100 iterations, κ = 2, the same two perturbation generators, cell at
the experimental Fe lattice constant, 2.866 Å).

### Method

The flatness is measured over the deposited film in each stack — Fe for Fe-on-MgO,
MgO (Mg + O) for MgO-on-Fe — so the comparison is apples-to-apples on wetting. (ΔZ over Fe in the
inverted stack would measure the substrate, which is flat by construction.) The ground state is the
lowest-energy structure of a stack, and the flat/island split is ΔZ ≤ 1.0 Å of the deposited film.
Only iterations ≥ 10 are used, and only completed searches enter the comparison.

**Table S6.** The two stacks at their ground states.

| Stack | Ground state | ΔZ of the deposited film | Flat film relative to the island |
|---|---|---|---|
| Fe on MgO (main text) | island | 3.65 Å | **+0.189 eV/atom** above |
| **MgO on Fe (inverted)** | **flat film** | **0.39 Å** | **−0.016 eV/atom** below |

**Figure S9.** (a) ΔZ of the deposited film at the ground state of each stack, against the 1.0 Å
flat/island threshold; (b) where the flat film lies relative to the island for each stack — positive
means the island is the ground state, negative means the flat film is.

### The ground state of the inverted stack is a flat MgO film — the opposite of Fe-on-MgO

On the
inverted stack the lowest structure found is a flat MgO film (ΔZ = 0.39 Å), and the flat film is
0.016 eV/atom below the corresponding island. For Fe-on-MgO the ordering is the reverse: the
island is the ground state (ΔZ = 3.65 Å), and the flat film sits 0.189 eV/atom above it. The
sign of the wetting preference therefore inverts between the two stacks — the layer that is deposited
keeps its flat, wetting configuration when it is the oxide, and breaks up into an island when it is
the metal.
