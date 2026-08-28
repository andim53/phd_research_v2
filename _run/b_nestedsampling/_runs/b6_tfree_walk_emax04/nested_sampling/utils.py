#!/usr/bin/env python3
"""Constants and small helpers for nested sampling."""

from __future__ import annotations

__version__ = "1.0.0"

# Boltzmann constant in eV/K
K_B = 8.617333262e-5   # eV/K


def shift_energies(energies):
    """Shift so minimum is zero (avoids overflow in exp(-beta*E))."""
    import numpy as np
    e = np.asarray(energies, dtype=float)
    return e - e.min()
