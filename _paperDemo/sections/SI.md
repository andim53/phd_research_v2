# Supplementary Material

<!-- DRAFT v1 · supplementary document (markdown-first, pre-LaTeX)
     Grounded in CLAIMS.md v3. Planned structure:
       S1  Performance of the biased exploration in finding the global minimum  [drafted here]
       S2  PDOS — origin of island formation (flat vs island)   [documented in experiment_log.md]
       S3  Method-parameter sensitivity (rattle / kappa / dipole) [documented in experiment_log.md]
     SI figures are flagged [SI]; SI claims are prefixed [SI] in paper_status.md.
     NOTE: the claim in S1 is NEW and is not yet in CLAIMS.md — see the pending SI-8 entry. -->

## S1 Performance of the biased exploration in finding the global minimum

The main text uses only structures from iteration ≥ 10, because relaxation of candidates begins
at that iteration. Here we instead use **all** iterations of the Fe/MgO model, which is the
model with the largest number of independent searches (13), to quantify how the biased
exploration approaches the global minimum and to show what the discarded early iterations
contain. Energies are given as ΔE/N = (E − E_globalmin)/N relative to the lowest energy found
anywhere in the 13 searches, so the best-known energy descends to zero (Fig. S1).

**Figure S1.** `figures/exploration_performance_femgo.png` — (a) best-so-far ΔE/N against
iteration for each of the 13 searches, with the median over searches in black; (b) the lowest
energy found in each iteration (points) and the best-known energy across all searches (black
line), with the iterations at which it first crosses 0.20, 0.10, 0.05, 0.02 and 0.005 eV/atom
marked; (c) the fraction of searches whose own best-so-far has come within 0.05 and 0.02 eV/atom
of the global minimum. The vertical line in each panel marks iteration 10, where relaxation
begins.

**The pre-relaxation iterations barely descend.** Over iterations 1–9 the best-known energy falls
only from 0.494 to 0.435 eV/atom — about 12 % of the total descent of the run — and in most
searches it does not improve at all between iterations 2 and 9. The first nine iterations
therefore evaluate unrelaxed placements that are mutually indistinguishable at this level: the
search explores structures but cannot rank them, because none of them is at a local minimum.

**Relaxation onset is the single largest step in the run.** At iteration 10 the best-known
energy drops from 0.435 to 0.250 eV/atom in one iteration, i.e. **about half of the entire
descent (49 %) is achieved at the moment relaxation begins**. The per-search drop across the
onset has a median of 0.165 eV/atom and a range of 0.084–0.233 eV/atom. This is the expected
behaviour of the scheme — the generator proposes a configuration and the surrogate relaxes it —
but it also means that the physically meaningful comparison between basins only starts at
iteration 10, which is why the main-text analysis discards what comes before.

**After the onset the descent is front-loaded, but the minimum itself arrives late.** The
best-known energy continues to fall to 0.219 (i = 20), 0.078 (i = 30) and 0.030 eV/atom
(i = 50), i.e. 84 % of the total descent is complete by iteration 30 and 94 % by iteration 50.
The crossing times are: within 0.20 eV/atom by i = 23, within 0.10 by i = 29, within 0.05 by
i = 46, within 0.02 by i = 57 and within 0.005 by i = 72. **The global minimum itself is first
found at iteration 77**, by one of the 13 searches, and is not improved afterwards. The search
therefore locates the *low-energy region* early after relaxation begins, but the exact global
minimum only in the last third of the run.

**The searches disagree about the answer.** Only 10 of the 13 searches end within 0.05 eV/atom
of the global minimum, and only 4 within 0.02 eV/atom; the median search finishes 0.040 eV/atom
above it (per-search final values range from 0.000 to 0.086 eV/atom). A single search supplies
the global minimum and a second comes within 0.001 eV/atom of it. This heterogeneity is the
reason the main text compares basins across searches rather than quoting one structure per
model.

**Consequences and caveats.** Three points follow for the interpretation of the main text.
(i) The pre-relaxation iterations carry no ranking information and their exclusion is not a loss
of evidence. (ii) The searches are **still improving when the run ends** at iteration 100: the
best-known energy is falling to the last few iterations, so the reported per-model reference
energies are not converged with respect to search length, and every relative energy in the main
text carries this additional systematic uncertainty alongside the statistical uncertainty of
§2.2. Settling it would need longer runs, not more analyses. (iii) The energies are single GPAW
steps on surrogate-relaxed structures (residual forces ~1–2 eV/Å), so this measures the
behaviour of the *search*, not the convergence of any individual structure. The quantities are
also specific to Fe/MgO and to the biased scheme: iteration is an AGOX counter, not a
computational cost, and the search is seeded from a flat reference layer, so the curve is a
performance characteristic of this scheme rather than an unbiased global-optimisation benchmark.
