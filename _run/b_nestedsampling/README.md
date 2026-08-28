# Nested Sampling on the combined multi-seed Fe/MgO AGOX dataset

Project: `/home/think/Desktop/research/_run/b_nestedsampling/`
Status: re-hosted under the AI-Agent Project Workflow (migrated from
`_run/8_nested_sampling`).

## What it does

1. Loads **every** structure from **every** seed database in
   `dataset/seed_*/1_db/db_*.db` (seeds 3–15, 1297 structures total, all
   Mg25O25Fe25 / 75 atoms).
2. Trains a single AGOX GPR surrogate on the combined 1297 structures (AGOX
   kernel recipe from `dataset/main.py`).
3. Runs the `NestedSampler` from the `nested_sampling/` package on the combined
   dataset (log-space evidence accumulation, `log L = -beta*(E - E_ref)`).
4. Runs a **state-density / landscape analysis** of the results (PCA landscape +
   KDE state density + Boltzmann probability vs temperature), comparing the
   posterior samples against the training set.

**What is the `log L` in nested sampling?** `L` is the **likelihood** — a measure of how
"good" a structure is. In the fixed-T mode it is `L(x) = exp(-β·(E(x) − E_ref))`, so a
structure is more likely the lower its GPR-predicted energy is. In temperature-free mode
`log L = −(E − E_ref)`, i.e. structures are ranked by energy alone. Nested sampling treats
`L` as an unnormalized posterior weight over configuration space; `log L` (its natural
logarithm) is what the code actually manipulates, because the raw likelihood spans
hundreds of orders of magnitude (energies ~ −400 eV, `β ~ 40 eV⁻¹`).

**What is the posterior, and what does "unnormalized" mean?** The **posterior** `P(x)`
is the probability distribution over configurations *given* the energy surface — "how likely is
each structure". It is the answer to "what should I believe about which structure is realized"
after weighting each configuration by how good (low-energy) it is. **"Unnormalized"** means the
weight is not yet divided by the total, so it does not sum/integrate to 1. The raw weight
`L(x)·π(x)` (likelihood × prior) is the **unnormalized posterior**; dividing by the
normalization `Z = ∫ L(x)·π(x) dx` gives the normalized posterior `P(x) = L(x)·π(x)/Z`, which
does sum to 1. Nested sampling deliberately works with the *unnormalized* weight — because the
normalization constant `Z` is exactly the quantity it is trying to compute. (So when you see
"`L` is an unnormalized posterior weight", it means: `L·π` is the posterior up to the unknown
factor `1/Z`.)

**What is `beta`, and why does it not always appear in `log L`?** `beta = 1/(k_B·T)`
is the **inverse temperature** (units eV⁻¹, `k_B = 8.617e-5 eV/K`). It is the thermodynamic
knob: in **fixed-T mode** the likelihood is `L(x) = exp(-β·(E(x)−E_ref))`, so `β` sits
*inside* the likelihood and controls how strongly low-energy structures are preferred during
sampling — at T = 300 K `β ≈ 38.68 eV⁻¹`, so each eV above the best structure costs a factor
`exp(-38.68) ≈ 10⁻¹⁷` in likelihood. Lower T (higher β) sharpens focus on the global minimum;
higher T flattens the landscape. **Why does `log L` sometimes have no `beta`?** Because in
**temperature-free mode** the sampling likelihood is `log L = −(E − E_ref)` — `β` is
deliberately left OUT. Nested sampling only needs to *rank* configurations by energy (a
strictly decreasing energy limit), and multiplying the exponent by `β` does not change that
ranking. So `β` is moved to post-processing: one temperature-free run records each sample's
`(E_i, w_i)` and then `Z(β) = Σ_i w_i·exp(−β(E_i − E_ref))` gives the partition function at
*any* temperature (see "Physics of temperature-free mode"). Fixed-T mode *does* include `β`
in `log L`, which is why it yields only a single-temperature result.

**What do you mean by "evidence"?** The **evidence `Z`** is the normalization constant of
the posterior, `Z = ∫ L(x)·π(x) dx`. It is a single number that measures how much
probability mass the likelihood assigns to the configuration space — i.e. how well the
"surface" is supported. In statistical mechanics `Z` is exactly the **canonical partition
function**, so it is both the Bayesian evidence and the object from which all
thermodynamics (free energy, heat capacity) is derived. It is the central quantity nested
sampling is designed to compute.

**What is a probability distribution, and why `P(x) = L(x)·π(x)/Z`?** A **probability
distribution** is a normalized assignment of "how likely" each possible outcome is: a set of
non-negative weights, one per configuration `x`, that sum (or integrate) to exactly 1. `P(x) =
L(x)·π(x)/Z` is just "the prior guess `π(x)`, re-weighted by how good the structure is `L(x)`,
then divided by the total `Z` so it sums to 1". **Why this form:** the prior `π` says how likely
`x` was before energy was considered; the likelihood `L` says how good it is; their product is
the relative belief after both; `Z` normalizes it.

**Does nested sampling only "calculate how dense the energy differs"?** Not exactly. NS does
not directly measure the *density* of states; it measures the **volume** of configuration space
contained below each energy level — encoded in the surviving prior-volume fractions `X_i`
(`X_i = exp(−i/K)`). The energy levels themselves come out in increasing order (top-down), and
each sample carries the volume of its "shell" `ΔX_i = X_{i−1} − X_i`. Dividing that consumed
volume by the shell's energy width gives the **density of states** `g(E) = ΔX/ΔE`. So NS gives
you `(E_i, ΔX_i)` pairs, and the state density is a *derived* quantity, not what it samples.

**How to compute the state density from the CSV result — example.** Each discarded sample in
`evidence_history.csv` (fixed-T) or `samples.csv` (temperature-free) has an energy `E_i` and a
prior-volume weight `w_i = ΔX_i = exp(−i/K) − exp(−(i+1)/K)`. To get `g(E)`:
1. Choose bins spanning your energy range (e.g. width `ΔE = 0.05` eV).
2. For each sample, add `w_i / ΔE` to the bin containing `E_i` (volume consumed, per unit energy).
3. The result is the state-density histogram `g(E)` — the (weighted) number of configurations
   per unit energy. This is *exactly* what `convert_to_density_of_states` does in the Fortran
   toy model, and what the KDE in `state_density.py` reproduces with smoothing.

**What is the posterior, its normalization constant, `π`, and `x`?** The **posterior**
`P(x)` is the probability distribution over configurations *given* the energy surface — "how
likely is each structure". It is `P(x) = L(x)·π(x)/Z`. The **normalization constant of the
posterior** is `Z`: because `P(x)` must integrate to 1, the unnormalized weight `L(x)·π(x)`
must be divided by `Z = ∫ L(x)·π(x) dx` — so `Z` is exactly the total probability mass and
is the object nested sampling computes. `π(x)` is the **prior** — the probability weight
assigned to configuration `x` *before* any energy information. Here it is the empirical
distribution over the 1297 database structures (uniform draw + small perturbation). `x` is
the **configuration variable**: a point in the 3N-dimensional configuration space, i.e. one
atomic structure (all atomic coordinates). So the equation just says: total weight of a
configuration = (how good it is, `L`) × (how much prior weight its region had, `π`), summed
(`∫`) over all configurations `x`. In the discrete NS sum this becomes `Z = Σ_i w_i·L_i`,
where `w_i` is the prior-volume weight of sample `i`.

**What is the probability weight `π` (the prior)?** `π(x)` is the **prior** — the
fraction of total prior probability your sampling starts by assigning to configuration `x`,
*before* any energy information. It is a probability weight in the sense that the values are
non-negative and sum to 1. Here the prior is the **empirical distribution over the database**:
it is simply the actual distribution of the structures you already collected, used as the pool
to draw new structures from. **Example:** if the combined DB has 1297 structures and you draw
uniformly, each structure gets prior weight `π = 1/1297`; a region containing 900 of them has
`≈ 900/1297 ≈ 0.69` of the total prior mass.

**Does a DB that is dense at low energy (island) give a prior dominated by the island?** In
this implementation — **yes**, because the prior is a uniform draw *over the DB structures*, so
it inherits the DB's density. If 900 of 1297 structures are near the island and 397 near the
flat, the prior assigns ~69% of its mass to the island region from the start. **Example:**
drawing a new structure picks an island-like one ~69% of the time. This is a modelling choice:
it biases sampling toward where you already have data. The Fortran toy model instead uses a
*flat* prior (uniform `x`), which avoids this bias. Whether the DB-dense prior is "good" depends
on whether you trust that the DB already covers the basins you care about (it makes sampling
efficient there but can under-explore underexplored regions).

**What is the prior-*volume* weight `w_i`, and how is it different from `π`?** `w_i = ΔX_i =
X_{i−1} − X_i = exp(−(i−1)/K) − exp(−i/K)` is the **configuration-space volume** (measure) of
the shell of samples removed at iteration `i` — the quadrature weight that turns the sample
list into an integral for `Z`. **Difference from `π`:** `π` is the prior *probability density*
(per unit configuration), a "how likely at one point" quantity; `w_i` is the *integrated prior
volume* of a whole region (a chunk of `X`), a "how much measure did this sample represent"
quantity. They play different roles: `π` sets the initial measure; `w_i` (computed from how the
volume shrinks) is what actually weights each sample in `Z = Σ_i w_i·L_i`. **Example:** with
`K = 50`, `w_1 = exp(0) − exp(−1/50) = 1 − 0.980 = 0.020` (the first sample represents 2% of the
total prior volume), whereas `π` for one DB structure would be `1/1297 ≈ 0.00077`.

**Why in log-space?** Because `Z` ranges from ~`10⁻²⁴²` early in the run to ~`10⁻⁴` at
the end. A linear `Z` under/overflows float64 (max ~`10³⁰⁸`, min normal ~`10⁻³⁰⁸`, and
the ratios involved are far more extreme). Working with `log Z` keeps every intermediate
value in a numerically safe range and never loses precision.

**What do you mean by "accumulation"?** Nested sampling shrinks the remaining prior
volume geometrically (by `exp(-1/K)` each iteration). It accumulates the evidence by
adding, at every iteration, the discarded sample's prior-volume slice times its
likelihood — done in **log space** with `np.logaddexp`, which is the numerically stable
way to add very different-magnitude numbers in log form. "Accumulation" = summing those
weighted slices over all iterations (plus a final live-set correction) to build up `Z`.

**"Geometrically"** means the remaining prior volume shrinks by a *constant
multiplicative ratio* each iteration — like a geometric series. Nested sampling shows that
after `i` iterations the surviving prior volume is `X_i = exp(−i/K)`.

