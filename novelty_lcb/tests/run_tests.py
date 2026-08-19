#!/usr/bin/env python3
"""
Unit tests for NoveltyLCBAcquisitor, is_distinct, and fingerprint_distance.

Run directly::

    python -m pytest novelty_lcb/tests/
    # or
    python novelty_lcb/tests/run_tests.py
"""

from __future__ import annotations

import sys
import os

import numpy as np

# Ensure project root is on sys.path
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from novelty_lcb.acquisitor import NoveltyLCBAcquisitor
from novelty_lcb.utils import is_distinct, fingerprint_distance
from novelty_lcb.tests.mock_objects import (
    MockDescriptor,
    MockModel,
    MockDatabase,
    make_candidate,
)


def test_basic():
    """Inside-window candidates with a non-empty DB.

    DB: two structures at features [0,0] and [1,0].
    Candidates:
      c0 at [0.1,0],  E=-2.4  -> near DB0, inside window
      c1 at [5.0,0],  E=-2.6  -> far from both, inside window
      c2 at [0.2,0],  E=-3.5  -> outside window (too low)
    Window: [-2.9, -2.1] eV (target=-2.5, delta=0.4)

    Expected negated acquisition values:
      c0: sigma=0.3, novelty=0.1 -> a=0.35 -> -0.35
      c1: sigma=0.3, novelty=4.0 -> a=2.30 -> -2.30
      c2: out-of-window -> +inf
    """
    fm = {}
    db_c0 = make_candidate(np.array([0.0, 0.0]), -2.5, fm)
    db_c1 = make_candidate(np.array([1.0, 0.0]), -2.3, fm)
    c0 = make_candidate(np.array([0.1, 0.0]), -2.4, fm)
    c1 = make_candidate(np.array([5.0, 0.0]), -2.6, fm)
    c2 = make_candidate(np.array([0.2, 0.0]), -3.5, fm)
    db = MockDatabase([db_c0, db_c1])

    desc = MockDescriptor(fm)
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

    # Expected negated: [-0.35, -2.30, +inf]
    print(f"  Raw (negated): {raw}")
    print(f"  Expected: [-0.35, -2.30, +inf]")

    assert np.isinf(raw[2]) and raw[2] > 0, "c2 should be +inf"
    assert raw[0] < 0, "c0 should be finite"
    assert raw[1] < 0, "c1 should be finite"
    assert raw[1] < raw[0], "c1 (higher a) should be more negative"

    # Sort
    sorted_cands, _ = acq.sort_according_to_acquisition_function([c0, c1, c2])
    order_ids = [id(c) for c in sorted_cands]
    print(f"  Sorted order ids: {order_ids}")
    assert order_ids[0] == id(c1), "Best (c1) should be first"
    assert order_ids[1] == id(c0), "c0 second"
    assert order_ids[2] == id(c2), "c2 (excluded) last"
    print("  PASSED")


def test_empty_db():
    """When the database is empty, Novelty(x)=0 and a(x)=sigma(x)."""
    fm = {}
    c0 = make_candidate(np.array([1.0, 2.0]), -2.4, fm)
    c1 = make_candidate(np.array([3.0, 4.0]), -2.3, fm)

    desc = MockDescriptor(fm)
    model = MockModel({id(c0): (-2.4, 0.5), id(c1): (-2.3, 0.1)})
    db = MockDatabase([])

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=1.0, order=4,
    )

    raw = acq.calculate_acquisition_function([c0, c1])
    # c0: a=0.5 -> -0.5; c1: a=0.1 -> -0.1
    print(f"  Raw: {raw}, expected: [-0.5, -0.1]")
    assert np.isclose(raw[0], -0.5), f"Expected -0.5, got {raw[0]}"
    assert np.isclose(raw[1], -0.1), f"Expected -0.1, got {raw[1]}"
    print("  PASSED")


def test_exclusion():
    """Candidates outside the energy window are excluded (+inf)."""
    fm = {}
    c0 = make_candidate(np.array([0.0, 0.0]), -2.4, fm)
    c1 = make_candidate(np.array([2.0, 0.0]), -2.6, fm)
    c2 = make_candidate(np.array([4.0, 0.0]), -5.0, fm)

    desc = MockDescriptor(fm)
    model = MockModel({
        id(c0): (-2.4, 0.2),
        id(c1): (-2.6, 0.3),
        id(c2): (-5.0, 0.1),
    })
    db = MockDatabase([])

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.3, novelty_weight=1.0, order=4,
    )

    raw = acq.calculate_acquisition_function([c0, c1, c2])
    print(f"  Raw: {raw}")
    print(f"  Window: [{-2.5-0.3}, {-2.5+0.3}] = [-2.8, -2.2]")
    print(f"  c0 E=-2.4 (in), c1 E=-2.6 (in), c2 E=-5.0 (out)")

    assert np.isinf(raw[2]) and raw[2] > 0, "c2 outside -> +inf"
    assert not np.isinf(raw[0]), "c0 inside -> finite"
    assert not np.isinf(raw[1]), "c1 inside -> finite"
    print("  PASSED")


