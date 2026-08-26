# TUTORIAL — Reproduce the nested-sampling run (Fe/MgO, combined multi-seed)

Step-by-step guide to reproduce this project's full pipeline from scratch.
Level: intermediate (assumes the `agox_v2` conda env and the dataset are in
place). Terminal only — no IDE required.

## Prerequisites
- Conda env **`agox_v2`** (AGOX 3.10.2 + ASE 3.25.0 + Ray).
  Python: `/home/think/miniconda3/envs/agox_v2/bin/python`.
- Dataset in place: `dataset/seed_*/1_db/db_*.db` (13 DBs, seeds 3–15, 1297
  structures, uniform Mg25O25Fe25).
- (Optional) HPC cluster with PJM batch for heavy runs — `pjsub`.

## Step 0 — Mental model
`main.py` does three things in sequence:
1. **Loads the combined dataset** — all structures from every seed DB
   (`dataset/seed_*/1_db/db_*.db`, 1297 structures).
2. **Trains one GPR surrogate** on all 1297 structures (AGOX Fingerprint
   descriptor, 720-dim, + standard kernel recipe). ~2 min.
3. **Runs nested sampling** — draws live points from the empirical DB
   distribution (small Gaussian perturbation on Fe only), iteratively shrinks the
   prior volume toward low energy, accumulates evidence `Z` in log space.

Output: evidence `Z` (and log Z), posterior energy statistics, weighted
posterior structures, and a state-density/landscape analysis.

## Step 1 — One-line run (default)
```bash
cd /home/think/Desktop/research/_run/b_nestedsampling
/home/think/miniconda3/envs/agox_v2/bin/python main.py
```
Defaults: `--temp 300 --n-live 50 --n-iters 300 --perturb 0.01
--perturb-symbols Fe --output ./ns_output_allseeds --rng 42`.

## Step 2 — Quick smoke test first
Always validate the pipeline on a tiny run before a long one:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temp 300 --n-live 30 --n-iters 20 --perturb 0.01 \
    --output /tmp/ns_smoke --rng 42
```
Trains on the full 1297 structures (needed for the surrogate) but only 30 live
points / 20 iterations — verifies the whole flow end to end.

## Step 3 — All CLI options
Run with `--help` to see them live. Table in `README.AI.md` §3.

## Step 4 — Understanding the run output (live log)
Per-20-iteration lines like:
```
  Iter    100/300  Z = 3.165698e-75  log_L_min = -165.3678  E: [-436.814, -432.634] eV  unphys: 0
```
- `Z` — running evidence (tiny early, plateaus near end).
- `log_L_min` — likelihood of the worst live point; **increases** as the sampler
  narrows onto low energy.
- `E: [min,max]` — live-point energy span, tightens and shifts toward `E_ref`.
- `unphys` — live points with absurd |E|>1e4 that were filtered; should be 0.

At the end:
```
Final evidence: Z = 4.168e-04  (log Z = -7.783)
Posterior: 300 physical / 300 total
  E_mean = -432.3524 eV   E_std = 6.2220 eV
  E_min  = -436.8325 eV   E_max = -397.1180 eV
```

## Step 5 — Output files
| File | Contents | Notes |
|---|---|---|
| `evidence_history.csv` | iteration, Z (one row/iter) | **Correct** layout |
| `log_evidence.csv` | iteration, log Z | **Malformed** — see Pitfall 3 |
| `final_live_energies.csv` | live-point energies at termination | 1 col, n_live rows |
| `posterior_summary.csv` | rank, energy_eV, weight, log_weight | all posterior samples |
| `posterior_structures/posterior_*.xsf` | posterior structures | ASE / VESTA readable |

## Step 6 — Internals (prior + sampler)
- **Prior / `sample_from_prior()`** — picks a random DB structure, copies it, and
  if `--perturb > 0` adds Gaussian noise (std = `perturb` Å) to **only the Fe
  atoms** (`--perturb-symbols`); Mg/O stay fixed. `--perturb 0` = pure resample.
- **Likelihood** — `log L = -beta·(E_pred - E_ref)`, `E_ref` = min training
  energy. Log space avoids overflow at ~−400 eV and beta~40 eV⁻¹.
- **NS loop (`step()`)** — removes worst-live point, shrinks prior volume by
  `exp(-1/n_live)`, accumulates evidence via `logaddexp`, replaces with a new
  point constrained to `log L > log_L_boundary`.

## Step 7 — Verifying the GPR fit
The run prints a validation table for the first 5 training structures:
```
  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)
    0   -395.3886   -395.4637     -0.0751
