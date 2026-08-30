# TUTORIAL — Reproduce the Wang–Landau density-of-states run

Step-by-step guide to reproduce this project's full pipeline from scratch.
Level: intermediate (assumes the `agox_v2` conda env and the datasets are in
place). Terminal only — no IDE required.

## Prerequisites
- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0 + Ray).
  Python: `/home/think/miniconda3/envs/agox_v2/bin/python`.
- Datasets in place (copied into this project, self-contained):
  - `dataset/seed_*/1_db/db_*.db` (13 DBs, seeds 3–15, 1297 structures, Fe25Mg25O25)
  - `dataset_boron3/seed_*/1_db/db_*.db` (7 DBs, B3Fe25Mg25O25)
  - `dataset_boron/seed_*/1_db/db_*.db` (5 DBs, B7Fe25Mg25O25)
- (Optional) HPC cluster with PJM batch for heavy runs — `pjsub`.

## Step 0 — Mental model
`main.py` does four things in sequence:
1. **Loads the chosen dataset** — all structures from every seed DB.
2. **Trains one GPR surrogate** on the combined structures (AGOX Fingerprint
   descriptor, 720-dim, + standard kernel recipe). ~2 min for Fe/MgO.
3. **Runs Wang–Landau** — a Monte-Carlo walk over the structures that rattles
   the mobile (Fe) atoms, accumulates a flat histogram over energy bins, and
   refines `ln g(E)` (standard `f→√f` scheme, then the 1/t algorithm).
4. **Derives thermodynamics** — normalises `g(E)` and computes `Z`, `F`, `C_V`
   at the requested temperatures.

Output: `g_of_E.csv` + `g_of_E.png`, `thermodynamics.csv`, `heat_capacity.csv`.

## Step 1 — Cheap local smoke test (no DFT, no heavy training)
Validates the entire `WangLandauSampler` code path on a **fake 1-atom GPR** that
reproduces the Fortran double-well potential `E(x)=A(x²−1)²+B·x`. This is the
direct Python analogue of `_tmp/main_wanglandau_1d.f` and should complete in
seconds:
```bash
cd /home/think/Desktop/research/_run/c_landausampling
/home/think/miniconda3/envs/agox_v2/bin/python smoke_test_wang_landau.py
```
Expected: 39/40 bins visited, 4 stages reached (with the default toy settings),
1/t switch reached, and a **temperature-dependent** free energy `F` (e.g.
`F ≈ −0.13 eV` at 100 K rising to `≈ +1.07 eV` at 1000 K) — the signature of a
genuinely spread `g(E)`.

## Step 2 — Compile check
```bash
/home/think/miniconda3/envs/agox_v2/bin/python -m py_compile \
    main.py wang_landau/*.py smoke_test_wang_landau.py
```

## Step 3 — Full run (default dataset, Fe/MgO)
```bash
cd /home/think/Desktop/research/_run/c_landausampling
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY main.py --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42
```
`--mc-steps 20000000` is the HPC-scale budget (the Fortran uses up to 2e7 steps).
For a quick local check use `--mc-steps 400000 --check-interval 100000
--n-stages-standard 3` so the run finishes in minutes and still exercises the
standard→1/t switch.

## Step 4 — Other datasets
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron3 --rng 42
$PY main.py --dataset dataset_boron  --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron  --rng 42
```

## Step 5 — HPC job
`j_wanglandau.sh` runs Wang–Landau on the HPC cluster (PJM, 24 cores,
`gpaw_env`), reading the existing `dataset/seed_*/1_db/db_*.db`:
```bash
pjsub j_wanglandau.sh
```
It activates `gpaw_env` (standing convention). **Caveat:** the sampling script
needs the AGOX/ASE stack from `agox_v2`; if the job fails on AGOX imports,
switch the `conda activate` line to `agox_v2`.

## Choosing a good `--e-max` (energy window)
`g(E)` is tracked over relative energy per atom `(E−E_min)/N`. The Fortran spans
from the island (global minimum, rel 0) **past the barrier top** separating the
flat and island basins, plus a small margin. For Fe/MgO the barrier/flat region
sits around 0.2–0.4 eV/atom, so `--e-max 0.40` is the recommended default. If
the run reports "No DB structure inside the bin range", `--e-max` is too low.

## Convergence: did it switch to 1/t?
Wang–Landau converges when the refinement `ln f` has decayed and the run has
switched to the **1/t algorithm** (`ln f = 1/t′`), which avoids the
error-saturation of the plain `f→√f` scheme. The sampler prints
`Switching to 1/t algorithm at step N` when this happens. If it instead prints
`NOTE: standard f->sqrt(f) scheme; did not reach the 1/t switch`, increase
`--mc-steps` (or lower `--n-stages-standard`, currently 14).

## Verification checklist
- [ ] `smoke_test_wang_landau.py` prints `[SMOKE] RESULT: PASS` and a
      T-dependent `F`
- [ ] `main.py` compiles and runs on `--dataset dataset`
- [ ] `g_of_E.csv` / `g_of_E.png` / `thermodynamics.csv` produced
- [ ] `heat_capacity.csv` written (needs ≥3 temperatures)
- [ ] Run reached the 1/t switch (or you consciously accept the standard scheme)
- [ ] `j_wanglandau.sh` kept bare; correct env (`gpaw_env`) and launch
      (`pjsub j_wanglandau.sh`)
