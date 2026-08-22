# Nested Sampling Run — What I Did

Run directory: `/home/think/Desktop/research/_run/8_nested_sampling/`
Date: 2026-08-20

## Goal
Write code to run nested sampling over the Fe/MgO AGOX dataset, using **all** the
data from the multiple seeds. Train a single GPR surrogate on the combined dataset,
then run the `nested_sampling` package's `NestedSampler` on it.

## Environment
- Conda env: `agox_v2` (AGOX 3.10.2 + ASE 3.25.0)
- Python: `/home/think/miniconda3/envs/agox_v2/bin/python`
- AGOX packages imported from the env; `nested_sampling` imported as a local package.

## Dataset
- Location: `dataset/seed_*/1_db/db_*.db`
- Seeds used: 3 through 15 (13 databases)
- Total structures: **1297**
- Composition: **Mg25O25Fe25** (75 atoms), uniform across every seed
- Energy range: **-436.909 eV .. -386.292 eV**

I verified the composition/atom-count consistency first so a single Fingerprint
descriptor and a single GPR model are valid for the combined set.

## What the code does (`run_nested_sampling.py`)
1. **Load combined dataset** — globs `seed_*/1_db/db_*.db`, restores each DB to a
   trajectory, concatenates all structures and their potential energies.
2. **Train GPR on the combined set** — builds a `Fingerprint` descriptor
   (`Fingerprint.from_atoms`, feature dim 720) and the AGOX kernel recipe from
   `dataset/main.py`:
   ```
   C(5000, (1,1e5)) * ( C(0.01)·RBF() + C(0.99)·RBF() ) + Noise(0.01)
   ```
   with a `Repulsive` prior, then `gpr.train(all_1297_structures)`.
3. **Run nested sampling** — builds `NestedSampler(gpr, structures, energies,
   n_live, beta, temperature, perturb, rng)`:
   - `beta = 1 / (K_B · T)`, log-likelihood `log L = -beta·(E - E_ref)`
   - `initialize()` draws the live points from the empirical DB distribution with
     optional position perturbation
   - `run(n_iterations)` accumulates evidence in log space and outputs posterior stats
   - `save(output)` writes CSVs + top-20 posterior structures.

Notes: 

What is posterior structures? Where do they come from? What do they present? What is the relation with the sampled structure?

Note:
**What are `n_live`, `beta`, `temperature`, and what are they used for?**

These are the three key parameters that control how the nested sampler behaves. They
are passed to `NestedSampler(...)` (and `n_live`/`temperature`/`beta` appear as CLI
options `--n-live`, `--temp`).

**`n_live` (number of live points)** — the core algorithm parameter of nested
sampling (classic "skilling" nested sampling). Nested sampling always maintains a
fixed-size *set of live points*, and `n_live` is how many. The algorithm works like
this:
  1. Draw `n_live` structures from the prior (here: the empirical DB distribution +
     small perturbation).
  2. Each iteration, find the live point with the *worst* (lowest) likelihood,
     remove it, and replace it with a new point drawn from the prior *constrained to
     have higher likelihood* than the removed one.
  3. As the boundary likelihood rises, the sampled prior-*volume* shrinks
     exponentially as `exp(-i/n_live)`.
The size of `n_live` directly controls the *accuracy/resolution* of the evidence
estimate: more live points = finer sampling of the shrinking volume = lower variance
in log Z (and better-resolved posterior), but more evaluations per iteration.
We used `n_live=50`.

**`temperature` / `beta`** — the thermodynamic settings. `beta` is the inverse
temperature, `beta = 1/(k_B·T)` (k_B = 8.617e-5 eV/K). They enter the likelihood:
`L(x) = exp(-beta·(E(x) - E_ref))`. `temperature` is the physically meaningful knob
(Kelvin); `beta` is what actually appears in the math. They are used to set *how
strongly the sampler favors low-energy structures*:
  - `T = 300 K  ->  beta = 38.68 eV^-1`. Each eV of energy above the best
    structure costs a factor `exp(-38.68) ~ 10^-17` in likelihood — low-energy
    structures are overwhelmingly preferred.
  - Lower T (higher beta) = sharper, more "greedy" focusing on the global minimum.
  - Higher T (lower beta) = flatter likelihood = more exploration of higher-energy
    structures.
This is the standard statistical-mechanics identification: the normalization constant
of `L(x)` is the canonical partition function `Z = ∫ exp(-beta·E) dx`, so `beta`
(effectively T) sets the temperature at which we compute the thermodynamic average.

## How I verified it
- Confirmed all 1297 structures share one composition → single descriptor/GPR valid.
- Checked the GPR API: `GPR.train(training_data)` takes a bare list of `Atoms` (the
  `database` kwarg is unused for train/predict), so combining DBs is clean.
- Timed GPR training on the full set: **~134 s**, validation deltas ≈ 0.02–0.10 eV.
- Smoke test (n-live 30, n-iters 20) ran end-to-end successfully.
- Then ran the full production run (see below).

## Full run command
```
cd /home/think/Desktop/research/_run/8_nested_sampling
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```

