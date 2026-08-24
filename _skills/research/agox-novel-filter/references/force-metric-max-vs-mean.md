# Force metric: max vs mean over mobile Fe atoms

Session-specific detail for `run_force_novel_filter.py` in `_run/9_novelFilter`.
Complement to `force-filter-and-minima-verification.md` — covers the selectable
`--force-metric` option added to the force filter.

## The option

`run_force_novel_filter.py` accepts `--force-metric {max,mean}` (default `max`).
It selects how the Fe-atom residual forces are aggregated into the per-structure
score used for filtering. The 50-atom MgO substrate is ALWAYS excluded (only the
25 mobile Fe atoms are measured).

```python
def fe_forces(atoms, forces, metric="max"):
    fe_idx = [i for i, s in enumerate(atoms.get_chemical_symbols()) if s == "Fe"]
    if not fe_idx:
        return np.nan
    mag = np.abs(forces[fe_idx])
    return float(np.mean(mag)) if metric == "mean" else float(np.max(mag))
```

- `max`  (default) — worst-atom residual force. Strictest: a structure passes
  only if EVERY Fe atom is below the threshold.
- `mean` — average residual force. A single badly-converged Fe atom is tolerated
  if the rest are relaxed.

The metric is written into each `force_<v>/filter_summary.txt` and the summary
CSV column is renamed to `max_F_eV_per_Ang` or `mean_F_eV_per_Ang`.

## Measured distributions (Fe/MgO, 75 atoms, 1297 structures)

- max|Fe force|: min 0.176, median ~1.30, max 10.08 eV/A
- mean|Fe force|: min 0.045, median ~0.33, max 3.20 eV/A

`max` is far stricter than `mean` on this data.

## Physical consequence (verified)

At threshold 0.5 eV/A:
- `--force-metric max` → keeps 27 structures; global minimum (-436.9) EXCLUDED.
- `--force-metric mean` → keeps 1059 structures; global minimum INCLUDED (its
  mean Fe force ≈ 0.23 eV/A).

The global-minimum geometry carries large residual forces on a few Fe atoms even
though the average is small. Choose the metric deliberately:
- `max`  = "every atom near its local minimum" (strict local-minimum surrogate).
- `mean` = "the structure on average near a minimum" (tolerates a few hot atoms).

## Interpretation for partition-function work

If the goal is a minima-only partition function over structures that are close
to converged DFT minima, `max` is the safer proxy (a single unrelaxed atom means
the geometry is not a true minimum). Use `mean` only when you want to keep
structures that are relaxed on average and are willing to accept a few
poorly-converged atoms.

## Run examples

```bash
# default (max)
/home/think/miniconda3/envs/agox_v2/bin/python run_force_novel_filter.py --outdir ./force_output
# mean metric
/home/think/miniconda3/envs/agox_v2/bin/python run_force_novel_filter.py \
    --outdir ./force_output_mean --force-metric mean
```
