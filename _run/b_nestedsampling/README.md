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

The central output is the **model evidence / partition function `Z`** (and
`log Z`) for the Fe/MgO system at a given temperature, plus the weighted
posterior set of structures.

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

With `--e-max-per-atom <eV/atom>`, excludes structures with E/atom above the given
threshold **before GPR training AND evaluation** (both CV and in-sample). Use it to
drop high-energy outlier structures that break the GPR fit (e.g. the B-doped dataset
has outliers up to −0.23 eV/atom that make the surrogate predict unphysically);
`--e-max-per-atom -5.2` keeps a spread comparable to the working Fe/MgO set.
Default: not set (keep all).

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
