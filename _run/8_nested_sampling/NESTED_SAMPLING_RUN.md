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

