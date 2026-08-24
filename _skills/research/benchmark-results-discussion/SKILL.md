---
name: benchmark-results-discussion
description: Analyze benchmark results and write a DISCUSSION.md.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [analysis, benchmark, discussion, research, results, writing]
    related_skills: [simulation-analysis, grounded-citations]
---

# Benchmark-Results Discussion (DISCUSSION.md)

Reusable workflow for the recurring task "read the benchmark results and write a
DISCUSSION.md" — analyzing a benchmark/sweep run's output (a `results.json` + `*.png`
plots + a generator script) and producing a structured, code-grounded discussion.
Applies broadly (AGOX acquisition benchmarks, ML model sweeps, any experiment that
emits a JSON of metrics plus plots).

## Ground every number in the JSON — never eyeball a PNG

- The plots are summaries; the truth is the `*results.json`. Read it and recompute
  aggregates programmatically (numpy): distinct configs, duplicates, best energy,
  energy range, discovery saturation, duplicate rate (% of evals).
- Extract the parameters block too (kappa, weight, window, seed list, N iterations) so
  the discussion states the exact setup.
- Always print the *per-run / per-combo* table, not just means — small-N results
  (5 seeds, 1 seed per sweep combo) hide the spread and are the whole story.

## Explain WHY, not just WHAT — read the generating code + the algorithm

A discussion that only describes a graph is weak. Read the `.py` that produced the
plots AND the underlying algorithm source to ground the mechanism behind the numbers.
This turns a figure caption into an insight.

Worked example — a sweep null result. A kappa × novelty_weight sweep produced identical
metrics across all λ for every fixed kappa (byte-identical energy arrays). The code
explained it: `kappa` drives the continuous LCB relaxation surface `E − κ·σ` (affects
trajectory), while `novelty_weight` only weights a *discrete* selection score; the
novelty term has **no force** (min-distance, non-differentiable), and with one fixed
seed + a smooth few-minima surface it never changed the argmax → λ was inert.
Lesson: for acquisition-function benchmarks, distinguish parameters that shape the
*relaxation surface* (affect trajectory) from those that only re-rank a discrete
selection (can be inert).

## Detect degenerate / null results proactively

- If a swept parameter produces identical metrics (and identical per-combo energy
  arrays) across its whole range, call it a **null result under these conditions** — do
  not dress it up as "parameter X has no role in general." State the concrete reasons
  (single seed, smooth landscape, parameter has no force) and the follow-up that would
  settle it (multi-seed sweep on a rough landscape).
- Verify degeneracy programmatically (e.g. compare the full energy arrays across
  combos), don't just eyeball a heatmap.

## DISCUSSION.md structure (full-depth, per-graph)

For each graph, break into the same four labelled blocks:
- **What it is** — what the panel plots (bars/lines/heatmap, axes, color legend).
- **What it means** — the metric it encodes (diversity, optimality, redundancy, speed).
- **What it implies** — the physical/methodological reading of the actual numbers.
- **Outcome** — the takeaway for that graph.

Plus: (1) "What was benchmarked" setup table, (2) aggregate statistics table with a
per-run/per-combo breakdown, (3) one section per PNG covering its subplots, (4) an
"Overall interpretation" with outcome/verdict, implication for the real physics target,
caveats/limitations, and a bottom line. Flag duplicate rates explicitly.

## Clarify before writing (standing user rule)

This user requires confirming **filename**, **graph scope**, and **depth** before
writing. Ask via the clarify tool, then write once. Specific gotchas seen in the wild:

- **Filename typo in the request.** The user asked for `DISUCCSION.md`; confirm the
  intended name (corrected to `DISCUSSION.md`) before writing.
- **Graph scope.** Clarify which PNGs count as "the results." Generator
  `confinement_plot_*.png` are search-box setup visuals, not benchmark results —
  exclude them unless explicitly requested.
- **Stale pre-existing DISCUSSION.md.** A results dir may already contain a
  DISCUSSION.md that is a *copy of a sibling project's* discussion (wrong filenames,
  wrong project id). Read it before assuming it is correct; confirm whether to
  overwrite or write a new file.

## Pitfalls

- Overwriting a stale discussion without confirming is risky; always ask.
- Not stating the duplicate/waste rate is a common omission — readers want it called out.
- Small-N stats: report per-run values, not just means.
