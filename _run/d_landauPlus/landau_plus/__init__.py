#!/usr/bin/env python3
"""Landau-Plus sampling on an AGOX GPR surrogate — organized package.

Inherent-structure (basin-hopping) Wang-Landau sampling of the Fe/MgO
flat<->island transition on a GPR energy surrogate trained from a GOFEE/AGOX
global-optimization database. No DFT evaluation anywhere: the surrogate is the
only energy/force model. Algorithmic sibling of `c_landausampling` (whose
`wang_landau` package this adapts), differing in that every proposal is a
rattle of the current structure followed by a GPR relaxation (basin-hopping),
initialised from the flat (high-energy) reference monolayer.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .wang_landau_sampler import LandauPlusSampler
from .gpr_training import load_all_seeds, build_gpr, validate_gpr
from .utils import K_B
from .thermodynamics import g_of_E_to_thermodynamics

__all__ = [
    "LandauPlusSampler",
    "load_all_seeds",
    "build_gpr",
    "validate_gpr",
    "K_B",
    "g_of_E_to_thermodynamics",
]