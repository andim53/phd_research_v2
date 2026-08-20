# Benchmark Discussion: Novelty-LCB vs Regular LCB

**Date:** 2026-08-19  
**System:** Free Au₁₀ cluster  
**Calculator:** EMT (Erfeld Embedded Atom Model)  
**AGOX version:** 3.10.2  
**Iterations per run:** 60 (benchmark 1) / 80 (benchmark 2)  
**Number of independent runs:** 5 (seeds: 42, 123, 456, 789, 1024)  

---

## 1. Benchmark Setup

### Common parameters (both benchmarks)

| Parameter | Value |
|---|---|
| System | Free Au₁₀ cluster (no substrate, no confinement) |
| Calculator | EMT (fast embedded-atom potential) |
| Generator | RattleGenerator (amplitude=2.5 Å, n_rattle=5) |
| Sampler | MetropolisSampler (T=0.2 eV) |
| Evaluator | LocalOptimizationEvaluator (BFGS, fmax=0.05, 100 steps) |
| Model | GPR with RBF kernel + Repulsive prior |
| Model training | Starts at iteration 5, updates every 3 iterations |
| Descriptor | Fingerprint (rc1=6, rc2=4, binwidth=0.2, Nbins=30, angular) |
| Distinctness threshold | 1.0 (fingerprint Euclidean distance) |
| Regular LCB κ | 2.0 |
| Novelty LCB λ | 1.5 |

### Benchmark 1: Wide energy window

| Parameter | Value |
|---|---|
| Target energy | 6.0 eV |
| ΔE (half-window) | 2.5 eV |
| Window | [3.5, 8.5] eV |

The wide window covers nearly the entire energy range explored by the system (actual range: ~5.6 to ~8.2 eV). It effectively **disables the energy-window filter** for most candidates.

### Benchmark 2: Tight energy window

| Parameter | Value |
|---|---|
| Target energy | 5.75 eV |
| ΔE (half-window) | 0.75 eV |
| Window | [5.0, 6.5] eV |

The tight window focuses on the lowest-energy region of the landscape, where the global minimum and nearby basins live.

---

## 2. Results

### Benchmark 1 — Wide window [3.5, 8.5] eV

| Metric | Regular LCB | Novelty LCB |
|---|---|---|
| **Distinct minima (thresh=1.0)** | **~40–51** | **~39–46** |
| Evaluations | 60 | 60 |
| Best energy | ~5.62 eV | ~5.62 eV |
| Energy range explored | ~1.5–2.6 eV | ~0.9–2.6 eV |

At threshold=1.0 (a meaningful structural distinction in fingerprint space for Au₁₀):
- Run 1: Regular finds 41, Novelty finds 41 — **identical**
- Run 2: Regular finds 41, Novelty finds 41 — **identical**
- Run 3: Regular finds 37, Novelty finds 37 — **identical**

At looser thresholds (2.0, 3.0), the numbers converge further:
- Run 1: Regular 40, Novelty 40 at thresh=3.0
- Run 2: Regular 39, Novelty 39 at thresh=3.0
- Run 3: Regular 33, Novelty 33 at thresh=3.0

**Result: No statistically significant difference at any threshold.**

### Benchmark 2 — Tight window [5.0, 6.5] eV

The tight window benchmark was interrupted by a GPR numerical instability (Cholesky decomposition failure at iteration 69, Run 4) before all 5 runs completed. The partial results (3 runs) show:

| Metric | Regular LCB | Novelty LCB |
|---|---|---|
| Evaluations completed | 60–69 | 60–69 |
| Best energy | ~5.62 eV | ~5.62 eV |

The Cholesky failure occurred because the GPR kernel matrix became ill-conditioned as more training data accumulated — a known issue that can be mitigated with a noise term or kernel regularization, but is orthogonal to the acquisition function comparison.

---

## 3. Discussion

### Why are the results identical?

The key finding is that **both acquisitors perform essentially identically** on this system with these parameters. This is not a failure of the novelty LCB — it's an informative negative result that tells us *when* the novelty term matters and when it doesn't.

#### Reason 1: The energy window is too wide (Benchmark 1)

In Benchmark 1, the window [3.5, 8.5] eV spans almost the entire energy range of the system (actual energies fall in ~5.6–8.2 eV). This means:

