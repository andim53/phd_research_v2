# DISCUSSION — Run b6_tfree_walk_emax04 (plain Fe/MgO, temperature-free NS)

Run: `_runs/b6_tfree_walk_emax04`
Data analysed: `_analysist/b6_tfree_walk_emax04/ns_output_tfree_walk_emax04/`
Analysis outputs: this directory (`_analysist/b6_tfree_walk_emax04/analysis_ns_output_tfree_walk_emax04/`)
Script: `_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b6_tfree_walk_emax04/ns_output_tfree_walk_emax04 \
    --outdir b6_tfree_walk_emax04/analysis_ns_output_tfree_walk_emax04 \
    --n-atoms 75
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 75` = atoms per structure (Fe/MgO) for the per-atom relative-energy
units of the state density.

This document discusses the results of the temperature-free nested-sampling (NS) run on the
plain Fe/MgO (no-Boron) system, using the flags `--e-max-per-atom 0.4`,
`--e-window-lo 0.3 --e-window-hi 0.35 --e-window-max-attempts 1000`,
`--walk --walk-steps 50 --walk-small 0.05 --walk-large 0.40 --walk-mode both`,
`--n-live 100 --n-iters 1000`, `--temperatures 100,200,300,500,1000 K`.

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

**Range of discarded samples:** `−430.94 .. −410.73 eV` (weighted mean `−419.50 eV`).

**Relative to the global minimum** (taken as the best live energy `−436.69 eV`, ~75 atoms):
- lowest discarded sample ≈ `+0.077 eV/atom`
- highest discarded sample ≈ `+0.346 eV/atom`

This confirms the run behaved as designed: the sampler operated **inside the targeted
0.08–0.35 eV/atom window** above the ground state — consistent with `--e-window-lo 0.3` /
`--e-window-hi 0.35` (the initial live set was pinned to that band) and `--e-max-per-atom 0.4`
(the dataset cap). In other words, the run **started near 0.3 eV/atom and descended toward the
ground state**, exactly the intended "windowed start" behaviour.

**Final live set:** `−436.69 .. −430.94 eV` (mean `−432.60 eV`). The live set has descended close
to the global minimum region, which is the expected NS convergence behaviour (the worst live point
keeps dropping as the prior volume shrinks).

**Commentary on the walk:** the dual-scale `--walk` (50 steps, small 0.05 Å / large 0.40 Å) was
used as the primary per-step move in `sample_constrained`, with the `--perturb 0.01` prior draw
handling initialization and fallback. The samples span a ~20 eV band, showing the sampler did
explore a range of configurations rather than collapsing to a single point — the walk plus windowed
seeding gave real coverage of the 0.08–0.35 eV/atom band.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`: each discarded sample contributes its prior-volume shell
`w_i` per unit energy. The **weighted peak** is at `≈ +0.154 eV/atom` above the ground state
(`state_density_gE.png`, peak `g ≈ 14.3 config./eV`).

Interpretation: most of the sampled probability mass sits around `+0.15 eV/atom` above the minimum
— not at the very ground state (which has almost zero prior volume by the end of the run) and not
at the top of the window. This is the classic NS behaviour: the discarded samples accumulate where
there is the most configuration-space volume, which here is in the higher-energy part of the
sampled window rather than at the single global-minimum structure. The `+0.15 eV/atom` peak is a
natural, physically meaningful feature of the weighted ensemble (not the unweighted minimum).

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−436.69 .. −430.94 eV` with mean `−432.60 eV`
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
| 100 | −40.09 | 3.89e−18 | 0.345 |
| 200 | −27.35 | 1.33e−12 | 0.471 |
| 300 | −23.10 | 9.29e−11 | 0.597 |
| 500 | −19.70 | 2.78e−09 | 0.849 |
| 1000 | −17.15 | 3.55e−08 | 1.478 |

- **`log Z` rises monotonically with T** (`−40 → −17`), and **`Z` grows** (`10⁻¹⁸ → 10⁻⁸`). This is
  the expected temperature dependence: higher T broadens the Boltzmann weight, so the partition
  function (total probability mass) increases. The absolute `Z` values are tiny because the
  evidence is normalized to the (very low prior-volume) absolute scale of this surrogate
  landscape — the **relative** trend with T is the meaningful physics.
- **Free energy `F = −k_B T ln Z` rises** with T (`0.35 → 1.48 eV`), consistent with
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
to coincide — the sanity check is that `Σ w_i → 1 − X_final`, which it does.

---

## 7. Overall interpretation and caveats

**What went well:**
- The windowed seeding (`[0.3, 0.35]` eV/atom) and `--e-max-per-atom 0.4` successfully focused the
  run on the intended band above the ground state.
- NS converged: the live set descended to near the global minimum, and the prior-volume weighting
  is internally consistent (`Σ w_i ≈ 1 − X_final`).
- The dual-scale walk + windowed start produced genuine coverage of the 0.08–0.35 eV/atom band.

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

---

## 8. Suggested next steps

- Increase `--n-live` / `--n-iters` toward literature scale and/or widen the energy window to
  include both the flat and island basins, to see whether a `C_V(T)` peak (phase transition)
  emerges.
- Cross-check the GPR energies against DFT for a few representative samples to gauge surrogate bias.
- Compare the `g(E)` peak here (~+0.15 eV/atom) against the reference island (0.074 eV/atom) /
  flat (0.255 eV/atom) peaks from the state-density analysis to see which basin this window's
  weighted mass corresponds to.
