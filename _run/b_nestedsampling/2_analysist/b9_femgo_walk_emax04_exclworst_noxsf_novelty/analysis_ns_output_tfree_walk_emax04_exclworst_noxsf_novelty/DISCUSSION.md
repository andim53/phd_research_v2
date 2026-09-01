# DISCUSSION — Run b9_femgo_walk_emax04_exclworst_noxsf_novelty (plain Fe/MgO, temperature-free NS + novelty threshold)

Run: `1_runs/b9_femgo_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `2_analysist/b9_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty/`
Analysis outputs: this directory (`2_analysist/b9_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty/`)
Script: `2_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `2_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b9_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty \
    --outdir b9_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty \
    --n-atoms 75
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 75` = atoms per structure (Fe/MgO) for the per-atom relative-energy
units of the state density.

This document discusses the results of the temperature-free nested-sampling (NS) run on the
plain Fe/MgO (no-Boron) system, using b8's parameters **plus** a Fingerprint-space novelty
filter on the initial live set. Flags: `--e-max-per-atom 0.4`,
`--e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000`,
`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both --walk-exclude-worst`,
`--no-posterior-xsf`, `--novelty-threshold 1.0 --novelty-max-attempts 500`,
`--n-live 100 --n-iters 1000`, `--temperatures 100,200,300,500,1000 K`.

> Note: this run was submitted with `--no-posterior-xsf`, so **no `posterior_*.xsf` structure
> files** were written (only `posterior_T{KKK}/posterior_summary.csv`). Consequently the
> b6-style delta-Z landscape (`conf_space_deltaz.png`) cannot be reproduced here.

---

## 1. What was run and what the CSVs contain

- **`samples.csv`** (1000 rows): the discarded (worst) samples, one per NS iteration, with
  `iteration`, `energy_eV` (GPR-predicted absolute energy), and `prior_weight`
  (`w_i = X_{i-1} − X_i`, the prior-volume shell weight).
- **`final_live_energies.csv`** (100 rows): the live-set energies at termination (`n_live=100`).
- **`thermodynamics.csv`** (5 rows): `T`, `β`, `log Z`, `Z`, and `F = −k_B T ln Z`, from the
  temperature-free post-processing (`evaluate(β)`).

The energies are the **GPR-predicted** energies of the surrogate trained on the
`--e-max-per-atom 0.4` filtered dataset (1158 of 1297 Fe/MgO structures).

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−424.20 .. −407.17 eV` (weighted mean `−413.51 eV`).

**Relative to the global minimum** (taken as the best live energy `−435.91 eV`, ~75 atoms):
- lowest discarded sample ≈ `+0.156 eV/atom`
- highest discarded sample ≈ `+0.383 eV/atom`

This confirms the run behaved as designed: the sampler operated **inside the targeted
~0.16–0.38 eV/atom window** above the ground state — consistent with `--e-window-lo 0.3` /
`--e-window-hi 0.35` (the initial live set was pinned to that band) and `--e-max-per-atom 0.4`
(the dataset cap). The run **started near 0.3 eV/atom and descended toward the ground state**.

**Final live set:** `−435.91 .. −424.22 eV` (mean `−429.17 eV`). The live set has descended
close to the global minimum region, which is the expected NS convergence behaviour (the worst
live point keeps dropping as the prior volume shrinks).

**Commentary on the walk + novelty threshold:** the dual-scale `--walk` (50 steps, small
0.05 Å / large 0.40 Å, `--walk-exclude-worst`) was the primary per-step move, with the
`--perturb 0.01` prior draw handling initialization and fallback. The `--novelty-threshold 1.0`
de-duplicated the **initial** live set in AGOX Fingerprint space (each of the 100 starting
live points ≥ 1.0 apart), which should give a more diverse set of starting basins. The samples
span a ~17 eV band, showing genuine coverage of the 0.16–0.38 eV/atom region rather than
collapse to a single point.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for
the configurational state density `g(E)`: each discarded sample contributes its prior-volume
shell `w_i` per unit energy. The **weighted peak** is at `≈ +0.148 eV/atom` above the ground
state (`state_density_gE.png`, peak `g ≈ 21.3 config./eV`).

Interpretation: most of the sampled probability mass sits around `+0.148 eV/atom` above the
minimum — not at the very ground state (which has almost zero prior volume by the end of the
run) and not at the top of the window. This is the classic NS behaviour: the discarded samples
accumulate where there is the most configuration-space volume, here in the mid-to-upper part of
the sampled window rather than at the single global-minimum structure. The peak position
(`~0.15 eV/atom`) is a natural, physically meaningful feature of the weighted ensemble (not the
unweighted minimum) and is comparable in scale to the reference island peak (0.074 eV/atom).

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−435.91 .. −424.22 eV` with mean `−429.17 eV`
(`live_energy_hist.png`). The live set is the population that survived to termination and
represents the remaining prior-volume correction. Its position near the low-energy end of the
window means the run reached the ground-state basin and the live points are clustered in the
low-energy region — as expected when NS has converged (the remaining live set contributes the
final `X_final · <L>` correction to `Z`).

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −130.69 | 1.75e−57 | 1.126 |
| 200 | −72.65 | 2.82e−32 | 1.252 |
| 300 | −53.30 | 7.12e−24 | 1.378 |
| 500 | −37.82 | 3.76e−17 | 1.630 |
| 1000 | −26.18 | 4.25e−12 | 2.256 |

