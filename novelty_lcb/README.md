Novelty-LCB Acquisitor — organized package
============================================

A custom AGOX acquisition function that blends uncertainty (LCB) with
structural novelty and an energy-window filter.

    a(x) = σ(x) + λ · Novelty(x)          [to MAXIMIZE]

    Novelty(x) = min_{i ∈ DB} ||fingerprint(x) − fingerprint(x_i)||₂

    subject to  E_target − ΔE ≤ μ(x) ≤ E_target + ΔE

Out-of-window candidates are excluded (a(x) = −∞).  Because AGOX sorts
**ascending** (lowest = best = selected first), the acquisitor returns
**−a(x)** so that the candidate with the largest true acquisition value
is picked first.

Conda environment
-----------------
Run from the ``agox_v2`` conda environment (AGOX 3.10.2 + ASE 3.25.0):

    conda activate agox_v2       # or: conda run -n agox_v2 python ...

Contents
--------
acquisitor.py      NoveltyLCBAcquisitor class + attach/cache logic
utils.py           is_distinct(), fingerprint_distance() helpers
benchmark_helpers.py  Factory for building AGOX stacks with either acquisitor
tests/             Unit tests
benchmarks/        Benchmark v1 (broad window) and v2 (tight window)
visualization/     3-panel concept figure generator

Quick start
-----------
    # Run the unit tests
    python -m pytest novelty_lcb/tests/   # or: python novelty_lcb/tests/run_tests.py

    # Run benchmark v1 (broad energy window)
    python -m novelty_lcb.benchmarks.benchmark_v1

    # Run benchmark v2 (tight energy window)
    python -m novelty_lcb.benchmarks.benchmark_v2

    # Generate the concept figure
    python -m novelty_lcb.visualization.concept

Reference
---------
- Design rationale + acquisition-function graph:
  ``graph_novelty_lcb_concept.py`` (project root) and
  ``novelty_lcb_concept.png``.
- End-to-end AGOX + nested-sampling glue:
  ``nested_sampling_agox.py`` (project root).
