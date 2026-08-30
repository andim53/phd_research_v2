# Wang-Landau density of states on an AGOX GPR surrogate

Project: `/home/think/Desktop/research/_run/c_landausampling/`
Status: created under the AI-Agent Project Workflow. Companion files:
`README.AI.md` (machine spec), `TUTORIAL.md` (reproduction), `LOG.md`
(action log), `AGENTS.md` (governing rules).

## What it does

This project applies the **Wang–Landau flat-histogram method** to estimate the
**density of states g(E)** of a structure pool, using an AGOX **GPR surrogate**
as the energy model. It is the sibling of `_run/b_nestedsampling`, which solved
the same "flat structure ↔ island structure" problem with **nested sampling**;
here the algorithm is Wang–Landau (WL) instead.

1. Loads **every** structure from **every** seed database of the chosen dataset
   (`dataset/` = Fe/MgO 1297 structures; `dataset_boron3/` = B3-doped;
   `dataset_boron/` = B7-doped).
2. Trains a **single AGOX GPR surrogate** on the combined structures (AGOX
   kernel recipe).
3. Runs the `WangLandauSampler` from the `wang_landau/` package: a Monte-Carlo
   walk that rattles the deposition-species atoms (small/large Gaussian steps)
   and accumulates a flat visitation histogram over energy bins, refining the
   log density of states `ln g(E)` by the standard `f → √f` scheme and then the
   **1/t algorithm** (Belardinelli & Pereyra 2007).
4. From the normalised `g(E)` derives the **partition function Z**, free energy
   `F = −k_B T ln Z`, and heat capacity `C_V(T)` at chosen temperatures.

The central output is the **density of states `g(E)`** and the thermodynamics
that follow from it.

## Algorithm & the Fortran reference

The algorithm is a faithful Python port of
`_tmp/main_wanglandau_1d.f` (kept as the reference skeleton). In that toy,
a walker moves on a 1D coordinate `x` over the asymmetric double well
`E(x) = A(x²−1)² + B·x`, and the density of states is accumulated over energy
bins between the island (global minimum) and just past the barrier top. The
Python code generalises that: the "coordinate" is the full atomic structure, the
"move" is a rattle of the mobile atoms, and the "energy" is the GPR prediction,
binned as **relative energy per atom**, `(E − E_min)/N`, over `[e_min, e_max]`
(default `[0, 0.40]` eV/atom — island at 0, past the flat/barrier region).

Both use the same Wang–Landau core:
- acceptance `ln(r) < ln g(cur) − ln g(trial)` against the density,
- every visit adds `ln f` to `ln g` and `+1` to the histogram `H`,
- when `H` is flat (`min H > criterion·mean H`) the refinement `ln f` is halved,
- after `n_stages_standard` halvings the run switches to the 1/t algorithm
  (`ln f = 1/t′`) to avoid the error-saturation of the plain scheme.

## Environment

Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```
The HPC batch script `j_wanglandau.sh` activates `gpaw_env` (standing
convention) — but the sampling script needs the AGOX/ASE stack from `agox_v2`;
if `gpaw_env` lacks it, switch to `conda activate agox_v2` before submitting.

## Usage

All commands use `PY=/home/think/miniconda3/envs/agox_v2/bin/python` and are run
from the project root.

### Full run (default dataset, Fe/MgO)
```bash
$PY main.py --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42
```

### Choose a different dataset (B-doped)
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron3 --rng 42
$PY main.py --dataset dataset_boron   --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron  --rng 42
```

### Cheap local smoke test (no DFT / no real GPR)
Validates the whole `WangLandauSampler` code path on a **fake 1-atom GPR**
reproducing the Fortran double-well potential — no heavy training needed:
```bash
$PY smoke_test_wang_landau.py
```

## Job (HPC)

`j_wanglandau.sh` runs Wang–Landau on HPC (PJM, 24 cores, `gpaw_env`), reading
the existing `dataset/seed_*/1_db/db_*.db`. Submit with `pjsub j_wanglandau.sh`.

## CLI reference

| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `dataset` | Dataset dir: `dataset` (Fe/MgO) \| `dataset_boron3` (B3) \| `dataset_boron` (B7). |
| `--n-bins` | `40` | Number of energy bins for `g(E)`. |
| `--e-min` | `0.0` | Lower bin edge (eV/atom relative to the minimum). |
| `--e-max` | `0.40` | Upper bin edge (eV/atom rel; island at 0, set past the barrier/flat region). |
| `--small-step` | `0.05` | Small Gaussian displacement scale (Å), local refinement. |
| `--large-step` | `0.40` | Large Gaussian displacement scale (Å), barrier crossing. |
| `--perturb-symbols` | `Fe` | Atom symbol(s) to rattle; all others stay fixed. |
| `--flatness-criterion` | `0.80` | Flatness threshold (`min H > criterion·mean H`). |
| `--check-interval` | `5000` | Flatness check interval (MC steps). |
| `--n-stages-standard` | `14` | Standard-scheme halvings before switching to the 1/t algorithm. |
| `--mc-steps` | `2000000` | Number of Wang–Landau MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Temperatures (K) for thermodynamics post-processing. |
| `--start-from-top` | on | Initialize the walker at the top of the bin range (flat-structure analogue, Fortran default). |
| `--output` | `./wl_output` | Output directory. |
| `--rng` | `42` | RNG seed (reproducibility). |
| `--use-ray` | off | Enable Ray in GPR training (default single-process). |

## Outputs (written to `--output`)

- `g_of_E.csv` — bin-center relative energy (eV/atom), `ln g`, histogram count.
- `g_of_E.png` — plot of `ln g(E)` vs relative energy per atom.
- `thermodynamics.csv` — `T_K, beta_eV-1, logZ, Z, F_eV` (from normalised g(E)).
- `heat_capacity.csv` — `T_K, C_V_eV_per_K` (needs ≥3 temperatures).

## Key decisions & tradeoffs

| Decision | Choice | Tradeoff |
|---|---|---|
| Energy model | AGOX GPR surrogate (not DFT-in-loop) | Fast enough for a long WL walk; energy errors from the surrogate (validated ~0.004 eV/atom MAE). |
| Sampling move | Rattle mobile atoms (small/large) | Local refinement + barrier crossing; extrapolating far can give unphysical GPR energies (guarded `\|E\|<1e4`). |
| Binning | Relative energy per atom `(E−E_min)/N` | Dataset/composition comparable; the `g(E)` is per-atom, so absolute Z is normalised to unit integral (only the additive constant is arbitrary). |
| Refinement | standard `f→√f` then 1/t | 1/t avoids error saturation of the plain scheme (Belardinelli & Pereyra 2007). |
| Data | self-contained copy of all 3 datasets | Fully reproducible in isolation (~300M regenerable data, gitignored). |

## Concepts & physics

**Density of states `g(E)`.** The number of configurations per unit energy at
energy `E` — the fundamental quantity of statistical mechanics from which
everything else follows. Wang–Landau estimates `ln g(E)` directly by making the
walk spend equal (flat) time in every energy bin.

**Wang–Landau acceptance.** A trial configuration is accepted with probability
`min(1, g(current)/g(trial))`. In log form this is
`accept if ln(r) < ln g(cur) − ln g(trial)`. This biases the walk toward
low-density (rare) energies, flattening the histogram — hence "flat histogram"
sampling. Each visit to a bin accumulates `ln f` into `ln g` and `+1` into `H`;
`ln f` starts at 1 (=`ln e`) and is halved whenever `H` becomes flat, refining
the estimate.

**Partition function `Z`.** `Z(β) = Σ_b g_b · exp(−β E_b) · ΔE` (bins b over
absolute energy). Since Wang–Landau gives `g(E)` only up to a multiplicative
constant, we normalise `g(E)` to unit integral; relative quantities and `C_V`
are unaffected by the constant. `F = −k_B T ln Z`.

**Heat capacity `C_V`.** `C_V = k_B β² · d²(ln Z)/dβ²`, computed by finite
differences. A peak in `C_V(T)` is the standard signature of a phase transition
(here the flat↔island transition), computed from the second derivative of
`ln Z`.

## Layout

```
c_landausampling/
├── main.py                    # entry point (root runner)
├── wang_landau/               # package: WangLandauSampler, GPR loader/trainer, thermodynamics, utils
├── scripts/                   # (analysis helpers as needed)
├── dataset/                   # Fe/MgO AGOX seed DBs (seed_3..15) + main.py + scripts
├── dataset_boron3/            # B3-doped AGOX seed DBs
├── dataset_boron/             # B7-doped AGOX seed DBs
├── j_wanglandau.sh            # PJM batch script (HPC)
├── smoke_test_wang_landau.py  # cheap local validation (fake double-well GPR)
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md / PROMPTS.md
├── _runs/                     # self-contained HPC run dirs (scaffolded)
├── _analysist/                # per-run analysed results (scaffolded)
├── _archives/                 # archived artifacts
└── _tmp/                      # scratch output (holds main_wanglandau_1d.f reference)
```

See `README.AI.md` for the machine-readable spec and `TUTORIAL.md` for
step-by-step reproduction.
