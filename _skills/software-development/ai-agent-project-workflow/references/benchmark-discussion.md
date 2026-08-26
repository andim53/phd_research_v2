# Benchmark-result discussions (`DISCUSSION.md`)

The user's standing pattern for writing up a benchmark run is a full, per-graph
writeup grounded in the actual result numbers (JSON), not a summary of intent. This
applies to the Novelty-LCB / Regular-LCB EMT benchmark family (`73_novel_benchEMT`,
`74_novel_benchSweep`, and the extended grid under `_run/10_lcbnovel/_runs/`).

## File naming

- The user originally typoed the name as `DISUCCSION.md`; confirm the corrected spelling
  `DISCUSSION.md` via clarify (they chose the corrected name).

## Scope decision (clarify)

Before writing, confirm which graphs to cover. Only the benchmark-result plots count;
the `confinement_plot_*.png` files in the project root are generator search-box visuals,
NOT benchmark results — exclude them unless asked.

## Structure (full depth, per-graph)

For every graph/subplot cover four things, in this order:

1. **What it is** — the plot type and exactly what is plotted (axes, per-seed bars,
   grouped bar, heatmap, curves, what a value means).
2. **What it means** — the metric's physical/algorithmic interpretation.
3. **What it implies** — the concrete read from the actual numbers (cite them).
4. **Outcome** — the verdict for that panel.

Also include:
- A **setup section** (what was benchmarked, the config table, run counts).
- An **aggregate statistics** section computed from the results JSON (means/stds,
  per-seed table). Always recompute the numbers yourself from the JSON rather than
  trusting memory — use a quick parse/aggregate step.
- An **overall interpretation + verdict + caveats** section tying the panels together
  and noting limits (seed count, single-seed-per-combo, smooth vs rough landscape).

## Workflow for producing it

1. Read the benchmark script to know exactly what each plot shows (plot code is ground
   truth for "what it is").
2. Parse `benchmark_results.json` with a small script to get aggregate stats and
   per-seed/per-combo tables; verify key claims numerically.
3. Write the DISCUSSION.md, then optionally offer to append a LOG.md entry and commit.

## Novelty-LCB null-result insight (reusable for interpretation)

A recurring, non-obvious result: **`novelty_weight` (λ) can have NO measurable effect.**
Grounded in `novelty_lcb/acquisitor.py`:

- `kappa` enters `get_acquisition_calculator()` → the **LCB relaxation surface**
  `E − κ·σ` on which every candidate is pre-relaxed. This shapes the actual search
  trajectory.
- `novelty_weight` (λ) enters only `calculate_acquisition_function()` → the **discrete
  selection** `a(x) = σ + λ·Novelty`. Novelty is a min-distance with no force, so it
  cannot drive relaxation.
- Therefore, with a **single fixed seed** (identical candidate pool) and a smooth
  few-minima surface, λ never changes the winning candidate → the whole trajectory is
  byte-identical across λ (all_energies identical per kappa). The sweep (`74`) showed
  this: only kappa moved any metric; λ=0.0..2.0 gave identical results.

Implication: if λ appears inert, don't conclude it's useless in general — it is a
null result under that specific setup (single seed, smooth landscape). The fix is a
multi-seed sweep on a rough landscape (the real Fe/MgO surface).

Another recurring finding: on these EMT surfaces both Regular-LCB and Novelty-LCB waste
~97% of evaluations on duplicates (discovery saturates after 1–2 distinct minima), so
downstream dedup (`_run/9_novelFilter`) is essential before basin statistics.