```
Deltas ~0.02–0.10 eV → well-fitted surrogate. Huge deltas or many `unphys`
points → GPR extrapolating badly; reduce `--perturb`.

## Step 8 — State-density / landscape analysis
Runs automatically after sampling (`--no-analysis` to skip). For each of
`training/` and `posterior/` (GPR-predicted energies, |E|<1e4 only):
- `conf_space.png` — PCA top-eigenvector scatter + KDE state-density panel.
- `binding_probability_vs_temperature.png` — `P(E)=rho(E)·exp(-dE/kbT)/Z` at
  298.15, 348.60, 447.875, 547.15, 646.425 K.
Plus `comparison_state_density.png` (overlaid training vs posterior KDE).
Re-run on a finished run without re-training:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```

## Step 8b — Temperature-free mode (consistent with the papers)
By default the sampler is **fixed-temperature** (`--temp`): β is inside the
likelihood, so Z and the posterior are for that one temperature. To match the
papers (Pártay 2021 / Yang 2024) and the wiki's `nested-sampling` page — where β is
**absent from sampling** and applied only in post-processing — add `--temperature-free`:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --output ./ns_output_tfree --rng 42
```
- **During sampling:** `log_likelihood` becomes β-free (`-(E - E_ref)`), i.e. an
  energy-constrained top-down pass. The sampler records, per discarded sample, its
  energy `E_i` and prior-volume weight `w_i = Γ(E_{i-1})−Γ(E_i) = ΔX`, and the final
  live set.
- **Post-processing (per `--temperatures` T):** `Z(β) = Σ_i w_i exp(−β E_i)`
  (+ final live term), `F = −k_B T ln Z`, and the posterior
  `weight_i = w_i exp(−β E_i)/Z(β)`. One sample set → thermodynamics at all T.
- **Outputs:** `samples.csv` (re-runnable: iteration, energy_eV, prior_weight),
  `thermodynamics.csv` (T, β, logZ, Z, F), and per-T posterior dirs
  `posterior_T{KKK}/` with `posterior_summary.csv`.
- **Smoke test:** `smoke_test_temperature_free.py` validates the T-free math against
  the paper formula and runs a tiny end-to-end T-free run.
- **Verification (smoke, real output):** at 100/300/1000 K, log Z = −27.2 / −11.6 /
  −6.1 and F = +0.235 / +0.300 / +0.530 eV — Z grows and F becomes less negative as
  T rises (physically correct).

## Step 8c — GPR accuracy vs energy range
`gpr_accuracy.py` evaluates how accurately the GPR predicts structure energies as a
function of the energy range (energy above the global minimum, in eV/atom, binned
into equal-width windows). Two modes:
```bash
# in-sample (default): train on all 1297, predict the same set (training-set fit)
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --bin-width 0.1 --output ./gpr_accuracy_out

