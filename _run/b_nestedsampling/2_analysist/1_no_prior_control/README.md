# Nested Sampling on the combined multi-seed Fe/MgO AGOX dataset

Run script: `run_nested_sampling.py`

## What it does
1. Loads **every** structure from **every** seed database in
   `dataset/seed_*/1_db/db_*.db` (seeds 3–15, 1297 structures total, all
   Mg25O25Fe25 / 75 atoms).
2. Trains a single AGOX GPR surrogate on the combined 1297 structures (AGOX
   kernel recipe from `dataset/main.py`).
3. Runs the `NestedSampler` from the `nested_sampling` package on the combined
   dataset (log-space evidence accumulation, `log L = -beta*(E - E_ref)`).
4. Runs a **state-density / landscape analysis** of the results (PCA landscape +
   KDE state density + Boltzmann probability vs temperature), comparing the
   posterior samples against the training set.

## Environment
Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```

## Usage (full run + automatic analysis)
```
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```
After sampling, the analysis writes to `<--output>/analysis/` automatically.

## Usage (standalone re-analysis of a finished run)
Re-run the state-density analysis on an already-completed run's output dir, without
re-loading data or re-training the GPR:
```
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```
The run dir must contain `posterior_structures/posterior_*.xsf` and
`posterior_summary.csv` (both written by the current sampler `save()`).

## Options
- `--temp`      temperature (K), default 300
- `--n-live`    number of live points, default 50
- `--n-iters`   nested-sampling iterations, default 300
- `--perturb`   perturbation amplitude (Å) for prior sampling, default 0.01
- `--perturb-symbols`  symbols of the atoms to perturb (default `Fe`, the deposition
  layer); all other atoms stay fixed during prior sampling
- `--output`    output directory, default `./ns_output_allseeds`
- `--rng`       RNG seed, default 42
- `--analysis-dir`  directory for analysis outputs (default `<--output>/analysis`)
- `--no-analysis`   skip the automatic analysis after sampling
- `--analyze-only <RUN_OUTPUT_DIR>`  re-run analysis on a saved run (see above)

## Outputs (written to `--output`)
- `evidence_history.csv`  — iteration, evidence Z
- `log_evidence.csv`      — iteration, log Z
- `final_live_energies.csv` — live-point energies at termination
- `posterior_summary.csv` — rank, energy_eV, weight, log_weight (all posterior samples)
- `posterior_structures/posterior_*.xsf` — all posterior structures (rank-ordered)

## Analysis outputs (written to `<--output>/analysis/`)
- `training/conf_space.png` + `training/binding_probability_vs_temperature.png`
  — landscape + Boltzmann probability for the 1297-structure training set
- `posterior/conf_space.png` + `posterior/binding_probability_vs_temperature.png`
  — landscape + Boltzmann probability for the sampled posterior
- `comparison_state_density.png` — overlaid training-vs-posterior KDE state density

# Complete nested-sampling algorithm

This section documents the exact algorithm implemented in
`nested_sampling/nested_sampler.py` (`NestedSampler`), as used by
`run_nested_sampling.py`. It is a **log-space** Skilling nested sampler whose
likelihood comes from the GPR energy surrogate. References are to source
`nested_sampler.py:LINE`.

## 0. Setup and constants

- Temperature `T` (K), `--temp`, default 300. Boltzmann constant
  `K_B = 8.617333262e-5 eV/K` (`utils.py:7`).
- Inverse temperature `beta = 1/(K_B*T)` (`run_nested_sampling.py:189`; inside the
  sampler `nested_sampler.py:42` when not passed explicitly).
- Live points `n_live`, default 50; iterations `n_iterations`, default 300.
- Perturbation amplitude `perturb` (Å), default 0.01; perturbed species
  `perturb_symbols = "Fe"`.

**Energy reference.** `E_ref = min(db_energies)`, the minimum DFT energy across
the whole combined training set (`nested_sampler.py:61`). Every energy is
measured relative to this reference.

**Perturbation mask.** From the first structure (dataset has uniform
composition), the atom indices to be perturbed are fixed once:
`perturb_indices = {i : symbol_i in {perturb_symbols}}` (`nested_sampler.py:50-58`).
Only these atoms (the Fe deposition layer) move; the substrate is frozen.

## 1. Likelihood model

The surrogate predicts an energy `E(x)` for structure `x` via the trained GPR.
The (log) likelihood is a canonical ensemble weight shifted so that the best
training structure has likelihood O(1) (`nested_sampler.py:98-110`):

```
log L(x) = -beta * (E(x) - E_ref)          # nested_sampler.py:98-103
L(x)     = exp(log L(x))                   # underflow-protected below log L < -700
```

Unphysical surrogate predictions are rejected: if `|E(x)| > 1e4` eV the
likelihood is set to `-inf` (`nested_sampler.py:101-102`).

## 2. Prior

The prior is the **empirical database distribution** plus Gaussian jitter on the
deposition layer (`sample_from_prior`, `nested_sampler.py:81-94`):

1. Uniformly pick an index `idx` in `[0, len(db_structures))`.
2. Copy that structure as the base.
3. If `perturb > 0`, add i.i.d. noise
   `positions[perturb_indices] += Normal(0, perturb)^(3)`
   to the Fe atoms only. All other atoms keep their database positions.

The prior is thus supported on `db_structures` with local Gaussian spread over
the Fe layer — it does not sample arbitrary atomic configurations.

## 3. Initialisation

`initialize()` (`nested_sampler.py:114-137`) draws `n_live` live points i.i.d.
from the prior, computing for each: energy `E`, `log L`. Then
`_filter_unphysical` (`nested_sampler.py:139-155`) replaces any live point with
`|E| >= 1e4` by re-drawing from the prior (up to 100 attempts) until a physical
one is found.

The likelihood boundary is initialised to the worst (smallest) live
log-likelihood:
```
log_L_boundary = min(live_log_L)            # nested_sampler.py:135
```

## 4. Main iteration

Each `step()` (`nested_sampler.py:170-208`) performs one nested-sampling
iteration `i = 0, 1, ..., n_iterations - 1`:

1. **Remove the worst live point.** Let
   `worst_idx = argmin(live_log_L)` and `log_L_min = live_log_L[worst_idx]`
   (`nested_sampler.py:172-173`).

2. **Prior-volume shrinkage.** The enclosing prior volume shrinks geometrically
   by the factor `exp(-1/n_live)` per iteration:
   ```
   X_prev  = exp(-i / n_live)               # nested_sampler.py:177
   X_this  = exp(-(i+1) / n_live)           # nested_sampler.py:178
   delta_X = X_prev - X_this                # nested_sampler.py:179
   ```

3. **Evidence accumulation (log-space).** The contribution of the removed point
   is `L_min * delta_X`. Evidence is updated by a log-sum-exp:
   ```
   term = exp(log_L_min) * delta_X          # nested_sampler.py:183
   log_Z = logaddexp(log_Z, log(term))      # nested_sampler.py:184-187
   Z_history.append(exp(log_Z))             # nested_sampler.py:189
   ```
   (`log Z` starts at `-inf` and is the numerically stable accumulator.)

4. **Record the posterior sample.** The removed structure becomes a posterior
   sample with log-weight `log_L_min + log(delta_X)` (`nested_sampler.py:191-195`).

5. **Replace the worst point** by a new draw from the prior constrained to
   `log L > log_L_boundary` (`sample_constrained`, `nested_sampler.py:159-166`):
   repeatedly draw from the prior until `log L(s) > log_L_boundary` AND
   `|E(s)| < 1e4`, at most `n_attempts = 500` attempts. If none found, fall back
   to an unconstrained prior draw (`nested_sampler.py:199-200`).

6. **Refresh the boundary.** `log_L_boundary = min(live_log_L)` and
   `iteration += 1` (`nested_sampler.py:206-207`).

## 5. Final correction and posterior

At the end of `run()` (`nested_sampler.py:212-267`) the remaining live points
are added back with the mean live likelihood over the final shell:
```
X_final  = exp(-n_iterations / n_live)          # nested_sampler.py:235
log_L_avg = mean(live_log_L)                    # nested_sampler.py:236
term_final = exp(log_L_avg) * X_final           # nested_sampler.py:237
log_Z = logaddexp(log_Z, log(term_final))       # nested_sampler.py:239
```
Posterior weights are normalised in log space (subtract `log Z`, computed via a
max-shifted softmax for stability) (`nested_sampler.py:246-251`).

## 6. What gets saved

`save()` (`nested_sampler.py:271-307`) writes to `--output`:
- `evidence_history.csv` — iteration, evidence Z (per-iteration, correct).
- `log_evidence.csv` — iteration, log Z (**note:** written as two transposed
  long rows by `save()`; the per-row `evidence_history.csv` is authoritative).
- `final_live_energies.csv` — live-point energies at termination.
- `posterior_summary.csv` + `posterior_structures/posterior_*.xsf` — posterior
  samples (physical only, sorted by weight, with weight & GPR energy in the
  filename).

## Algorithm summary (pseudocode)

```
beta = 1/(K_B*T); E_ref = min(db_energies)
perturb_indices = indices of atoms in {perturb_symbols}
log_Z = -inf
# initialise
for k in 1..n_live:
    x = sample_from_prior()            # db structure + Fe-only Gaussian jitter
    (live_structures[k], live_log_L[k]) = (x, log L(x))