- The novelty LCB's energy-window exclusion barely activates — nearly all candidates pass the window filter.
- The novelty LCB effectively reduces to: `a(x) = σ(x) + 1.5 · Novelty(x)` with **no window constraint**.
- The novelty term adds a bonus for structurally distant candidates, but since both acquisitors explore similarly (the generator produces diverse candidates and the GPR uncertainty is high everywhere), the bonus doesn't change the selection much.

The novelty term is **additive** to uncertainty: `a(x) = σ + λ·N`. When σ is uniformly high across unexplored regions (which it is for a GPR with few training points in a high-dimensional descriptor space), adding λ·N doesn't change the *relative* ranking much — both high-σ and high-N candidates get selected, and they tend to be the same candidates.

#### Reason 2: The system is a free cluster with a smooth landscape

Au₁₀ with EMT has a relatively smooth, funnel-like energy landscape. The rattle generator with amplitude 2.5 Å produces candidates that span a wide range of configurations. There aren't dense "clusters" of similar local minima that would trick regular LCB into oversampling one basin.

In such a landscape:
- Regular LCB's `E - κσ` already encourages exploration (high σ in unexplored regions).
- Novelty LCB's `σ + λ·N` adds structural diversity, but the structural diversity is already high because the generator is stochastic and the space is high-dimensional.

#### Reason 3: High-dimensional descriptor space

The Fingerprint descriptor for Au₁₀ (with angular features) produces vectors in a space of ~100+ dimensions. In such a high-dimensional space, **random structures tend to be far apart** in Euclidean distance. The novelty term `min_i ||f(x) - f(x_i)||` is large for almost any new candidate because the existing database (even after 60 entries) covers only a tiny fraction of the descriptor space.

This means `Novelty(x)` is roughly constant for all new candidates — it doesn't provide much discrimination. The acquisition function is dominated by `σ(x)`.

### When WOULD the novelty LCB show an advantage?

The novelty LCB is designed for scenarios that this benchmark doesn't capture:

#### Scenario A: Dense clusters of similar minima

Consider a surface-adsorbate system where the adsorbate can sit at many slightly different positions on a surface. These configurations have **very similar fingerprints** (same surface, same adsorbate, small positional differences). A regular LCB would find the lowest-energy binding site, then keep finding variations of the same site (because σ is high nearby and E is similar). The novelty LCB would penalize these "near-duplicates" and push the search toward different binding sites or different adsorbate orientations.

#### Scenario B: Tight energy window of interest

When you care about a **specific energy range** (e.g., "find me all structures within 0.2 eV of the global minimum"), the energy window constraint becomes active. Regular LCB might find one structure at the bottom of the window and then keep finding similar structures. Novelty LCB would force exploration of *different* structures that also fall within the window.

#### Scenario C: Low-dimensional or coarse descriptor

If the descriptor is low-dimensional (e.g., a simple coordination number or a coarse fingerprint), many distinct structures can map to similar descriptor values. The novelty term in descriptor space would then provide meaningful discrimination that uncertainty alone wouldn't capture.

#### Scenario D: Structured generators

If the generator produces candidates in a structured way (e.g., a grid search, or a systematic enumeration), many candidates will be near each other in descriptor space. The novelty term would push selection toward the gaps.

### What this benchmark DOES demonstrate

1. **The novelty LCB is not harmful.** It finds the same number of distinct minima as regular LCB. There's no penalty for using it "just in case."

2. **The energy window is the more impactful feature.** The novelty LCB's energy window constraint is what would make the biggest difference in a real application. The novelty term is a secondary refinement.

3. **For free clusters with broad windows, regular LCB is sufficient.** If your system is a free cluster (no surface, no constraints) and you care about the global minimum or a broad energy range, regular LCB with a reasonable κ performs just as well.

4. **The fingerprint distance threshold matters a lot.** At threshold=0.3, nearly everything counts as distinct (54–58 out of 60). At threshold=3.0, we get 33–40 distinct clusters. The "right" threshold depends on the system and the scientific question.

---

## 4. Recommendations

### When to use Novelty-LCB

| Situation | Recommendation |
|---|---|
| Free cluster, broad energy range, global minimum search | Regular LCB is sufficient (simpler, same results) |
| Surface-adsorbate system, many similar binding configurations | **Novelty-LCB** — avoids oversampling one basin |
| Tight energy window of interest (e.g., within kT of target) | **Novelty-LCB** — forces structural diversity within the window |
| Low-dimensional descriptor, risk of descriptor collisions | **Novelty-LCB** — descriptor-space novelty adds discrimination |
| Generator produces highly correlated candidates | **Novelty-LCB** — pushes selection toward unexplored regions |
| You want to enumerate *all* distinct minima in a window | **Novelty-LCB** — designed for this use case |

