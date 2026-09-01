#!/usr/bin/env python3
"""Derive thermodynamics (Z, free energy, heat capacity) from a Wang-Landau
density of states g(E)."""

from __future__ import annotations

__version__ = "1.0.0"

import numpy as np

from .utils import K_B, _logsumexp


def _normalise_g(ln_g: np.ndarray, bin_width_rel: float, n_atoms: int):
    """Normalise g(E) to unit integral over absolute energy.

    Wang-Landau yields g(E) up to an overall multiplicative constant (an
    additive constant in ln_g). We fix the constant by requiring the integral
    ``sum_b g_b * bin_width_abs = 1`` (treat g as a normalised state density).
    Only the constant is affected; relative quantities (differences, C_V) are
    invariant.
    """
    ln_g = np.asarray(ln_g, dtype=float)
    bin_width_abs = bin_width_rel * n_atoms
    log_int = _logsumexp(ln_g) + np.log(bin_width_abs)
    return ln_g - log_int, bin_width_abs


def g_of_E_to_thermodynamics(
    bin_centers_rel: np.ndarray,
    ln_g: np.ndarray,
    E_ref: float,
    n_atoms: int,
    temperatures: list,
):
    """Compute Z, logZ, free energy and heat capacity from g(E).

    Parameters
    ----------
    bin_centers_rel : np.ndarray
        Bin centers in eV/atom relative to the training minimum.
    ln_g : np.ndarray
        Log density of states per bin (Wang-Landau output).
    E_ref : float
        Training-minimum (absolute) energy in eV.
    n_atoms : int
        Number of atoms (to convert eV/atom -> eV).
    temperatures : list
        Temperatures (K) at which to evaluate.

    Returns
    -------
    rows : list of (T, beta, logZ, Z, F_eV)
    """
    ln_g_n, bin_width_abs = _normalise_g(ln_g, bin_centers_rel[1] - bin_centers_rel[0],
                                         n_atoms)
    # absolute energy at each bin center (eV)
    E_abs = E_ref + bin_centers_rel * n_atoms

    rows = []
    for T in temperatures:
        beta = 1.0 / (K_B * T)
        logL = -beta * E_abs
        logZ = _logsumexp(ln_g_n + logL) + np.log(bin_width_abs)
        Z = np.exp(logZ) if logZ > -700 else 0.0
        F = -K_B * T * logZ        # free energy F = -k_B T ln Z  (eV)
        rows.append((T, beta, logZ, Z, F))
    return rows


def heat_capacity_from_thermo(rows):
    """C_V(T) = k_B beta^2 d^2(ln Z)/d beta^2, by finite differences over rows.

    Requires at least 3 temperature points.
    """
    if len(rows) < 3:
        return []
    T = np.array([r[0] for r in rows])
    logZ = np.array([r[2] for r in rows])
    beta = 1.0 / (K_B * T)
    # second derivative of logZ wrt beta (smooth, equally-ish spaced beta)
    d2 = np.gradient(np.gradient(logZ, beta), beta)
    cv = K_B * beta ** 2 * d2
    return list(zip(T.tolist(), cv.tolist()))