## Results (verified, written to `ns_output_allseeds/`)
- GPR trained on 1297 structures (~134 s); sample validation deltas ≈ 0.02–0.10 eV.
- Final evidence: **Z = 4.168e-04** (log Z = **-7.783**).
- Posterior: 300/300 physical samples; **E_mean = -432.35 eV, E_std = 6.22,
  E_min = -436.83 eV** (training min E_ref = -436.91 eV).
- Live energies converged toward E_ref as iterations progressed.

Notes:

**What is "Final evidence"? Why use Z? Why use log Z?**

**"Final evidence" = the model evidence `Z`** computed after all nested-sampling
iterations (plus the final live-point correction term added at the end of `run()`).
It is a single number — the value printed as `Z = 4.168e-04 (log Z = -7.783)` in the
run output.

**What is `Z` (the evidence / marginal likelihood / partition function)?**
`Z = ∫ L(x)·π(x) dx` — the integral of the likelihood over the prior. It is the
*normalization constant of the posterior*: `P(x) = L(x)·π(x) / Z`. The name
"evidence" comes from Bayesian model comparison: for two or more candidate models,
`Z = P(data|model)` is the probability the data would have been observed under that
model, so the ratio of evidences (Bayes factor) tells you which model is
preferred. In statistical mechanics it is exactly the **canonical partition
function**, `Z = ∫ exp(-beta·E(x)) dx`, which is what makes it physically meaningful:
from `Z` you get the free energy `F = -k_B·T·ln Z` and hence all thermodynamic
averages. So `Z` is the central quantity nested sampling is designed to compute.

**Why do we use `Z` at all here?** Because we want more than just the lowest-energy
structure — we want the *partition function / free energy* of the Fe/MgO system at a
given temperature, which weights *all* structures by `exp(-beta·E)`. `Z` is also what
lets us convert the discarded (posterior) sample weights into a proper normalized
probability distribution over structures, and what makes runs at different T or on
different datasets comparable.

**Why `log Z` instead of `Z`?** Two reasons, both about keeping numbers
representable:
  1. **Magnitude range.** The energies are ~ −400 eV and `beta ~ 40 eV^-1`, so
     likelihoods `exp(-beta·(E - E_ref))` span *hundreds* of orders of magnitude. Even
     in an easy case, during this run `Z` grew from ~`10^-242` at iteration 20 up to
     `4.2e-04` at the end. A linear `Z` is impossible to store/accumulate without
     going to `0.0` or `inf` (float64 under/overflow).
  2. **Evidence is accumulated multiplicatively by construction.** Nested sampling
     sums `Z += L_min · ΔX` at every step, and each term is tiny. Doing that in log
     space with `np.logaddexp` avoids both underflow (values collapse to 0) and
     overflow (values explode to inf), keeping the running estimate stable.
In short: we use `Z` because it *is* the physically/bayesian-meaningful output, and we
track `log Z` because the magnitudes involved (a product of `exp(-beta·E)` factors)
are so extreme that linear arithmetic would silently overflow or underflow.

Output files:
| File | Contents |
|---|---|
| `evidence_history.csv` | iteration, evidence Z (one row per iteration) |
| `log_evidence.csv` | iteration, log Z (see caveat below) |
| `final_live_energies.csv` | live-point energies at termination (50) |
| `posterior_structures/posterior_000..019_xsf` | top-20 weighted posterior structures |

## Caveat / note
The imported `nested_sampling` package's `save()` writes `log_evidence.csv` in a
malformed layout (iterations and log_Z written as two long transposed rows instead of
one row per iteration). No data is lost — `evidence_history.csv` is correct. This is a
pre-existing bug in `nested_sampling/nested_sampler.py`, not in `run_nested_sampling.py`.

## What does "feature dim 720" mean?
This is the length of the descriptor vector the GPR uses to represent each structure.
It came from `Fingerprint.create_features(atoms).shape[1]` in the code. The AGOX
`Fingerprint` descriptor (the "oganov" atom-centered symmetry-function fingerprint from
`dataset/main.py`) converts a 75-atom Fe/MgO structure into a fixed 720-number vector.

How 720 is built up (verified against the actual descriptor object for the Fe/MgO
structures):

- Species = 3 (Fe, Mg, O). The descriptor has two parts:

  1. **2-body / radial part — 180 values.** The code counts distinct atom-pair
     "bond types". For 3 species, unordered pairs that occur with periodic boundary
     conditions: 3 same-species pairs (Fe–Fe, Mg–Mg, O–O) + 3 cross pairs (Fe–Mg,
     Fe–O, Mg–O) = 6 bond types. Each pair type is binned over radial distance into
     30 bins (`Nbins1 = ceil(rc1/binwidth) = ceil(6/0.2) = 30`). 6 × 30 = 180.

  2. **3-body / angular part — 540 values.** 18 distinct 3-atom "triple" types × 30
     angular bins (`Nbins2 = 30`, from `binwidth2 = π/Nbins2`). 18 × 30 = 540.

- Total = 180 + 540 = **720**.

So "720" means each structure is described by 720 real numbers capturing the
distribution of interatomic distances (radial) and bond angles (angular) around the
atoms — the descriptor's "feature dimension". It is fixed regardless of the exact
geometry (always 720 for any Fe/MgO structure with these default `Fingerprint`
parameters), which is what lets the GPR treat structures as points in a 720-D feature
space and measure similarity between them via the kernel.

