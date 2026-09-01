# DISCUSSION — Run b11_boron_walk_emax04_exclworst_noxsf_novelty (iter20000)

Run: `_runs/b11_boron_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `_analysist/b11_boron_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000/`
Analysis outputs: this directory (`_analysist/b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000/`)
Script: `_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b11_boron_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000 \
    --outdir b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000 \
    --n-atoms 82
```

Parameters: `--data` = the run's temperature-free output dir (samples.csv,
final_live_energies.csv, thermodynamics.csv); `--outdir` = this analysis dir;
`--n-atoms 82` = atoms per structure (B-doped Fe/MgO: Fe25Mg25O25B7) for the per-atom
relative-energy units of the state density.

This document discusses the results of the temperature-free nested-sampling (NS) run on the
**B-doped Fe/MgO** system (Fe25Mg25O25B7, 82 atoms, 5 seeds), using b9's treatment applied to
boron (temperature-free; `--e-max-per-atom 0.4`; window `[0.3, 0.35]`; `--walk` with
`--walk-exclude-worst`; `--no-posterior-xsf`; `--novelty-threshold 1.0`; `--perturb-symbols Fe,B`)
at **`--n-iters 20000`**, `--n-live 100`, `--temperatures 100,200,300,500,1000 K`.

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
`--e-max-per-atom 0.4` filtered boron dataset.

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−481.70 .. −448.82 eV` (weighted mean `−453.22 eV`).

**Relative to the global minimum** (best live energy `−481.75 eV`, 82 atoms):
- lowest discarded sample ≈ `+0.0001 eV/atom`
- highest discarded sample ≈ `+0.401 eV/atom`

The sampler operated across the full band above the ground state, descending all the way to the
minimum.

**Final live set:** `−481.75 .. −477.70 eV` — a tight cluster near the global minimum.

**Commentary on the walk + novelty:** the dual-scale `--walk` (50 steps, small 0.05 Å / large
0.40 Å, `--walk-exclude-worst`) was the primary per-step move; `--novelty-threshold 1.0`
de-duplicated the initial live set.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`. The **weighted peak** is at `≈ +0.341 eV/atom` above the
ground state (`state_density_gE.png`, peak `g ≈ 12.3 config./eV`).

Interpretation: most sampled probability mass sits around `+0.34 eV/atom` above the minimum —
consistent with the 5000- and 10000-iteration runs.

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−481.75 .. −477.70 eV` (`live_energy_hist.png`).
The live set is clustered near the low-energy end of the window — the run reached the
ground-state basin, as expected when NS has converged.

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −53.38 | 6.58e−24 | 0.460 |
| 200 | −45.58 | 1.60e−20 | 0.786 |
| 300 | −42.84 | 2.47e−19 | 1.108 |
| 500 | −40.60 | 2.34e−18 | 1.749 |
| 1000 | −38.81 | 1.39e−17 | 3.345 |

- **`log Z` rises monotonically with T** (`−53.4 → −38.8`).
- **`F = −k_B T ln Z` rises** with T (`0.46 → 3.34 eV`).
- **Heat capacity `C_V ≈ 0`** — no strong first-order phase transition resolved in this range.

> These `log Z` values are essentially identical to the 5000- and 10000-iteration runs
> (differences ≲ 0.01 nats) — the boron evidence is fully converged by 5000 iterations.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 1.000000` over the 20000 discarded samples (`samples_cumulative_Z.png`).
`X_final = exp(−20000/100) = exp(−200) ≈ 0`, so `sum(w_i) ≈ 1`, which **matches** — the prior
volume is fully consumed. Bookkeeping is internally consistent.

---

## 7. Overall interpretation and caveats

**Key finding (convergence):** `log Z` here (−53.4 → −38.8) matches the 5000- and 10000-iteration
runs — the boron evidence is **converged by 5000 iterations**; 20000 iterations only further shrink
the already-negligible `X_final`. Contrast with the 1000-iteration run, which was incomplete.

**Caveats:**
- Energies are **GPR predictions**, not DFT; absolute `E`/`Z` values are surrogate-relative.
- `g(E)` is a weighted histogram over the sampled band, a proxy.
- No posterior `.xsf` (`--no-posterior-xsf`).

---

## 8. Suggested next steps

- Compare the `g(E)` peak (~+0.34 eV/atom) against the reference island (0.074 eV/atom) / flat
  (0.255 eV/atom) peaks to identify the basin.
- The reliable boron thermodynamics is in this run and the iter5000/iter10000 runs (all converged).
