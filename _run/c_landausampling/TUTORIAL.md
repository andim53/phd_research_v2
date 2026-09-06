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
    --mc-steps 20000000 --small-step 0.05 --large-step 0.20 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42
```
`--mc-steps 20000000` is the HPC-scale budget (the Fortran uses up to 2e7 steps).
For a quick local check use `--mc-steps 400000 --check-interval 100000
--n-stages-standard 3` so the run finishes in minutes and still exercises the
standard→1/t switch. The `--large-step 0.20` default and the `--e-reject`
extrapolation guard (default `5×e_max`) are active automatically (v1.3.0+).

## Step 4 — Other datasets
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron3 --rng 42
$PY main.py --dataset dataset_boron  --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron  --rng 42
```

## Step 4b — Enable the swap (permutation) move
The boron-doped datasets have two mobile species (B + Fe), so permutation moves
can exchange their positions. Enable with `--swap-prob`; each swap move performs
a random `1..--max-swaps` position exchanges between two different mobile species
and rattles them by `--swap-rattle` (mirrors the reference
`GlobalPermutationGenerator`):
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --perturb-symbols Fe,B \
    --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 \
    --output ./wl_output_boron3_swap --rng 42
```
The plain Fe/MgO `dataset` has a single mobile species (Fe); there
`--swap-prob` is ignored with a WARNING and the walk falls back to rattling only.

## Step 4c — Mode A parallel walkers (`--n-walkers`, v1.5.0)
To reach flatness faster, run **N concurrent Wang–Landau walkers** that share
one histogram `H`/`ln_g` via Ray actors (seeds `--rng+i`; flatness/refinement
act on the combined histogram). The c3 run uses 500 walkers:
```bash
cd /home/think/Desktop/research/_run/c_landausampling
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY main.py --dataset dataset --n-bins 100 --e-max 0.40 --mc-steps 30000 \
    --small-step 0.05 --large-step 0.20 --perturb-symbols Fe --relax-steps 100 \
    --temperatures 100,200,300,500,1000 \
    --n-walkers 500 --output ./wl_output_parallel --rng 42
```
Each walker costs ≈ 135 MB (GPR copy + Ray process); 500 walkers ≈ 68 GB
(≈73% of the 92.7 GB genkai node limit). On a 64-core node wall-time speedup
saturates near ~64 (over-subscribed ~8×); the win is statistical — independent
chains aggregate to flatness in fewer total MC steps. For a quick local test
use `--n-walkers 24 --mc-steps 1000 --check-interval 250`.

## Basin-hopping mode (GPR relax, `--relax-steps`)
To sample the density of *minimized* (basin) energies instead of raw rattled
energies — the "MC step + GPR relax" idea — add `--relax-steps N` (e.g. 100).
Each proposed trial is relaxed to a local minimum of the GPR potential (N BFGS
steps, only the mobile atoms free) before binning. This makes large rattles
(barrier hopping) safe, but the resulting `g(E)` is over minima, not
configurations; re-add the vibrational contribution for a canonical `Z`. Default
`--relax-steps 0` = off (the plain flat-histogram walk). Each step is ~N× more
expensive, so cut `--mc-steps` accordingly.

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

## Pitfall: delta g(E) at the top bin (the c1/c2 collapse)
If `g_of_E.png` shows a single spike at the top bin (rel ≈ e_max) and `F` is
**constant** across all temperatures (`C_V ≈ 0`), the walk escaped the
ground-state basin into GPR-extrapolation territory and got trapped in the
capped top bin. This was the observed failure of the c1 (Fe/MgO) and c2 (B3)
sweeps. Two fixes are now in v1.3.0:
- **Default `--large-step` reduced 0.40 → 0.20 Å**, so a single rattle is less
  likely to catapult the walker into extrapolation territory.
- **`--e-reject` extrapolation guard** (default `5×e_max` eV/atom): any trial
  with rel E > e_reject is rejected (revisits the current bin) instead of being
  capped into the top bin. Moderate over-window energies (`e_max..e_reject`)
  are still capped (Fortran behaviour); only clearly-unphysical extrapolations
  are rejected. Set `--e-reject` ≤ e_max to disable.
Re-run the smoke test to confirm the guard: `smoke_test_wang_landau.py` now
includes a `test_extrapolation_guard` case.

## Verification checklist
- [ ] `smoke_test_wang_landau.py` prints `[SMOKE] RESULT: PASS` and a
      T-dependent `F`
- [ ] `main.py` compiles and runs on `--dataset dataset`
- [ ] `g_of_E.csv` / `g_of_E.png` / `thermodynamics.csv` produced
- [ ] `heat_capacity.csv` written (needs ≥3 temperatures)
- [ ] Run reached the 1/t switch (or you consciously accept the standard scheme)
- [ ] (Optional) `--n-walkers N` parallel run completes and writes aggregate
      `g_of_E.csv` from the shared actor
- [ ] `j_wanglandau.sh` kept bare; correct env (`gpaw_env`) and launch
      (`pjsub j_wanglandau.sh`)
