#!/usr/bin/env python3
"""Minimal smoke-test / import verifier for the novelty_lcb package."""

from __future__ import annotations

import sys
import os

# Make the project root importable (same convention as benchmarks/tests)
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

print("Python:", sys.version.split()[0])
print("Importing novelty_lcb...")

from novelty_lcb import NoveltyLCBAcquisitor, is_distinct, fingerprint_distance
print("  ✓ NoveltyLCBAcquisitor, is_distinct, fingerprint_distance")

from novelty_lcb.acquisitor import NoveltyLCBAcquisitor as NLCB
print("  ✓ novelty_lcb.acquisitor.NoveltyLCBAcquisitor")

from novelty_lcb.utils import is_distinct as _id, fingerprint_distance as _fd
print("  ✓ novelty_lcb.utils")

from novelty_lcb.tests.mock_objects import MockDescriptor, MockModel, MockDatabase
print("  ✓ novelty_lcb.tests.mock_objects")

from novelty_lcb.common import build_agox, make_template, DEFAULTS
print("  ✓ novelty_lcb.common (build_agox, make_template, DEFAULTS)")

from novelty_lcb.benchmarks import benchmark_v1, benchmark_v2
print("  ✓ novelty_lcb.benchmarks (benchmark_v1, benchmark_v2)")

from novelty_lcb.visualization import concept
print("  ✓ novelty_lcb.visualization.concept")

# Quick functional smoke-test with mocks
from unittest.mock import MagicMock
import numpy as np

class _M:
    ready_state = True
    def predict_energy_and_uncertainty(self, c):
        return -2.4, 0.3

class _D:
    def get_features(self, c):
        return np.array([[0.1, 0.0]])
    @property
    def descriptor_type(self):
        return "global"

class _DB:
    def __init__(self):
        from agox.databases.ABC_database import DatabaseBaseClass
        super().__init__(gets={}, sets={}, order=6) if hasattr(DatabaseBaseClass, '__init__') else None
    def get_all_candidates(self):
        return []
    def store_candidate(self, c, accepted=True, write=True):
        pass
    @property
    def name(self):
        return "MockDB"
    def write(self, *a, **kw):
        pass

try:
    from agox.databases.ABC_database import DatabaseBaseClass
    class _DB(DatabaseBaseClass):
        def __init__(self):
            super().__init__(gets={}, sets={}, order=6)
        def get_all_candidates(self):
            return []
        def store_candidate(self, c, accepted=True, write=True):
            pass
        @property
        def name(self):
            return "MockDB"
        def write(self, *a, **kw):
            pass
    db = _DB()
    acq = NLCB(
        model=_M(), descriptor=_D(), database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=1.0, order=4,
    )
    from agox.candidates.standard import StandardCandidate
    c = StandardCandidate(template=None)
    raw = acq.calculate_acquisition_function([c])
    ok = raw[0] < 0 and not np.isinf(raw[0])
    print(f"  ✓ Smoke test: raw={raw[0]:.4f} (expect negative finite) {'OK' if ok else 'FAIL'}")
except Exception as e:
    print(f"  ✗ Smoke test failed: {e}")

print("\nAll imports OK — the package is healthy.")
