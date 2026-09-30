#!/usr/bin/env python3
"""2D Landau sampling (g(E, dZ)) on an AGOX GPR surrogate — organized package.

Inherent-structure 2D Wang-Landau sampling of the Fe/MgO flat<->island
transition, binned over (E, island-height dZ), on a GPR surrogate trained from
the GO/GOFEE ``data/femgo`` database. No DFT anywhere. Algorithmic
generalisation of ``d_landauPlus`` (1D g(E)) to a 2D (E, dZ) histogram with a
generator-based jump proposal and a dZ-preserving (z-ceiling) relaxation.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .wang_landau_2d import WangLandau2DSampler
from .generator import DeltaZGenerator
from .gpr_training import load_all_seeds, build_gpr, validate_gpr
from .utils import K_B
from .thermodynamics import reweight_2d, E_min_curve

__all__ = [
    "WangLandau2DSampler",
    "DeltaZGenerator",
    "load_all_seeds",
    "build_gpr",
    "validate_gpr",
    "K_B",
    "reweight_2d",
    "E_min_curve",
]