**What is a geometric series? — example.** A **geometric series/sequence** is a list
where each term is the previous one multiplied by the *same constant ratio*. Example: `1, 1/2,
1/4, 1/8, ...` (ratio `1/2` each step). Nested sampling's prior volume behaves this way:
`X_i = exp(−i/K)`, so `X_{i+1}/X_i = exp(−1/K)` is the same ratio at every iteration. **Concrete
example (K = 100):** `X_0 = 1`, `X_1 = exp(−0.01) ≈ 0.9900`, `X_2 ≈ 0.9802`, `X_3 ≈ 0.9704`, ...
each step multiplies by the constant `0.990`. That "constant-ratio" property is exactly what the
word *geometric* means here — the surviving volume shrinks by a fixed fraction per iteration.

**What is the `exp(−1/K)` factor?** It is the fraction by which the prior volume shrinks on
every single iteration: `X_{i+1}/X_i = exp(−1/K)`. Reason: with `K` live points the expected
volume fraction left after removing the worst and replacing it is `K/(K+1)`, so after `i`
steps `X_i ≈ (K/(K+1))^i ≈ exp(−i/K)`. It is **necessary** because it assigns each discarded
sample its correct configuration-space weight `w_i = X_{i−1} − X_i = ΔX` — the amount of
prior volume that sample represents. Without it you could not turn the sample list into an
integral for `Z`. Its **impact**: the shrinkage converts NS into a quadrature rule; larger `K`
shrinks more slowly (smaller `ΔX`, finer resolution, error `∝ 1/√K`).

**What is the "prior" and "prior volume"?** The **prior** `π(x)` is the initial sampling
distribution over configurations before energy is used — the *measure* on configuration space.
Here it is the empirical DB distribution (uniform draw over the 1297 structures +
perturbation). **Prior volume** is the total measure of configuration space the sampler
starts with, normalized to `X_0 = 1`; NS progressively "eats" it as the energy/likelihood
cutoff tightens, and `X_i` is the fraction remaining after iteration `i`. "Why in volume":
configurations form a high-dimensional space (3N coordinates), so a distribution over them has
a volume (Lebesgue measure / count of distinct structures); `π(x)dx` is a probability element
over that volume and `X` is the surviving fraction.

**Why is `π` a "probability"? — explain without background.** A **probability** is just
a number from 0 to 1 saying how likely something is (0 = never, 1 = always). **Example:** for 3
configurations, `π = (0.2, 0.5, 0.3)` means "20% likely it's config A, 50% B, 30% C". The prior
`π` is your *starting guess* of these likelihoods *before* you look at energy; they sum to 1. So
"`π` is a probability" simply means "it is the pre-energy set of weights, normalized to sum to 1".

**Is it better to choose a prior based on a higher energy (e.g. 0.25 eV/atom above the global
minima), since sampling will slowly lower it?** Yes — that is precisely the right design for
connecting the basins, and it is what the Fortran model does. NS starts from the top (high
energy) and descends, so the prior's upper bound (where `X_0 = 1` is defined) should sit a small
**margin above the energy barrier** separating the basins you care about — here, above the
island↔flat barrier — so the full "window" containing *both* basins is inside the prior. If the
cutoff were set below the barrier, crossing between basins would rely on rare lucky jumps.
Choosing a prior whose upper energy is ~0.25 eV/atom above the global minimum (i.e. past the
barrier, capturing both flat and island) makes the top-down pass correctly traverse the barrier
and give properly weighted traffic between the two phases. (That is the "windowed" design in the
Fortran header: `X_0=1` is the region past the barrier that includes BOTH basins.)

**What is the "surviving fraction", why a fraction, how to compute it — without background.**
The **surviving fraction** is how much of the starting configuration volume is still not yet
"used up" after `i` iterations. It is a fraction because NS starts with the whole space (fraction
`X_0 = 1`, i.e. 100%) and each step removes a slice, leaving `X_i`. **Example (K = 100):** after
0 iterations 100% remains (`X_0 = 1`); after 100 iterations `X_100 = exp(−100/100) = exp(−1) ≈
0.368` → 36.8% remains; after 300 iterations `X_300 = exp(−3) ≈ 0.0498` → ~5% remains. You
compute it as `X_i = exp(−i/K)` (or `(K/(K+1))^i`). The lower it is, the more of the prior volume
NS has already integrated, which is why papers run until it is negligible.

**"Slice × likelihood"?** At each iteration the removed worst sample sits at the current
prior-volume boundary; the thin shell of prior volume consumed between two successive energy
levels is the **slice** `ΔX = X_{i−1} − X_i`, and the **likelihood** `L` is how good a sample
is (evaluated at that boundary, `L_min`). The contribution of that slice to `Z` is `L_min × ΔX`
— the probability mass (likelihood × prior volume) in that shell. During sampling the slice is
the newly-excluded region and `L` is its weight.

**What is `K`?** `K = n_live`, the number of live points. It appears in `exp(−1/K)` because it
sets the shrinkage rate and therefore the resolution/noise of the `Z` estimate.

**What is the "shrinkage rate"? — without background.** The **shrinkage rate** is how
fast the surviving volume `X` gets smaller from one iteration to the next. It is the constant
ratio `X_{i+1}/X_i = exp(−1/K)`. It is called a "shrinkage" rate because `X` is always
*decreasing* (NS keeps eating the prior volume). **How it shrinks:** each iteration removes the
shell between two energy levels, so the remaining volume multiplies by `exp(−1/K)`. **Example:**
with `K = 50`, each iteration leaves `exp(−1/50) ≈ 0.980` of the previous volume (2% eaten each
step); with `K = 500` it leaves `exp(−1/500) ≈ 0.998` (only 0.2% eaten each step). So larger `K`
= **slower** shrinkage = finer resolution in `Z` (but more samples). A slower shrinkage rate
means each removed shell is thinner, which is why the statistical error of `Z` goes as `1/√K`.

**What is `beta`?** `beta = 1/(k_B·T)` is the **inverse temperature** (units eV⁻¹, with
`k_B = 8.617e-5 eV/K`). It is the thermodynamic knob in the likelihood: at T = 300 K,
`beta ≈ 38.68 eV⁻¹`, so each eV above the best structure costs a factor
`exp(-38.68) ≈ 10⁻¹⁷` in likelihood — low-energy structures are overwhelmingly preferred.
Lower T (higher β) sharpens focus on the global minimum; higher T flattens the landscape.

**"Thermodynamic knob"?** A knob you turn to set the *effective temperature* of the
statistical-mechanical ensemble: `β = 1/(k_B T)` dials the system from deep-freeze (focus on
the global minimum) to hot (explore everything). **"In the likelihood"?** In fixed-T mode `β`
literally multiplies the energy inside the exponent of `L(x) = exp(−β·(E(x)−E_ref))`, so it
directly sets how sharply the *sampling* penalizes higher-energy structures.

**What is `E`, and why `− E_ref`?** `E = E(x)` is the **GPR-predicted energy** of a
structure (eV). The likelihood only cares about energy *differences*, so `E` is shifted by
a reference. **`E_ref` = the minimum training energy** (the lowest-energy structure in the
dataset). Subtracting `E_ref` makes the best structure have `E − E_ref = 0` → `L = 1`
(its likelihood is 1, i.e. the highest), while any higher-energy structure has `E − E_ref
> 0` → `L < 1`. This shifts the whole likelihood to O(1) at the optimum, avoiding
overflow and giving a clean, physically sensible reference point.

**Why is `L = 1` when `E − E_ref = 0`?** Because `L = exp(−β·0) = exp(0) = 1`. So the
best (lowest-energy) structure gets the maximum possible likelihood, normalized to 1.

**"Shifts the whole likelihood"?** Subtracting `E_ref` changes the origin of the energy scale
so every likelihood is measured *relative to the best structure*: the exponent becomes
`E − E_ref`, which is `0` at the optimum and `>0` everywhere else. **`O(1)`** means "order of
magnitude 1" — the likelihood is now roughly unit-sized at the optimum instead of astronomically
large. **Why `O(1)`**: the raw likelihoods are enormous in absolute value (energies ≈ −400 eV,
`β ≈ 40 eV⁻¹` → `exp(16000)`), and only their relative ranking matters; normalizing so the best
is exactly 1 keeps the numbers manageable and physically clean. **"At the optimum"** = at the
best (lowest-energy) structure, the reference point where `E − E_ref = 0`.

The central output is the **model evidence / partition function `Z`** (and
`log Z`) for the Fe/MgO system at a given temperature, plus the weighted
posterior set of structures.

**Where is `Z` in the result files, and how do I get the state density / phase
probability from it?** `Z` lives in `evidence_history.csv` / `log_evidence.csv` (fixed-T, one
row per iteration) and in `thermodynamics.csv` (temperature-free, one row per temperature:
`T, β, logZ, Z, F`). You use it via `F = −k_B T ln Z` and its derivatives (mean energy, heat
capacity). For the **configurational state density** `g(E)` per energy level, build a KDE over
the per-atom relative energies of the sampled set — exactly what `state_density.py` does
(`gaussian_kde` over `(E − minE)/N`, giving "State Density (config./eV)"). Alternatively, in
temperature-free mode, histogram the discarded samples of `samples.csv` *weighted by their
prior weights* `w_i` per energy bin. For the **temperature-dependent flat-vs-island
probability**, split the posterior samples into the two growth modes by the Fe island height
`Δz = max(Fe z) − min(Fe z)` (as in `gpr_accuracy.py --fez`), compute each mode's state density
`g_flat(E)`, `g_island(E)`, and form `P_mode(T) = ∫ g_mode(E)·exp(−(E−E_ref)/(k_B T)) dE / Z(T)`.
At low T the lower-energy island mode dominates; as T rises the higher-entropy (flat) mode
gains weight. This is the island-growth manuscript result: island peak at 0.074 eV/atom,
metastable flat peak at 0.255 eV/atom.

**How do papers use the NS result / what analysis do they do?** They construct
temperature-dependent **phase diagrams** from `Z(T)` and locate **phase transitions via peaks
in the heat capacity** `C_V = k_B β² ∂²lnZ/∂β²`; map the PES into **energy-landscape charts**
(basins); compute **free energies / Bayes factors** from `ΔlnZ`; and use the weighted posterior
ensemble for **structure statistics** per phase. Examples: Pártay 2021 (pressure–temperature
phase diagrams of bulk LJ/Al/Fe), Yang 2024 (coverage–temperature surface phase diagrams),
Chatbipho 2025 (adsorbate phase transitions on nanoclusters). Temperature-free post-processing
is what lets one sample set yield `Z(T)`, `F(T)`, `C_V(T)` for all temperatures.

**What is model evidence?** Model evidence is `Z`, the normalization constant of the
posterior `Z = ∫ L(x)·π(x) dx`. It answers "how much total probability (likelihood ×
prior) does the model place over the structures?" — a single scalar that, for a given
energy surface and temperature, quantifies how well-supported the configuration space is.
Because of the statistical-mechanics identification, `Z` is also the **partition
function**, so it is the quantity from which the free energy `F = −k_B T ln Z` and all
other thermodynamic averages are obtained. (The earlier "What is the evidence" note in the
What-it-does section covers the same concept; this is the "model evidence" phrasing used
in the Bayesian literature.)