---

# Tutorial: how to run the nested sampling script end-to-end

> Level: intermediate (assumes the agox_v2 conda env is already set up and the
> dataset + scripts are in place). You only need the terminal — no IDE required.

## 0. What this script actually does (mental model)

Running `run_nested_sampling.py` does three things in sequence:

1. **Loads the combined dataset** — all structures from every seed DB
   (`dataset/seed_*/1_db/db_*.db`, 1297 structures, Fe25Mg25O25).
2. **Trains one GPR surrogate** on all 1297 structures (AGOX Fingerprint
   descriptor + the standard kernel recipe). This is the expensive prep step
   (~2 min).
3. **Runs nested sampling** with the trained GPR as the energy model. It draws
   live points from the empirical DB distribution (with a small perturbation to
   only the Fe atoms), iteratively shrinks the prior volume toward the
   low-energy region, and accumulates the evidence `Z` in log space.

The output is: the marginal-likelihood evidence `Z` (and log Z), posterior
energy statistics, and a set of top-weighted posterior structures.

## 1. One-line run (the default)

```bash
cd /home/think/Desktop/research/_run/8_nested_sampling
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py
```

Defaults: `--temp 300 --n-live 50 --n-iters 300 --perturb 0.01
--perturb-symbols Fe --output ./ns_output_allseeds --rng 42`.

That runs the full production configuration from this session. Expect ~2 min of
GPR training, then the sampling loop (a few minutes total).

## 2. A quicker smoke test first

Always validate the pipeline on a tiny run before committing to a long one:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 30 --n-iters 20 --perturb 0.01 \
    --output /tmp/ns_smoke --rng 42
```

This trains on the full 1297 structures (unavoidable — it needs the surrogate)
but only draws 30 live points and runs 20 iterations. It verifies the whole
flow end to end before the full run.

## 3. All CLI options

Run with `--help` to see them live:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py --help
```

| Option | Default | Purpose |
|---|---|---|
| `--temp` | `300` | Temperature (K). Sets `beta = 1/(k_B·T)`; controls how strongly low-energy structures are favored. Lower T = sharper focus on the minimum. |
| `--n-live` | `50` | Number of nested-sampling live points. More live points = finer evidence resolution, more evaluations per iteration. |
| `--n-iters` | `300` | Number of nested-sampling iterations. |
| `--perturb` | `0.01` | Perturbation amplitude (Å) added to Fe atoms during prior sampling. `0` = sample DB structures with no noise. |
| `--perturb-symbols` | `Fe` | Element(s) perturbed (the deposition layer). All other atoms stay fixed. Since 2026-08-20 the code perturbs ONLY these atoms, not all. |
| `--output` | `./ns_output_allseeds` | Output directory for results. |
| `--rng` | `42` | Random seed for the sampler's RNG (reproducibility). |

## 4. Understanding the run output (live log)

At startup the script prints, then during the run you'll see per-20-iteration
lines like:

```
  Iter    100/300  Z = 3.165698e-75  log_L_min = -165.3678  E: [-436.814, -432.634] eV  unphys: 0
```

- `Z` — running evidence, accumulated in log space (tiny early on, grows and
  plateaus to the final value near the end).
- `log_L_min` — likelihood of the current worst live point; **increases** as the
  sampler narrows onto the low-energy region.
- `E: [min, max]` — span of live-point energies, **tightens** and shifts toward
  `E_ref` (the training minimum) as iterations progress.
- `unphys` — live points with absurd energies (|E| > 1e4 eV) that got filtered;
  should be 0 in a healthy run.

At the end:
```
Final evidence: Z = 4.168e-04  (log Z = -7.783)
Posterior: 300 physical / 300 total
  E_mean = -432.3524 eV   E_std = 6.2220 eV
  E_min  = -436.8325 eV   E_max = -397.1180 eV
```

## 5. The output files

| File | Contents | Notes |
|---|---|---|
| `evidence_history.csv` | iteration, Z (one row per iteration) | Correct layout |
| `log_evidence.csv` | iteration, log Z | **Malformed** — see the Caveat section |
| `final_live_energies.csv` | live-point energies at termination | 1 column, n_live rows |
| `posterior_structures/posterior_000..019_*.xsf` | top-20 weighted posterior structures | readable by ASE / VESTA |

`evidence_history.csv` is the reliable record of the evidence as a function of
iteration.

## 6. What the "internals" do (prior + sampler)

- **Prior / `sample_from_prior()`**: picks a random structure from the combined
  DB, copies it, and — if `--perturb > 0` — adds Gaussian noise (std = `perturb`
  Å, in each x/y/z) to **only the Fe atoms** (`--perturb-symbols`). The substrate
  (Mg, O) is left exactly in its database positions. `--perturb 0` = pure DB
  resampling, no noise.
- **Likelihood**: `log L = -beta·(E_pred - E_ref)` where `E_ref` is the minimum
  training energy. Working in log space avoids `exp(beta·E)` overflow at ~ −400 eV
  energies and `beta ~ 40 eV⁻¹`.