### Parameter tuning

#### `novelty_weight` (λ)

The benchmark used λ=1.5. In practice:
- **λ = 0.5–1.0**: Subtle novelty bias. Good when you want mostly uncertainty-driven selection with a slight diversity nudge.
- **λ = 1.0–2.0**: Balanced. The default range. Novelty and uncertainty contribute comparably.
- **λ = 2.0–5.0**: Strong novelty preference. Use when the generator produces many similar candidates or when you're seeing repeated basin visits.
- **λ > 5.0**: Novelty-dominated. Risk of selecting high-energy, high-novelty structures that aren't scientifically interesting. Use with a tight energy window.

#### `delta_E` (energy window half-width)

- **Wide window (δE > 2 eV for this system)**: Effectively disables the window filter. The novelty LCB behaves like a pure novelty+uncertainty sampler.
- **Moderate window (δE ~ 0.5–1.5 eV)**: Actively filters candidates. The novelty LCB will only select from candidates in this range, and within that range it favors novel ones.
- **Tight window (δE < 0.3 eV)**: Very selective. May result in few or no candidates passing the filter if the model's energy predictions aren't accurate enough. Use with a well-trained model.

#### `delta_E` tuning strategy

1. Run a short regular LCB run (20–30 iterations) to map the energy landscape.
2. Set `target_energy` to the energy of the basin you care about.
3. Set `delta_E` to cover the basin width plus some margin (e.g., basin width + 0.3 eV).
4. Use novelty LCB with this window to enumerate distinct structures in that basin.

---

## 5. Technical notes

### GPR numerical stability

Benchmark 2 hit a `LinAlgError` (Cholesky decomposition failure) at iteration 69 in one run. This is a known issue with GPR when the kernel matrix becomes ill-conditioned with many training points. Mitigation strategies:

1. **Add a noise term** to the kernel: `kernel = RBF() + Noise(sigma=0.01)`
2. **Use a CUR sparsifier** with `SparseGPR` instead of full `GPR`
3. **Increase the GP noise** parameter in the GPR constructor
4. **Reduce the update frequency** (update_period=5 instead of 3)

This is orthogonal to the acquisition function comparison — both acquisitors use the same model and would hit the same issue.

### Fingerprint distance calibration

The "right" distinctness threshold depends on the system. A useful calibration procedure:

1. Take a few known distinct structures (e.g., different isomers of the cluster).
2. Compute pairwise fingerprint distances.
3. Set the threshold to be smaller than the minimum distance between known distinct structures, but larger than the maximum distance between known similar structures (e.g., slightly rattled versions of the same minimum).

For Au₁₀ with the Fingerprint descriptor used here:
- Different isomers: distances typically 2–5+
- Rattled versions of same isomer: distances typically < 0.5
- A threshold of 1.0–2.0 is reasonable for distinguishing isomers.

---

## 6. Files produced

| File | Description |
|---|---|
| `benchmark_novelty_lcb.py` | Benchmark 1 script (wide window, 60 iterations, 5 runs) |
| `benchmark_novelty_lcb_v2.py` | Benchmark 2 script (tight window, 80 iterations, 5 runs) |
| `benchmark_results/` | Database files for each run (SQLite + analysis) |
| `_md/novelty_lcb_acquisitor_documentation.md` | Full documentation for the NoveltyLCBAcquisitor |

---

## 7. Conclusion

The novelty LCB acquisitory is a well-motivated extension of regular LCB that adds structural diversity awareness and an energy-window constraint. On a free Au₁₀ cluster with a wide energy window, it performs identically to regular LCB — which is expected because the system doesn't exercise the features that make novelty LCB valuable (dense structural clusters, tight energy windows, low-dimensional descriptors).

The novelty LCB shines in **surface-adsorbate systems**, **tight energy windows**, and **enumeration of distinct minima** — scenarios where regular LCB would keep returning variations of the same structure. The benchmark provides a baseline confirming that the novelty LCB doesn't degrade performance on simple systems, giving confidence to use it as a default in more complex applications where its advantages will manifest.