**What is free energy, and how do I compute it?** The **free energy** `F = −k_B T ln Z`
is the thermodynamic potential of the ensemble; it encodes the balance between energy and
entropy at temperature `T`, and all equilibrium properties derive from it. You calculate it
directly from your result: in temperature-free mode `thermodynamics.csv` already contains
`F = −k_B T ln Z` per temperature (written by `main.py` post-processing); in fixed-T mode use
the accumulated `log Z` with `F = −k_B T·logZ`.

**What is the "weight" and its relation to `Z`?** Each discarded sample has a
configuration-space weight `w_i = Γ(E_{i−1}) − Γ(E_i) = ΔX_i = exp(−i/K) − exp(−(i+1)/K)` —
the fraction of the (normalized) prior volume that sample represents. **Relation to `Z`:**
`Z = Σ_i w_i·L_i`, i.e. `Z` is the sum over all samples of (prior-volume weight × likelihood);
the weights are the quadrature integration weights of NS.

**How do we count the weight?** In `NestedSampler.step()`, `X_prev = exp(−i/K)`,
`X_this = exp(−(i+1)/K)`, `delta_X = X_prev − X_this`. In temperature-free mode this `delta_X`
is stored in `sample_prior_weights`; in fixed-T mode the posterior weight is
`log(w) = log_L_min + log(delta_X)`.

**How do we build `Z` from weight + energy in the NestedSampler?** Fixed-T: each step does
`log_Z = np.logaddexp(log_Z, log(exp(log_L_min)·delta_X))`, plus a final live-set correction.
Temperature-free: `NestedSampler.evaluate(beta)` computes `Z(β) = Σ_i w_i·exp(−β(E_i − E_ref))`
via the numerically stable `_logsumexp(log w + log L)`, plus the final live-point term — one
call per `--temperatures` value.

**What did they do?** The pipeline: (1) load all seed structures, (2) train a single GPR
surrogate on them, (3) run `NestedSampler` to sweep the configuration space from high to
low energy, collecting `(energy, weight)` pairs for every discarded sample and
accumulating `log Z` in log space, (4) write `Z`/`log Z` (plus the weighted posterior set),
and (5) run the state-density analysis. So "what they did" = turned the raw energy
landscape into a numerically stable estimate of the evidence/partition function and the
weighted ensemble.

**Where do we get the `Z` result?** `Z` is computed inside `NestedSampler` (accumulated
via `np.logaddexp` over the iterations, plus the final live-set correction) and written to
the output directory as `evidence_history.csv` (columns: iteration, Z) and `log_evidence.csv`
(iteration, log Z). In **temperature-free** mode, `Z(β)` for any temperature is produced in
post-processing by `sampler.evaluate(beta)` and written to `thermodynamics.csv`
(columns T, β, logZ, Z, F). So the `Z` result is in those CSVs, one row per iteration
(for the run) or one row per temperature (for the temperature-free scan).

**How do papers define convergence / when is `Z` converged?** Nested sampling is exact
once it has consumed (almost) all the prior volume, so the practical criteria are: (1) **`log Z`
plateaus** — plotting `log Z` vs iteration (`evidence_history.csv`), the curve flattens and
changes by less than a small tolerance (typically ≲ 0.1–0.5 nats) between iteration blocks;
(2) **the energy limit has descended** — the worst-live-point energy / `log_L_boundary` has
reached (below) the global-minimum / structural phase-transition region; (3) **remaining prior
volume is negligible** — `X_final = exp(−n_iters/K)` is tiny, so the live-set correction no
longer changes `Z` materially; and (4) the **statistical error** `∝ Z/√K` is small enough for
your purpose. Papers run until `X` is negligible (the top-down pass has eaten the whole prior
volume). Our code stops at a fixed `--n-iters`; you check convergence by plotting `log Z` vs
iteration for a plateau and by inspecting `X_final`.

**How to plot it?** Plot `Z` (or `log Z`) against the **iteration** from
`evidence_history.csv` to see the evidence converge; or plot `log Z` / `Z` and
`F = −k_B T ln Z` against **temperature** from `thermodynamics.csv` to see the
temperature dependence. The state-density analysis (`analysis/conf_space.png`,
`binding_probability_vs_temperature.png`) already visualizes the landscape and the
Boltzmann probability vs T. For a dedicated `Z`/`log Z`/`F` vs `T` figure (and an
optional heat-capacity `C_V(T)` panel), use `scripts/plot_thermodynamics.py`
(see "Usage (thermodynamics plot)" below).

**How to make the new `Z`-vs-`T` / `F`-vs-`T` plot.** `thermodynamics.csv` has columns
`T_K, beta_eV-1, logZ, Z, F_eV` (one row per temperature). This is now a committed script,
`scripts/plot_thermodynamics.py` (see "Usage (thermodynamics plot)" below), which reads the
CSV and draws `Z`, `log Z` and `F = −k_B T ln Z` vs `T` (plus an optional `C_V(T)` panel with
`--cv`). The one-line essentials it encapsulates: `logZ` is the robust column
(`Z = exp(logZ)` underflows at low `T`), and the free energy is `F = −k_B T ln Z`.

**What do we need `log Z` for?** (1) **Numerical stability** — `Z` under/overflows
float64 (range ~`10⁻²⁴²`→`10⁻⁴`), `log Z` does not. (2) **Thermodynamics** — the free
energy is `F = −k_B T ln Z`, and derivatives of `ln Z` w.r.t. `β` give mean energy and
heat capacity (heat-capacity peaks mark phase transitions). (3) **Bayesian model
comparison** — differences in `log Z` between models give Bayes factors. So `log Z` is
the robust quantity the code keeps and that you use for all the physics and statistics.

**What is heat capacity, how is it computed here, why does it matter?** Heat capacity
`C_V = ∂⟨E⟩/∂T` measures how much energy the system absorbs per unit temperature rise. It is
computed from the partition function as `C_V = k_B β² ∂²lnZ/∂β²`. In this sampling you already
have `ln Z(β)` at many temperatures (`thermodynamics.csv`), so `C_V(T)` follows from a numerical
second derivative of `ln Z` with respect to `β = 1/(k_B T)`. **Why it matters:** a peak in
`C_V(T)` is the standard thermodynamic signature of a phase transition — the hallmark NS
analysis (Pártay 2021 etc.). Here it would locate the flat↔island (and any solid↔liquid)
transitions directly from your `Z` data.

## Environment

Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```
The HPC batch script `j_nestedsampling.sh` activates `gpaw_env` (standing
convention) — see the TUTORIAL caveat: the sampling script itself needs the
AGOX/ASE stack from `agox_v2`.

## Usage (full run + automatic analysis)
```
cd /home/think/Desktop/research/_run/b_nestedsampling
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```
After sampling, the analysis writes to `<--output>/analysis/` automatically.

## Usage (temperature-free mode — consistent with the papers)
```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --output ./ns_output_tfree --rng 42
```
In temperature-free mode beta is kept OUT of the likelihood (energy-constrained
top-down pass, per Pártay 2021 / Yang 2024). The partition function, free energy
`F = -k_B T ln Z`, and the posterior are evaluated in **post-processing** at each
`--temperatures` value, so one sample set yields thermodynamics at all temperatures.
Writes `samples.csv` (re-runnable), `thermodynamics.csv`, and per-T posterior dirs
`posterior_T{KKK}/`.

## Usage (thermodynamics plot)
`scripts/plot_thermodynamics.py` plots the thermodynamics of a finished
temperature-free run from its `thermodynamics.csv` (columns `T_K, beta_eV-1, logZ,
Z, F_eV`, one row per temperature). It draws `Z`, `log Z` and `F = −k_B T ln Z` vs
`T` in one figure, and with `--cv` adds a heat-capacity `C_V(T)` panel computed from
the numerically stable `log Z` via `C_V = k_B·β²·d²(lnZ)/dβ²` (needs ≥3 temperature
points; peaks mark phase transitions). Needs only numpy + matplotlib (no AGOX):
```bash
/home/think/miniconda3/envs/agox_v2/bin/python scripts/plot_thermodynamics.py \
    --input ns_output_tfree/thermodynamics.csv --output thermodynamics_Z_F.png --cv
```

**Where does `thermodynamics.csv` come from?** It is produced **only** by a
**temperature-free** nested-sampling run (`main.py --temperature-free ...`) — it is
written to the run's `--output` directory (e.g. `./ns_output_tfree/thermodynamics.csv`)
by the temperature-free post-processing step. It does **not** exist for a default
fixed-T run: fixed-T mode writes `evidence_history.csv` / `log_evidence.csv` instead.
To generate it:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --output ./ns_output_tfree --rng 42
```
The run trains the GPR on the combined dataset, samples temperature-free, and the
post-processing loop calls `sampler.evaluate(beta)` per `--temperatures` value to
write `T_K,beta_eV-1,logZ,Z,F_eV` rows. (No `thermodynamics.csv` is present in the
repo or in the existing `_runs/*` — run the command above to create one, locally or
via the HPC temperature-free job.)

## Physics of temperature-free mode

In canonical statistical mechanics the **partition function** of a system of atoms is

$$Z(\beta) = \sum_i e^{-\beta E_i} = \int \Omega(E)\, e^{-\beta E}\, dE,$$

where $\beta = 1/(k_B T)$ and $\Omega(E)$ is the **density of states** (the number of
microstates at energy $E$). Every macroscopic observable — free energy, internal
energy, heat capacity, phase behaviour — follows from $Z(\beta)$:

- **Free energy:** $F = -k_B T \ln Z(\beta)$
- **Mean energy:** $\langle E \rangle = -\partial \ln Z/\partial\beta$
- **Heat capacity:** $C_V = k_B \beta^2\, \partial^2 \ln Z/\partial\beta^2$

**Why sample temperature-free.** Nested sampling is fundamentally temperature-
independent: it does one top-down pass over configuration space, constrained only by a
monotonically *decreasing* energy limit (the "worst" live point). It never needs $\beta$
to decide where to sample — $\beta$ only weights the results *afterwards*. By keeping
$\beta$ out of the sampling likelihood, one single run stores, for every discarded
sample, its energy $E_i$ and its configuration-space (prior-volume) weight
$w_i = \Gamma(E_{i-1}) - \Gamma(E_i)$. The partition function at **any** temperature is
then just the weighted Boltzmann sum (computed in `NestedSampler.evaluate`):

$$Z(\beta) = \sum_i w_i\, e^{-\beta (E_i - E_{ref})},$$

plus a final live-set correction. This is exactly the Pártay 2021 / Yang 2024 approach:
$\beta$ is absent from the sampling and applied only in post-processing, so one sample
set yields $Z(T)$, $F(T)$, $C_V(T)$, and the temperature-dependent posterior for all $T$
of interest. (The default fixed-T mode instead puts $\beta$ inside the likelihood, giving
a single-temperature run.)

