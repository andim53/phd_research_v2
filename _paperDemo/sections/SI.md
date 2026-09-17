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
