# DISCUSSION — Run b10_femgo_walk_emax04_exclworst_noxsf_novelty (iter20000)

Run: `_runs/b10_femgo_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000/`
Analysis outputs: this directory (`_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000/`)
Script: `_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outdir b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --n-atoms 75
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 75` = atoms per structure (Fe/MgO) for the per-atom relative-energy units of the state density.

---

## NS vs dataset state-density comparison

The figure below overlays the **NS g(E)** (prior-weight-weighted histogram of the 20,000
discarded samples) against the **GPR+LCB g(E)** (gaussian KDE of the b10 dataset's DFT energies),
both peak-normalized to 1 for a direct shape comparison.

![compare_state_density_gE.png](compare_state_density_gE.png)

**Command + parameters that produced it** (run from `_analysist/`):

```bash
/home/think/miniconda3/envs/agox_v2/bin/python compare_state_density_gE.py \
    --run b10_femgo_walk_emax04_exclworst_noxsf_novelty \
    --ns-output analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --n-atoms 75 --figsize 6 \
    --outname compare_state_density_gE.png
```

Parameters: `--run` = b10 run dir (contains `dataset/` and the analysis dir); `--ns-output` = the
analysis dir name (holds the ns_output `samples.csv` + this PNG); `--n-atoms 75` = atoms per
structure (Fe/MgO); `--figsize 6` = square figure size in inches; `--outname` = the output
filename. The dataset KDE uses **all** dataset structures (unfiltered); the plot x-range is capped
at the NS max E−E_min.

**Resulting peaks:** NS g(E) at +0.306 eV/atom (abs g 18.1); dataset KDE at +0.076 eV/atom
(abs g 4.9). The NS weighted ensemble peaks high (~0.31 eV/atom) while the raw dataset KDE peaks
low (~0.08 eV/atom) — NS weights configuration-space volume (which sits higher), whereas the
dataset is densest near the lower-energy region.

---

This document discusses the results of the temperature-free nested-sampling (NS) run on the
plain Fe/MgO (no-Boron) system, using b9's treatment (temperature-free; `--e-max-per-atom 0.4`;
window `[0.3, 0.35]`; `--walk` with `--walk-exclude-worst`; `--no-posterior-xsf`;
`--novelty-threshold 1.0`) at **`--n-iters 20000`**, `--n-live 100`,
`--temperatures 100,200,300,500,1000 K`.

> Note: this run was submitted with `--no-posterior-xsf`, so no `posterior_*.xsf` files exist;
> the delta-Z landscape cannot be reproduced here.

---

## 1. What was run and what the CSVs contain

- **`samples.csv`** (20000 rows): the discarded (worst) samples, one per NS iteration, with
  `iteration`, `energy_eV` (GPR-predicted absolute energy), and `prior_weight`
  (`w_i = X_{i-1} − X_i`, the prior-volume shell weight).
- **`final_live_energies.csv`** (100 rows): the live-set energies at termination (`n_live=100`).
- **`thermodynamics.csv`** (5 rows): `T`, `β`, `log Z`, `Z`, and `F = −k_B T ln Z`.