**How does nested sampling decide what to sample?** It keeps a set of `K` live points.
Each iteration it (1) removes the **worst** live point (lowest `log L` / highest energy),
(2) shrinks the prior volume and records the sample's weight, and (3) **replaces** the removed
point with a new structure drawn from the prior but **constrained to be better than the current
boundary** — `sample_constrained()` repeatedly draws until it finds a structure with
`log L > log_L_boundary` (equivalently, in temperature-free mode, energy below the current
worst-energy limit) and `|E| < 1e4`; if none after 500 attempts it falls back to an
unconstrained prior draw. So sampling is a repeated *random draw from the DB distribution +
small perturbation*, filtered by the likelihood/energy threshold.

**What is `w_i` in the equation, and how is it computed?** `w_i` is the prior-volume
(configuration-space) weight of sample `i`: `w_i = Γ(E_{i−1}) − Γ(E_i) = ΔX =
exp(−i/K) − exp(−(i+1)/K)`, computed in `step()` as `delta_X`. It is the fraction of the
normalized prior volume that sample represents. It is used because `Z = Σ_i w_i·L_i` — the
weights turn the sequence of samples into a numerical integration of `Z` over the prior volume.

**What is `n_live` and how does it relate to `log L`, `Z`, and the top-down pass?** `n_live`
(`K`) is the number of live points. It sets the shrinkage rate (`X_i = exp(−i/K)`) and thus
the resolution/noise of the `Z` estimate (error `∝ 1/√K`): more live points → each iteration
consumes a smaller volume slice → finer, lower-variance evidence. The top-down pass removes
points worst-first, so it naturally descends energy levels, and `K` is how many samples coexist
at each level.

**How is one top-down step performed here (and does it use the DB throughout)?** A step is NOT
just a single 0.01 Å perturbation. `step()`: find the worst live point (`argmin log L`), shrink
the prior volume (`ΔX`), accumulate evidence / record the weight, then replace the worst point
via `sample_constrained()` — which copies a **random structure from the database** and adds a
Gaussian perturbation (amplitude `perturb = 0.01 Å`) to the Fe atoms (`perturb_indices`).
**Initial structures:** `initialize()` draws `n_live` such DB-resample + perturb structures with
no boundary constraint yet. **The database stays the pool for the whole run:** `sample_from_prior()`
is the *only* source of new structures, and every call (initial and every replacement) picks a
random DB structure (`idx = rng.integers(0, len(db_structures))`) and perturbs it. So yes — the
sampler keeps re-initializing from the DB at every step; it never evolves the removed point (no
clone-and-MC decorrelation walk, the modelling gap vs the papers noted above).

**Contrast with the fixed-T mode.** In fixed-T mode, `log L = -β·(E − E_ref)` ranks the
live set, so the whole run is tied to one temperature and $Z$ is that temperature's
partition function. In temperature-free mode, `log L = −(E − E_ref)` ranks by energy
alone; $\beta$ never enters sampling, and `evaluate(β)`/`posterior_at(β)` turn the
recorded $(E_i, w_i)$ into $Z(\beta)$ and the posterior at any temperature.

**Difference between fixed-T and temperature-free in the equations.** Fixed-T:
`log L = −β(E − E_ref)` → `L(x) = exp(−β(E − E_ref))`, so `β` (the temperature) is inside the
sampling likelihood and `Z` is that single temperature's partition function. Temperature-free:
`log L = −(E − E_ref)` → `L(x) = exp(−(E − E_ref))`, no `β`; `β` appears only in post-processing
as `Z(β) = Σ_i w_i·exp(−β(E_i − E_ref))`.

**Why can we even drop `β` from the equation?** Because the top-down NS pass is
temperature-independent: it only needs to *rank* configurations by energy (a strictly decreasing
energy limit), and multiplying the exponent by `β` (a positive constant) does not change that
ranking — it changes only how the recorded `(E_i, w_i)` are re-weighted. So `β` can be moved
entirely to post-processing without changing which samples are collected.

**What does each represent?** Fixed-T represents a single-thermodynamic-state estimate: all
sampling is focused at one temperature and yields that temperature's `Z` (and weighted
posterior). Temperature-free represents a complete thermodynamic function of `T`: one sample set
yields `Z(T)`, `F(T)`, `C_V(T)`, and the temperature-dependent posterior for every temperature
of interest, because the energy levels and weights are `β`-independent.

**From $Z$ to observables.** The code writes `thermodynamics.csv` with columns
T, β, logZ, Z, and `F = −k_B T ln Z`. Derivatives of $\ln Z$ with respect to $\beta$
would give $\langle E\rangle$ and $C_V(T)$ — useful for identifying phase transitions
via heat-capacity peaks (a hallmark of the nested-sampling approach in the papers).

## Nested sampling in 1D (Fortran toy model)

`_tmp/nested_sampling_windowed_fixed.f` is a self-contained **Fortran** toy model of the
*same* temperature-free nested-sampling algorithm the Python `NestedSampler` implements, but
reduced to a **1D double-well potential** so every step is transparent and cheap to run. It
maps one-to-one onto the Python concepts above.

**The model.** The potential is an asymmetric double well
`E(x) = A·(x²−1)² + B·x` (A = 1, B = 0.3, `x ∈ [−3, 3]`):
- `x ≈ −1` — the **island** structure (global minimum, lower energy)
- `x ≈ +1` — the **flat** structure (higher-energy metastable basin)
- `x ≈ 0`  — the **energy barrier** separating the two basins

`x` plays the role of the configuration variable (the README's `x`); `E(x)` plays the role of
the energy surface (here exact, in the Python project a GPR surrogate). This is the flat-vs-island
picture from the state-density analysis, in 1D.

**Key design choice ("windowed").** `X_0 = 1` (the reference "entire configuration space") is
deliberately defined NOT as the flat basin alone but as the region that extends **past the
barrier and includes both basins** (`E_max = E_barrier + 0.10` margin). This is what makes
correctly-weighted traffic between flat and island possible — the same reasoning as the
"is it better to choose a higher-energy prior, 0.25 eV/atom above the global minimum?" note:
the prior window must span the barrier to connect the two phases.

**Routine-by-routine mapping to the Python code**

| Fortran routine | What it does | Maps to (Python `NestedSampler`) |
|---|---|---|
| `energy(x,A,B)` | Exact potential `A(x²−1)²+Bx` | `gpr.predict_energy(atoms)` (here exact, not a surrogate) |
| `gaussian_random()` | Box–Muller Gaussian draws for the rattle moves | `rng.normal(0, perturb, ...)` in `sample_from_prior` |
| `locate_features` | Grid search for island/flat/barrier positions + energies | (diagnostic) `E_ref = min training energy`; the barrier is the flat↔island transition |
| init loop (lines 66–77) | Draw `K=100` walkers uniform over `{E ≤ E_max}` via rejection sampling | `initialize()` drawing `n_live` prior samples (here a flat 1D prior, not a DB resample) |
| main loop `dead_X(iter) = (K/(K+1))**iter` | Record surviving prior volume `X_i` each iteration | `X_i = exp(−i/K)` (`X_prev/X_this` in `step()`); `(K/(K+1))^i ≈ exp(−i/K)` |
| `idx_worst = maxloc(walkers_E)` | Remove the worst (highest-energy) walker | `worst_idx = argmin(live_log_L)` (temperature-free ⇒ highest energy) |
| clone + `constrained_walk` | Pick a random other walker and run an MCMC walk that keeps `E < dead_E(iter)` | `sample_constrained()` (draw until `log L > log_L_boundary`); **difference:** Fortran does a real multi-step MC decorrelation walk, Python does single random draws without the walk (the "walk length L" gap noted in the README) |
| `constrained_walk` rattle | Mix of small (`0.05`) and large (`0.40`) Gaussian displacements, reject out-of-`[−L,L]` or above energy limit | `--perturb` (small Gaussian displacement of the Fe atoms); here two scales to also allow basin crossing |
| `print_thermodynamics` | For T ∈ {0.05,0.1,0.2,0.3,0.5,1.0}: `Z=Σ ΔX·e^(−E/T)`, `U`, `F=−T ln Z`, `S=(U−F)/T` | `evaluate(beta)` per `--temperatures` value → `thermodynamics.csv` (Z, F); also gives `⟨E⟩` and entropy |
| `convert_to_density_of_states` | Histogram `g(E) = Σ ΔX/ΔE` over bins spanning `[island−0.15, flat+0.15]` | `state_density.py` KDE over per-atom relative energies; the exact-histogram counterpart |

**Does the Python code define an `E_max`? — the honest answer.** No — the Python
`NestedSampler` does **not** set an explicit upper-energy `E_max` like the Fortran toy's
`E_max = E_barrier + margin`. The two codes shape the prior window differently:

- **Fortran:** explicitly picks `E_max` = barrier + margin, so `X_0 = 1` deliberately spans
  *both* basins (the "windowed" design).
- **Python:** the prior is a uniform draw over the database structures + a tiny perturb, so the
  top of its "window" is *implicitly* the highest-energy structure in the DB — there is no
  barrier-relative margin. The window is just "whatever the collected DB spans".

**1. What does "keeping the energy cutoff at the current worst live point" mean?**
The energy cutoff is the highest energy still allowed inside the sample set. "The current worst
live point" is the *highest-energy* structure still alive (the live points are the `K` structures
currently being kept). "Keeping the cutoff at the worst live point" means: every iteration the
cutoff is set exactly equal to the energy of the current worst live point, i.e.
`log_L_boundary = live_log_L.min()` (line 265) after each `step()`. So the cutoff is not a number
you choose and fix; it is always "whatever is currently the highest live-point energy."

**2. In the Fortran, is an upper value set first and then decreased via `X_i=(K/(K+1))^i`?**
Almost, but with an important correction. In the Fortran there are **two different quantities**,
and you must not mix them up:
- **`E_max` (line 61, = barrier + margin)** is set **once**, and used **only to generate the
  *initial* `K` walkers** (rejection sampling, lines 66–77). It is **never** used again in the
  loop and never decreased.
- **The energy cutoff used during the loop** is `dead_E(iter) = walkers_E(idx_worst)` (line 82) —
  the energy of the current worst walker. This is passed to `constrained_walk` as the
  `E_max_local` bound (line 91). It is **re-computed every iteration** from the worst walker, just
  like Python's `log_L_boundary`.
- **`dead_X(iter) = (K/(K+1))**iter` (line 83)** is the **prior-*volume* weight** (the shrinking
  shell), NOT the energy cutoff. It is only stored and later used in `print_thermodynamics` /
  `convert_to_density_of_states` to weight `Z` and `g(E)`.

So: the Fortran's *energy* cutoff is `dead_E` (dynamic, worst-walker), and `X_i=(K/(K+1))^i` is
the *volume* weight — the two play different roles. The Python code is exactly the same: the
energy cutoff is `log_L_boundary`/`E_boundary` (dynamic, worst live point, line 265), and the
volume weight is `ΔX = exp(−i/K) − exp(−(i+1)/K)` (lines 232–234). The only cosmetic difference is
the formula for the volume fraction: `(K/(K+1))^i` (Fortran) vs `exp(−i/K)` (Python) — they are
the same to leading order, `exp(−i/K) = [exp(−1/K)]^i ≈ (K/(K+1))^i`.

