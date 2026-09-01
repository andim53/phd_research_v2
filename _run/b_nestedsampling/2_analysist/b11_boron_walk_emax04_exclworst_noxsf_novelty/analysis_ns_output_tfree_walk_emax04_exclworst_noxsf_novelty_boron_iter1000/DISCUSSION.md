# DISCUSSION — Run b11_boron_walk_emax04_exclworst_noxsf_novelty (iter1000)

Run: `1_runs/b11_boron_walk_emax04_exclworst_noxsf_novelty`
Data analysed: `2_analysist/b11_boron_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter1000/`
Analysis outputs: this directory (`2_analysist/b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter1000/`)
Script: `2_analysist/analyze_tfree_outputs.py`

## Analysis reproduction (command used)

Run from `2_analysist/`:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
    --data b11_boron_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter1000 \
    --outdir b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter1000 \
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
at **`--n-iters 1000`**, `--n-live 100`, `--temperatures 100,200,300,500,1000 K`.

> Note: this run was submitted with `--no-posterior-xsf`, so no `posterior_*.xsf` files exist;
> the delta-Z landscape cannot be reproduced here.

---

## 1. What was run and what the CSVs contain

- **`samples.csv`** (1000 rows): the discarded (worst) samples, one per NS iteration, with
  `iteration`, `energy_eV` (GPR-predicted absolute energy), and `prior_weight`
  (`w_i = X_{i-1} − X_i`, the prior-volume shell weight).
- **`final_live_energies.csv`** (100 rows): the live-set energies at termination (`n_live=100`).
- **`thermodynamics.csv`** (5 rows): `T`, `β`, `log Z`, `Z`, and `F = −k_B T ln Z`.

The energies are the **GPR-predicted** energies of the surrogate trained on the
`--e-max-per-atom 0.4` filtered boron dataset.

---

## 2. Sampling: discarded-sample descent and the energy window

**Range of discarded samples:** `−464.33 .. −448.84 eV` (weighted mean `−453.22 eV`).

**Relative to the global minimum** (best live energy `−481.63 eV`, 82 atoms):
- lowest discarded sample ≈ `+0.211 eV/atom`
- highest discarded sample ≈ `+0.400 eV/atom`

The discarded samples sit in the `0.21–0.40 eV/atom` band — the run started in the windowed
`[0.30, 0.35]` band and descended only partway.

**Final live set:** `−481.63 .. −464.33 eV`. The live set is **still spread out** — it spans from
near the global minimum (−481.6) up to −464.3. This is the key signature that **1000 iterations
is NOT enough** for the boron system: at termination the sampler still has live points high above
the minimum, i.e. the top-down pass has not yet drained to the ground state.

**Commentary on the walk + novelty:** the dual-scale `--walk` (50 steps, small 0.05 Å / large
0.40 Å, `--walk-exclude-worst`) was the primary per-step move; `--novelty-threshold 1.0`
de-duplicated the initial live set.

---

## 3. Prior-weight histogram (configurational state-density proxy)

The `prior_weight`-weighted energy histogram (`samples_weighted_histogram.png`) is a proxy for the
configurational state density `g(E)`. The **weighted peak** is at `≈ +0.168 eV/atom` above the
ground state (`state_density_gE.png`, peak `g ≈ 16.8 config./eV`).

Interpretation: most sampled probability mass sits around `+0.17 eV/atom` — but because the run
only descended partway (live set still spread to −464 eV), this g(E) reflects an **incomplete**
portion of the band and should be treated cautiously (compare with the iter5000/10000/20000 runs,
which are converged).

---

## 4. Final live-point distribution

`final_live_energies.csv` (100 points) spans `−481.63 .. −464.33 eV` (`live_energy_hist.png`).
The live set is **not** yet clustered at the bottom — it is spread over a ~17 eV range. This
confirms the run terminated before full descent.

---

## 5. Thermodynamics: partition function, free energy, heat capacity

From `thermodynamics.csv`:

| T (K) | log Z | Z | F = −k_B T ln Z (eV) |
|---|---|---|---|
| 100 | −27.94 | 7.37e−13 | 0.241 |
| 200 | −21.27 | 5.78e−10 | 0.367 |
| 300 | −19.05 | 5.33e−09 | 0.493 |
| 500 | −17.27 | 3.16e−08 | 0.744 |
| 1000 | −15.94 | 1.20e−07 | 1.373 |

- **`log Z` rises monotonically with T** (`−27.9 → −15.9`).
- **`F = −k_B T ln Z` rises** with T (`0.24 → 1.37 eV`).
- **Heat capacity `C_V ≈ 0`** — no resolved phase transition in this range.

> **CAUTION:** these `log Z` values (−27.9 → −15.9) are much *less negative* than the converged
> 5000/10000/20000 runs (−52.8 → −38.8) of the same system. Because the 1000-iteration run did not
> descend to the ground state, its evidence is **underestimated** (it has not integrated the
> low-energy probability mass). Do not compare these numbers directly against the converged runs.

---

## 6. Cumulative weighted evidence (sanity check)

`sum(w_i) = 0.99995` over the 1000 discarded samples (`samples_cumulative_Z.png`), i.e.
`1 − X_final` with `X_final = exp(−1000/100) = exp(−10) ≈ 4.5e−5`. Internally consistent — but this
only confirms the *bookkeeping*, not that the run converged.

---

## 7. Overall interpretation and caveats

**Key finding:** at `--n-iters 1000`, the boron run is **NOT converged** — the live set is still
spread up to −464 eV (≈ +0.21 eV/atom above the min) at termination, and `log Z` (−27.9 → −15.9)
is well below (less negative than) the converged value (−52.8 → −38.8). This differs from the
plain Fe/MgO b10 run, where 5000 iterations was already converged — the boron (82-atom) landscape
needs more iterations to drain to the ground state.

**Caveats:**
- Energies are **GPR predictions**, not DFT; absolute `E`/`Z` values are surrogate-relative.
- `g(E)` is a weighted histogram over the sampled band, a proxy — and here the band is incomplete.
- No posterior `.xsf` (`--no-posterior-xsf`).

---

## 8. Suggested next steps

- Treat the iter1000 result as an **incomplete** run; the reliable boron thermodynamics is in the
  iter5000/10000/20000 runs (see their DISCUSSION.md).
