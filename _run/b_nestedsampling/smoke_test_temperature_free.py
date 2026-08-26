#!/usr/bin/env python3
"""
Smoke test for the temperature-free nested-sampling mode (project b_nestedsampling).

Validates two things WITHOUT needing the full AGOX/GPR stack or the 1297-set:

1. Unit-style check of the temperature-free math: given a tiny set of discarded
   samples with known (E_i, w_i), `NestedSampler.evaluate(beta)` and
   `posterior_at(beta)` must reproduce the paper formula
       Z(beta) = sum_i w_i * exp(-beta * E_i)   (+ final live term)
   to high precision, and posterior weights must sum to 1.

2. End-to-end smoke run of `main.py --temperature-free` on the real dataset with
   tiny n-live/n-iters, confirming thermodynamics.csv + per-T posterior dirs are
   written and the run exits 0.

Run with the agox_v2 env:
    /home/think/miniconda3/envs/agox_v2/bin/python smoke_test_temperature_free.py
"""

from __future__ import annotations

__version__ = "1.0.0"

import os
import sys
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _tiny_sampler():
    """Build a NestedSampler-like object carrying temperature-free bookkeeping,
    without constructing a real GPR (bypass __init__ internals)."""
    from nested_sampling.nested_sampler import NestedSampler

    # Bypass __init__ (which needs a GPR/dataset) by creating via object.__new__
    # and setting the minimal attributes used by evaluate/posterior_at.
    s = object.__new__(NestedSampler)
    s.temperature_free = True
    s.E_ref = -400.0
    s.sample_prior_weights = [0.1, 0.2, 0.3, 0.25, 0.15]   # sum = 1.0
    s.sample_energies = [-400.0, -395.0, -390.0, -385.0, -380.0]
    s.n_live = 2
    s.iteration = 5
    s.live_energies = np.array([-401.0, -398.0])
    s.live_structures = [None, None]
    s.posterior_samples = [None] * len(s.sample_energies)
    return s


def test_evaluate_matches_formula():
    s = _tiny_sampler()
    beta = 1.0 / (8.617333262e-5 * 300.0)   # ~38.68 eV^-1

    # Z(beta) = sum_i w_i exp(-beta (E_i - E_ref)) + X_final * mean_live
    w = np.array(s.sample_prior_weights)
    E = np.array(s.sample_energies)
    logZ_disc = np.log(np.sum(w * np.exp(-beta * (E - s.E_ref))))
    X_final = np.exp(-s.iteration / s.n_live)
    E_live = s.live_energies
    logmean_live = np.log(np.mean(np.exp(-beta * (E_live - s.E_ref))))
    logZ_expected = np.logaddexp(logZ_disc, np.log(X_final) + logmean_live)

    Z, logZ = s.evaluate(beta)
    assert np.isclose(logZ, logZ_expected, rtol=1e-9, atol=1e-9), \
        f"logZ mismatch: got {logZ}, expected {logZ_expected}"
    assert np.isclose(Z, np.exp(logZ_expected), rtol=1e-6), "Z mismatch"

    # posterior weights sum to 1 and respect Z(beta)
    structs, weights = s.posterior_at(beta)
    assert np.isclose(weights.sum(), 1.0, atol=1e-9), \
        f"posterior weights do not sum to 1: {weights.sum()}"
    print(f"[OK] evaluate()/posterior_at() match paper formula "
          f"(logZ={logZ:.6f}, posterior weight sum={weights.sum():.6f})")


def test_end_to_end():
    PY = "/home/think/miniconda3/envs/agox_v2/bin/python"
    out = "/tmp/ns_smoke_tfree"
    cmd = [
        PY, os.path.join(_HERE, "main.py"),
        "--temperature-free",
        "--temperatures", "100,300,1000",
        "--n-live", "10",
        "--n-iters", "15",
        "--perturb", "0.01",
        "--perturb-symbols", "Fe",
        "--output", out,
        "--rng", "7",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("--- end-to-end tail ---")
    tail = "\n".join(r.stdout.splitlines()[-30:])
    print(tail)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-2000:])
        raise SystemExit(f"end-to-end temperature-free run FAILED (exit {r.returncode})")

    # verify outputs
    import os.path as p
    for f in ["samples.csv", "final_live_energies.csv", "thermodynamics.csv"]:
        assert p.exists(p.join(out, f)), f"missing {f}"
    for T in [100, 300, 1000]:
        assert p.isdir(p.join(out, f"posterior_T{T}")), f"missing posterior_T{T}"
        assert p.exists(p.join(out, f"posterior_T{T}", "posterior_summary.csv")), \
            f"missing posterior_T{T}/posterior_summary.csv"
    thermo = np.loadtxt(p.join(out, "thermodynamics.csv"), delimiter=',', skiprows=1)
    print("[OK] end-to-end temperature-free run exit=0; thermodynamics rows =")
    print(thermo)
    assert thermo.shape[0] == 3, "expected 3 thermodynamics rows (100/300/1000 K)"


if __name__ == "__main__":
    test_evaluate_matches_formula()
    test_end_to_end()
    print("\nALL TEMPERATURE-FREE SMOKE TESTS PASSED")