- **Nested-sampling loop** (`step()`): removes the worst-live likelihood point,
  shrinks the prior volume by `exp(-1/n_live)`, accumulates evidence via
  `logaddexp`, and replaces the removed point with a new one drawn from the prior
  constrained to `log L > log_L_boundary`.

## 7. Verifying the GPR fit (quick sanity check)

The run prints a small validation table for the first 5 training structures, e.g.:
```
  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)
    0   -395.3886   -395.4637     -0.0751
```
Deltas of ~0.02–0.10 eV indicate a well-fitted surrogate. If deltas are huge or
the run reports many `unphys` live points, the GPR is extrapolating badly — reduce
`--perturb` or go back to a smaller amplitude.

### What does "extrapolate to unphysical energies" actually mean?

This is the key reason `--perturb` must stay small (0.01 Å, or 0). In full:

The pipeline is `structure → Fingerprint descriptor (720 numbers) → GPR.predict_energy()`.

1. **The GPR was trained on 1297 structures** whose descriptors all lie in a tight
   region of the 720-D feature space (the DFT-relaxed Fe/MgO structures).

2. **`--perturb` adds Gaussian noise to atom positions** *before* the sampler
   computes the likelihood `L(x) = exp(-beta·(E_gpr(x) − E_ref))`, so the GPR's
   energy prediction directly drives nested sampling.

3. **The Fingerprint is the atom-centered symmetry-function descriptor** from
   `dataset/main.py`; it bins radial distances (`rc1=6 Å`, `binwidth=0.2`) and bond
   angles. Even a modest position shake shifts atoms relative to their neighbours,
   which redistributes counts across the histogram bins.

4. **A Gaussian process is only trustworthy when interpolating.** Its predictive
   mean is essentially a distance-weighted average of the training energies. Once the
   perturbed descriptor sits far from *every* training point in 720-D space, the
   kernel covariances all collapse toward zero and the prediction is pulled back to
   the GP's prior mean (a large, physically meaningless offset). Result: a
   nonsense energy — e.g. thousands of eV — instead of something in the physical
   range [−436.9, −386.3] eV.

Concrete evidence observed this session: with `--perturb 0.5`, the log showed
`Replacing 2 unphysical live points` and an absurd `E_boundary = 2414.7 eV`, with a
posterior `E_mean = +724 eV` (real energies are ~ −400 eV). All of those are
extrapolations.

How the code handles it: any `|E_gpr| > 1e4 eV` is flagged unphysical —
`log_likelihood` returns `-inf` for it, and `_filter_unphysical()` /
`sample_constrained()` drop or redraw those points. This keeps the run stable.

Caveat: "|E| < 1e4" is a pragmatic filter, *not* a guarantee of physical validity. A
perturbed structure can sit just inside the threshold yet still be a far-from-training
extrapolation with a nonsense energy. So a large `--perturb` won't always crash the
run — it can silently corrupt the posterior/evidence with unphysical extrema. This is
why "use `--perturb 0.01` (or 0)" is a hard pitfall, not a performance tip.

## 8. Tuning checklist (what to change and why)

- **Want a more accurate evidence estimate?** Increase `--n-live` (more live
  points → lower variance in log Z). Cost: more GPR evaluations per iteration.
- **Want broader exploration (not just the minimum)?** Raise `--temp` (lower
  beta → flatter likelihood → higher-energy structures get weight).
- **Want the structure search to stay on the deposition layer?** Leave
  `--perturb-symbols Fe` (default); only Fe moves. Don't raise `--perturb` too
  high or the Fingerprint GPR extrapolates badly.
- **Reproducibility:** keep `--rng` fixed at `42` (or note your value) so the
  same command reproduces the same run.

---

# State-density / landscape analysis of the results

After sampling, `run_nested_sampling.py` automatically runs a state-density /
landscape analysis (`nested_sampling/state_density.py`, modeled on
`_run/9_novelFilter/run_analysis_thresholds.py`), comparing the posterior samples
against the 1297-structure training set.

## What it produces
For each of `training/` and `posterior/`, using GPR-predicted energies
(`gpr.predict_energy`, physical |E|<1e4 only):
- **Landscape** `conf_space.png` — PCA top-eigenvector scatter + KDE state-density
  panel (per-atom relative energy axis).
- **Boltzmann probability** `binding_probability_vs_temperature.png` —
  `P(E) = rho(E)·exp(-dE/kbT)/Z` at the reference temperatures 298.15, 348.60,
  447.875, 547.15, 646.425 K.
And one **comparison** panel `comparison_state_density.png` — overlaid training vs
posterior KDE state density on a common energy axis.

Outputs land in `<--output>/analysis/` (per-set subfolders + comparison at the root).

## Standalone re-analysis (no GPR, no re-training)
`NestedSampler.save()` now writes ALL posterior structures (`posterior_structures/`)
plus `posterior_summary.csv` (rank, energy_eV, weight, log_weight). This makes the
analysis re-runnable on a finished run without re-loading data or re-training:

```
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```

