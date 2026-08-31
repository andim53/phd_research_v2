#!/usr/bin/env python3
"""Wang-Landau sampling with an AGOX GPR surrogate — organized package.

Computes the density of states g(E) (and from it the partition function,
free energy, heat capacity) by Wang-Landau flat-histogram sampling over a GPR
energy surrogate of an AGOX global-optimization database. The algorithmic
reference is the 1D toy in `_tmp/main_wanglandau_1d.f`.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .wang_landau_sampler import WangLandauSampler
from .gpr_training import load_all_seeds, build_gpr, validate_gpr
from .utils import K_B
from .thermodynamics import g_of_E_to_thermodynamics

__all__ = [
    "WangLandauSampler",
    "load_all_seeds",
    "build_gpr",
    "validate_gpr",
    "K_B",
    "g_of_E_to_thermodynamics",
]