**Q1. Can we turn `max_E` into a relative "eV/atom above the global minimum" filter?**

Yes, that is both possible and, in fact, already partly implemented — but under a different name
and at a different stage. Two distinct things are involved:

1. **The internal `max_E` (in `_filter_unphysical(max_E=1e4)` and the `abs(E) > 1e4` guards)** is
   an **absolute energy** check used to discard *unphysical GPR extrapolations* (|E| ≳ 1e4 eV). It
   is meant as a sanity guard, not a physical energy-window selector. Re-purposing it to a relative
   eV/atom threshold would be wrong for two reasons: (a) it would then also silently drop physical
   structures, and (b) it is applied *inside* the sampler on every prediction, where you usually
   do **not** want to filter, just to reject garbage.
2. **The relative "eV/atom above the dataset minimum" filter already exists as the
   `--e-max-per-atom` CLI flag** (in `main.py`). It drops DB structures with
   `(E/atom − min E/atom) > value` **before** GPR training and before sampling. That is exactly a
   "relative-to-global-minimum, per-atom" filter — just applied to the *dataset*, not as a runtime
   `max_E`.

So: to filter *which structures enter the pool* by relative eV/atom above the minimum, use
`--e-max-per-atom`. What the code does **not** currently have is a runtime *relative* `max_E`
filter applied during sampling. That could be added (see Q2) as a small change — convert the
absolute check `abs(E) > max_E` into a relative one like `(E − E_ref)/N > threshold` or keep both.

**Q2. Can we set the initial energy window ourselves, e.g. sample only a band starting 0.25
eV/atom above the global minimum?**

Yes — in fact this is precisely the "windowed" design the Fortran toy model uses (its `E_max`),
and it is the idea behind "choose a higher-energy prior." It is feasible but requires a code
change, because the current Python prior is a **uniform draw over the (filtered) database** with
no explicit lower or upper energy window. To restrict sampling to a band `[0, 0.25]` eV/atom
above the minimum you would:

1. **Upper bound (the "start" of sampling):** filter the DB to keep only structures with
   `(E/atom − min E/atom) ≤ 0.25` (this is `--e-max-per-atom 0.25`). This caps the prior window
   at 0.25 eV/atom above the global minimum — the highest-energy structures you will ever sample.
2. **Lower bound (optional, the "floor"):** if you want to *start* above the minimum rather than
   at it, also require `(E/atom − min E/atom) ≥ some lower value`. The current code has **no** flag
   for a lower bound; only an upper bound (`--e-max-per-atom`). Adding `--e-min-per-atom` would
   restrict the prior to a window like `[0.05, 0.25]` eV/atom. Otherwise the prior includes the
   global minimum itself, so sampling will also touch the very lowest structures.

**How to force NS to start from 0.25 eV/atom above the global minimum, regardless of the
initial DB draw.**

Your observation is correct: `initialize()` (lines 162–185) draws the `K` initial live points
with `sample_from_prior()` — a **uniform draw over the DB + noise** with **no** energy condition.
The worst of those (the highest-energy one) becomes the first `log_L_boundary`/`E_boundary`
(line 183). Because the DB is dense near the ground state, most initial draws land at low energy,
so the initial boundary is typically *much lower* than 0.25 eV/atom — i.e. the run effectively
starts low, not at your chosen window top.

**To force the start at the top (≈0.25 eV/atom), you must constrain the *initial* live draws, not
just the prior pool.** Concretely, add a rejection condition inside `initialize()`'s draw loop so
every initial live point satisfies a lower energy bound relative to the minimum. Conceptually:

```python
# pseudo-code for a forced-start initialize loop
for i in range(n_live):
    while True:
        s = sample_from_prior()
        E = gpr.predict_energy(s)
        rel = (E - E_ref) / N_atoms               # eV/atom above the global minimum
        if abs(E) < 1e4 and rel >= e_min_per_atom: # e.g. >= 0.25
            break
    live_structures.append(s); ...
```

Here `e_min_per_atom` is the lower bound you want the *initial* live points to sit above — e.g.
`0.25`. This forces every one of the `K` starting walkers to be at **≥ 0.25 eV/atom** above the
minimum, so the initial `E_boundary` (the worst of them) is *at or just above* 0.25, and NS then
descends from there. (If you instead want the top *capped* at 0.25 and to descend from it, you
combine this with `--e-max-per-atom 0.25`, which restricts the pool so `rel ≤ 0.25`; then the
initial boundary lands near 0.25 and descends toward the minimum.)

**The trade-off you must weigh before doing this.** A strict lower bound on the **initial** live
set (requiring `rel ≥ 0.25`) has real costs:

1. **It may be impossible to fill the live set.** If the (filtered) DB has few or no structures
   with `rel ≥ 0.25`, the `while True` loop can spin (or time out) without collecting `K` valid
   walkers. You need enough high-energy structures in the pool — this is exactly why the Fortran
   toy uses rejection sampling over a *continuous* 1D potential, where such a draw always exists;
   a finite discrete DB may not have enough.
2. **It throws away information and wastes the low-energy data.** Every initial draw below 0.25 is
   discarded, even though those are precisely your best structures. NS is designed to *start high
   and descend* precisely so it can weight the whole range of `Z`; forcing the start high without
   also sampling the low region means the low-energy basin contributes only via later constrained
   draws, and you may lose the low-energy weight unless the window extends to the minimum.
3. **The `≤`/`<` boundary choice matters.** "Start at 0.25" is ambiguous: do you accept `rel ==
   0.25` or `rel > 0.25`? For a discrete DB, requiring `rel ≥ 0.25` usually yields *strictly
   above* (no exact hit); requiring `rel > 0.25` is a stricter criterion and even harder to fill.
4. **A cleaner alternative for "start at the top".** Rather than forcing a lower bound, set only
   the **upper** window (`--e-max-per-atom 0.25`) and let NS start automatically at the top of
   that window. NS always begins at the highest-energy point of its prior pool, so if the pool is
   capped at 0.25, the run *does* start near 0.25 and descends — no rejection loop needed, and no
   risk of an unfillable live set. The forced lower bound is only needed if you specifically want
   to *exclude the region below 0.25 entirely* (i.e. never sample the ground state), which is
   physically unusual because the whole point of `Z` is to include the low-energy basin.

**Recommendation.** Use `--e-max-per-atom 0.25` to set the window top, and (if you want to guard
against accidental very-low starts) add the rejection condition in `initialize()` only as an
optional `--e-min-per-atom` flag with a warning if too few structures satisfy it. That keeps the
"start near the top" behavior without breaking the run or discarding the low-energy data you care
about. (This is the same "windowed" reasoning as the Fortran `E_max`; the difference is that the
Fortran can always fill its live set from a continuous potential, whereas your DB may not.)

**Understood — you want the initial live set's *worst* point at 0.25 eV/atom while *keeping*
the lower-than-0.25 structures in the live set. Good news: that requires **no rejection and
nothing discarded** — it is exactly the "upper-window-only" case.

**How to get it.** Cap the prior pool's upper bound at 0.25 eV/atom with `--e-max-per-atom 0.25`.
This keeps every DB structure with `(E/atom − min E/atom) ≤ 0.25`, which includes:
- the low-energy structures (down to the global minimum), and
- the near-0.25 ones.

Then `initialize()` draws the `K` initial live points *uniformly from that pool*. Because the
pool's top is 0.25, no initial live point can exceed 0.25 — so the **worst** of them (the initial
`E_boundary`, `log_L_boundary = live_log_L.min()`, line 183) is **at most 0.25**, and in practice
lands close to 0.25 whenever the pool has structures near the top. The rest of the live set spans
downward from there (including the <0.25 structures), exactly as you want. NS then descends from
~0.25 toward the minimum, weighting the whole range.

**So the recipe is just one flag:** `--e-max-per-atom 0.25` (plus `--n-live`/`--n-iters` as
usual). No `--e-min-per-atom`, no rejection loop, no wasted data.

**How to guarantee the initial live set's worst point lands in the 0.25±0.01 band.**

Your concern is correct: with a uniform draw over a DB capped at 0.25 but dense near 0, the *max*
of the `K` initial draws can still come out well below 0.25 (e.g. 0.1), because the worst is the
highest of `K` independent draws and there are far more low-energy structures. To make the worst
≈0.25 **guaranteed** (not just likely), you must **ensure at least one initial live point is
seeded in the 0.24–0.26 band**, and ensure **none exceeds 0.25**. The other live points can stay
wherever they land — nothing is discarded.

Concretely, inside `initialize()` (lines 162–185), after filling the live set by the usual draws,
**replace one of the draws with a point drawn from the band** `[0.24, 0.26]` eV/atom (intersected
with the pool ≤0.25). Because the worst live point is `max(live_log_L)` → `E_boundary` (line 183),
seeding one point in that band forces the worst to be at least that high, while the ≤0.25 cap keeps
it from being higher. So the initial `E_boundary` lands **in the band**, and all other live points
span downward (including the <0.25 structures).

**Simplest robust implementation (pseudo-code):**

```python
# inside initialize(), instead of K purely uniform draws:
#   1) first, seed ONE live point from the 0.24-0.26 band:
while True:
    s = sample_from_prior()
    rel = (gpr.predict_energy(s) - E_ref) / N_atoms
    if 0.24 <= rel <= 0.26 and abs(gpr.predict_energy(s)) < 1e4:
        break
live_structures.append(s); ...

**Assessing the bounded-attempt version — it fixes the unbounded-loop risk, but has a key
limitation the anchor approach does not.**

Your idea: instead of `while True`, use a **bounded attempt count** — try up to `N` draws to find a
structure in the 0.25±0.01 band, and **raise an error** if none is found within `N`. This is a
reasonable robustness improvement over the unbounded `while True`, and it is the standard pattern
for rejection sampling:

```python
max_attempts = 1000        # your "attempt value"
found = False
for _ in range(max_attempts):
    s = sample_from_prior()
    rel = (gpr.predict_energy(s) - E_ref) / N_atoms
    if 0.24 <= rel <= 0.25 and abs(gpr.predict_energy(s)) < 1e4:
        live_structures.append(s); found = True; break
if not found:
    raise RuntimeError(f"No structure found in [0.24, 0.25] eV/atom after {max_attempts} draws")
