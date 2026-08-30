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
