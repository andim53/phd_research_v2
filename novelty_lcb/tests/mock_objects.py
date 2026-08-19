#!/usr/bin/env python3
"""
Mock objects for Novelty-LCB unit tests.

Provides MockDescriptor, MockModel, and MockDatabase that satisfy the
AGOX ABC interfaces well enough to exercise NoveltyLCBAcquisitor without
a real GPR, fingerprint, or persistent database.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import numpy as np

from agox.candidates.standard import StandardCandidate
from agox.databases.ABC_database import DatabaseBaseClass


# =============================================================================
# Mock descriptor
# =============================================================================

class MockDescriptor:
    """Descriptor that returns fixed feature vectors keyed by ``id(candidate)``.

    Parameters
    ----------
    feature_map : dict
        Mapping ``id(candidate) -> np.ndarray`` (the feature vector,
        either 1-D or 2-D — will be reshaped to (1, -1) internally).
    """

    def __init__(self, feature_map: Dict[int, np.ndarray]) -> None:
        self._fm = feature_map
        self.environment = MagicMock()

    def get_features(self, candidate: Any) -> np.ndarray:
        cid = id(candidate)
        if cid not in self._fm:
            raise KeyError(f"Candidate id {cid} not in feature map")
        arr = self._fm[cid]
        return arr.reshape(1, -1) if arr.ndim == 1 else arr

    @property
    def descriptor_type(self) -> str:
        return "global"

    def get_number_of_centers(self, atoms: Any) -> int:
        return 1


# =============================================================================
# Mock model
# =============================================================================

class MockModel:
    """Model returning fixed (energy, uncertainty) pairs per candidate.

    Parameters
    ----------
    predictions : dict
        Mapping ``id(candidate) -> (energy, uncertainty)``.
    ready : bool
        Value returned by ``ready_state``.  Default True.
    """

    def __init__(self, predictions: Dict[int, tuple], ready: bool = True) -> None:
        self._pred = predictions
        self._ready = ready

    def predict_energy_and_uncertainty(self, candidate: Any) -> tuple:
        cid = id(candidate)
        return self._pred.get(cid, (0.0, 0.0))

    def predict_energy(self, atoms, **kw):
        E, _ = self.predict_energy_and_uncertainty(atoms)
        return E

    def predict_uncertainty(self, atoms, **kw):
        _, s = self.predict_energy_and_uncertainty(atoms)
        return s

    def get_model_parameters(self) -> dict:
        return {}

    def set_model_parameters(self, p):
        pass

    def converter(self, atoms, **kw):
        return {}

    @property
    def ready_state(self) -> bool:
        return self._ready


# =============================================================================
# Mock database
# =============================================================================

class MockDatabase(DatabaseBaseClass):
    """Minimal DB storing a list of candidates.  Dispatches to observers
    after ``store_candidate`` so the NoveltyLCBAcquisitor's cache-rebuild
    observer fires in tests."""

    def __init__(self, candidates: Optional[List[Any]] = None) -> None:
        super().__init__(
            gets={"get_key": "evaluated_candidates"},
            sets={"set_key": "stored_candidates"},
            order=6,
        )
        self._cands: List[Any] = list(candidates) if candidates else []

    def get_all_candidates(self) -> List[Any]:
        return list(self._cands)

    def store_candidate(self, candidate: Any, accepted: bool = True,
                        write: bool = True) -> None:
        if candidate is not None and candidate not in self._cands:
            self._cands.append(candidate)

    def __repr__(self) -> str:
        return f"MockDB(n={len(self._cands)})"

    @property
    def name(self) -> str:
        return "MockDB"

    def write(self, *args, **kwargs) -> None:
        pass


# =============================================================================
# Candidate factory
# =============================================================================

def make_candidate(
    feature: np.ndarray,
    energy: float,
    feature_map_ref: Optional[Dict[int, np.ndarray]] = None,
) -> StandardCandidate:
    """Create a StandardCandidate carrying a feature vector and energy.

    The returned candidate's ``id()`` is registered in *feature_map_ref*
    (if provided) so that the MockDescriptor can look it up later.

    Parameters
    ----------
    feature : np.ndarray
        Feature vector (1-D) to associate with this candidate.
    energy : float
        Potential energy to set via a SinglePointCalculator.
    feature_map_ref : dict or None
        Dict to update with ``id(candidate) -> feature``.
    """
    from ase.calculators.singlepoint import SinglePointCalculator
    from ase import Atoms

    template = Atoms()
    c = StandardCandidate(template=template)
    c.set_calculator(SinglePointCalculator(c, energy=energy))

    if feature_map_ref is not None:
        feature_map_ref[id(c)] = np.asarray(feature).ravel()

    return c
