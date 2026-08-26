#!/usr/bin/env python3
"""
Standalone duplicate-rejection and fingerprint-distance utilities.

These use the *same* novelty measure as NoveltyLCBAcquisitor (minimum
Euclidean distance in descriptor feature space) so they compose cleanly
with the acquisitor: the same distance threshold used for acquisition
can be used for pre-storage duplicate filtering.
"""



from __future__ import annotations

__version__ = "1.0.0"

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agox.candidates.standard import StandardCandidate
    from agox.databases.ABC_database import DatabaseBaseClass
    from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


# =============================================================================
# Duplicate rejection
# =============================================================================


def is_distinct(
    candidate: StandardCandidate,
    database: DatabaseBaseClass,
    descriptor: DescriptorBaseClass,
    threshold: float = 0.1,
) -> bool:
    """
    Return ``True`` if *candidate* is structurally distinct from every
    structure already in *database*, as measured by the minimum Euclidean
    distance in descriptor (fingerprint) feature space.

    This is the same novelty measure used by ``NoveltyLCBAcquisitor`` and
    can be used as a pre-storage duplicate filter to avoid accumulating
    structurally similar variants of the same local minimum.

    Example
    -------
    >>> if is_distinct(new_struct, db, fingerprint, threshold=0.15):
    ...     db.store_candidate(new_struct)

    Parameters
    ----------
    candidate : StandardCandidate
        Structure to test.
    database : DatabaseBaseClass
        Database to check against.
    descriptor : DescriptorBaseClass
        Descriptor used to compute structural distances (e.g.
        ``Fingerprint``).
    threshold : float, optional
        Minimum distance required to be considered distinct.  Default
        0.1.

    Returns
    -------
    bool
        ``True`` if the candidate is farther than *threshold* from
        **all** database entries.
    """
    db_candidates = database.get_all_candidates()
    if not db_candidates:
        return True

    cand_feat = descriptor.get_features(candidate).ravel()
    for db_c in db_candidates:
        db_feat = descriptor.get_features(db_c).ravel()
        if np.linalg.norm(cand_feat - db_feat) <= threshold:
            return False
    return True


# =============================================================================
# Pairwise fingerprint distance
# =============================================================================


def fingerprint_distance(
    descriptor: DescriptorBaseClass,
    a: StandardCandidate,
    b: StandardCandidate,
) -> float:
    """
    Euclidean distance between the fingerprint feature vectors of two
    structures.

    Parameters
    ----------
    descriptor : DescriptorBaseClass
        Descriptor with a ``get_features`` method.
    a, b : StandardCandidate
        Structures to compare.

    Returns
    -------
    float
        Euclidean distance in descriptor space.
    """
    fa = descriptor.get_features(a).ravel()
    fb = descriptor.get_features(b).ravel()
    return float(np.linalg.norm(fa - fb))