def test_is_distinct():
    """Duplicate detection via fingerprint distance."""
    fm = {}
    db_c = make_candidate(np.array([0.0, 0.0]), -2.0, fm)
    db = MockDatabase([db_c])
    distinct_c = make_candidate(np.array([10.0, 0.0]), -2.1, fm)
    dup_c = make_candidate(np.array([0.05, 0.0]), -2.0, fm)

    desc = MockDescriptor(fm)

    r1 = is_distinct(distinct_c, db, desc, threshold=0.5)
    r2 = is_distinct(dup_c, db, desc, threshold=0.5)

    print(f"  distinct (dist~10): {r1} (expected True)")
    print(f"  dup (dist~0.05):  {r2} (expected False)")
    assert r1, "distinct should be True"
    assert not r2, "dup should be False"
    print("  PASSED")

    # Empty DB
    empty_db = MockDatabase([])
    assert is_distinct(distinct_c, empty_db, desc, threshold=0.1), \
        "empty DB: all distinct"
    print("  Empty DB: all distinct")


def test_fingerprint_distance():
    """Euclidean distance between two feature vectors."""
    fm = {}
    a = make_candidate(np.array([1.0, 2.0, 3.0]), -1.0, fm)
    b = make_candidate(np.array([4.0, 5.0, 6.0]), -1.1, fm)

    desc = MockDescriptor(fm)

    d = fingerprint_distance(desc, a, b)
    expected = np.linalg.norm(np.array([1, 2, 3]) - np.array([4, 5, 6]))
    print(f"  Distance: {d:.4f}, expected: {expected:.4f}")
    assert np.isclose(d, expected), f"Mismatch: {d} vs {expected}"
    print("  PASSED")


def test_lambda_scaling():
    """novelty_weight controls the trade-off between sigma and Novelty."""
    fm = {}
    db_c = make_candidate(np.array([0.0, 0.0]), -2.0, fm)
    db = MockDatabase([db_c])
    c_near = make_candidate(np.array([0.1, 0.0]), -2.4, fm)
    c_far = make_candidate(np.array([10.0, 0.0]), -2.4, fm)

    # lambda=0: same sigma (0.3) -> tie
    model0 = MockModel({id(c_near): (-2.4, 0.3), id(c_far): (-2.4, 0.3)})
    acq0 = NoveltyLCBAcquisitor(
        model=model0, descriptor=MockDescriptor(fm), database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=0.0, order=4,
    )
    raw0 = acq0.calculate_acquisition_function([c_near, c_far])
    print(f"  lambda=0: raw = {raw0}")
    assert np.isclose(raw0[0], raw0[1]), f"lambda=0 tie failed: {raw0}"

    # lambda=2: far candidate wins (higher novelty)
    model2 = MockModel({id(c_near): (-2.4, 0.3), id(c_far): (-2.4, 0.3)})
    acq2 = NoveltyLCBAcquisitor(
        model=model2, descriptor=MockDescriptor(fm), database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=2.0, order=4,
    )
    raw2 = acq2.calculate_acquisition_function([c_near, c_far])
    print(f"  lambda=2: raw = {raw2}")
    assert raw2[1] < raw2[0], f"lambda=2: far should win, got {raw2}"
    print("  PASSED")


def test_cache_rebuild():
    """Feature cache is populated at init and grows on store."""
    fm = {}
    db_c0 = make_candidate(np.array([0.0, 0.0]), -2.0, fm)
    db_c1 = make_candidate(np.array([5.0, 0.0]), -2.1, fm)
    db = MockDatabase([db_c0, db_c1])

    desc = MockDescriptor(fm)
    model = MockModel({})
    model._ready = True  # so do_check() returns True

    acq = NoveltyLCBAcquisitor(
        model=model, descriptor=desc, database=db,
        target_energy=-2.5, delta_E=0.5, novelty_weight=1.0, order=4,
    )

    assert acq._db_features is not None, "Cache should be populated"
    assert len(acq._db_features) == 2, \
        f"Expected 2, got {len(acq._db_features)}"
    print(f"  DEBUG: after init, db._cands={len(db._cands)}, "
          f"acq._db_features={len(acq._db_features)}")

    # Add new candidate
    db_c2 = make_candidate(np.array([10.0, 0.0]), -2.2, fm)
    db.store_candidate(db_c2)
    print(f"  DEBUG: after store, db._cands={len(db._cands)}")
    print(f"  DEBUG: acq.database is db? {acq.database is db}")
    all_c = acq.database.get_all_candidates()
    print(f"  DEBUG: get_all_candidates returned {len(all_c)} candidates")
    acq._rebuild_feature_cache()
    print(f"  DEBUG: after rebuild, "
          f"acq._db_features={len(acq._db_features) if acq._db_features is not None else None}")
    assert len(acq._db_features) == 3, \
        f"Expected 3 after rebuild, got {len(acq._db_features)}"
    print("  PASSED")


def main():
    np.set_printoptions(precision=4, suppress=True)

    test_basic()
    test_empty_db()
    test_exclusion()
    test_is_distinct()
    test_fingerprint_distance()
    test_lambda_scaling()
    test_cache_rebuild()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
