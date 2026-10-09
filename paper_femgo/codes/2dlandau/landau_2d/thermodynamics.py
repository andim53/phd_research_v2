#!/usr/bin/env python3
"""Reweight the 2D g_IS(E, dZ) to temperature-dependent observables.

Wang-Landau samples uniform in (E, dZ) — i.e. each accepted structure carries
weight 1/g_IS(E_i, dZ_i). Reweight to a canonical ensemble at temperature T by
``w_i(T) = exp(-E_total_i / k_B T) / g_IS(E_i, dZ_i)`` where E_total is the
TOTAL (per-structure) energy (E_rel * n_atoms; using per-atom E would mis-scale
T by n_atoms). From the weights:
  - <dZ(T)> and std(dZ(T)): the film-height distribution vs T — the primary
    observable; the flat<->island transition is read directly off this shift
    (no two-state label);
  - effN(T) = 1 / sum(w_norm^2): the effective sample size of the reweighted
    weights — a run with effN ~ 1 is degenerate (one structure carries ~all the
    weight) and is the acceptance gate for a "physical" result.

g_IS is defined up to a multiplicative constant (additive in ln_g), so only
free-energy *differences* are physical.
"""

from __future__ import annotations

__version__ = "1.1.0"

import numpy as np

from .utils import K_B, _logsumexp


def reweight_2d(ensemble_rows, ln_g, e_centers_rel, dz_centers,
                e_min, e_width, dz_min, dz_width, n_atoms, temperatures):
    """Reweight the accepted ensemble to canonical observables at each T.

    Parameters
    ----------
    ensemble_rows : list of (E_total, E_rel, dZ, i, j)
    ln_g : 2D array [E bin, dZ bin]  (log density of states)
    e_centers_rel, dz_centers : bin centers (rel eV/atom; Angstrom)
    temperatures : list of float (K)

    Returns
    -------
    rows : list of dict {T, <dZ>, std(dZ), effN}
    """
    # Work entirely in log-space: w_i = exp(-beta E_total - ln_g[i,j]) up to an
    # additive constant in ln_g, which cancels in every ratio below. Direct
    # w = exp(-beta E)/g overflows/underflows because WL's ln_g spans many
    # orders of magnitude.
    out = []
    for T in temperatures:
        beta = 1.0 / (K_B * T)
        logw = []
        dzs = []
        for (E_total, E_rel, dz, i, j) in ensemble_rows:
            logw.append(-beta * E_total - ln_g[i, j])
            dzs.append(dz)
        logw = np.asarray(logw, dtype=float)
        dzs = np.asarray(dzs, dtype=float)

        lse = _logsumexp(logw)
        w_norm = np.exp(logw - lse)

        mean_dz = float(np.sum(w_norm * dzs))
        var_dz = float(np.sum(w_norm * (dzs - mean_dz) ** 2))
        std_dz = float(np.sqrt(max(var_dz, 0.0)))
        effN = float(1.0 / np.sum(w_norm ** 2))

        out.append({
            "T_K": float(T),
            "mean_dZ_A": mean_dz,
            "std_dZ_A": std_dz,
            "effN": effN,
        })
    return out


def E_min_curve(ln_g, e_centers_rel, dz_centers, accessible):
    """Per-dZ minimum relative energy (eV/atom) over visited E cells.

    Returns (dz_centers, E_min_rel) with E_min_rel = nan where no cell visited.
    """
    n_dz = len(dz_centers)
    E_min = np.full(n_dz, np.nan)
    for j in range(n_dz):
        mask = accessible[:, j]
        if mask.any():
            E_min[j] = e_centers_rel[mask].min()
    return dz_centers, E_min