# DISCUSSION — Run b10_femgo_walk_emax04_exclworst_noxsf_novelty (iter20000)

Run: `_runs/b10_femgo_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000/`
Analysis outputs: this directory (`_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000/`)
Script: `_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outdir b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --n-atoms 75
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 75` = atoms per structure (Fe/MgO) for the per-atom relative-energy units of the state density.

---

## NS vs dataset state-density comparison

The figure below overlays the **NS g(E)** (prior-weight-weighted histogram of the 20,000
discarded samples) against the **GPR+LCB g(E)** (gaussian KDE of the b10 dataset's DFT energies),
both peak-normalized to 1 for a direct shape comparison.

![compare_state_density_gE.png](compare_state_density_gE.png)

**Command + parameters that produced it** (run from `_analysist/`):

```bash
/home/think/miniconda3/envs/agox_v2/bin/python compare_state_density_gE.py \
    --run b10_femgo_walk_emax04_exclworst_noxsf_novelty \
    --ns-output analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --n-atoms 75 --figsize 6 \
    --outname compare_state_density_gE.png
```

Parameters: `--run` = b10 run dir (contains `dataset/` and the analysis dir); `--ns-output` = the
analysis dir name (holds the ns_output `samples.csv` + this PNG); `--n-atoms 75` = atoms per
structure (Fe/MgO); `--figsize 6` = square figure size in inches; `--outname` = the output
filename. The dataset KDE uses **all** dataset structures (unfiltered); the plot x-range is capped
at the NS max E−E_min.

**Resulting peaks:** NS g(E) at +0.306 eV/atom (abs g 18.1); dataset KDE at +0.076 eV/atom
(abs g 4.9). The NS weighted ensemble peaks high (~0.31 eV/atom) while the raw dataset KDE peaks
low (~0.08 eV/atom) — NS weights configuration-space volume (which sits higher), whereas the
dataset is densest near the lower-energy region.

---

This document discusses the results of the temperature-free nested-sampling (NS) run on the
plain Fe/MgO (no-Boron) system, using b9's treatment (temperature-free; `--e-max-per-atom 0.4`;
window `[0.3, 0.35]`; `--walk` with `--walk-exclude-worst`; `--no-posterior-xsf`;
`--novelty-threshold 1.0`) at **`--n-iters 20000`**, `--n-live 100`,
`--temperatures 100,200,300,500,1000 K`.

> Note: this run was submitted with `--no-posterior-xsf`, so no `posterior_*.xsf` files exist;
> the delta-Z landscape cannot be reproduced here.

---

## 1. What was run and what the CSVs contain

- **`samples.csv`** (20000 rows): the discarded (worst) samples, one per NS iteration, with
  `iteration`, `energy_eV` (GPR-predicted absolute energy), and `prior_weight`
  (`w_i = X_{i-1} − X_i`, the prior-volume shell weight).
- **`final_live_energies.csv`** (100 rows): the live-set energies at termination (`n_live=100`).
- **`thermodynamics.csv`** (5 rows): `T`, `β`, `log Z`, `Z`, and `F = −k_B T ln Z`.

The energies are the **GPR-predicted** energies of the surrogate trained on the
`--e-max-per-atom 0.4` filtered dataset (1158 of 1297 Fe/MgO structures).

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−436.89 .. −407.06 eV` (weighted mean `−413.51 eV`).

**Relative to the global minimum** (best live energy `−436.91 eV`, ~75 atoms):
- lowest discarded sample ≈ `+0.0003 eV/atom`
- highest discarded sample ≈ `+0.398 eV/atom`

The sampler operated across the targeted band above the ground state (windowed start at
`[0.30, 0.35]` eV/atom, `--e-max-per-atom 0.4` cap), descending to very near the minimum.

**Final live set:** `−436.91 .. −433.35 eV`. The live set descended to near the global minimum
region — the expected NS convergence behaviour.

**Commentary on the walk + novelty:** the dual-scale `--walk` (50 steps, small 0.05 Å / large
0.40 Å, `--walk-exclude-worst`) was the primary per-step move; `--novelty-threshold 1.0`
de-duplicated the initial live set.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`. The **weighted peak** is at `≈ +0.306 eV/atom` above the
ground state (`state_density_gE.png`, peak `g ≈ 18.1 config./eV`).

