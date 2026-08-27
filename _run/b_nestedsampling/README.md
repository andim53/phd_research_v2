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

Notes:

**What is the `log L` in nested sampling?** `L` is the **likelihood** — a measure of how
"good" a structure is. In the fixed-T mode it is `L(x) = exp(-β·(E(x) − E_ref))`, so a
structure is more likely the lower its GPR-predicted energy is. In temperature-free mode
`log L = −(E − E_ref)`, i.e. structures are ranked by energy alone. Nested sampling treats
`L` as an unnormalized posterior weight over configuration space; `log L` (its natural
logarithm) is what the code actually manipulates, because the raw likelihood spans
hundreds of orders of magnitude (energies ~ −400 eV, `β ~ 40 eV⁻¹`).

**What do you mean by "evidence"?** The **evidence `Z`** is the normalization constant of
the posterior, `Z = ∫ L(x)·π(x) dx`. It is a single number that measures how much
probability mass the likelihood assigns to the configuration space — i.e. how well the
"surface" is supported. In statistical mechanics `Z` is exactly the **canonical partition
function**, so it is both the Bayesian evidence and the object from which all
thermodynamics (free energy, heat capacity) is derived. It is the central quantity nested
sampling is designed to compute.

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

**What is `beta`?** `beta = 1/(k_B·T)` is the **inverse temperature** (units eV⁻¹, with
`k_B = 8.617e-5 eV/K`). It is the thermodynamic knob in the likelihood: at T = 300 K,
`beta ≈ 38.68 eV⁻¹`, so each eV above the best structure costs a factor
`exp(-38.68) ≈ 10⁻¹⁷` in likelihood — low-energy structures are overwhelmingly preferred.
Lower T (higher β) sharpens focus on the global minimum; higher T flattens the landscape.

**What is `E`, and why `− E_ref`?** `E = E(x)` is the **GPR-predicted energy** of a
structure (eV). The likelihood only cares about energy *differences*, so `E` is shifted by
a reference. **`E_ref` = the minimum training energy** (the lowest-energy structure in the
dataset). Subtracting `E_ref` makes the best structure have `E − E_ref = 0` → `L = 1`
(its likelihood is 1, i.e. the highest), while any higher-energy structure has `E − E_ref
> 0` → `L < 1`. This shifts the whole likelihood to O(1) at the optimum, avoiding
overflow and giving a clean, physically sensible reference point.

The central output is the **model evidence / partition function `Z`** (and
`log Z`) for the Fe/MgO system at a given temperature, plus the weighted
posterior set of structures.

Notes:

**What is model evidence?** Model evidence is `Z`, the normalization constant of the
posterior `Z = ∫ L(x)·π(x) dx`. It answers "how much total probability (likelihood ×
prior) does the model place over the structures?" — a single scalar that, for a given
energy surface and temperature, quantifies how well-supported the configuration space is.
Because of the statistical-mechanics identification, `Z` is also the **partition
function**, so it is the quantity from which the free energy `F = −k_B T ln Z` and all
other thermodynamic averages are obtained. (The earlier "What is the evidence" note in the
What-it-does section covers the same concept; this is the "model evidence" phrasing used
in the Bayesian literature.)

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

**How to plot it?** Plot `Z` (or `log Z`) against the **iteration** from
`evidence_history.csv` to see the evidence converge; or plot `log Z` / `Z` and
`F = −k_B T ln Z` against **temperature** from `thermodynamics.csv` to see the
temperature dependence. The state-density analysis (`analysis/conf_space.png`,
`binding_probability_vs_temperature.png`) already visualizes the landscape and the
Boltzmann probability vs T. There is no dedicated "Z vs T" plot currently written by the
code — if you want one, it is a small addition (plot `thermodynamics.csv`).

**What do we need `log Z` for?** (1) **Numerical stability** — `Z` under/overflows
float64 (range ~`10⁻²⁴²`→`10⁻⁴`), `log Z` does not. (2) **Thermodynamics** — the free
energy is `F = −k_B T ln Z`, and derivatives of `ln Z` w.r.t. `β` give mean energy and
heat capacity (heat-capacity peaks mark phase transitions). (3) **Bayesian model
comparison** — differences in `log Z` between models give Bayes factors. So `log Z` is
the robust quantity the code keeps and that you use for all the physics and statistics.

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

**Contrast with the fixed-T mode.** In fixed-T mode, `log L = -β·(E − E_ref)` ranks the
live set, so the whole run is tied to one temperature and $Z$ is that temperature's
partition function. In temperature-free mode, `log L = −(E − E_ref)` ranks by energy
alone; $\beta$ never enters sampling, and `evaluate(β)`/`posterior_at(β)` turn the
recorded $(E_i, w_i)$ into $Z(\beta)$ and the posterior at any temperature.

**From $Z$ to observables.** The code writes `thermodynamics.csv` with columns
T, β, logZ, Z, and `F = −k_B T ln Z`. Derivatives of $\ln Z$ with respect to $\beta$
would give $\langle E\rangle$ and $C_V(T)$ — useful for identifying phase transitions
via heat-capacity peaks (a hallmark of the nested-sampling approach in the papers).

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