# 5-fold CV (out-of-sample generalization): stratified by energy bin, each fold
# trains on 4/5 and predicts the held-out 1/5; held-out errors pooled per bin
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 5 --bin-width 0.1 --output ./gpr_accuracy_cv_out
```
- `--bin-width` — energy-bin width (eV/atom), default 0.1 (≈7 bins over the
  ~0.675 eV/atom range).
- `--output` — output dir; writes per-bin CSV + plot + printed table.
- `--use-ray` — use AGOX Ray for training (default single-process).
- `--cv` / `--cv-folds N` — opt-in K-fold CV (default 5), stratified by energy bin;
  writes pooled `..._cv<K>folds.csv` + `cv_fold_summary_<K>folds.csv`.
- **Interpretation:** in-sample errors are tiny (MAE~0.001 eV/atom, R²≈1.0,
  interpolation points). CV gives the truthful out-of-sample picture: 5-fold CV
  overall MAE=0.0040 RMSE=0.0067 R²=0.998 eV/atom, with error **increasing toward
  higher-energy bins** (MAE~0.010, R²~0.58 at 0.39–0.48 eV/atom) — the GPR
  generalizes worse at the energy extremes (fewer structures, more extrapolation).

## Step 9 — Tuning checklist
- **Finer evidence / lower variance:** raise `--n-live` (resolution ∝ 1/√K).
- **Broader exploration (higher-E weight):** raise `--temp`.
- **Sharper focus on minimum:** lower `--temp` (e.g. 100–300 K).
- **Stay on the deposition layer:** keep `--perturb-symbols Fe`; do **not** raise
  `--perturb` (see Pitfall 4).
- **Reproducibility:** keep `--rng` fixed (e.g. 42).

## Heavy, supercomputer run (Fujitsu PJM)
`j_nestedsampling.sh` is a **nested-sampling-only job** — it reads the existing
`dataset/seed_*/1_db/db_*.db` and runs `main.py`:
```sh
# (from the project root, on HPC)
OMP_NUM_THREADS=1 python ./main.py \
    --temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 \
    --perturb-symbols Fe --output ./ns_output_T300_100_1000_0.01 --rng 42
```
- Header: `vnode-core=24 / mpi proc=24`.
- Submit with `pjsub j_nestedsampling.sh`, check `pjstat`, kill `pjdel`.
- **Env caveat:** the script activates `gpaw_env` (standing HPC convention). The
  sampling script needs the AGOX/ASE stack; on HPC `gpaw_env` has it (it generated
  the original dataset via `dataset/job_5x5_9.sh`). If the job fails on AGOX
  imports, edit `j_nestedsampling.sh`: `conda activate gpaw_env` →
  `conda activate agox_v2` (locally `agox_v2` has AGOX 3.10.2 + ASE 3.25.0 + GPAW).
- **Current NS params are conservative** (`--n-live 100 --n-iters 1000`). For
  literature-scale resolution, use the heavy settings below.

### Optional: add the AGOX search step back
By default the job does **not** run the AGOX search — it samples the already-present
dataset (seeds 3–15). To regenerate/extend the dataset, run `dataset/main.py`
first (AGOX search over ALL seeds 3..104, writing DBs into
`dataset/seed_<N>/1_db/db_<N>.db`), then `main.py`:
```sh
cd ./dataset
OMP_NUM_THREADS=1 python ./main.py            # AGOX search (all seeds 3..104)
cd ..
OMP_NUM_THREADS=1 python ./main.py ...        # then nested sampling (above)
```
Note: `dataset/main.py` uses `SubprocessGPAW(ncores=24)` (matching the job's 24-core
header) and runs the full seed range in one job.

### Literature-scale NS parameters (from the papers)
The nested-sampling literature sets accuracy via the **live-set size K** (and walk
length L). Source: the `wiki-research` pages `concepts/nested-sampling.md`,
`concepts/nested-sampling-validation.md`, and
`raw/syntheses/nested-sampling_synthesis.md`; PDFs under
`wiki-research/raw/papers/nested-sampling/`.

| Paper | System | K (live set) | L (walk length) | Iterations | Notes |
|---|---|---|---|---|---|
| Pártay, Csányi & Bernstein 2021 (EPJ B 94, 159) | bulk periodic solids | **500–5000** walkers | 100s–1000s | **10⁵–10⁷** | N=32–256 atoms; error in ln Γ ∝ 1/√K; too-small K → basin *extinction* |
| Yang, Pártay & Wexler 2024 (PCCP 26, 13862) | surfaces / adsorbates | **80 walkers per free particle** | ~250 iterations/walker | 80×250×16 = **320 000** at full coverage | closest analogue to Fe-on-MgO deposition; 25 Fe → K≈2000, iters≈500 000 |
| Chatbipho et al. 2025 (JCP 163, 174701) | LJ38 nanocluster adsorbates | extends Yang's surface NS | same walk/move scheme | comparable | confirms surface-NS recipe at small-system end |

**Meaning for this project (Fe25Mg25O25, 75 atoms):**
- The strict Yang-surface analogue for 25 free Fe atoms is `--n-live ~2000` /
  `--n-iters ~500 000` — very expensive.
- A tractable literature-informed middle ground is **`--n-live 500 --n-iters 5000`**
  (Pártay bulk lower bound; 1/√500 resolution, ≈10× the default depth):
```bash
OMP_NUM_THREADS=1 python ./main.py \
    --temp 300 --n-live 500 --n-iters 5000 --perturb 0.01 \
    --perturb-symbols Fe --rng 42 --output ./ns_output_allseeds_heavy
