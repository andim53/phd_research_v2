# DISCUSSION — Run b10_femgo_walk_emax04_exclworst_noxsf_novelty (iter5000)

Run: `1_runs/b10_femgo_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `2_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter5000/`
Analysis outputs: this directory (`2_analysist/b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter5000/`)
Script: `2_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `2_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter5000 \
    --outdir b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter5000 \
    --n-atoms 75
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 75` = atoms per structure (Fe/MgO) for the per-atom relative-energy units of the state density.

This document discusses the results of the temperature-free nested-sampling (NS) run on the
plain Fe/MgO (no-Boron) system, using b9's treatment (temperature-free; `--e-max-per-atom 0.4`;
window `[0.3, 0.35]`; `--walk` with `--walk-exclude-worst`; `--no-posterior-xsf`;
`--novelty-threshold 1.0`) at **`--n-iters 5000`**, `--n-live 100`,
`--temperatures 100,200,300,500,1000 K`.

> Note: this run was submitted with `--no-posterior-xsf`, so no `posterior_*.xsf` files exist;
> the delta-Z landscape cannot be reproduced here.

---

## 1. What was run and what the CSVs contain

- **`samples.csv`** (5000 rows): the discarded (worst) samples, one per NS iteration, with
  `iteration`, `energy_eV` (GPR-predicted absolute energy), and `prior_weight`
  (`w_i = X_{i-1} − X_i`, the prior-volume shell weight).
- **`final_live_energies.csv`** (100 rows): the live-set energies at termination (`n_live=100`).
- **`thermodynamics.csv`** (5 rows): `T`, `β`, `log Z`, `Z`, and `F = −k_B T ln Z`, from the
  temperature-free post-processing (`evaluate(β)`).

The energies are the **GPR-predicted** energies of the surrogate trained on the
`--e-max-per-atom 0.4` filtered dataset (1158 of 1297 Fe/MgO structures).

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−436.87 .. −407.13 eV` (weighted mean `−413.51 eV`).

**Relative to the global minimum** (best live energy `−436.90 eV`, ~75 atoms):
- lowest discarded sample ≈ `+0.0004 eV/atom`
- highest discarded sample ≈ `+0.397 eV/atom`

The sampler operated across the targeted band above the ground state (windowed start at
`[0.30, 0.35]` eV/atom, `--e-max-per-atom 0.4` cap), descending to very near the minimum.

**Final live set:** `−436.90 .. −433.87 eV` (mean `−435.3 eV`). The live set descended to near the
global minimum region — the expected NS convergence behaviour.

**Commentary on the walk + novelty:** the dual-scale `--walk` (50 steps, small 0.05 Å / large
0.40 Å, `--walk-exclude-worst`) was the primary per-step move; `--novelty-threshold 1.0`
de-duplicated the initial live set. The samples span a ~30 eV band, giving broad coverage.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`. The **weighted peak** is at `≈ +0.305 eV/atom` above the
ground state (`state_density_gE.png`, peak `g ≈ 16.8 config./eV`).

Interpretation: most sampled probability mass sits around `+0.31 eV/atom` above the minimum — in
the mid-to-upper part of the window (the island region), which is the classic NS behaviour: the
discarded samples accumulate where there is the most configuration-space volume. The absolute
`Z` values are tiny because the evidence is normalized to the very-low prior-volume absolute scale
of this surrogate landscape; the **relative** trend with T is the meaningful physics.

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−436.90 .. −433.87 eV` (`live_energy_hist.png`).
The live set is clustered near the low-energy end of the window — the run reached the
ground-state basin, as expected when NS has converged.

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −46.41 | 7.01e−21 | 0.400 |
| 200 | −42.84 | 2.48e−19 | 0.738 |
| 300 | −41.54 | 9.07e−19 | 1.074 |
| 500 | −40.42 | 2.80e−18 | 1.742 |
| 1000 | −39.42 | 7.59e−18 | 3.397 |

- **`log Z` rises monotonically with T** (`−46.4 → −39.4`), and `Z` grows — the expected
  temperature dependence of the partition function.
- **`F = −k_B T ln Z` rises** with T (`0.40 → 3.40 eV`), consistent with a more positive free
  energy as thermal agitation increases.
- **Heat capacity `C_V ≈ 0`** (values ~10⁻⁴–10⁻¹⁹ eV/K) — `log Z` vs `β` is nearly linear over
  100–1000 K, so its second derivative is ~0. This means **no strong first-order phase
  transition / latent-heat peak is resolved** in this temperature range for this surrogate and
  window; the system behaves like a single-basin, weakly-entropic ensemble here.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 1.000000` over the 5000 discarded samples (`samples_cumulative_Z.png`). In NS the
total prior volume removed should be `1 − X_final`, where `X_final = exp(−iters/n_live) =
exp(−5000/100) = exp(−50) ≈ 2e−22`. So `sum(w_i) ≈ 1`, which **matches** — the prior volume is
essentially fully consumed at 5000 iterations (X_final is astronomically small), so the
bookkeeping is internally consistent and the trace is numerically sound.

---

## 7. Overall interpretation and caveats

**What went well:**
- The windowed seeding + `--e-max-per-atom 0.4` focused the run on the intended band.
- NS converged: the live set descended to near the global minimum, and the prior-volume weighting
  is internally consistent (`Σ w_i ≈ 1`).
- The walk + novelty threshold gave broad coverage of the band.

**Convergence note (this is the iteration-sweep run):** `log Z` here (−46.4 → −39.4) is
essentially identical to the iter10000 and iter20000 runs — strong evidence that the evidence has
already converged by 5000 iterations for this setup (larger `--n-iters` only shrinks the already-
negligible `X_final`). See the sibling DISCUSSION.md files for iter10000/iter20000.

**Caveats:**
- Energies are **GPR predictions**, not DFT; absolute `E`/`Z` values are surrogate-relative.
- `g(E)` is a weighted histogram over the sampled band, a proxy — not a full state density over
  the entire configurational space.
- No posterior `.xsf` (`--no-posterior-xsf`), so no per-structure/delta-Z analysis.

---

## 8. Suggested next steps

- Compare the `g(E)` peak here (~+0.31 eV/atom) against the reference island (0.074 eV/atom) /
  flat (0.255 eV/atom) peaks to identify which basin the weighted mass corresponds to.
- Since `log Z` is converged across 5000/10000/20000, further iteration increases add little;
  consider widening the window or raising `--n-live` if finer phase-transition features are needed.
- Cross-check GPR energies against DFT on a few representative samples to gauge surrogate bias.