New CLI options:
- `--analysis-dir <dir>` — analysis output dir (default `<--output>/analysis`)
- `--no-analysis` — skip the automatic analysis after sampling
- `--analyze-only <RUN_OUTPUT_DIR>` — standalone re-analysis of a saved run

## New/changed code
- `nested_sampling/state_density.py` (new) —
  `analyze_state_density`, `analyze_saved_output`, `load_saved_run` (+ helpers)
- `nested_sampling/nested_sampler.py` — `save()` now writes all posterior XSFs +
  `posterior_summary.csv` (previously only top-20 XSFs)
- `nested_sampling/__init__.py` — exports the new analysis functions
- `run_nested_sampling.py` — runs analysis automatically + `--analyze-only`
- Degenerate-data guard: skips a panel if a set has <2 distinct energies
  (where `gaussian_kde` would be singular)

## Usage note (Fe-only perturbation)
As of this session, the prior perturbation is applied ONLY to the deposition-species
atoms (`--perturb-symbols Fe`, default), leaving substrate (Mg, O) atoms fixed —
verified in `nested_sampler.py` (`sample_from_prior` perturbs `perturb_indices` only).

## Verified
- All 5 analysis outputs generate correctly (synthetic end-to-end test).
- `--analyze-only` standalone path verified end-to-end (REAL_EXIT=0).
- Full-production re-run on the real 1297 set was NOT repeated due to concurrent
  memory-heavy `relax_and_partition.py` (Ray OOM under 98% RAM); the earlier
  300-iter production run succeeded under lower load.

---

# Ray `ActorUnavailableError` in GPR — fixed with `use_ray=False`

## Symptom
Running the script crashed at the very first GPR step with:

```
  gpr = build_gpr(structures)
  gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
  ...
  ray.exceptions.ActorUnavailableError: The actor ... is unavailable:
  The actor is temporarily unavailable: IOError: The actor was restarted.
```

This happened **before any sampling** — so it is independent of `--perturb`,
`--n-iters`, etc.

## Root cause
`GPR(...)` defaults to `use_ray=True`. AGOX then calls
`pool_add_module(self)` → `ray.get(futures)`, which spawns **one Ray actor per CPU
(4 actors on this node)** to hold copies of the model for parallel hyperparameter
optimization. When the node's RAM is already nearly exhausted (e.g. the concurrent
`relax_and_partition.py` job from `_run/9_novelFilter` plus Obsidian, IDE/LSP
servers, and Hermes gateways push memory to ~95–100%), the OS / Ray kills one of
those actors -> `ActorUnavailableError` (or, at lower pressure, a Ray OOM kill). It
is purely an environmental resource problem, not a code bug: the identical script
succeeded earlier under lower load.

## Fix
Add `use_ray=False` to the `GPR(...)` constructor in `build_gpr`
(`run_nested_sampling.py`):

```python
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(),
          use_ray=False)
```

Verified directly in the AGOX source (`agox/models/GPR/GPR.py`, `__init__`):
when `use_ray=False`, the `else` branch runs — it does **not** call
`pool_add_module(self)` (so no Ray actors are spawned, `ActorUnavailableError` is
structurally impossible) and sets `n_optimize = 1` (single-process hyperparameter
optimization). This uses far less memory and removes the whole crash class,
regardless of what else is running.

## Verification
- Confirmed the Ray-actor path is skipped when `use_ray=False` (source inspection).
- Real tiny smoke run (`--temp 300 --n-live 5 --n-iters 3 --no-analysis`) on the
  full 1297 set: **REAL_EXIT=0**, GPR trained, NO Ray pool spawned, no crash.

## Trade-off / notes
- **Cost:** GPR hyperparameter optimization now runs on 1 process instead of 4,
  so training may take a bit longer (~2 min → potentially a few minutes). For the
  1297-point set and typical `--n-iters` this is still fast; it does not alter the
  sampling math or the analysis.
- **Important (unrelated to the fix):** using a large `--perturb` (e.g. 0.5 Å)
  makes the Fingerprint GPR extrapolate to unphysical energies (live points with
  |E| → thousands of eV get replaced, posterior E_mean balloons). Use the safe
  default `--perturb 0.01` (or 0). See the Pitfalls section above.

---

# Full, heavy supercomputer run (Fujitsu PJM batch)

## Job scheduler summary (`job.sh`, this directory)
The batch script in `job.sh` targets a Fujitsu PJM-style job manager on the
supercomputer:

```
#PJM -L rscgrp=a-pj24001864   # resource group
#PJM -L vnode-core=64          # cores per node
#PJM --mpi proc=64             # MPI processes
#PJM -L elapse=120:00:00       # 120 h walltime
#PJM -j  -X
source ~/.bashrc
conda activate gpaw_env
module load intel impi
python ./run_nested_sampling.py --temp 300 --n-live 20 --n-iters 300 --perturb 0.01 --output ./ns_output_allseeds --rng 42
```

Submit with `pjsub job.sh`, check with `pjstat`, kill with `pjdel`.
> Note: `job.sh` currently activates the `gpaw_env` conda env. This nested-sampling
> script needs the `agox_v2` env (AGOX/ASE stack). Change
> `conda activate gpaw_env` → `conda activate agox_v2` before submitting this job.

## Canonical heavy run command (literature scale)

