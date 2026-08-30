#!/usr/bin/env python3
"""Constants and small helpers for Wang-Landau sampling."""

from __future__ import annotations

__version__ = "1.0.0"

import numpy as np

# Boltzmann constant in eV/K
K_B = 8.617333262e-5   # eV/K


def shift_energies(energies):
    """Shift so minimum is zero (avoids overflow in exp(-beta*E))."""
    e = np.asarray(energies, dtype=float)
    return e - e.min()


def _logsumexp(a: np.ndarray) -> float:
    """Numerically stable log(sum(exp(a)))."""
    a = np.asarray(a, dtype=float)
    m = a.max()
    if not np.isfinite(m):
        return m
    return m + np.log(np.sum(np.exp(a - m)))
