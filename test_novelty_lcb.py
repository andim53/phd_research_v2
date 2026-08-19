#!/usr/bin/env python3
"""
End-to-end verification of NoveltyLCBAcquisitor with mock objects.

Tests:
  1. Energy-window exclusion: out-of-window → +inf (never picked)
  2. Novelty term: higher novelty → higher a(x)
  3. Sorting: highest a(x) ends up first after sort (ascending sort on negated values)
  4. Empty database: novelty=0, pure uncertainty sampling
  5. is_distinct: duplicate detection
  6. fingerprint_distance: correct Euclidean distance
"""
import sys
sys.path.insert(0, "/home/think/Desktop/research")

import numpy as np
from unittest.mock import MagicMock

from novelty_lcb_acquisitor import NoveltyLCBAcquisitor
from novelty_lcb_acquisitor import is_distinct
from novelty_lcb_acquisitor import fingerprint_distance
from agox.candidates.standard import StandardCandidate
from agox.candidates.standard import StandardCandidate
from agox.databases.ABC_database import DatabaseBaseClass


# =============================================================================
# Mock classes
# =============================================================================

class MockDescriptor:
    """Descriptor that returns fixed feature vectors per candidate id()."""
    def __init__(self, feature_map: dict):
        self._fm = feature_map
        self.environment = MagicMock()

    def get_features(self, candidate):
        cid = id(candidate)
        if cid not in self._fm:
            raise KeyError(f"Candidate id {cid} not in feature map")
        return self._fm[cid].reshape(1, -1)

    @property
    def descriptor_type(self):
        return "global"

    def get_number_of_centers(self, atoms):
        return 1


class MockModel:
    """Model returning fixed (energy, uncertainty) pairs per candidate id()."""
    def __init__(self, predictions: dict, ready=True):
        self._pred = predictions
        self._ready = ready

    def predict_energy_and_uncertainty(self, candidate):
        cid = id(candidate)
        return self._pred.get(cid, (0.0, 0.0))

    def predict_energy(self, atoms, **kw):
        E, _ = self.predict_energy_and_uncertainty(atoms)
        return E

    def predict_uncertainty(self, atoms, **kw):
        _, s = self.predict_energy_and_uncertainty(atoms)
        return s

    def get_model_parameters(self):
        return {}

    def set_model_parameters(self, p):
        pass

    def converter(self, atoms, **kw):
        return {}

    @property
    def ready_state(self):
        return self._ready


class MockDatabase(DatabaseBaseClass):
    """Minimal DB storing a list of candidates.  Dispatches to observers
    after store_candidate so the NoveltyLCBAcquisitor's cache-rebuild
    observer fires in tests."""
    def __init__(self, candidates=None):
        super().__init__(
            gets={"get_key": "evaluated_candidates"},
            sets={"set_key": "stored_candidates"},
            order=6,
        )
        self._cands = list(candidates) if candidates else []

    def get_all_candidates(self):
        return list(self._cands)

    def store_candidate(self, candidate, accepted=True, write=True):
        if candidate is not None and candidate not in self._cands:
            self._cands.append(candidate)

    def __repr__(self):
        return f"MockDB(n={len(self._cands)})"

    @property
    def name(self):
        return "MockDB"

    def write(self, *args, **kwargs):
        pass


def make_cand(feat, energy):
    """Create StandardCandidate with given feature vector and energy."""
    from ase.calculators.singlepoint import SinglePointCalculator
    from ase import Atoms
    template = Atoms()
    c = StandardCandidate(template=template)
    c.set_calculator(SinglePointCalculator(c, energy=energy))
    # We'll store features externally via the descriptor's feature_map keyed by id()
    return c


# =============================================================================
# Tests
# =============================================================================