```
`OMP_NUM_THREADS=1` keeps each single-process job to one thread so many
independent jobs share the node evenly (after `use_ray=False` the sampler is
single-process → scale by submitting many jobs, not MPI-parallelising one).

**Suggested temperature scan** (compare thermodynamics across T; each T its own
job/output, free energy F = −k_B·T·ln Z from each evidence):
```bash
for T in 100 200 300 500 1000; do
  OMP_NUM_THREADS=1 python ./main.py \
      --temp $T --n-live 500 --n-iters 5000 --perturb 0.01 \
      --perturb-symbols Fe --output ./ns_T${T} --rng 42
done
```

## Discussion — parameters in the nested-sampling literature
Sources: Pártay, Csányi & Bernstein, "Nested sampling for materials", EPJ B 94,
159 (2021); Yang, Pártay & Wexler, PCCP 26, 13862 (2024).

- **K (live set)** is the central accuracy knob: volume at iteration i is
  `Γ_i = Γ_0 [K/(K+1)]^i`; the finite set gives error in ln Γ ∝ 1/√K. Papers use
  bulk K=500–5000; surfaces 80 walkers per free particle (Yang: 250 iter/walker).
  Too-small K can *extinguish* low-energy basins.
- **L (walk length)** — clone a surviving walker and MC-diffuse it to decorrelate.
  Minimum sufficient L **decreases as K grows** (clone only needs to blend into
  neighbours). Our sampler has **no explicit L**: the prior is DB-resample +
  small perturb (each draw independent) — the single biggest structural
  difference to the papers.
- **Iterations** are not free — set by the target minimum temperature; scale
  ~linearly with K.
- **Temperature β is NOT a sampling parameter in the papers** — they sample the
  PES once and apply β only in post-processing to get Z(β) and any observable at
  any T. **Our sampler puts β inside the likelihood** (`L(x)=exp(-β·(E-E_ref))`),
  i.e. single-temperature NS — a major modelling difference and the reason our
  evidence Z is T-dependent.

Q: When you say they sample the PES once, does that mean they apply for 0 K for their sampling based on the current code?

**Answer:** No — "sample the PES once" does **not** mean 0 K sampling. In the
papers, the sampling itself is **temperature-independent**: β never appears in the
NS algorithm. The distinction matters, and it is the crux of the "major difference"
noted above.

1. **In the papers (Pártay 2021 / Yang 2024):** the run is a single top-down pass
   over configuration space constrained only by a monotonically *decreasing* energy
   limit `U_limit`. It starts at high-energy "gas-like" configurations and, over
   10⁵–10⁷ iterations, descends toward the global minimum. There is **no β anywhere
   during sampling**. Temperature enters only in **post-processing**: from one sample
   set `{E_i}` and its configuration-space weights `{w_i}` you evaluate
   `Z(β) = Σ_i w_i exp(−β E_i)` at **any** temperature. So:
   - The sample set is temperature-agnostic and spans the whole energy range — it is
     **not** a 0 K ensemble.
   - 0 K appears only as the post-processing limit `T→0` (`β→∞`), where `Z(β)` is
     dominated by the single lowest-energy sample (the global minimum). The sampling
     is not "done at 0 K"; it merely makes the 0 K ground state the final, deepest
     level of the top-down pass.
   - This is the key advantage: one NS run yields `Z(T)`, free energy, heat capacity,
     etc. across all temperatures.

2. **In this project's code (`main.py` + `nested_sampling/nested_sampler.py`):** we
   do the **opposite**. In `nested_sampler.py`, `log_likelihood` is
   ```
   log L = -self.beta * (E - self.E_ref),   with beta = 1/(K_B * --temp)
   ```
   so β is **inside the likelihood**: we run a **single-temperature** (fixed-β) NS,
   where low-energy structures are Boltzmann-weighted at that one temperature
   (default `--temp 300 K`). Our evidence `Z` and posterior are therefore
   **temperature-specific** — not temperature-free. This is exactly the "major
   difference" flagged in the table above.

To answer directly: **No.** The papers' "sample the PES once" is a temperature-*free*
sample (0 K enters only as a post-processing extreme), whereas our current code
samples at one fixed temperature and cannot reuse the sample set across temperatures.
Matching the papers would mean moving β out of the likelihood into post-processing
(computing `Z(β)` from the saved energy+weight history) — the open modelling gap
discussed at the end of this section (and the subject of the wiki's
`★[[nested-sampling-validation]]★` page).


### Mapping to our flags
| Literature | Our flag | Notes |
|---|---|---|
| K (live points) | `--n-live` | Same role (resolution ∝ 1/√K); papers K=500–5000, ours default 50 |
| walk length L | implicit (`--n-iters` + refill) | **Missing** — no clone-and-MC decorrelation |
| iterations | `--n-iters` | Explicit here; derived from K×β in papers |
| system size N | 75 atoms (fixed) | Within papers' 32–256 range |
| temperature β | `--temp` | **In the likelihood** (differs from papers) |

The open modelling gap (clone-and-MC prior + β in post-processing) is exactly the
subject of the wiki's `★[[nested-sampling-validation]]★` — NS is proposed there
as the rigorous cross-check of the GOFEE/LCB Fe/MgO partition function from the
rejected manuscript (LT19702J). This project is a stepping stone toward that.

## Common Pitfalls
1. **`GPR` `database=` kwarg is a red herring** — combine DBs by concatenating
   `restore_to_trajectory()` lists; don't point the model at multiple DB files.
2. **Composition mismatch breaks the descriptor** — a combined GPR only works if
   every structure has the same stoichiometry/atom count. Check `Counter` first.
   Fe/MgO is uniform (1297 × Mg25O25Fe25).
3. **`log_evidence.csv` is malformed** (pre-existing package save bug) — two
   transposed rows instead of one row per iteration. No data lost;
   `evidence_history.csv` is correct. Regenerate per-row log_Z from it if needed.
4. **Large `--perturb` → GPR extrapolates to unphysical energies** — with
   `--perturb 0.5`, live points hit |E|→thousands of eV, posterior E_mean
   balloons. Use `--perturb 0.01` (or 0). The |E|<1e4 filter is pragmatic, *not*
   a physical guarantee — a structure just inside the threshold can still be a
   bad extrapolation.
5. **Ray `ActorUnavailableError`** — environmental (RAM exhaustion); fixed with
   `use_ray=False` in `build_gpr` (single-process hyperparameter opt).
6. **Use the absolute env python** — base `python3` has no AGOX/ASE.
7. **Ray stderr noise is expected** — don't mistake it for a crash.

## Verification checklist
- [ ] `Counter(get_chemical_symbols())` confirms one uniform composition across seeds
- [ ] Run via `/home/think/miniconda3/envs/agox_v2/bin/python`
- [ ] GPR validation deltas ~0.02–0.10 eV; `unphys: 0` in the live log
- [ ] Live-energy range converges toward `E_ref` over iterations
- [ ] `evidence_history.csv` + `posterior_structures/*.xsf` + analysis PNGs produced
- [ ] If parsing `log_evidence.csv`, re-derive from `evidence_history.csv` (save bug)