```

**Why this is good.** It cannot hang forever, and it gives a clear, debuggable failure signal
("the DB has no structure near 0.25") instead of silently doing something unintended.

**The limitation vs the anchor approach.** A bounded-attempt rejection **can still fail** when the
DB is sparse in the 0.24–0.25 band — after `N` draws, if no structure lands in-band, it errors,
even though a perfectly good "closest available" structure exists just outside the band. By
contrast, the **anchor approach** (previous note) never fails: it deterministically takes the
structure nearest 0.25 (e.g. 0.22), so the run always proceeds, gracefully degrading the start to
"closest available ≈ 0.25." In other words:
- **Bounded-attempt:** strict about the band, but hard-fails on sparse DBs.
- **Anchor:** never fails, but softens the guarantee to "closest available to 0.25."

**Which to prefer?** For a real DB, the anchor approach is usually better: it is deterministic,
cannot error, and "closest available to 0.25" is almost always what you actually want (a structure
at 0.22 vs erroring out entirely). The bounded-attempt version makes sense only if you have a hard
requirement that the worst be *within* 0.25±0.01 — in which case the anchor's "closest" is not
strict enough and you genuinely want to reject-and-error if the band is empty.

**A hybrid that gets the best of both.** Use the anchor to find the closest structure; if it is
within the band (`0.24 ≤ rel ≤ 0.25`), use it; if not, decide explicitly: (a) error, or (b) warn
and proceed with the closest available. That keeps the deterministic no-loop property and lets you
choose the strict-vs-forgiving policy. All three options are small, local changes to
`initialize()` and none affects the rest of the sampler.


**Assessing your proposal — yes, this is a cleaner and fully deterministic design.**

Your approach: as a flag, (1) **immediately pick the DB structure closest to the desired energy
window (0.25±0.01)** as one initial live point (the "anchor"), then (2) fill the remaining
`K−1` live points with **uniform random capped at the window max (0.25)**. This is better than a
`while True` band seeding in three ways:

1. **Deterministic and always terminates.** No rejection loop — you just find the argmin of
   `|(E−E_ref)/N − 0.25|` over the pool and take that structure. It cannot spin.
2. **Pins the worst to the closest-to-0.25 structure.** The anchor is the structure whose
   relative energy is *nearest* 0.25, and every other live point is ≤ 0.25 (capped pool). So the
   worst live point = `max(live_log_L)` → `E_boundary` (line 183) is **exactly that anchor** —
   the closest the DB provides to 0.25, i.e. worst ≈ 0.25 within whatever the DB has.
3. **Keeps everything below.** All other live points stay wherever uniform draws land (including
   the <0.25 structures), so nothing is discarded and the low-energy basin is fully represented.

**Does it "guarantee" worst ≈ 0.25?** Yes, *within the DB's resolution*: the worst is pinned to
the closest-to-0.25 structure that exists at or below 0.25. If the DB is dense near 0.25, that
structure is ≈0.25 (well within 0.25±0.01). If the DB is sparse there (e.g. its highest structure
≤0.25 is 0.22), the worst lands at 0.22 — still the *best possible* anchor, but not literally
0.25. So the guarantee is "worst = the DB's best available approximation of 0.25," which is the
strongest guarantee a finite discrete DB can give.

**Sensible flag semantics.** Make it `--e-anchor-per-atom 0.25` (optional). When set:
- Pre-filter the pool with `--e-max-per-atom` semantics so no structure exceeds the anchor value
  (so the anchor is indeed the global worst; if you don't cap, a structure above 0.25 would win
  `max` and defeat the purpose — so anchor and cap should move together).
- In `initialize()`, draw the anchor structure first (closest to the anchor value), then draw the
  other `K−1` live points uniformly from the capped pool.
- Edge case: if the pool is empty at/above the anchor (no structure ≤ 0.25 at all), error clearly.

**Tie-break / determinism.** If two structures are equidistant from 0.25, pick either
deterministically (e.g. lowest index) so `--rng` still reproduces the run. Drawing the anchor
*first* also keeps the subsequent uniform draws' RNG stream identical to a run without the anchor.

**Net assessment.** This is the right design — simpler, deterministic, and it achieves exactly
"worst ≈ 0.25 (closest available), keep everything below." The only caveat is the inherent
discrete-DB resolution: "guaranteed ≈ 0.25" really means "guaranteed = the closest available
structure to 0.25 that is ≤ 0.25."


#   2) then draw the remaining K-1 live points as usual (uniform over the <=0.25 pool).
```

**Why "none above 0.25" is automatic here.** The prior pool is capped at ≤0.25 by
`--e-max-per-atom 0.25`, so no drawn structure can exceed 0.25 anyway — the worst can never be
above 0.25, and the seeded band point guarantees it is at least ~0.24.

**Edge cases to handle:**
- **Band may be empty / undersampled.** If the DB has no (or too few) structures in
  `[0.24, 0.26]`, the `while True` seeding loop can spin. Mitigate: relax the band if not found
  (e.g. accept the highest structure present ≤0.25), or error with a clear message. Since you only
  need **one** such point, it is cheap unless the DB truly lacks the band.
- **`≤` vs `<` at the boundary.** "Around 0.25±0.01" → band `[0.24, 0.26]`; use `<= 0.26` and
  `>= 0.24`. Because the pool is capped at 0.25, the effective band is really `[0.24, 0.25]` — you
  cannot exceed 0.25, so "worst ≈ 0.25" means "as close to 0.25 as the DB's band provides, within
  [0.24, 0.25]".
- **Determinism/RNG.** Seeding one point changes the draw; if you want reproducibility, keep the
  same `--rng` and draw the band point first so the subsequent draws are unaffected.

**Net effect.** This is a small, additive change to `initialize()`: seed one live point in the
0.24–0.25 band (so the worst is pinned there) and cap the pool at 0.25 — all other structures,
including everything below, are kept and span the live set. It directly answers "I don't want to
start from 0.1; I want the worst ≈ 0.25±0.01," with nothing discarded and no rejection over the
whole set.


**Caveat on "exactly 0.25".** Because the draw is uniform over a *discrete* DB, the worst live
point is pinned to the *highest structure actually present at or below 0.25* — which is typically
≈0.25 but not guaranteed to be exactly 0.25 (unless the DB has a structure at precisely that
energy). If you specifically need the worst to sit at the *top of the pool*, the cleanest is to
seed one initial live point at the highest-energy structure in the filtered pool — but for most
purposes `--e-max-per-atom 0.25` gives "start at ~0.25, keep everything below" without any
discarding. (This is the "cleaner alternative" from the previous note; your requirement is exactly
what it delivers.)



**Important nuance about what "starting from 0.25 eV/atom" means in NS.** Nested sampling does
not need you to set the *start* — it **automatically starts at the top of whatever window you
give it** (the highest-energy structure in the prior pool) and descends to the bottom. So:
- If you only set the **upper** bound to 0.25 eV/atom (via `--e-max-per-atom 0.25`), NS starts
  near 0.25 and automatically descends toward 0 (the global minimum). That matches "sample
  starting from 0.25 eV/atom above the minimum and go down."
- If you also want to **stop at 0.25** (i.e. only sample the window *above* 0.25, excluding the
  ground state), you would need a **lower** bound flag (`--e-min-per-atom`), which does not exist
  yet.

**Practical note on your "already normalized per atom, 0 eV/atom at the minimum" description.**
The code works in **absolute eV**, not eV/atom. `E_ref = db_energies.min()` is the minimum
*absolute* energy (≈ −437 eV), and the relative quantity is `(E − E_ref)`, which in *per-atom*
form is `(E − E_ref)/N`. The `--e-max-per-atom` threshold already uses exactly this per-atom
relative form. So "0.25 eV/atom above the global minimum" maps directly to
`--e-max-per-atom 0.25` for the upper bound, and a hypothetical `--e-min-per-atom 0.25` for the
lower bound.


**3. What would happen if I set `max_E` to 0.25 eV/atom above the lowest energy?**
It would be a **serious bug**, because `max_E` in the Python code is an **absolute energy in eV**,
NOT a relative "eV/atom above the minimum". It appears in `_filter_unphysical(max_E=1e4)` and in
the `abs(E) < 1e4` / `|E| > 1e4` checks. The system's absolute energies are ≈ −437 eV (very
negative), so every structure has `|E| ≈ 437`, which is far above 0.25. Setting `max_E = 0.25`
would make `abs(E) < 0.25` **false for every real structure**, so the sampler would reject/replace
*everything* as "unphysical" and the run would fail or produce nothing. The relative "eV/atom
above the minimum" filter you are thinking of is a **different mechanism**: the `--e-max-per-atom`
CLI flag (in `main.py`), which drops DB structures with `(E/atom − min E/atom) > value` *before*
training, using a relative threshold — not the internal `max_E`. And the **variable name for the
lowest energy** is **`E_ref`** (`self.E_ref = db_energies.min()`, line 99), i.e. the minimum
training energy. (The per-atom minimum is `db_energies.min()/N`; `--e-max-per-atom` compares
`E/atom − min(E/atom)`.)

**4. `E_ref`, `log_L_boundary`, `E_boundary` — what they are, how computed, how used.**
- **`E_ref`** (line 99): `self.E_ref = db_energies.min()` — the lowest energy in the training set
  (a scalar, eV). It is the **energy origin**: the likelihood is written relative to it,
  `log L = −(E − E_ref)` (temperature-free), so the best structure has `E − E_ref = 0`. It is
  computed once from the dataset and never changes.
- **`log_L_boundary`** (init `−np.inf` line 119; set to `live_log_L.min()` at line 183 and 265):
  the current **log-likelihood cutoff** = the `log L` of the current worst live point. It is the
  threshold that `sample_constrained()` requires new draws to beat (`ll > log_L_boundary`). It is
  recomputed every iteration as the worst point is replaced.
- **`E_boundary`** (derived, printed line 185): the **energy** cutoff that `log_L_boundary`
  corresponds to. In temperature-free mode, `log L = −(E − E_ref)`, so
  `log_L_boundary = −(E_boundary − E_ref)` ⇒ **`E_boundary = E_ref − log_L_boundary`**. It is not
  stored as a separate variable — it is the energy implied by `log_L_boundary`; the code prints it
  at line 185 as `E_ref - log_L_boundary`. You read `E < E_boundary` as "new samples must be lower
  in energy than the current cutoff."

**5. Does the Fortran also re-compute the cutoff from the live set each step?**
**Yes — exactly.** In the Fortran main loop, `dead_E(iter) = walkers_E(idx_worst)` (line 82) is the
current worst walker's energy, and it is passed as `E_max_local` to `constrained_walk` (line 91)
to constrain the new sample. Because `idx_worst` is re-found each iteration
(`maxloc(walkers_E)`), the Fortran cutoff is **re-computed from the worst live walker every step**,
just like Python's `log_L_boundary = live_log_L.min()`. This corrects the earlier wording in this
section, which implied Fortran used only a fixed `E_max`: the fixed `E_max` is used **only for the
initial walkers**; the in-loop cutoff is the dynamic worst-walker energy in both codes.