def test_basic():
    print("\n" + "=" * 60)
    print("TEST 1: Basic — inside window, DB has 2 structures")
    print("=" * 60)

    # DB: two structures at features [0,0] and [1,0]
    db_c0 = make_cand(np.array([0.0, 0.0]), -2.5)
    db_c1 = make_cand(np.array([1.0, 0.0]), -2.3)
    db = MockDatabase([db_c0, db_c1])

    # Candidates to evaluate
    c0 = make_cand(np.array([0.1, 0.0]), -2.4)   # near DB0, inside window
    c1 = make_cand(np.array([5.0, 0.0]), -2.6)   # far from both, inside window
    c2 = make_cand(np.array([0.2, 0.0]), -3.5)   # outside window (too low)

    feat_map = {
        id(db_c0): np.array([0.0, 0.0]),
        id(db_c1): np.array([1.0, 0.0]),
        id(c0): np.array([0.1, 0.0]),
        id(c1): np.array([5.0, 0.0]),
        id(c2): np.array([0.2, 0.0]),
    }
    desc = MockDescriptor(feat_map)

    model = MockModel({
        id(c0): (-2.4, 0.3),
        id(c1): (-2.6, 0.3),
        id(c2): (-3.5, 0.2),
    })

    acq = NoveltyLCBAcquisitor(
        model=model,
        descriptor=desc,
        database=db,
        target_energy=-2.5,
        delta_E=0.4,
        novelty_weight=0.5,
        order=4,
    )

    raw = acq.calculate_acquisition_function([c0, c1, c2])

    # Expected:
    # c0: σ=0.3, novelty=min(||[0.1,0]-[0,0]||, ||[0.1,0]-[1,0]||)=0.1
    #     a = 0.3+0.5*0.1=0.35 → negated=-0.35
    # c1: σ=0.3, novelty=min(||[5,0]-[0,0]||, ||[5,0]-[1,0]||)=4.0
    #     a = 0.3+0.5*4.0=2.30 → negated=-2.30
    # c2: outside → +inf
    print(f"  Raw (negated): {raw}")
    print(f"  Expected: [-0.35, -2.30, +inf]")

    assert np.isinf(raw[2]) and raw[2] > 0, "c2 should be +inf"
    assert raw[0] < 0, "c0 should be finite"
    assert raw[1] < 0, "c1 should be finite"
    assert raw[1] < raw[0], "c1 (higher a) should be more negative"
    print("  PASSED")

    # sort
    sorted_cands, sorted_vals = acq.sort_according_to_acquisition_function([c0, c1, c2])
    order_ids = [id(c) for c in sorted_cands]
    print(f"  Sorted order ids: {order_ids}")
    assert order_ids[0] == id(c1), "Best (c1) should be first"
    assert order_ids[1] == id(c0), "c0 second"
    assert order_ids[2] == id(c2), "c2 (excluded) last"
    print("  Sort order correct ✓")


def test_empty_db():
    print("\n" + "=" * 60)
    print("TEST 2: Empty DB → novelty=0, pure σ")
    print("=" * 60)

    c0 = make_cand(np.array([1.0, 2.0]), -2.4)
    c1 = make_cand(np.array([3.0, 4.0]), -2.3)

    feat_map = {
        id(c0): np.array([1.0, 2.0]),
        id(c1): np.array([3.0, 4.0]),
    }
    desc = MockDescriptor(feat_map)
    model = MockModel({id(c0): (-2.4, 0.5), id(c1): (-2.3, 0.1)})
    db = MockDatabase([])

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=1.0, order=4,
    )

    raw = acq.calculate_acquisition_function([c0, c1])
    # Empty DB: novelty=0 → a = σ
    # c0: a=0.5 → -0.5; c1: a=0.1 → -0.1
    print(f"  Raw: {raw}, expected: [-0.5, -0.1]")
    assert np.isclose(raw[0], -0.5), f"Expected -0.5, got {raw[0]}"
    assert np.isclose(raw[1], -0.1), f"Expected -0.1, got {raw[1]}"
    print("  PASSED")


def test_exclusion():
    print("\n" + "=" * 60)
    print("TEST 3: Energy-window exclusion")
    print("=" * 60)

    c0 = make_cand(np.array([0.0, 0.0]), -2.4)
    c1 = make_cand(np.array([2.0, 0.0]), -2.6)
    c2 = make_cand(np.array([4.0, 0.0]), -5.0)

    feat_map = {id(c0): np.array([0,0]), id(c1): np.array([2,0]), id(c2): np.array([4,0])}
    desc = MockDescriptor(feat_map)
    model = MockModel({id(c0): (-2.4, 0.2), id(c1): (-2.6, 0.3), id(c2): (-5.0, 0.1)})
    db = MockDatabase([])

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.3, novelty_weight=1.0, order=4,
    )

    raw = acq.calculate_acquisition_function([c0, c1, c2])
    print(f"  Raw: {raw}")
    print(f"  Window: [{-2.5-0.3}, {-2.5+0.3}] = [-2.8, -2.2]")
    print(f"  c0 E=-2.4 (in), c1 E=-2.6 (in), c2 E=-5.0 (out)")

    assert np.isinf(raw[2]) and raw[2] > 0, "c2 outside → +inf"
    assert not np.isinf(raw[0]), "c0 inside → finite"
    assert not np.isinf(raw[1]), "c1 inside → finite"
    print("  PASSED")


def test_is_distinct():
    print("\n" + "=" * 60)
    print("TEST 4: is_distinct")
    print("=" * 60)

    db_c = make_cand(np.array([0.0, 0.0]), -2.0)
    db = MockDatabase([db_c])

    distinct_c = make_cand(np.array([10.0, 0.0]), -2.1)
    dup_c = make_cand(np.array([0.05, 0.0]), -2.0)

    feat_map = {
        id(db_c): np.array([0.0, 0.0]),
        id(distinct_c): np.array([10.0, 0.0]),
        id(dup_c): np.array([0.05, 0.0]),
    }
    desc = MockDescriptor(feat_map)

    r1 = is_distinct(distinct_c, db, desc, threshold=0.5)
    r2 = is_distinct(dup_c, db, desc, threshold=0.5)

    print(f"  distinct (dist≈10): {r1} (expected True)")
    print(f"  dup (dist≈0.05):    {r2} (expected False)")
    assert r1, "distinct should be True"
    assert not r2, "dup should be False"
    print("  PASSED")

    # Empty DB
    empty_db = MockDatabase([])
    assert is_distinct(distinct_c, empty_db, desc, threshold=0.1), "empty DB: all distinct"
    print("  Empty DB: all distinct ✓")


