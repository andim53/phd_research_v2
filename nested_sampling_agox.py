#!/usr/bin/env python3
"""
Nested Sampling using AGOX GPR surrogate model
================================================
Loads the AGOX database from a completed run, trains a GPR model on the
DFT energies, and performs nested sampling to compute the Bayesian evidence
(partition function) Z = integral L(x) pi(x) dx.

Likelihood: L(x) = exp(-beta * E_GPR(x))  where beta = 1/(kB*T)

IMPORTANT: energies are shifted so E_min_training = 0, avoiding overflow
in exp(-beta * E) at room temperature (E ~ -400 eV would give inf).

Prior: empirical distribution from the AGOX database with optional small
perturbation for diversity.  Perturbation amplitudes > 0.01 A cause the
Fingerprint Cython module to produce unphysical GPR predictions.

References:
    AGOX analysis codes in _analysist/codes/ and _analysist/scripts/
    Fingerprint.from_atoms() usage from codes/98_configurational.py

Usage:
    python nested_sampling_agox.py [options]

This file is a backward-compatibility shim.  The canonical implementation
now lives in the ``nested_sampling/`` package:

    from nested_sampling import NestedSampler, train_gpr, K_B
    # or run the CLI with:  python -m nested_sampling --help
"""

import nested_sampling  # noqa: F401 — re-exports everything
