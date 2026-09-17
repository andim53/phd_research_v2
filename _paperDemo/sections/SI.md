# Supplementary Material
     v3 (2026-09-17): S2 (PDOS / island origin) and S3 (method-parameter sensitivity) added;
     S3 numbers purged to completed searches only. Awaiting review.

<!-- DRAFT v3 · supplementary document (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v8. Planned structure:
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

**Figure S1.** `figures/exploration_performance_femgo.png` — (a) best-so-far ΔE/N against
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
width 0.15 eV, Fermi-shifted). Projections are per atom: Fe `dz2` (l = 2, m = 2) and O `pz`
(l = 1, m = 0). d-band moments are taken over [−5, +3] eV around E_F. All numbers in this section
trace to `analysis/pdos_metrics.csv` and `analysis/interface_analysis.csv`.

**Figure S2.** `figures/pdos_flat_vs_island.png` — total DOS, Fe-dz2 and O-pz for the flat
monolayer (blue) and the island ground state (red).

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

**Defining the interface by geometry, not by height.** An early version of this analysis split the
Fe atoms into bottom-8 and top-8 by z. That split is arbitrary — the island is a buckled cluster,
not a stack of layers — and it is superseded here by a geometric criterion: **interface Fe := Fe
with a nearest O within 2.8 Å**, i.e. Fe actually in contact with the oxide. By this criterion the
flat monolayer is 25/25 interface atoms and the island only 9/25.

**Figure S3.** `figures/interface_registry_topview.png` — top view of the interface, showing the
metal atoms registered directly above the substrate oxygen on the MgO(001) lattice.

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
distance** (2.3311 Å island vs 2.3000 Å flat), and that distance is the construction parameter
`dist_fe2o = 2.3 Å` surviving relaxation (§1.3) rather than an emergent quantity — so the
electronic difference **cannot** be a per-bond-length effect. Second, the flat layer's registry is
perfect (offset 0.0000 Å) and uniform, whereas the island's 9 contacts are buckled (offset
0.3722 Å) and only a third of the film. The flat monolayer's strong Fe–O coupling is therefore a
**collective** property of all 25 metal atoms being registry-locked in one plane, not a property
of an individual Fe–O bond.

**The Fe-atop-O registry is a consistency check.** *[SI-4]* Every in-contact Fe sits directly atop
an oxygen — 25/25 in the flat monolayer and 9/9 in the island — and **none** atop Mg. This is the
registry determined experimentally for the first monolayer of Fe on MgO(001) by LEED I–V analysis
\cite{urano1988} and used in first-principles models of the Fe|MgO|Fe interface \cite{butler2001},
and it is also the registry the reference layer is built with: `build_mgo_stack` places the
substrate oxygen directly above the metal sites, so the flat film's registry follows from the
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
lattice constant (§1.1, §3.5).

**Caveats.** These are single-point electronic structures on surrogate-relaxed, non-converged
geometries (residual forces ~1–2 eV/Å), and a DOS carries no total energy — the energy ordering
between the two configurations comes from the search energies, not from these curves, and a
quantitative claim would require re-relaxed geometries. The d-band moments depend on the
[−5, +3] eV window, which is a convention. The analysis is for Fe/MgO only; the other three models
were not recomputed. `analysis/pdos_site_metrics.csv` and `figures/pdos_sites.png` come from the
superseded bottom-8/top-8 split and should not be used; Table S2 supersedes them.

## S3 Method-parameter sensitivity of the biased exploration

The search used here is a custom, biased scheme — GOFEE (a GPR surrogate with an LCB acquisition
function) seeded from a flat Fe reference layer, with `HeteroStructRandomize` and
`RattleGenerator` supplying the perturbation. Here we vary **three method parameters** on the same
Fe25Mg25O25 system and ask whether the method's conclusions survive the choice: is the island
still the ground state, how far does a single search reach, and is the flat/island basin picture
preserved. The baseline for every family is the plain Fe/MgO run (rattle 1.5/2.3, kappa = 2, no
dipole correction). Energies are per-seed best ΔE/N relative to the lowest energy found in any of
these runs, −436.909 eV.

**Only completed searches are used.** Several run directories in this study contain searches that
were **stopped early**, and they are excluded everywhere in this paper. A short search has had less
time to descend, so its per-seed best is systematically worse — every unfinished search in this set
is a severe outlier (0.23–0.35 eV/atom, against ~0.03–0.09 for completed searches) — and because
the unfinished runs are not distributed evenly across settings they would distort the comparison
between them. The rule is applied by a single shared function (`run_selection.py`) in every
analysis script, and it is determined from the **iteration number stored in each database rather
than from the directory name**, because a `seed_*` directory can stop early just as a `stop_*` one
can. The practical consequence here is that the rattle and kappa families lose their worst searches
and the baseline drops from 14 directories to **13 completed searches**, matching the replica count
used in the main text.

**Table S3.** Method-parameter sensitivity; completed searches only (100 iterations). All numbers
trace to `analysis/method_sensitivity.csv`. *[SI-5, SI-6, SI-7]*

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

**Figure S4.** `figures/method_sensitivity_rattle.png` — convergence, per-seed best, basin sampling
and diversity for the rattle-strength family (four panels).

**Figure S5.** `figures/method_sensitivity_kappa.png` — the same four panels for the kappa family.

**Figure S6.** `figures/method_sensitivity_dipole.png` — the same four panels for the dipole family.

**Reducing the rattle strength degrades the search by about 7×.** *[SI-7]* Cutting the
`HeteroStructRandomize` / `RattleGenerator` amplitudes roughly in half raises the per-seed best
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
particular **no value of kappa can be identified as better than another** from these runs. This is
worth stating explicitly, because an earlier reading of the same data singled out kappa = 1 as the
best setting; that ranking came from an unfinished search sitting in the baseline rather than from
any property of kappa = 1, and it does not survive the completed-search statistic. There is a small,
monotone trend in the flat-basin fraction — 0.182, 0.165, 0.149 and 0.132 for kappa = 1, 2, 3 and 4
— i.e. more exploration relative to exploitation samples slightly less of the flat basin, but the
effect is within the same order as the seed-to-seed spread.

**The dipole correction does not change the outcome.** *[SI-6]* The per-seed best moves from
0.03683 ± 0.02575 to 0.03770 ± 0.02436 eV/atom, a difference of 0.0009 eV/atom — an order of
magnitude smaller than the standard deviation. **Caveat:** these are two *separate* searches, so the difference
mixes the correction with sampling noise. This is an outcome-level comparison only; isolating the
dipole energy shift would require recomputing the *same* structures with and without the
correction, which was not done.

**Caveats for the whole study.** Seed counts are unequal (13 / 2 / 4 for rattle, 13 / 16 / 10 / 9
for kappa, 13 / 11 for dipole), and the truncated-search exclusion is disclosed above. The rattle
sweep explores only *lower* rattle — there is no higher-rattle arm, so this is not a maximum and
the baseline should not be read as an optimum. "Diversity" (the mean pairwise AGOX-Fingerprint
distance) is **inversely correlated with convergence** — a better-converged population is more
concentrated — so it is not interpreted as exploration breadth. The kappa directories contain a
scratch `trash/` database of 41 Fe9Mg9O9 structures, which the loader excludes by skipping `trash/`
and filtering to the target composition; the rattle and dipole directories are clean.