This is a **full-pipeline** heavy job, sized to the nested-sampling literature rather
than the conservative defaults. It gives near-1/√K evidence resolution with a deep
top-down pass. Replace the `python ./run_nested_sampling.py ...` line in `job.sh`
with:

```bash
OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
    --temp 300 \
    --n-live 500 \
    --n-iters 5000 \
    --perturb 0.01 \
    --perturb-symbols Fe \
    --rng 42 \
    --output ./ns_output_allseeds_heavy
```

### Per-parameter comparison: literature vs this run

| Parameter | Pártay et al. 2021 \cite{Partay2021} (bulk) | Yang et al. 2024 \cite{Yang2024} (surfaces) | Chatbipho et al. 2025 \cite{Chatbipho2025} (nanocluster) | This run (proposed heavy) |
|---|---|---|---|---|
| **Live set K** | 500–5000 walkers | 80 per free particle (all coverages) | extends Yang's surface NS to LJ38 | **500** (a.k.a. `--n-live`) |
| **Walk length L** | 100s–1000s steps | ~250 iterations/walker | same NS walk/move scheme | *no explicit L* (see gap below) |
| **System size N** | 32–256 atoms | 4×4 surface cell, ≤16 free particles | LJ38 + up to a few free adsorbates | 75 atoms (Fe25Mg25O25) |
| **Iterations** | 10^5 – 10^7 | 80×250×16 = 320 000 | comparable | **5000** (`--n-iters`) |
| **Temperature β** | **absent from sampling** (post-process only) | absent | absent | **in the likelihood** (`--temp`), major difference |

Notes on the table:
- K=500 is the lower end of Pártay's bulk guidance (500–5000) and the pragmatic scale
  for this GPR-based sampler (each "walker" here is a GPR `predict_energy`, far cheaper
  than direct DFT/DFTB evaluations, but still sampled per live point).
- Yang's surface recipe (80/prop-free-particle × 250 iters, i.e. ~320 000 iterations
  at full coverage) is the *strictest* analogue to our Fe-on-MgO deposition; scaling it
  to our 25 Fe atoms gives K≈2000, iters≈500 000 — see the tuning table for that
  option. K=500 / iters=5000 is a tractable literature-informed middle ground.
- Chatbipho et al. 2025 \cite{Chatbipho2025} applies the same surface-NS machinery to
  LJ38 nanoclusters, confirming the surface recipe at the small-system end; it does not
  change the parameter guidance above.

**Meaning of the heavy settings:**
- `--n-live 500` — literature-scale live set; evidence resolution ∝ 1/√500, well below
  the 1/√250 noise of the 200-point run.
- `--n-iters 5000` — deep pass (≈10× the default), driving prior-volume shrinkage far
  toward the global-minimum basin.
- `--temp 300` — canonical 300 K (Boltzmann weights); adjust per the tuning list.
- `--perturb 0.01` — safe default for the Fingerprint GPR (do NOT raise; see pitfall).
- `--rng 42` — reproducible.
- `--output` separate dir (keeps the previous runs intact).
- Analysis **runs automatically** here (full pipeline).

### About `OMP_NUM_THREADS=1`

`OMP_NUM_THREADS` is an OpenMP environment variable that caps how many threads any
OpenMP-parallel library (BLAS/LAPACK, NumPy/SciPy, GPAW/AGOX Cython kernels) may
spawn. Setting it to **1** means: "use exactly one thread per process".

- **What it sets within the job node:** every process inherits it, so e.g. NumPy's
  BLAS dot products, the AGOX Fingerprint Cython loops, and any `omp`-enabled kernel
  run single-threaded instead of grabbing all 64 cores.
- **Why:** the node exposes 64 cores. Since this script is now single-process
  (`use_ray=False`) and you *scale out* by submitting many independent jobs (one per
  temperature / seed), you don't want a single job silently using 64 threads — that
  would oversubscribe the node and degrade everything. `OMP_NUM_THREADS=1` keeps each
  job to one thread so multiple jobs share the cores evenly.
- **Effect within Ray:** after `use_ray=False` there is no Ray pool in this run, so
  `OMP_NUM_THREADS=1` no longer matters for Ray at all. If you were to re-enable
  `use_ray=True`, the per-actor BLAS/OpenMP would be capped to 1 thread/actor too —
  which is the *correct* setting when Ray spawns many actors (it prevents each actor
  from trying to use the whole node).
- **Bottom line:** harmless, recommended, and effectively free on a shared 64-core
  node that runs several jobs at once. It mainly prevents over-subscription; it has no
  accuracy/statistics effect.

## Tuning knobs (choose per what you want)

| Goal | Option | Direction |
|---|---|---|
| Finer evidence / better resolution | `--n-live` | higher — 500 (paper bulk) up to 2000 (Yang surface) |
| Deeper search toward minimum | `--n-iters` | higher — 5000 up to 10^5 (paper bulk) |
| Full Yang-surface analogue (25 Fe ≈ 25 free particles) | `--n-live 2000 --n-iters 500000` | strictest, very expensive |
| Focus on global minimum (sharper) | `--temp` | lower (e.g. 100–300 K) |
| Broader exploration (higher-E weight) | `--temp` | higher (e.g. 600–1000 K) |
| Switch off prior noise | `--perturb 0` | sample DB structures exactly |
| Restrict motion to a species | `--perturb-symbols Fe` | deposition layer only (default) |
| Skip the state-density analysis | `--no-analysis` | sampling-only run |
| Analysis only (reuse saved run) | `--analyze-only <RUN_OUTPUT_DIR>` | no re-sampling |
| Reproducible run | `--rng <int>` | fix the seed |