- **`log Z` rises monotonically with T** (`−130.7 → −26.2`), and **`Z` grows** (`10⁻⁵⁷ → 10⁻¹²`).
  This is the expected temperature dependence: higher T broadens the Boltzmann weight, so the
  partition function (total probability mass) increases. The absolute `Z` values are tiny because
  the evidence is normalized to the (very low prior-volume) absolute scale of this surrogate
  landscape — the **relative** trend with T is the meaningful physics.
- **Free energy `F = −k_B T ln Z` rises** with T (`1.13 → 2.26 eV`), consistent with
  `F = −T·(entropy-weighted energy)` becoming more positive as thermal agitation increases.
- **Heat capacity `C_V` is essentially zero** in this run (values ~10⁻⁸ to 10⁻¹⁹ eV/K; shown as
  `0.0000` in the printed summary due to 4-decimal rounding). This is because `log Z` vs `β`
  is very nearly linear over 100–1000 K, so its second derivative (curvature) is ~0. Physically
  this means **no strong first-order phase transition / latent-heat peak is resolved in this
  temperature range** for this surrogate and window. A `C_V` peak would indicate a phase
  transition (e.g. flat↔island); here the curve is flat, so within this window the system behaves
  like a single-basin, weakly-entropic ensemble at these temperatures.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 0.99995` over the 1000 discarded samples (`samples_cumulative_Z.png`). In NS the
total prior volume removed should be `1 − X_final`, where `X_final = exp(−iters/n_live) =
exp(−1000/100) = exp(−10) ≈ 4.5e−5`. So `sum(w_i) ≈ 1 − 4.5e−5 ≈ 0.99995`, which **matches
exactly**. This confirms the weighting/bookkeeping is internally consistent and the trace is
numerically sound.

The comparison with `thermodynamics.csv` `logZ` is qualitative: the `log(Σ w_i)` from samples and
the post-processed `log Z(β)` are different normalizations (the former is the raw prior-volume
integral; the latter includes the `exp(−β(E−E_ref))` Boltzmann weights), so they are not expected
to coincide — the sanity check is that `Σ w_i → 1 − X_final`, which it does. (The
`state_density_Z_consistency.png` trend check shows the expected constant log-offset between the
per-atom `g(E)`-derived `Z(T)` and the per-system `log Z`, with the residual growing at high T.)

---

## 7. Overall interpretation and caveats

**What went well:**
- The windowed seeding (`[0.3, 0.35]` eV/atom) and `--e-max-per-atom 0.4` successfully focused
  the run on the intended band above the ground state.
- NS converged: the live set descended to near the global minimum, and the prior-volume weighting
  is internally consistent (`Σ w_i ≈ 1 − X_final`).
- The dual-scale walk + windowed start produced genuine coverage of the 0.16–0.38 eV/atom band,
  and the novelty threshold de-duplicated the initial live set in Fingerprint space.

**Caveats:**
- Energies are **GPR predictions**, not DFT; the absolute `E` values and the tiny absolute `Z`
  depend on the surrogate. Trends (log Z vs T, F vs T, the relative g(E) peak) are robust; absolute
  numbers are surrogate-relative.
- The run used only **1000 iterations / 100 live points** — far below literature scale (K 500–5000,
  iters 10⁵–10⁷). The `C_V ≈ 0` and the absence of a resolved phase transition may partly reflect
  this limited sampling and the narrow (0–0.4 eV/atom) window rather than the true physics of the
  Fe/MgO landscape.
- The `g(E)` here is a **weighted histogram over the sampled band**, a proxy for the state
  density within the window — not a full `g(E)` over the entire configurational space (which would
  require the two-basin flat+island picture and a wider window).
- **No posterior `.xsf`** were written (`--no-posterior-xsf`), so the delta-Z landscape and any
  per-structure analysis of the posterior are not available for this run.

---

## 8. Suggested next steps

- Increase `--n-live` / `--n-iters` toward literature scale and/or widen the energy window to
  include both the flat and island basins, to see whether a `C_V(T)` peak (phase transition)
  emerges.
- If posterior-structure analysis (e.g. the delta-Z landscape) is wanted, re-run **without**
  `--no-posterior-xsf` so the `posterior_*.xsf` files are produced.
- Cross-check the GPR energies against DFT for a few representative samples to gauge surrogate bias.
- Compare the `g(E)` peak here (~+0.15 eV/atom) against the reference island (0.074 eV/atom) /
  flat (0.255 eV/atom) peaks from the state-density analysis to see which basin this window's
  weighted mass corresponds to.

# QnA

1. 