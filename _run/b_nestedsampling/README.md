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
```
Outputs: `gpr_accuracy_by_energy_range*.csv` (per-bin metrics) + matplotlib plot
+ printed table. In CV mode it also writes `cv_fold_summary_<K>folds.csv`
(fold-averaged MAE) and names outputs `..._cv<K>folds.*`.

With `--uncertainty`, additionally writes `uncertainty_by_energy_range.csv`
(per-bin mean GPR predictive std) and adds a `mean_model_std_eV_per_atom` column
to the accuracy CSV + per-bin 1σ model-std error bars on the plot. In in-sample
mode this is the trained model's std on the training set; in CV mode it is the
average std of the held-out predictions pooled across folds.

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
  deposition layer); all other atoms stay fixed during prior sampling
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