**How the Python loop "lowers the energy window" — the running `E_boundary`.** As clarified
above (Q2/Q5), the Fortran's *energy* cutoff is also dynamic (`dead_E(iter)` = worst-walker
energy, line 82), and `X_i = (K/(K+1))^i` is only the prior-*volume* weight, not the cutoff. The
Python code does the same descending idea: it keeps the energy cutoff at the current worst live
point and re-computes it every iteration. There is no fixed upper value in the loop; the cutoff is
re-derived from the live set each step. Concretely:

**Initialize (`initialize()`, lines 162–185).**
- Draw `K = n_live` structures from the prior (`sample_from_prior()`: random DB structure +
  perturb). These are the "live" points — the current window occupants.
- Remove unphysical ones (`_filter_unphysical`, `|E| > 1e4`).
- Set the first cutoff to the *worst* live point:
  `log_L_boundary = live_log_L.min()` (line 183). In temperature-free mode this corresponds to an
  energy `E_boundary = E_ref − log_L_boundary` (printed line 185) — this is the "E_max" of the
  current window.

**Iterate (`run()` → `step()`, lines 271–267), repeated `n_iterations` times:**
1. **Find the worst** live point: `worst_idx = argmin(live_log_L)` (line 226) — the highest-energy
   one in temperature-free mode. This is the Fortran `idx_worst = maxloc(walkers_E)`.
2. **Record the shell weight** `ΔX = X_{i−1} − X_i = exp(−i/K) − exp(−(i+1)/K)` (lines 232–234),
   and save the discarded sample with that weight (lines 246–254) — the Fortran `dead_X`/
   `dead_E`.
3. **Replace** the worst point with a new structure that must be *better* than the cutoff:
   `sample_constrained()` (lines 207–220) draws from the prior until
   `log L > log_L_boundary` and `|E| < 1e4` (i.e. `E < E_boundary`), up to 500 attempts; if it
   fails, it falls back to an unconstrained draw (lines 257–259).
4. **Update the cutoff**: `log_L_boundary = live_log_L.min()` (line 265). Because the new point is
   better than the old worst, the *new* worst is at least as good — so the energy window has
   **moved down** (tightened).

So each iteration "lowers the window": the worst surviving energy is removed and replaced by
something lower, so the boundary `E_boundary` creeps downward exactly like the Fortran's in-loop
cutoff `dead_E(iter)` descending — the descent is *data-driven* (wherever the worst live point
currently is) in **both** codes, not a fixed value. (The only thing fixed in the Fortran is
`E_max`, used solely to generate the initial walkers.)

**Example (concrete numbers, temperature-free).** Suppose `E_ref = −437 eV`, and the 50 initial
live points span `−420` to `−430 eV`. Initialize sets `E_boundary ≈ −420` (the worst). Iteration 1:
remove the `−420` structure, draw a new one constrained to `E < −420`; suppose it lands at `−424`.
Now the worst live point is `−421`, so `E_boundary` becomes `−421`. Iteration 2 removes `−421`,
replaces it with something `< −421`, say `−423`; worst is now `−422`, boundary → `−422`. Each step
the window's ceiling drops, so the sampled structures concentrate ever closer to the ground state
`E_ref`. The volume removed each step is `ΔX = exp(−i/50) − exp(−(i+1)/50)` — the same geometric
shrink as Fortran, just expressed via `exp` instead of `(K/(K+1))^i`.

**Analogy (no basis needed).** Imagine a net with 50 holes floating on a lake, and the water level
is the energy cutoff. Both codes first fill the net to a starting level, then proceed the same way
each round: look at the *highest* spot still inside the net, drain the thin slice of water just
below it, drop a new weight that must be below that level, then look at the new highest spot and
repeat. The lake drains toward the bottom, and the level is set each step by "where the worst
remaining sample currently is" — in both Python and Fortran. The only Fortran-specific wrinkle is
that its *starting* fill level is a chosen `E_max` (barrier + margin), used just to seed the
initial walkers. The amount of water each drained step represents (`ΔX`, the prior-volume slice)
is what later gets multiplied into the partition function `Z`.


What the Python code does define, and how:

1. **`E_ref` (line 99) = `db_energies.min()`** — the **lowest** training energy. This is a
   *lower* reference, not an upper bound. It shifts the likelihood so the best structure has
   `E − E_ref = 0` (`log L = −(E − E_ref)` in temperature-free mode).
2. **Implicit upper boundary (the prior).** `sample_from_prior()` (line 123) draws a random DB
   structure and adds a Gaussian perturb to the Fe atoms. Its energy is whatever that structure
   has — the highest-energy DB structure effectively caps the window. No `E_max` is chosen.
3. **Dynamic cutoff `log_L_boundary` (line 119, set at 183/265).** After the initial live set,
   `log_L_boundary = live_log_L.min()`, i.e. the cutoff sits at the current worst live point. In
   temperature-free mode `log L > log_L_boundary` ⟺ `E < E_ref − log_L_boundary`, so the
   *energy* cutoff `E_boundary` is `E_ref − log_L_boundary` (printed at line 185). It **moves
   down** every iteration as the worst point is removed — it is a running energy limit, not a
   fixed `E_max`.
4. **Physical sanity filter `1e4` eV (lines 147, 218, 187).** `|E| > 1e4` is treated as an
   unphysical GPR extrapolation and rejected/replaced. This is *not* the Fortran's `E_max`; it is
   just a guard against bad surrogate predictions.