### Suggested heavy scan (compare thermodynamics across T)
Run several jobs at different temperatures (independent outputs so they don't
clobber each other), each `--n-live 500 --n-iters 5000 --temp <Ti>`:

```bash
for T in 100 200 300 500 1000; do
  OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
      --temp $T --n-live 500 --n-iters 5000 --perturb 0.01 \
      --perturb-symbols Fe --output ./ns_T${T} --rng 42
done
```
Each produces its own evidence Z → free energy F = −k_B·T ln Z, so the temperature
dependence of the partition function is read directly from the evidence across T.
> Run each T as a separate `pjsub` job (or a PJM array) to use the 64 cores / 120 h
> budget efficiently. After the `use_ray=False` fix the script is single-process, so
> scale **many independent jobs** rather than MPI-parallelising one invocation.

## Supercomputer-specific notes
- The 120 h elapsed budget comfortably accommodates this heavy run (and allows the
  T-scan). A full Yang-scale job (K=2000, ~5×10^5 iters) may approach the budget.
- Since `use_ray=False` makes the sampler single-process, scale out by submitting
  **many independent jobs** (one per T and/or per `--rng` seed) rather than one
  `mpiexec` invocation — this is the efficient use of the node.
- Wall-clock estimate: GPR training ~2–5 min (single-core); sampling cost scales
  ~ linearly with `--n-iters ×` effective draws per iteration. 5000 iters / 500 live
  is comfortable within the budget; a Yang-scale job is the upper end.

---

# Discussion: the parameters used in the nested-sampling literature, and why

> Sources: Pártay, Csányi & Bernstein, "Nested sampling for materials", Eur. Phys. J. B
> 94, 159 (2021) (`raw/papers/nested-sampling/2021partay_nested-sampling.pdf`) and
> Yang, Pártay & Wexler, "Surface phase diagrams from nested sampling", PCCP 26,
> 13862 (2024) (`2023yang_nested-sampling.pdf`), cross-referenced against the
> wiki-research concepts ★[[nested-sampling]]★ and ★[[nested-sampling-validation]]★.

Nested sampling (NS) is controlled by a small set of parameters. The two that
dominate accuracy are the **live-set size K** and the **walk length L**; the number
of iterations follows from them and from the target minimum temperature. This section
reports what the papers actually use, and *why*.

Note:
What is K and L based on our code? Is there any? What is the relation to our code if there any? How do we justify our nested sampling based on these sources?

## The parameters, and their meaning

| Parameter | Meaning | Paper values |
|---|---|---|
| `K` (live points / walkers) | number of concurrently-held configurations; sets the phase-space-volume resolution | bulk: **K = 500–5000**; surfaces: **80 per free particle** |
| `L` (walk length) | number of MC steps used to decorrelate a cloned configuration into an independent sample | **100s to 1000s** (decreases as K grows) |
| `N` (system size) | number of atoms | **32–256** for periodic solids |
| iterations | top-down pass to pre-set η (min temp) | **10^5 – 10^7** (bulk); Yang: **250 × K** per surface |

## Why K is what it is (the central accuracy parameter)

Both papers make the **live-set size K the primary accuracy knob**. The reason is in
the way NS estimates configuration-space volume: at iteration *i* the volume below the
current energy limit is

$$\Gamma_i = \Gamma_0 \left[\frac{K}{K+1}\right]^i .$$

The finite live set gives a *statistical* error in **ln Γ_i proportional to
1/√K** — so the resolution with which the PES is mapped, and the error on ln Γ and on
any observable, is set almost entirely by K:

> "The size of the live set K is another important factor in the accuracy of the
> results, determining the resolution with which the PES is mapped during the
> sampling. If it is too low, there will be systematic discretization errors, as well
> as noise, in the configuration space volume estimates." (2021, §2.2)

Two further reasons K must be large enough in materials:

1. **Extinction of basins.** If K is too small, basins separated by energy barriers
   can fluctuate to zero samples once the limiting energy cuts them off; knowledge of
   that basin is then lost forever. For the highly multimodal PES of real materials
   this is a hard floor on K.
2. **Resolution vs volume of basins.** Because K sets the PES resolution, narrow but
   thermodynamically relevant low-energy basins are only captured if K is large
   enough (can require *superposition-enhanced* NS for the tightest basins).

Concrete values from the two papers:
- **2021 (bulk review):** "for good convergence, periodic solids require system sizes
  of N = 32–256 atoms, walk lengths L of 100s to 1000s, and K = 500–5000 walkers.
  These result in 10^5 to 10^7 iterations being needed to reach the global minimum."
  The figure panels (heat capacity vs temperature for 64-atom LJ) show K increasing
  160 → 320 → 640 sharpening the Cp peak toward the true discontinuity, at rising cost.