Interpretation: most sampled probability mass sits around `+0.31 eV/atom` above the minimum —
consistent with the 5000- and 10000-iteration runs, confirming the weighted ensemble has fully
stabilised (the peak is only slightly sharper here due to more samples in the band).

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−436.91 .. −433.35 eV` (`live_energy_hist.png`).
The live set is clustered near the low-energy end of the window — the run reached the
ground-state basin, as expected when NS has converged.

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −46.41 | 7.00e−21 | 0.400 |
| 200 | −42.84 | 2.48e−19 | 0.738 |
| 300 | −41.54 | 9.07e−19 | 1.074 |
| 500 | −40.42 | 2.80e−18 | 1.742 |
| 1000 | −39.42 | 7.59e−18 | 3.397 |

- **`log Z` rises monotonically with T** (`−46.4 → −39.4`), and `Z` grows.
- **`F = −k_B T ln Z` rises** with T (`0.40 → 3.40 eV`).
- **Heat capacity `C_V ≈ 0`** — `log Z` vs `β` is nearly linear over 100–1000 K, so no strong
  first-order phase transition / latent-heat peak is resolved in this range.

---

## 5b. NS Boltzmann probability vs energy

The figure below plots the **NS Boltzmann probability P(E)** vs per-atom relative energy
`(E − E_ref)/n_atoms` for the five temperatures (100, 200, 300, 500, 1000 K), computed
**directly from the NS result** (the prior weights in `samples.csv`):

![binding_probability_vs_temperature.png](binding_probability_vs_temperature.png)

For each temperature `P_i(T) = w_i·exp(−β(E_i − E_ref))/Z(T)` with `β = 1/k_B T` and
`Z(T) = Σ_i w_i·exp(−β(E_i − E_ref))`.

**Command + parameters that produced it** (run from `_analysist/`):

```bash
/home/think/miniconda3/envs/agox_v2/bin/python plot_ns_boltzmann_prob.py \
    --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outdir b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
    --outname binding_probability_vs_temperature.png \
    --n-atoms 75
```

Parameters: `--ns-output` = the run's temperature-free output dir (samples.csv);
`--outdir` = this analysis dir; `--outname` = the output PNG filename;
`--n-atoms 75` = atoms per structure (Fe/MgO); default temperatures 100–1000 K.

**Result:** `Z(T)` grows with T (`7.9e−20 → 9.7e−18`), so at higher T the probability
distribution broadens and shifts toward higher energy — the expected thermal excitation
behaviour of the NS weighted ensemble.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 1.000000` over the 20000 discarded samples (`samples_cumulative_Z.png`).
`X_final = exp(−iters/n_live) = exp(−20000/100) = exp(−200) ≈ 0`, so `sum(w_i) ≈ 1`, which
**matches** — the prior volume is fully consumed. Bookkeeping is internally consistent.

---

## 7. Overall interpretation and caveats

**Convergence note (iteration sweep):** `log Z` here (−46.4 → −39.4) is essentially identical to
the iter5000 and iter10000 runs (differences ≲ 0.002 nats). Together with the stable `g(E)` peak
(~+0.31 eV/atom), this confirms the evidence is fully converged by 5000 iterations for this
setup; 20000 iterations only further shrink the already-negligible `X_final`.

**Caveats:**
- Energies are **GPR predictions**, not DFT; absolute `E`/`Z` values are surrogate-relative.
- `g(E)` is a weighted histogram over the sampled band, a proxy.
- No posterior `.xsf` (`--no-posterior-xsf`), so no per-structure/delta-Z analysis.

---

## 8. Suggested next steps

- Compare the `g(E)` peak (~+0.31 eV/atom) against the reference island (0.074 eV/atom) / flat
  (0.255 eV/atom) peaks.
- Since `log Z` is converged across 5000/10000/20000, further iteration increases add little;
  consider widening the window or raising `--n-live` for finer phase-transition features.
