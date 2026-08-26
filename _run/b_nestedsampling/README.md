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
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --output ./ns_output_allseeds --rng 42
```
After sampling, the analysis writes to `<--output>/analysis/` automatically.

## Usage (standalone re-analysis of a finished run)
```
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```
The run dir must contain `posterior_structures/posterior_*.xsf` and
`posterior_summary.csv`.

## Options
- `--temp`      temperature (K), default 300
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
├── run_nested_sampling.py   # entry point (root runner)
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