- **2024 (pymatnest surfaces, directly analogous to the Fe/MgO adsorbate problem):**
  "**80 walkers per free particle**", "**250 iterations per walker**". For the maximum
  coverage (16 free particles / ML) this gives 80 × 250 × 16 = **320 000 iterations**.

## Why L (walk length) exists, and its trade-off with K

When a walker is removed, the new configuration is produced by **cloning a random
surviving walker and then moving it away via Monte Carlo** until it becomes an
independent sample. L is the number of those decorrelation steps. It must be long
enough that the clone is no longer correlated with its source and again samples the
allowed region — too short, and you re-introduce the same structures instead of new
phase space.

The subtle, well-known trade-off (2021, §2.2) is that **the minimum sufficient L
decreases as K increases**:

> "there is some evidence … that with increasing K, the minimum sufficient L
> decreases … This may be understood if the distance that the cloned configuration
> needs to diffuse in configuration space decreases as K increases, for example, if it
> only needs to be lost among the neighboring configurations, rather than fully
> explore the entire available space."

So K and L are not independent: higher K → denser live set → each clone only needs to
diffuse to a *neighbouring* region, needing fewer MC steps. This is why the 2024
surface work, with K=80/particle, uses a modest L (250 iter/walker) and observes the
iteration count scaling only ~linearly with K.

## Why the number of iterations is not a free choice

The iteration count is set by the **minimum temperature** one wants to resolve, not
picked arbitrarily:

> "The number of NS iterations is set by the minimum temperature that needs to be
> described, since the range of configurations relevant at each temperature is set by
> the balance between the decreasing configuration space volume and the increasing
> Boltzmann factor as iteration number increases and energy decreases."

For a fixed minimum temperature the total volume compression is fixed, so the number
of iterations scales **linearly with K**. This is the direct reason Yang 2024 uses
250 *iterations per walker*.

## Temperature is NOT a sampling parameter

A crucial point repeatedly emphasised by both papers — and structurally different from
our implementation:

> "It is important to note the **absence of the temperature β from the actual sampling
> algorithm**. Even without explicit dependence on the temperature, the sequence of
> configurations and weights generated by NS can be used to efficiently calculate
> expectation values with the Boltzmann weight." (2021)

NS samples the PES once, top-down, and **β is only introduced in post-processing** to
evaluate $Z(β)$, $\langle A\rangle(β)$, and the heat capacity at any temperature from a
single sample set. This is the core advantage enabling the surface phase diagrams of
2024 (a whole coverage–temperature diagram from one NS run per coverage).

## How the papers' choices map onto the current script's parameters

Our `NestedSampler` maps the NS parameters onto CLI flags, but with an important
modelling difference:

| Literature param | Our flag | Notes |
|---|---|---|
| `K` (live points) | `--n-live` | Same role: evidence resolution ∝ 1/√K. Paper "heavy" guidance: K=500–5000; our heavy job uses 200 (see § above) — conservative vs. the materials literature. |
| walk length `L` | (implicit in `--n-iters` + refill) | **Missing:** our prior is an *empirical DB distribution* + `--perturb`, not clone-then-MC-decorrelate. There is no explicit decorrelation length; each constrained draw is an independent sample from the DB. This is the single biggest structural difference to the papers. |
| iterations | `--n-iters` | In the papers this is derived from K × (target β). We set it explicitly. |
| system size `N` | fixed Fe25Mg25O25 = 75 atoms | Within the papers' 32–256 range. |
| temperature `β` | `--temp` | **Major difference:** the papers keep β out of sampling and apply it only in post-processing. Our sampler puts `L(x)=exp(-β·(E−E_ref))` **inside** the likelihood, i.e. it samples a *fixed-temperature* Boltzmann weight and the posterior/evidence are temperature-specific. This is one reason the evidence Z here is T-dependent (we effectively do a single-temperature NS rather than a T-free posterior). |

## What this implies for the present run

- **`--n-live` is the lever that most directly controls accuracy** of the evidence and
  posterior. If the goal is to compare against the materials-science literature, the
  paper-scale choice is K ≈ 500–1000+, not 50 or 200.
- **The iteration count should follow K × (needed log-β range).** Our pipeline keeps
  it explicit via `--n-iters`; the papers derive it. For a given target lowest T, more
  live points require proportionally more iterations — plan the supercomputer budget
  accordingly (heavy job: 200 live × 2000 iters; a literature-scale K=500 would want
  ~5000+ iters).
- **The open modelling gap to the papers is the prior.** The papers clone-and-diffuse
  with a real walk length L; our DB-resample+small-perturb prior (restricted to Fe) is
  the simpler empirical alternative. Exactly this gap is the subject of the wiki's
  ★[[nested-sampling-validation]]★ page — NS is proposed there as the *rigorous,
  bias-corrected* cross-check of the GOFEE/LCB Fe/MgO partition function claimed in the
  rejected manuscript (LT19702J). The current script is a stepping stone toward that
  validation; adopting a true clone-and-MC decorrelation move (L walk length) and
  moving β to post-processing would bring it in line with Partay/Yang.