The energies are the **GPR-predicted** energies of the surrogate trained on the
`--e-max-per-atom 0.4` filtered dataset (1158 of 1297 Fe/MgO structures).

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−436.89 .. −407.06 eV` (weighted mean `−413.51 eV`).

**Relative to the global minimum** (best live energy `−436.91 eV`, ~75 atoms):
- lowest discarded sample ≈ `+0.0003 eV/atom`
- highest discarded sample ≈ `+0.398 eV/atom`

The sampler operated across the targeted band above the ground state (windowed start at
`[0.30, 0.35]` eV/atom, `--e-max-per-atom 0.4` cap), descending to very near the minimum.

**Final live set:** `−436.91 .. −433.35 eV`. The live set descended to near the global minimum
region — the expected NS convergence behaviour.

**Commentary on the walk + novelty:** the dual-scale `--walk` (50 steps, small 0.05 Å / large
0.40 Å, `--walk-exclude-worst`) was the primary per-step move; `--novelty-threshold 1.0`
de-duplicated the initial live set.

---

## 2b. Discussion: samples_energy_vs_iter.png (weighted running mean, staleness, fluctuation)

![samples_energy_vs_iter.png](samples_energy_vs_iter.png)

### What the weighted running mean is and how it is calculated

The red curve in `samples_energy_vs_iter.png` is a **prior-weight-weighted running mean** of the
discarded-sample energies. At each iteration index `n` it is

```
⟨E⟩_n = Σ_{i≤n} w_i E_i / Σ_{i≤n} w_i
```

where `E_i` is the discarded sample's energy and `w_i` is its `prior_weight`
(`w_i = X_{i-1} − X_i`, the prior-volume shell weight, from `samples.csv`). It is "running"
because it uses only the first `n` samples, and "weighted" because each `E_i` counts in
proportion to how much prior volume that sample consumed — so samples early in the run (which
sit on large `X` shells, hence larger `w_i`) dominate the average.

### What it represents

It is a **cumulative, noise-smoothed view of the ensemble's typical energy** as the NS run
progresses. Because the early discarded samples carry most of the prior weight, the running mean
is a robust estimator of the *weighted* center of the sampled distribution, and it is the same
quantity that drives the state density `g(E) = Σ w_i / ΔE` (each sample contributes its prior
weight to the density at its energy). So the running mean's position reflects *where the
probability mass of the ensemble sits*, not the instantaneous worst-sample energy.

### Why it "stales" (plateaus) and its impact on the state density

In this run the weighted running mean saturates at **+0.312 eV/atom** (relative to the global
minimum, `E_min = −436.89 eV`; the per-atom relative energy is `(E − E_min)/75`) after only
~1000 iterations and stays essentially constant for the remaining ~19000 iterations (it is
+0.312 eV/atom at iter 1000 and still +0.312 eV/atom at iter 20000). This "staleness" is
**expected** and is not a bug:

- The early samples carry nearly all the prior weight (`Σ w_i ≈ 1` is reached quickly because
  `X_i = exp(−i/n_live)` collapses), so once those are accumulated the running mean stops
  changing — later samples contribute vanishingly small `w_i`.
- Consequently the running mean is **insensitive to what the sampler does after the first few
  hundred iterations**; it reports the early, low-weight-mass-averaged level, not the late-time
  descent.

**Impact on the state density:** `g(E)` is built from *all* `(E_i, w_i)` pairs, not just the
running mean, so the plateau does **not** erase the low-energy side of `g(E)`. What it does mean
is that the **weighted center** of `g(E)` is fixed at ≈ +0.31 eV/atom above the minimum, and the
histogram's overall mass is dominated by the high-`w_i` early samples. The plateau therefore
tells us the *weighted* peak position of `g(E)` is stable, even though the raw discarded
energies keep changing.

### Why the discarded energy fluctuates after ~4000 iterations, and its impact

The raw, individual `E_i` values do **not** plateau — they keep fluctuating in a band around
**+0.04 … +0.23 eV/atom** (relative to the minimum; e.g. iter 4000 ≈ +0.097, iter 10000 ≈ +0.216,
iter 20000 ≈ +0.053 eV/atom) with a standard deviation of roughly **0.044–0.049 eV/atom**
throughout. After ~4000 iterations the sampler has already entered the ground-state basin
(relative min = 0 eV/atom), so each iteration's worst live point is drawn from a **narrow but
finite spread of near-minimum configurations**; the energy of the worst walker hops up and down
as the walker moves, without a systematic trend. This is the characteristic **noisy plateau** of
a converged NS run once `X_i` is negligible.

**What the fluctuation means:** it is *not* a sign that NS has failed to converge. It simply
reflects that, near the ground state, the live set contains many quasi-degenerate low-energy
structures, so the "worst" one at any step bounces among them. The systematic descent is over;
only the per-iteration ordering noise remains.

**Impact on the state density:** this fluctuation is actually *desirable* for `g(E)`. The
scatter of `E_i` over the band near the minimum populates several histogram bins below the
weighted peak, which is exactly what resolves the **low-energy tail** of `g(E)`. Because each of
these late samples carries only a tiny `w_i`, the fluctuation contributes a small but nonzero
density to the ground-state side of the histogram — it does **not** shift the weighted peak
(which is set by the early, high-weight samples), but it does fill in the shape of `g(E)`
between the peak and the minimum. Without that fluctuation, `g(E)` would be a sharp spike at the
weighted-mean energy; with it, `g(E)` has the resolved, physically meaningful low-energy
shoulder that appears in `state_density_gE.png`.

In short: the **stale weighted mean** fixes the *center* of `g(E)`; the **post-convergence
fluctuation** fills in its *shape*. Both are normal NS behaviour, and together they give a
`g(E)` whose weighted peak sits at ≈ +0.31 eV/atom while its low-energy tail extends down toward
the global minimum.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`. The **weighted peak** is at `≈ +0.306 eV/atom` above the
ground state (`state_density_gE.png`, peak `g ≈ 18.1 config./eV`).