filter_unphysical(live)                # redraw any |E|>=1e4
log_L_boundary = min(live_log_L)

for i in 0..n_iterations-1:
    worst = argmin(live_log_L); Lmin = live_log_L[worst]
    X_prev = exp(-i/n_live); X_this = exp(-(i+1)/n_live); dX = X_prev - X_this
    log_Z = logaddexp(log_Z, log(Lmin*dX))
    posterior.append(live[worst]); weight = log(Lmin) + log(dX)
    x_new = sample_constrained(log_L_boundary)  # log L(x) > boundary, |E|<1e4, <=500 tries
    if x_new is None: x_new = sample_from_prior()
    live[worst] = (x_new, log L(x_new))
    log_L_boundary = min(live_log_L)

# final shell
log_Z = logaddexp(log_Z, log(exp(mean(live_log_L)) * exp(-n_iterations/n_live)))
normalise posterior weights (subtract log Z)
save outputs
```

## Key design choices

- **Log-space evidence** avoids underflow (evidence starts ~10^-200 and grows to
  ~10^-4; only `log Z` is robust).
- **Empirical-DB prior + Fe-only jitter** keeps the MgO substrate frozen and
  restricts sampling to the physical deposition layer, per the run setup.
- **Energy shift `E_ref`** keeps `L` O(1) at the best structures so `beta` is not
  astronomically large.
- **Unphysical GPR filtering** (`|E| >= 1e4`) guards against surrogate blow-ups.
- **Convergence check:** live energies converge toward `E_ref` as iterations
  progress (`E_live_max -> E_ref`).


# Prompt

In my case, we want to calculate for the partition function, comparing flat and island state using this nested sampling code. In the dataset provided, we have a collection of configurations for both flat and island states, but for the flat, we have two kinds, the high energy flat and the lower energy flat. In the nesting sampling we have to decide the initial structure (e.g., the --n-live) to start from the high energy flat or the low energy flat. How can we decide which one should be the --n-live starting point? Use the llm wiki, wiki-research and the raw/papers for nesting sampling that is provided. Write the result in a new section in this note. Clarify for each step. 

# Answer: how to choose the "starting point" for a flat-vs-island partition function

## 0. The key correction first

`--n-live` is **not** a starting structure. It is the **number of live points `K`** —
the resolution of the phase-space-volume estimate (statistical error in `ln Γ`
scales as `1/√K`). Nothing in the code ever "starts from" a high- or low-energy
flat structure via `--n-live`.

What actually controls the *starting* behaviour is the **prior distribution** —
the pool of `db_structures` that `sample_from_prior()` draws from
(`nested_sampler.py:81-94`) — and hence the **initial live set** drawn i.i.d.
from that prior in `initialize()` (`nested_sampler.py:114-137`).

So the real question is not "high-flat or low-flat for `--n-live`?" but "**what
should the prior contain so the evidence integral is unbiased?**" The answer,
from Skilling's nested sampling and its materials adaptation (Pártay 2021, Yang
2024; wiki [[nested-sampling]]): **the prior must cover the full configuration
space (island + high-flat + low-flat together), and the initial live points must
be a random draw from that full prior — not biased toward any one basin.**

Grounding: wiki [[nested-sampling]] states the initial live set is "K uniformly
distributed random configurations (the live set / walkers), representing
high-energy gas-like configurations" — i.e. a spread over the whole prior, not a
seeded minimum.

## 1. Step-by-step clarification

### Step 1 — Understand what NS actually computes

Nested sampling evaluates the evidence integral

```
Z(β) = ∫ L(x) π(x) dx,   with  log L(x) = -β (E(x) - E_ref)
```

(`nested_sampler.py:98-103`). For the partition function this is the weighted
sum over *all* configurations: `Z ≈ Σ_i w_i exp(-β E_i)` (wiki
[[nested-sampling]], [[partition-function-sampling]]). The weights `w_i` are the
phase-space volume slices `Γ(E_{i-1}) - Γ(E_i)`, which NS obtains by contracting
the prior volume. **Every configuration that should contribute must be reachable
from the prior**, or its weight is silently zero.

### Step 2 — The prior must contain island + high-flat + low-flat

Because the likelihood weights each structure by `exp(-β(E - E_ref))`, the
*energetic* separation between high-flat, low-flat, and island is handled by β —
**not** by which structure you seed. But NS can only assign weight to structures
the prior can generate. If you seed the prior with *only* low-flat, the sampler
can never discover the island or high-flat basins, and `Z` is wrong (a biased
prior, not a thermodynamic partition function).

For this code, `sample_from_prior()` picks uniformly from `db_structures`
(`nested_sampler.py:88`) then adds Fe-only Gaussian jitter
(`nested_sampler.py:90-93`). Therefore:
- The **DB composition decides the prior support**. To compare flat vs island you
  must train/collect a DB that contains **all three populations** — island,
  high-flat, and low-flat — and let `sample_from_prior` draw from that full set.
- Do **not** filter the DB to one flat variant before running NS. That would bias
  the prior and corrupt `Z`.

### Step 3 — The initial live set is a random draw, not a "chosen" structure

`initialize()` draws `K = n_live` structures i.i.d. from `sample_from_prior()`
(`nested_sampler.py:117-124`). By construction the starting ensemble is a *mix*
of island and both flat variants, in proportion to the DB composition — which is
exactly what an unbiased prior requires. You should **not** try to force the
initial live points into high-flat or low-flat; doing so violates the i.i.d.-over-
the-prior assumption and biases `Γ(E)` and hence `log Z`.

### Step 4 — How high-vs-low flat is resolved

Within a correct run, both flat populations are present in the posterior with
weights `exp(-β(E_i - E_ref))`. At a given `T`:
- low-energy flat: larger Boltzmann weight;
- high-energy flat: exponentially smaller weight.

The *relative* contribution is a physical result of the temperature, not an input
you choose up front. To study it, run NS once and post-process
`Z(β)` / `⟨E⟩(β)` / heat capacity across `T` from the same sample set — the
temperature-independence of the sampling is the whole point of NS (Pártay 2021;
wiki [[nested-sampling]]). Note the present implementation puts `β` inside the
likelihood (fixed-temperature sampling); the literature removes `β` from the walk
and reweights in post-processing (see §5, gap 2).

### Step 5 — How flat-vs-island are compared

Do **one** global run whose prior contains all modes, then:
1. Keep every posterior sample (the code already writes *all* posterior XSFs +
   `posterior_summary.csv`, `nested_sampler.py:283-302`).
2. Classify each sample as island / high-flat / low-flat by a structural order
   parameter — e.g. interfacial height variation `Δz` (island `Δz ≈ 2.5–5.0 Å`,
   flat much smaller; wiki [[state-density-g-e]]), or the PCA/landscape projection
   already used in the analysis step.
3. Sum the posterior weights per class to get `Z_island(β)`, `Z_flat(β)`, and the
   relative probability `p_mode = Z_mode / Z_total`.

This is the surface-phase-diagram strategy of Yang 2024: one temperature-
independent sample, then per-phase partition functions and free energies
`F_mode = -k_B T ln Z_mode`.

### Step 6 — Practical decisions (what you actually choose)

| You control | How | Guidance |
|---|---|---|
| Prior support | Which structures are in `db_structures` (`sample_from_prior`, `nested_sampler.py:88`) | Include island + high-flat + low-flat. Check composition uniformity first (all Mg25O25Fe25). |
| `--n-live` (K) | Live-point count | Resolution knob, error ∝ 1/√K; prefer `K ≈ 500–2000` per the literature to avoid basin extinction, not 50. |
| `--n-iters` | Iteration count | Set by how deep you must resolve (scales ~linearly with K). |
| `--temp` / β | Likelihood steepness | Decides the flat-vs-island balance *physically*; scan T to read `Z(β)` vs temperature. |
| `--perturb` / `--perturb-symbols` | Prior spread | Keep Fe-only, small (0.01 Å) so the GPR fingerprint stays in-manifold (see pitfalls in README). |

### Step 7 — Answer to the original question directly

You should **not** decide to start from high-flat *or* low-flat. The starting
ensemble must be an unbiased draw from the full prior containing both flat
variants and the island state. The "which flat dominates" question is answered by
the Boltzmann weight at the target temperature (Step 4), and the flat-vs-island
comparison by classifying posterior samples and summing weights per mode
(Step 5). The only "starting" lever that matters is making sure the **DB/prior
covers all three populations**; `--n-live` then sets how *accurately* the evidence
(and each mode's weight) is resolved.

## 2. Caveats specific to this codebase

- **Empirical-DB prior ≠ full configuration space.** The prior is supported on
  the 1297 DB structures plus Fe-only jitter. If a mode (e.g. high-flat) is
  under-represented or absent in the DB, NS cannot weight it. This is the main
  bias risk for the flat-vs-island comparison — fix it at the prior/DB level, not
  by changing `--n-live`.
- **β is in the likelihood (fixed-T sampling).** The papers leave β out of the
  walk and apply it in post-processing. Here each run gives one temperature's `Z`;
  scan `--temp` for a T-dependence (see multi-seed guide §15, "two gaps").
- **No walk-length L / clone-then-MC-decorrelate.** Each constrained draw is an
  independent DB sample, so basin escape between modes is limited by the DB
  composition and `--perturb`. For a clean flat↔island *transition* this is the
  gap to close (guide §15).
- **Basin extinction.** Even with a full prior, a basin can lose its live points
  once the energy limit cuts it off. Larger `K` and a full-coverage prior mitigate
  this (wiki [[nested-sampling]]).

## 3. References

- Wiki (research): [[nested-sampling]], [[partition-function-sampling]],
  [[state-density-g-e]], [[nested-sampling-validation]] —
  `/home/think/MEGA/Obsidian-Notes/wiki/wiki-research/`.
- Pártay, Csányi & Bernstein, "Nested sampling for materials", Eur. Phys. J. B
  94, 159 (2021) — `raw/papers/nested-sampling/2021partay_nested-sampling.pdf`.
- Yang, Pártay & Wexler, "Surface phase diagrams from nested sampling", PCCP 26,
  13862 (2024) — `raw/papers/nested-sampling/2023yang_nested-sampling.pdf`.
- This implementation: `nested_sampling/nested_sampler.py` (NestedSampler,
  `sample_from_prior`, `initialize`, `run`), run by `run_nested_sampling.py`.