**Consequence vs the Fortran design.** Because the Python prior window is set by the DB's own
energy range (not a deliberate "past-the-barrier" margin), whether the Python run connects the
flat and island basins depends on whether the DB already contains structures across that
barrier. That is the same trade-off raised in the earlier note ("is it better to choose a
higher-energy prior, 0.25 eV/atom above the global minimum?") — the Python code does not enforce
it; you would influence it by what structures are in the database or by `--e-max-per-atom`.

**Example (no basis needed).** Think of nested sampling as slowly draining a tank of water and
recording the level after each bucket is removed. Fortran sets the *starting* water level at the
top of a window that covers two connected pools (`E_max` past the barrier). Python instead
starts with "however much water the database already contains" — its starting level is set by the
highest-energy structure it happened to collect, with no explicit choice of where the top is.
Both then lower the level bucket by bucket (the running `E_boundary`), but only Fortran has
deliberately chosen the initial window to include both basins.


**How it connects to the README.** Every concept from the README appears verbatim in this toy:
- **Prior volume / shrinkage:** `X_i = (K/(K+1))^i` is the discrete form of the README's
  `X_i = exp(−i/K)`; the per-iteration shell `ΔX = X_{i−1} − X_i` is the prior-volume weight
  `w_i` used in `Z = Σ_i w_i·L_i`.
- **Temperature-free mode:** the sampling never uses `β` — it ranks by energy alone (the
  constraint is `E < E_dead`, i.e. `log L = −(E − E_ref)`), and all thermodynamics is computed
  in post-processing at several T. This is exactly the "Physics of temperature-free mode" above.
- **Density of states `g(E)`:** the final histogram is the README's `g(E) = ΔX/ΔE`, the 
  configurational state density from which `Z(T) = ∫ g(E) e^(−βE) dE` and the flat-vs-island
  probability follow.
- **Convergence:** it runs 3000 iterations and papers-style records `dead_X` down to negligible
  values, matching the "run until `X` is negligible" convergence criterion.

This toy is the pedagogical skeleton of the whole project: solve it, and you have solved the
conceptual structure of the Python pipeline. It is `_tmp/` scratch (gitignored), so it is not
part of the reproducible deliverable — it exists to illustrate the algorithm.

## Usage (GPR accuracy vs energy range)
`gpr_accuracy.py` trains the GPR on the combined 1297-structure dataset and reports
prediction accuracy (MAE, RMSE, R²) as a function of the energy range (energy above
the minimum, eV/atom, binned):
```bash
# in-sample (default): measures training-set fit
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --bin-width 0.1 --output ./gpr_accuracy_out

# K-fold cross-validation (opt-in): out-of-sample generalization estimate
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 5 --bin-width 0.1 --output ./gpr_accuracy_cv_out

# Add the GPR's own predictive uncertainty (posterior std) per energy bin
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --uncertainty --bin-width 0.1 --output ./gpr_accuracy_uncert_out

# Add accuracy (+ uncertainty) vs delta Fe_z (Fe island height), ~0.5 A bins
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --fez --uncertainty --bin-width 0.1 --output ./gpr_accuracy_fez_out

# Rattling-distance sensitivity: how much positional disorder the kernel tolerates
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --rattle --uncertainty --rattle-dist 0.05,0.1,0.2,0.5,1.0 \
    --rattle-symbols Fe --output ./gpr_accuracy_rattle_out
```
Outputs: `gpr_accuracy_by_energy_range*.csv` (per-bin metrics) + matplotlib plot
+ printed table. In CV mode it also writes `cv_fold_summary_<K>folds.csv`
(fold-averaged MAE) and names outputs `..._cv<K>folds.*`.

With `--uncertainty`, additionally writes `uncertainty_by_energy_range.csv`
(per-bin mean GPR predictive std) and adds a `mean_model_std_eV_per_atom` column
to the accuracy CSV + per-bin 1σ model-std error bars on the plot. In in-sample
mode this is the trained model's std on the training set; in CV mode it is the
average std of the held-out predictions pooled across folds.

With `--fez`, additionally reports accuracy (and, with `--uncertainty`,
uncertainty) vs **delta Fe_z** (the Fe island height = max(Fe z) − min(Fe z),
Å), binned ~0.5 Å. Writes `gpr_accuracy_by_fe_z.csv` (+ `uncertainty_by_fe_z.csv`
with `--uncertainty`), a `gpr_accuracy_by_fe_z.png` plot, and a `DISCUSSION.md`
in the output dir. Works in in-sample and CV modes.

With `--rattle`, additionally reports accuracy (and, with `--uncertainty`,
uncertainty) vs **rattling distance** (Gaussian displacement of `--rattle-symbols`
atoms, default Fe). A sample of DB structures is rattled at several amplitudes and
predicted with the GPR. Writes `gpr_accuracy_by_rattle.csv`
(+ `uncertainty_by_rattle.csv` with `--uncertainty`), a
`gpr_accuracy_by_rattle.png` plot, and a `DISCUSSION.md`. In-sample mode only.
Flags: `--rattle-dist` (comma amplitudes, default 0.05,0.1,0.2,0.5,1.0),
`--rattle-symbols` (default Fe), `--rattle-n` (sample size, default 200),
`--rattle-copies` (default 5). Predictions with |E|>1e4 eV (unphysical
extrapolation) are excluded and counted.

With `--e-max-per-atom <eV/atom>`, excludes structures whose **relative energy above
the dataset minimum** exceeds the threshold — i.e. keeps `(E/atom − min E/atom) ≤
value` — **before GPR training AND evaluation** (both CV and in-sample). Use it to
drop high-energy outlier structures that break the GPR fit (e.g. the B-doped dataset
has outliers up to 5.6 eV/atom above the minimum that make the surrogate predict
unphysically); `--e-max-per-atom 0.67` keeps a spread comparable to the working
Fe/MgO set. Default: not set (keep all).

Observed (real output, 5-fold CV): overall MAE=0.0040 RMSE=0.0067 R²=0.998 eV/atom —
error grows toward higher-energy bins (MAE~0.010, R²~0.58 at 0.39–0.48 eV/atom),
i.e. the GPR generalizes worse at the energy extremes. In-sample errors are much
smaller (~0.001 eV/atom) because those are interpolation points.

## Usage (standalone re-analysis of a finished run)
```
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```
The run dir must contain `posterior_structures/posterior_*.xsf` and
`posterior_summary.csv`.

## Job (HPC — nested sampling only)
`j_nestedsampling.sh` runs **nested sampling** on HPC (PJM, 24 cores, `gpaw_env`):
`python ./main.py --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01
--perturb-symbols Fe --output ./ns_output_T300_100_1000_0.01 --rng 42`. It reads
the existing `dataset/seed_*/1_db/db_*.db` (seeds 3–15, already present — no AGOX
search step). Submit with `pjsub j_nestedsampling.sh`. The optional AGOX search
step (`dataset/main.py`, all seeds 3..104) can be added back — see TUTORIAL.
For literature-scale settings and the paper-derived parameter table, see
`TUTORIAL.md` ("Literature-scale NS parameters").

## Options
- `--temp`      temperature (K), default 300 (fixed-T mode only)
- `--temperature-free`  temperature-free NS: beta kept OUT of the likelihood
  (energy-constrained top-down pass); evaluates Z/F/posterior at `--temperatures`
- `--temperatures`  comma-separated T (K) for temperature-free post-processing
  (default 100,200,300,500,1000)
- `--n-live`    number of live points, default 50
- `--n-iters`   nested-sampling iterations, default 300
- `--perturb`   perturbation amplitude (Å) for prior sampling, default 0.01
- `--perturb-symbols`  symbols of the atoms to perturb (default `Fe`, the
  deposition layer); **comma-separated for multiple**, e.g. `Fe,B` or `Fe, B` —
  all matching atoms move, all others stay fixed during prior sampling
- `--e-max-per-atom`  exclude structures whose RELATIVE energy above the dataset
  minimum exceeds this threshold (eV/atom); applies to the dataset used for nested
  sampling, the GPR training data, and the initial sampler structures (filtered once
  after loading). Use to drop high-energy outliers that break the GPR fit
  (e.g. `0.67`); default not set = keep all
- `--output`    output directory, default `./ns_output_allseeds`
- `--rng`       RNG seed, default 42
- `--analysis-dir`  directory for analysis outputs (default `<--output>/analysis`)
- `--no-analysis`   skip the automatic analysis after sampling
- `--analyze-only <RUN_OUTPUT_DIR>`  re-run analysis on a saved run (see above)

## Outputs (written to `--output`)
- `evidence_history.csv`  — iteration, evidence Z
- `log_evidence.csv`      — iteration, log Z (malformed layout; see TUTORIAL)
- `final_live_energies.csv` — live-point energies at termination
- `posterior_summary.csv` — rank, energy_eV, weight, log_weight (all posterior samples)
- `posterior_structures/posterior_*.xsf` — all posterior structures (rank-ordered)

## Analysis outputs (written to `<--output>/analysis/`)
- `training/conf_space.png` + `training/binding_probability_vs_temperature.png`
- `posterior/conf_space.png` + `posterior/binding_probability_vs_temperature.png`
- `comparison_state_density.png` — overlaid training-vs-posterior KDE state density

## Key decisions & tradeoffs
| Decision | Choice | Tradeoff |
|---|---|---|
| GPR `use_ray` | `False` | Single-process hyperparameter opt → no Ray actors (no `ActorUnavailableError` under RAM pressure), but slightly slower training |
| Prior perturbation | small (`--perturb 0.01`), Fe-only | Large `--perturb` makes the Fingerprint GPR extrapolate to unphysical energies; Fe-only keeps substrate fixed |
| Temperature in likelihood | `--temp` in `L(x)=exp(-β·(E−E_ref))` | Single-temperature NS (vs. papers that keep β out of sampling); see TUTORIAL discussion |
| Live set / iterations | `--n-live 50 --n-iters 300` defaults | Literature scale is K=500–5000, iters 10^5–10^7 (see TUTORIAL) |

## Concepts & physics

### What are the posterior structures?
The posterior structures are the **discarded (worst-live) samples** collected during
nested sampling, each with a weight. Nested sampling removes the lowest-likelihood
live point every iteration and saves it; these saved points, weighted by their
prior-volume share `w_i = Γ(E_{i-1})−Γ(E_i)`, form the weighted posterior set.
`posterior_structures/posterior_*.xsf` are these structures (rank-ordered by weight).
They represent the *thermodynamically weighted* ensemble of structures at the run's
temperature — the physically meaningful output, not just the single global minimum.

### `n_live`, `beta`, `temperature` — what they are and do
- **`n_live` (K, live points)** — the core algorithm parameter. Nested sampling keeps a
  fixed set of K live points; each iteration removes the worst and draws a new one
  constrained to higher likelihood. More live points → finer evidence resolution
  (error ∝ 1/√K) but more evaluations. We use `--n-live 50` (literature uses 500–5000).
- **`temperature` / `beta`** — the thermodynamic settings. `beta = 1/(k_B·T)`
  (k_B = 8.617e-5 eV/K) enters the likelihood `L(x)=exp(-beta·(E(x)−E_ref))`.
  `temperature` is the physical knob (Kelvin); `beta` is what appears in the math.
  - T = 300 K → beta ≈ 38.68 eV⁻¹. Each eV above the best structure costs a factor
    `exp(-38.68) ≈ 10⁻¹⁷` in likelihood — low-energy structures are overwhelmingly
    preferred.
  - Lower T (higher beta) = sharper focus on the global minimum; higher T = flatter
    likelihood, more exploration of higher-energy structures.
  - This is the canonical statistical-mechanics identification: the normalization of
    `L(x)` is the partition function `Z = ∫ exp(-beta·E) dx`, so `beta` sets the
    temperature of the thermodynamic average.

### What is "final evidence"? Why `Z`, why `log Z`?
- **`Z` = the evidence / marginal likelihood / partition function.** It is the
  normalization constant of the posterior, `Z = ∫ L(x)·π(x) dx`, computed after all NS
  iterations (plus the final live-point correction). In statistical mechanics it is
  exactly the canonical partition function, so from it you get the free energy
  `F = −k_B T ln Z` and all thermodynamic averages. It is the central quantity NS is
  designed to compute.
- **Why `log Z`:** the energies are ~−400 eV and `beta ~ 40 eV⁻¹`, so likelihoods span
  hundreds of orders of magnitude. `Z` grows from ~`10⁻²⁴²` early to ~`10⁻⁴` at the
  end — a linear `Z` under/overflows float64. NS accumulates evidence multiplicatively
  (in log space with `np.logaddexp`), so `log Z` is the robust, stable number.

### What does "feature dim 720" mean?
The `Fingerprint` descriptor (oganov atom-centered symmetry functions from
`dataset/main.py`) converts each 75-atom Fe/MgO structure into a fixed 720-number
vector, which the GPR uses as the feature space. Verified breakdown for 3 species
(Fe, Mg, O):
- **2-body / radial — 180 values:** 6 distinct atom-pair bond types (3 same-species
  + 3 cross) × 30 radial bins (`ceil(rc1/binwidth) = ceil(6/0.2) = 30`). 6×30 = 180.
- **3-body / angular — 540 values:** 18 triple types × 30 angular bins. 18×30 = 540.
- **Total = 180 + 540 = 720.** Fixed regardless of geometry for any Fe/MgO structure,
  which is what lets the GPR treat structures as points in a 720-D space and measure
  similarity via the kernel.

## Operational notes

### State-density / landscape analysis
After sampling, `main.py` automatically runs a state-density analysis
(`nested_sampling/state_density.py`, modeled on `_run/9_novelFilter/`). For each of
`training/` and `posterior/` it produces a PCA-landscape + KDE state-density panel
(`conf_space.png`) and a Boltzmann probability vs temperature plot
(`binding_probability_vs_temperature.png`), plus a `comparison_state_density.png`
overlay. Re-runnable standalone via `--analyze-only <RUN_OUTPUT_DIR>`.

### Ray `ActorUnavailableError` (fixed with `use_ray=False`)
`GPR(...)` defaults to `use_ray=True`, which spawns one Ray actor per CPU for parallel
hyperparameter optimization. Under high RAM pressure (concurrent jobs, Obsidian,
IDE/LSP, gateways), Ray kills an actor → `ActorUnavailableError` at the first GPR
step. This is environmental, not a code bug. Fix: `use_ray=False` in `build_gpr`
(runs single-process hyperparameter optimization, no Ray pool, `ActorUnavailableError`
structurally impossible). Cost: slightly slower training (~2 min → a few minutes).
The safe `--perturb 0.01` default is unrelated but important — large perturb makes
the Fingerprint GPR extrapolate to unphysical energies.

### Literature scale & heavy-run guidance
| Parameter | Pártay 2021 (bulk) | Yang 2024 (surfaces) | Chatbipho 2025 (nanocluster) | This project |
|---|---|---|---|---|
| Live set K | 500–5000 | 80/free particle | extends Yang to LJ38 | 50 (default) / 100 (job) |
| Walk length L | 100s–1000s | ~250 iter/walker | same scheme | no explicit L |
| System N | 32–256 atoms | ≤16 free particles | LJ38 | 75 atoms (Fe25Mg25O25) |
| Iterations | 10⁵–10⁷ | 320 000 | comparable | 300 (default) / 1000 (job) |
| Temperature β | post-process only | post-process only | post-process only | **in the likelihood** (`--temp`) |

Literature-informed heavy run (`--n-live 500 --n-iters 5000`) and the temperature scan
are documented in `TUTORIAL.md` ("Literature-scale NS parameters"). Note the modelling
gap to the papers: our prior is DB-resample + small perturb (no clone-and-MC
decorrelation walk length L), and we put β in the likelihood (single-temperature NS)
rather than applying it only in post-processing.

## Layout
```
b_nestedsampling/
├── main.py                  # entry point (root runner; renamed from run_nested_sampling.py)
├── nested_sampling/         # package: NestedSampler, train_gpr, state_density, utils
├── scripts/                 # clean slab/generator builders used by dataset/main.py
├── dataset/                 # AGOX seed DBs (seed_3..15, stop_16) + dataset/main.py + scripts
├── j_nestedsampling.sh      # PJM batch script (HPC)
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md / PROMPTS.md
├── _runs/                   # (scaffolded) self-contained run dirs
├── _analysist/              # (scaffolded) analysis outputs
├── _archives/               # (scaffolded) archived artifacts
└── _tmp/                    # (scaffolded) scratch output
```
See `README.AI.md` for the machine-readable spec and `TUTORIAL.md` for
step-by-step reproduction.