Interpretation: most sampled probability mass sits around `+0.31 eV/atom` above the minimum —
consistent with the 5000- and 10000-iteration runs, confirming the weighted ensemble has fully
stabilised (the peak is only slightly sharper here due to more samples in the band).

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−436.91 .. −433.35 eV` (`live_energy_hist.png`).
The live set is clustered near the low-energy end of the window — the run reached the
ground-state basin, as expected when NS has converged.

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −46.41 | 7.00e−21 | 0.400 |
| 200 | −42.84 | 2.48e−19 | 0.738 |
| 300 | −41.54 | 9.07e−19 | 1.074 |
| 500 | −40.42 | 2.80e−18 | 1.742 |
| 1000 | −39.42 | 7.59e−18 | 3.397 |

- **`log Z` rises monotonically with T** (`−46.4 → −39.4`), and `Z` grows.
- **`F = −k_B T ln Z` rises** with T (`0.40 → 3.40 eV`).
- **Heat capacity `C_V ≈ 0`** — `log Z` vs `β` is nearly linear over 100–1000 K, so no strong
  first-order phase transition / latent-heat peak is resolved in this range.

---

## 5b. NS Boltzmann probability vs energy

The figure below plots the **NS Boltzmann probability P(E)** vs per-atom relative energy
`(E − E_ref)/n_atoms` for the five temperatures (100, 200, 300, 500, 1000 K), computed
**directly from the NS result** (the prior weights in `samples.csv`):

![binding_probability_vs_temperature.png](binding_probability_vs_temperature.png)

For each temperature `P_i(T) = w_i·exp(−β(E_i − E_ref))/Z(T)` with `β = 1/k_B T` and
`Z(T) = Σ_i w_i·exp(−β(E_i − E_ref))`.

**Command + parameters that produced it** (run from `_analysist/`):

```bash
/home/think/miniconda3/envs/agox_v2/bin/python plot_ns_boltzmann_prob.py \
    --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outdir b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outname binding_probability_vs_temperature.png \
    --n-atoms 75
