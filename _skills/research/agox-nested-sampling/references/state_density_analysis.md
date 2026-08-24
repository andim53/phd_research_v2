# Post-run state-density / landscape / Boltzmann analysis + special sampling prior

Captured 2026-08 from the multi-seed Fe/MgO nested-sampling work in
`/home/think/Desktop/research/_run/8_nested_sampling/`. Two additions that extend the
base nested-sampling recipe in SKILL.md: a **deposition-species-only prior perturbation**
and an **automatic state-density / landscape / probability post-analysis**.

## 1. Perturb only the deposition species (NOT the whole cell)

Original bug: `sample_from_prior()` added Gaussian noise to ALL atoms' positions
(`base.positions += noise`, shape (75,3)). Even a 0.01 Å noise on the fixed Mg/O
substrate pushed the Fingerprint GPR off the training manifold → unphysical (>1e4 eV)
extrapolation, which then had to be filtered.

Correction (deliberate user request): perturb **only** the deposition element.

```python
# in NestedSampler.__init__
symbols = np.array(db_structures[0].get_chemical_symbols())
self.perturb_indices = np.where(np.isin(symbols, [perturb_symbols]))[0]  # perturb_symbols="Fe"

# in sample_from_prior()
if self.perturb > 0:
    noise = self.rng.normal(0, self.perturb, (len(self.perturb_indices), 3))
    base.positions[self.perturb_indices] += noise   # substrate atoms stay fixed
```

- Compute `perturb_indices` once (uniform-composition dataset) and reuse every draw.
- Verify with a tiny check: `(s.positions[fe_idx] != a.positions[fe_idx]).any()` True,
  `np.allclose(s.positions[mg_idx], a.positions[mg_idx])` True.
- CLI: `--perturb-symbols Fe` (default). `--perturb 0` = pure DB resampling, no noise.

## 2. Automatic state-density / landscape / Boltzmann analysis

`run_nested_sampling.py` now calls `analyze_state_density(...)` (module
`nested_sampling/state_density.py`) after `sampler.save()`. Logic ported from
`_run/9_novelFilter/run_analysis_thresholds.py`. Produces, for the **training** set AND
the **posterior** set:

- `conf_space.png` — PCA on Fingerprint descriptors (top eigenvector of covariance) vs
  per-atom relative energy, + KDE state-density panel. Reuses
  `scripts/plot_structure_landscape` from `_analysist/scripts` (add `_analysist`,
  `_analysist/scripts` to sys.path).
- `binding_probability_vs_temperature.png` — Boltzmann P(E)=rho(E)·exp(-dE/kbT)/Z at
  TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425] K.
- `comparison_state_density.png` — overlaid KDE curves (training vs posterior) on a
  common per-atom-relative-energy axis (density-only panel, pass energies as a dict
  `{"Training":..., "Posterior":...}` and `plot_density_only=True`).

### Energy basis
`analyze_state_density(posterior_structures, training_structures, gpr, output_dir, ...)`
recomputes energies with `gpr.predict_energy` so both sets share one surrogate basis.
`predict_energies()` keeps only physical (|E| < 1e4 eV) samples, preserving array order.
Both sets are then shifted to a common minimum and divided by atom count
(`(E - common_min) / num_atoms`) so the comparison axis is a true eV/atom baseline.

### Standalone re-analysis (no GPR retrain)
To re-plot a finished run without re-training:
`run_nested_sampling.py --analyze-only <run_output_dir> --output <dest>`.
- Requires the run dir to have `posterior_structures/posterior_*.xsf` (ALL of them) +
  `posterior_summary.csv` (rank, energy_eV, weight, log_weight). The sampler's `save()`
  writes both (all posterior XSF + summary) since 2026-08 — older outputs only have the
  top-20 XSFs and no summary, so re-analyzing them fails with a clear FileNotFoundError.
- `analyze_saved_output(run_output_dir, training_structures, training_energies, output_dir, ...)`
  loads posterior from saved XSFs + summary CSV, training from the DB (DFT energies), no GPR.

## 3. Degenerate-KDE guard (do not skip)

`scipy.stats.gaussian_kde` raises `LinAlgError` ("data appears to lie in a
lower-dimensional subspace") if a set has < 2 distinct energy values — e.g. a tiny/synthetic
posterior where every GPR energy came out identical. Guard every set before plotting:

```python
def _is_degenerate(rel):
    return len(np.unique(np.round(rel, 6))) < 2
# skip make_landscape / make_probability / comparison for any degenerate set, with a warning
```
This is a defensive guard, not a symptom of broken sampling — the real 1297-structure
training set always has plenty of distinct energies.

## 4. Plotting notes / gotchas
- Set `matplotlib.use('Agg')` before importing the plotting stack.
- `plot_structure_landscape` writes `conf_space.png` (and optionally `z_vs_energy_correlation.png`);
  for the comparison panel renames the produced `conf_space.png` to the comparison name.
- Keep `_ANALYSIST` and `_ANALYSIST/scripts` on sys.path or the shared plot function import
  (`from scripts.plot_structure_landscape import ...`) fails.