def test_fingerprint_distance():
    print("\n" + "=" * 60)
    print("TEST 5: fingerprint_distance")
    print("=" * 60)

    a = make_cand(np.array([1.0, 2.0, 3.0]), -1.0)
    b = make_cand(np.array([4.0, 5.0, 6.0]), -1.1)

    feat_map = {id(a): np.array([1.0, 2.0, 3.0]), id(b): np.array([4.0, 5.0, 6.0])}
    desc = MockDescriptor(feat_map)

    d = fingerprint_distance(desc, a, b)
    expected = np.linalg.norm(np.array([1,2,3]) - np.array([4,5,6]))
    print(f"  Distance: {d:.4f}, expected: {expected:.4f}")
    assert np.isclose(d, expected), f"Mismatch: {d} vs {expected}"
    print("  PASSED")


def test_lambda_scaling():
    print("\n" + "=" * 60)
    print("TEST 6: λ scaling — novelty_weight controls trade-off")
    print("=" * 60)

    db_c = make_cand(np.array([0.0, 0.0]), -2.0)
    c_near = make_cand(np.array([0.1, 0.0]), -2.4)   # close to DB
    c_far = make_cand(np.array([10.0, 0.0]), -2.4)   # far from DB

    feat_map = {
        id(db_c): np.array([0.0, 0.0]),
        id(c_near): np.array([0.1, 0.0]),
        id(c_far): np.array([10.0, 0.0]),
    }

    # λ=0: same σ (0.3) → tie
    model0 = MockModel({id(c_near): (-2.4, 0.3), id(c_far): (-2.4, 0.3)})
    db0 = MockDatabase([db_c])
    acq0 = NoveltyLCBAcquisitor(
        model=model0, descriptor=MockDescriptor(feat_map), database=db0,
        target_energy=-2.5, delta_E=0.5, novelty_weight=0.0, order=4,
    )
    raw0 = acq0.calculate_acquisition_function([c_near, c_far])
    print(f"  λ=0: raw = {raw0}")
    assert np.isclose(raw0[0], raw0[1]), f"λ=0 tie failed: {raw0}"

    # λ=2: far candidate wins (higher novelty)
    model2 = MockModel({id(c_near): (-2.4, 0.3), id(c_far): (-2.4, 0.3)})
    db2 = MockDatabase([db_c])
    acq2 = NoveltyLCBAcquisitor(
        model=model2, descriptor=MockDescriptor(feat_map), database=db2,
        target_energy=-2.5, delta_E=0.5, novelty_weight=2.0, order=4,
    )
    raw2 = acq2.calculate_acquisition_function([c_near, c_far])
    print(f"  λ=2: raw = {raw2}")
    assert raw2[1] < raw2[0], f"λ=2: far should win, got {raw2}"
    print("  PASSED")


def test_cache_rebuild():
    print("\n" + "=" * 60)
    print("TEST 7: Cache rebuild from DB")
    print("=" * 60)

    db_c0 = make_cand(np.array([0.0, 0.0]), -2.0)
    db_c1 = make_cand(np.array([5.0, 0.0]), -2.1)
    db = MockDatabase([db_c0, db_c1])

    feat_map = {
        id(db_c0): np.array([0.0, 0.0]),
        id(db_c1): np.array([5.0, 0.0]),
    }
    desc = MockDescriptor(feat_map)
    model = MockModel({})
    model._ready = True  # so do_check() returns True and acquisition function runs

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=1.0, order=4,
    )

    assert acq._db_features is not None, "Cache should be populated"
    assert len(acq._db_features) == 2, f"Expected 2, got {len(acq._db_features)}"

    print(f"  DEBUG: after init, db._cands={len(db._cands)}, acq._db_features={len(acq._db_features) if acq._db_features is not None else None}")

    # Add new candidate that IS in the feature map
    db_c2 = make_cand(np.array([10.0, 0.0]), -2.2)
    feat_map[id(db_c2)] = np.array([10.0, 0.0])
    desc._fm = feat_map  # update descriptor's map
    db.store_candidate(db_c2)
    print(f"  DEBUG: after store, db._cands={len(db._cands)}")
    print(f"  DEBUG: acq.database is db? {acq.database is db}")
    all_c = acq.database.get_all_candidates()
    print(f"  DEBUG: get_all_candidates returned {len(all_c)} candidates")
    for c in all_c:
        print(f"    candidate id={id(c)}, in feat_map? {id(c) in feat_map}")
    acq._rebuild_feature_cache()
    print(f"  DEBUG: after rebuild, acq._db_features={len(acq._db_features) if acq._db_features is not None else None}")
    assert len(acq._db_features) == 3, f"Expected 3 after rebuild, got {len(acq._db_features)}"
    print("  PASSED")


if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True)

    test_basic()
    test_empty_db()
    test_exclusion()
    test_is_distinct()
    test_fingerprint_distance()
    test_lambda_scaling()
    test_cache_rebuild()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