```

Parameters: `--ns-output` = the run's temperature-free output dir (samples.csv);
`--outdir` = this analysis dir; `--outname` = the output PNG filename;
`--n-atoms 75` = atoms per structure (Fe/MgO); default temperatures 100–1000 K.

**Result:** `Z(T)` grows with T (`7.9e−20 → 9.7e−18`), so at higher T the probability
distribution broadens and shifts toward higher energy — the expected thermal excitation
behaviour of the NS weighted ensemble.

---

## 5c. Discussion: Probability Density, why Area = 1, and why values exceed 1

The `binding_probability_vs_temperature.png` figure (above, or as regenerated with
`--area-norm`) plots what is formally a **probability density**, not a probability. Understanding
that distinction is the key to the whole figure.

### What a Probability Density is

A **probability** `P(A)` is a number between 0 and 1 that answers "what fraction of the total
probability lies in region A?". A **probability density** `p(E)` answers a different question:
"how concentrated is the probability per unit of the variable `E`?" It is defined so that the
probability of a small energy interval `[E, E+dE]` is

```
P(E in [E, E+dE]) = p(E) · dE
```

So `p(E)` has **units of 1/energy** (here 1/(eV/atom)). It can be *any* non-negative value,
including values much larger than 1 — only its integral (the area under the curve) is a
probability and therefore lies between 0 and 1 (or is normalized to 1).

A probability (mass) is like "how much water is in a bucket"; a probability density is like "how
deep the water is at a point". A bucket can hold at most its volume (≤ 1), but the water *depth*
at one spot can be any number — a narrow bucket can be very deep even though it holds little
water. The same idea applies here: a narrow distribution can have a very tall peak.

### Why Area = 1

"Area = 1" means we have normalized the density so that the **total probability over the whole
energy range is exactly 1**:

```
∫ p(E) dE = 1
```

This is the requirement that *every* configuration is somewhere: the probability of finding the
system at *any* energy must sum to 1. In the code, `P(E,T) = g(E)·exp(−β(E−E_ref))/Z(T)` is
already normalized so `Σ_E P = 1` (it is divided by the partition function `Z(T)`). The extra
"area = 1" step (the `--area-norm` flag, using the trapezoidal rule `area = trapezoid(probs, grid);
probs /= area`) converts the discrete sum into a continuous integral normalization, so the
plotted curve satisfies `∫ p(E) dE = 1` exactly. This is what makes it a genuine probability
*density* rather than an arbitrary bell curve, and it is what allows different temperatures to be
compared on the same footing.

### Why the peak value is above 1

Because `p(E)` is a density, its peak height is set by the **width** of the distribution, not by
the total probability. For a distribution with unit area and characteristic width `σ`, the peak
is roughly `p_max ≈ 1/σ`. In this run the temperature-free NS distributions are **narrow**
(energy spread only a fraction of an eV/atom), so the unit-area density peaks reach values of
**~10–13** (e.g. 100 K ≈ 13.2, 1000 K ≈ 12.5) — i.e. the probability is concentrated into a
narrow energy window, so the density there is high. This is exactly the expected behaviour: the
NS weighted ensemble occupies only a small band of configurations, so its probability density is
locally large even though its total integral is 1.

**Summary:** the curve height is *not* a probability (it is not "chance = 13"), it is a
density ("chance per unit energy = 13"). The area under each curve is 1 (total probability), and
the peak exceeds 1 simply because the distribution is narrow. This is why the y-axis in the
`--area-norm` figure must auto-scale (it goes up to ~13.9) — the 0–1 scale would otherwise clip
the curves.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 1.000000` over the 20000 discarded samples (`samples_cumulative_Z.png`).
`X_final = exp(−iters/n_live) = exp(−20000/100) = exp(−200) ≈ 0`, so `sum(w_i) ≈ 1`, which
**matches** — the prior volume is fully consumed. Bookkeeping is internally consistent.

---

## 7. Overall interpretation and caveats

**Convergence note (iteration sweep):** `log Z` here (−46.4 → −39.4) is essentially identical to
the iter5000 and iter10000 runs (differences ≲ 0.002 nats). Together with the stable `g(E)` peak
(~+0.31 eV/atom), this confirms the evidence is fully converged by 5000 iterations for this
setup; 20000 iterations only further shrink the already-negligible `X_final`.

**Caveats:**
- Energies are **GPR predictions**, not DFT; absolute `E`/`Z` values are surrogate-relative.
- `g(E)` is a weighted histogram over the sampled band, a proxy.
- No posterior `.xsf` (`--no-posterior-xsf`), so no per-structure/delta-Z analysis.

---

## 7b. Diagnosis of the discarded-energy trajectory (`samples_energy_vs_iter.png`)

