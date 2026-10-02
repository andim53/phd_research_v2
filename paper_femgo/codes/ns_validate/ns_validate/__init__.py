#!/usr/bin/env python3
"""1D nested sampling validation of the 2D WL DOS — organized package.

Independent validation of the 2D Wang-Landau inherent-structure DOS g_IS(E, dZ)
of the Fe/MgO flat<->island transition, using 1D nested sampling on the SAME
GPR surrogate. Each NS live point is relaxed to its basin minimum (inherent
structure) before binning, so NS produces an inherent-structure DOS g_NS(E)
matching the WL's definition. Spec 202610012020 (v18).
"""

from __future__ import annotations

__version__ = "1.0.0"

from .nested_sampler import NestedSampler
from .gpr_training import load_all_seeds, build_gpr, validate_gpr
from .generator import DeltaZGenerator
from .utils import K_B

__all__ = [
    "NestedSampler",
    "load_all_seeds",
    "build_gpr",
    "validate_gpr",
    "DeltaZGenerator",
    "K_B",
]
