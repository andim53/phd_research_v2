# Temperature-free nested sampling (papers/wiki-consistent)

How to make the AGOX-GPR NestedSampler consistent with the nested-sampling
literature (Pártay/Csányi/Bernstein 2021 EPJ B 94:159; Yang/Pártay/Wexler 2024
PCCP 26:13862) and the wiki `★[[nested-sampling]]★` page: **β kept OUT of the
sampling likelihood**, with Z(β), free energy, and the posterior evaluated in
post-processing at any temperature. Implemented in project
`/home/think/Desktop/research/_run/b_nestedsampling/` (canonical NS project;
migrated from `_run/8_nested_sampling`, runner renamed `run_nested_sampling.py`
→ `main.py`).

## The core idea (vs the fixed-T default)

- **Fixed-T mode (default, `--temp 300`):** `log_likelihood = -beta*(E - E_ref)`.
  β is inside the likelihood → single-temperature NS; Z and the posterior are
  temperature-specific.
- **Temperature-free mode (`--temperature-free`):** `log_likelihood = -(E - E_ref)`
  — β-free, i.e. an **energy-constrained top-down pass** (the "worst" live point is
  the highest-energy one). The sampler records, per discarded sample, its energy
  `E_i` and prior-volume weight `w_i = Γ(E_{i-1})−Γ(E_i) = ΔX` (plus the final live
  set). Then in post-processing, at any β:
    - `Z(β) = Σ_i w_i exp(−β E_i)`  (+ final live-point term `X_final·<exp(−β(E−E_ref))>_live`)
    - `F = −k_B T ln Z`  (free energy, eV)
    - posterior `weight_i = w_i exp(−β E_i) / Z(β)`
  One sample set → thermodynamics at ALL temperatures.

## CLI

```bash
/home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 \
    --output ./ns_output_tfree --rng 42
```

- `--temperature-free` — opt-in; fixed-T path stays the default (backward compat).
- `--temperatures` — comma-separated K list for post-processing (default
  100,200,300,500,1000). Z/F/posterior evaluated at each.

## Sampler design (nested_sampling/nested_sampler.py)

- `NestedSampler(..., temperature_free=False)`; when True, `beta=None`.
- `log_likelihood()` branches: `-(E-E_ref)` when T-free, else `-beta*(E-E_ref)`.
- `step()`: in T-free mode appends `E_worst` to `sample_energies` and `ΔX` to
  `sample_prior_weights` (fixed-T mode keeps the old log_Z accumulation).
- `run()`: T-free progress prints remaining prior volume `X = exp(-(i+1)/n_live)`
  instead of Z; no final β evidence correction.
- `evaluate(beta) -> (Z, logZ)` and `posterior_at(beta) -> (structs, weights)`
  implement the post-processing formulas. `_logsumexp` helper keeps it stable.
- `save()`: T-free writes re-runnable `samples.csv`
  (iteration, energy_eV, prior_weight) + `final_live_energies.csv`; fixed-T writes
  the old evidence/posterior files.

## main.py post-processing

After `save()`, when T-free, main.py writes per-T:
- `thermodynamics.csv` (T_K, beta_eV-1, logZ, Z, F_eV)
- `posterior_T{KKK}/posterior_{rank}_w{w:.4e}_E{E:.3f}.xsf` + `posterior_summary.csv`
  (rank, energy_eV, weight) — ranked by descending posterior weight.

Use the GPR prediction for the XSF filename energy (`gpr.predict_energy(s)`), not
`atoms.get_potential_energy()` (the copied DB structures carry a stale calculator).

## Smoke test

`smoke_test_temperature_free.py` (project root) does two things:
1. Unit test: build a bare `NestedSampler` via `object.__new__` (bypasses the
   GPR/dataset `__init__`), set synthetic `(E_i, w_i)` + live set, and assert
   `evaluate(beta)`/`posterior_at(beta)` reproduce the paper formula to 1e-9 and
   posterior weights sum to 1.
2. End-to-end: `main.py --temperature-free --n-live 10 --n-iters 15` on the real
   1297-set; asserts samples.csv, thermodynamics.csv, posterior_T{100,300,1000}
   all written, exit 0.

## Verified physics (real output)

T=100/300/1000 K → log Z = −27.2 / −11.6 / −6.1; F = +0.235 / +0.300 / +0.530 eV.
Z grows and F becomes less negative as T rises — physically correct. (In the
fixed-T run the sampler's own Z, e.g. Z=4.168e-04 / log Z=−7.783 at 300 K over 300
iters, is the same style of quantity.)

## Pitfalls specific to this mode

- Do NOT call `evaluate()`/`posterior_at()` in fixed-T mode — they raise
  `ValueError`; use the accumulated `sampler.log_Z` instead.
- LSP (Pyright under base python3) flags `ase.io` unresolved and
  `-beta` "optional operand" (beta is None in T-free mode) — both are false
  positives; judge by `py_compile` under `agox_v2`.
- Two `main.py` files coexist: root `main.py` = the NS sampler entry point;
  `dataset/main.py` = the original AGOX search generator (no CLI, loops seeds
  3..104). The HPC job runs only the root one by default.