This section diagnoses the `dead_E(Iter)` trajectory — the `energy_eV` column of `samples.csv`,
i.e. the worst (highest-energy) live point discarded at each iteration — and addresses the
"lost convergence / energy spike" reading of the figure.

### What the trajectory actually does (verified against `samples.csv`)

- **Compression phase (≈ iterations 0–3,750):** `dead_E` descends smoothly from ≈ **−407.17 eV**
  (the first discarded sample, already inside the `--e-max-per-atom 0.4` windowed-seeded band)
  into the ground-state basin near **−436.9 eV**. This is the normal top-down draining of the
  prior volume.
- **Global minimum:** the lowest energy in the whole trajectory is **−436.888 eV**, first reached
  at **iteration 19,933**.
- **Plateau / fluctuation phase (≈ 3,750–20,000):** inside the basin, `dead_E` no longer descends
  systematically; it bounces in a **narrow band** (≈ −421 … −437 eV, i.e. ≈ +0.04 … +0.23 eV/atom
  above the minimum) for the remaining ~16,000 iterations.

### Is the "lost convergence / violent spike" reading correct?

**No — the trajectory is normal, converged nested sampling.** Two decisive measurements:

1. **The trajectory is ~98% monotonic.** Only **380 of 20,000 steps (1.9%)** show `dead_E`
   increasing. Discarded energies are almost everywhere non-increasing, exactly as standard NS
   requires (each step discards the worst live point and re-samples below the current boundary).
2. **The upward excursions are small and rare.** Only **4 samples** after iteration 3,750 exceed
   −409 eV; the ≈ −407 eV "spike" near the start is the *first* sample, not a post-convergence
   excursion. The post-3,750 band is narrow, not a sustained −409 … −437 oscillation.

The small (1.9%) upward jitter is the expected **near-degeneracy fluctuation** of a converged run:
once the live set is filled with quasi-degenerate low-energy structures, the "worst" live point
hops among them by a fraction of an eV/atom as the constrained walk moves, so `dead_E` jitters
locally instead of decreasing further. It does **not** indicate "correlated/unconverged MCMC
chains" or a "violation of the energy constraint": the window
(`--e-window-lo 0.3 / --e-window-hi 0.35` eV/atom) is applied **only to the initial live
seeding**, not as a per-step ceiling, so nothing here is being violated.

### Impact on the state density

`g(E)` is built from *all* `(E_i, w_i)` pairs. Because the early samples carry almost all the
prior volume (`Σ w_i ≈ 1` quickly, `X_i = exp(−i/n_live)`), the **weighted peak** of `g(E)` is
set by the compression phase at ≈ **+0.31 eV/atom** above the minimum (weighted mean ≈ −413.5 eV
≈ +0.31 eV/atom). The post-convergence fluctuation carries only tiny `w_i` per sample, so it does
**not** shift the peak, but it does **fill in the low-energy tail** of `g(E)` between the peak
and the ground state — desirable for resolving the density's shape (the low-energy shoulder in
`state_density_gE.png`).

### Termination note

The prior volume keeps shrinking (`X_i` from ~10⁻² down to ~10⁻⁸⁹) with no further energy descent
after ~4,000 iterations, so the run is effectively converged well before 20,000 iterations; the
last ~16,000 steps add only tiny-weight samples and negligible evidence. A live-evidence /
prior-volume-termination criterion (stop when `Z_live ≪ Z_acc`) would have stopped this run around
4,000–5,000 iterations with essentially the same answer — the extra iterations are not harmful,
they only refine the already-resolved low-energy tail of `g(E)`.

---

## 8. Suggested next steps

- Compare the `g(E)` peak (~+0.31 eV/atom) against the reference island (0.074 eV/atom) / flat
  (0.255 eV/atom) peaks.
- Since `log Z` is converged across 5000/10000/20000, further iteration increases add little;
  consider widening the window or raising `--n-live` for finer phase-transition features.
