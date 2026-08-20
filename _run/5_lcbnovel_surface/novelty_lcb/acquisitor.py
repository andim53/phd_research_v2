#!/usr/bin/env python3
"""
Organized, clean implementation of the Novelty-LCB acquisition function
for AGOX.

Implements:

    a(x) = sigma(x) + lambda * Novelty(x)   [to MAXIMIZE]

    Novelty(x) = min_{i in DB} ||fingerprint(x) - fingerprint(x_i)||_2

subject to:

    E_target - delta_E <= mu(x) <= E_target + delta_E

Candidates outside the energy window are excluded (a(x) = -inf).

**AGOX sorting convention:** AGOX sorts **ascending** (lowest value = best
= selected first).  We therefore return **-a(x)** so that the candidate
with the *largest* true acquisition value ends up with the most negative
sorting value and is picked first.  Out-of-window candidates receive
+np.inf in the sorting space → excluded forever.

Novelty is computed as the minimum Euclidean distance in descriptor
(fingerprint) feature space between the candidate and every structure
already stored in the database.  When the database is empty, Novelty(x)=0
for all candidates and the acquisitor reduces to pure uncertainty sampling
within the energy window.

Canonical import::

    from novelty_lcb import NoveltyLCBAcquisitor, is_distinct, fingerprint_distance
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional

from agox.acquisitors.ABC_acquisitor import AcquisitorBaseClass
from agox.candidates.standard import StandardCandidate
from agox.databases.ABC_database import DatabaseBaseClass
from agox.main import State
from agox.models.ABC_model import ModelBaseClass
from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.observer import Observer


# =============================================================================
# Novelty-LCB Acquisitor
# =============================================================================

class NoveltyLCBAcquisitor(AcquisitorBaseClass):
    """
    Lower-confidence-bound-style acquisition with a structural-novelty
    bonus and an energy-window filter.  Selects candidates that are
    simultaneously **uncertain** and **structurally dissimilar** to
    everything seen so far, within a target energy window.

    Acquisition function (to be MAXIMIZED — higher is better):

        a(x) = σ(x) + λ · Novelty(x)

    where:

        Novelty(x) = min_{i ∈ DB} ||fingerprint(x) − fingerprint(x_i)||₂

    The energy window is:

        E_target − ΔE  ≤  μ(x)  ≤  E_target + ΔE

    Candidates whose predicted energy falls outside the window are
    excluded (they receive +∞ in the sorting space).  When the database
    is empty, Novelty(x) = 0 for all candidates and the acquisitor
    reduces to pure uncertainty sampling within the energy window.

    Because AGOX's ``AcquisitorBaseClass.sort_according_to_acquisition_function``
    sorts **ascending** (lowest value = best = selected first), this module
    returns the **negated** acquisition value from ``calculate_acquisition_function``
    so that the candidate with the *largest* a(x) ends up with the most
    negative sorting value and is picked first.

    Out-of-window candidates receive ``+np.inf`` in the sorting space,
    effectively excluding them forever.

    Parameters
    ----------
    model : ModelBaseClass
        GPR / surrogate that provides ``predict_energy_and_uncertainty``.
    descriptor : DescriptorBaseClass
        Fingerprint / descriptor used for the novelty distance (e.g.
        ``Fingerprint``, ``SimpleFingerprint``, ``SOAP``).
    database : DatabaseBaseClass
        Database to compute novelty against; also attached for live
        updates so the novelty cache stays fresh as new structures arrive.
    target_energy : float
        Centre of the energy window (eV).
    delta_E : float, optional
        Half-width of the energy window (eV).  Default 0.5.
    novelty_weight : float, optional
        Weight λ multiplying the novelty term.  Default 1.0.
    **kwargs
        Passed through to ``AcquisitorBaseClass.__init__`` (``order``,
        ``gets``, ``sets``, ``surname``, …).
    """

    name = "NoveltyLCBAcquisitor"

    def __init__(
        self,
        model: ModelBaseClass,
        descriptor: DescriptorBaseClass,
        database: DatabaseBaseClass,
        target_energy: float,
        delta_E: float = 0.5,
        novelty_weight: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.model = model
        self.descriptor = descriptor
        self.target_energy = target_energy
        self.delta_E = delta_E
        self.novelty_weight = novelty_weight

        # Cached feature array: shape (n_db, n_features), or None.
        self._db_features: Optional[np.ndarray] = None

        # Attach to the database so we receive notifications.
        self.attach_to_database(database)

    # ------------------------------------------------------------------ #
    #  Database attachment                                                #
    # ------------------------------------------------------------------ #

    def attach_to_database(self, database: DatabaseBaseClass) -> None:
        """Validate *database* and attach observer + seed feature cache."""
        if not isinstance(database, DatabaseBaseClass):
            raise TypeError(
                f"Expected DatabaseBaseClass, got {type(database)}"
            )

        self.writer.write_header(self.name)
        self.writer(f"Attaching to database: {database}")

        self.add_observer_method(
            self._on_database_store,
            gets={},
            sets={},
            order=self.order[0],
            handler_identifier="database",
        )

        self.database = database
        self.attach(database)              # connect observer → handler
        self._rebuild_feature_cache()     # seed cache from existing DB

    # ------------------------------------------------------------------ #
    #  Feature cache                                                      #
    # ------------------------------------------------------------------ #

    def _rebuild_feature_cache(self) -> None:
        """(Re)compute the cached feature array from current DB contents."""
        candidates = self.database.get_all_candidates()
        if not candidates:
            self._db_features = None
            return

        feats = []
        for c in candidates:
            try:
                f = self.descriptor.get_features(c).ravel()
            except Exception:
                continue
            feats.append(f)
        self._db_features = (
            np.array(feats) if feats else None
        )

    @Observer.observer_method
    def _on_database_store(
        self, database: DatabaseBaseClass, state: State
    ) -> None:
        """Called by the database dispatcher whenever new candidates
        are stored.  Extends the feature cache with the new entries."""
        all_c = database.get_all_candidates()
        total = len(all_c)

        if self._db_features is None or total <= len(self._db_features):
            return

        # Append features for genuinely new candidates.
        new_feats = []
        for c in all_c[len(self._db_features):]:
            try:
                new_feats.append(self.descriptor.get_features(c).ravel())
            except Exception:
                continue
        if new_feats:
            self._db_features = np.vstack(
                [self._db_features, np.array(new_feats)]
            )

    # ------------------------------------------------------------------ #
    #  Acquisition function                                               #
    # ------------------------------------------------------------------ #

    def calculate_acquisition_function(
        self, candidates: List[StandardCandidate]
    ) -> np.ndarray:
        """Evaluate the (negated) novelty-LCB acquisition function.

        AGOX sorts **ascending** — lowest value = best = selected first.
        We therefore return ``-a(x)`` so that the candidate with the
        *largest* a(x) ends up with the most negative value and is
        picked first.

        Out-of-window candidates receive ``+np.inf`` which sorts last.

        Returns
        -------
        np.ndarray, shape (n_candidates,)
            Negated acquisition values.  Higher *true* a(x) → more
            negative here → selected first.  Out-of-window candidates
            get ``+np.inf``.
        """
        n = len(candidates)
        # Start with +inf: out-of-window candidates keep this value,
        # which sorts them last (never selected).
        values = np.full(n, np.inf)

        db_feats = self._db_features  # may be None

        for i, cand in enumerate(candidates):
            E, sigma = self.model.predict_energy_and_uncertainty(cand)

            # --- energy window filter --------------------------------- #
            if self.target_energy is not None:
                lo = self.target_energy - self.delta_E
                hi = self.target_energy + self.delta_E
                if E < lo or E > hi:
                    continue  # values[i] stays +inf → excluded

            # --- novelty ---------------------------------------------- #
            cand_feat = self.descriptor.get_features(cand).ravel()

            if db_feats is not None and db_feats.size > 0:
                dists = np.linalg.norm(db_feats - cand_feat, axis=1)
                novelty = np.min(dists)
            else:
                novelty = 0.0

            # True acquisition: a(x) = sigma + lambda * Novelty  (higher better)
            # Negate it so AGOX's ascending sort picks the best.
            values[i] = -(sigma + self.novelty_weight * novelty)

            # stash metadata for printing / analysis
            cand.add_meta_information("model_energy", E)
            cand.add_meta_information("uncertainty", sigma)
            cand.add_meta_information("novelty", novelty)
            cand.add_meta_information(
                "in_window",
                self.target_energy is None or (lo <= E <= hi),
            )

        return values

    # ------------------------------------------------------------------ #
    #  Printing                                                           #
    # ------------------------------------------------------------------ #

    def print_information(
        self,
        candidates: List[StandardCandidate],
        acquisition_values: np.ndarray,
    ) -> None:
        """Print a table of acquisition values for debugging / analysis.

        Shows the *true* (positive) a(x) = σ + λ·Novelty, not the
        negated value used for sorting.
        """
        for i, cand in enumerate(candidates):
            val = acquisition_values[i]
            if np.isinf(val) and val > 0:
                self.writer(
                    f"  [{i:3d}] OUTSIDE ENERGY WINDOW — excluded"
                )
                continue

            E = cand.get_meta_information("model_energy")
            s = cand.get_meta_information("uncertainty")
            nov = cand.get_meta_information("novelty")

            if E is None or s is None or nov is None:
                # Model not trained yet; show raw sorting value
                self.writer(
                    f"  [{i:3d}] (model not ready) sorting_val={val:.4f}"
                )
                continue

            # The true (positive) acquisition value:
            true_a = s + self.novelty_weight * nov

            self.writer(
                f"  [{i:3d}] E={E:9.4f}  σ={s:8.3f}  "
                f"novelty={nov:8.3f}  a(x)={true_a:9.4f}"
            )

    # ------------------------------------------------------------------ #
    #  Readiness check                                                    #
    # ------------------------------------------------------------------ #

    def do_check(self, **kwargs) -> bool:
        """The acquisitor is ready when the model is trained."""
        return self.model.ready_state


# =============================================================================
# Standalone duplicate-rejection utility
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
# Convenience: fingerprint distance between two structures
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


# =============================================================================
# Convenience: canonical import path
# =============================================================================
# The old monolithic file at the project root still exists for backwards
# compatibility.  New code should import from here (the package) instead:
#
#     from novelty_lcb import NoveltyLCBAcquisitor, is_distinct, fingerprint_distance
#
# The package's __init__.py re-exports these three names, so both forms
# work.  The root-level file novelty_lcb_acquisitor.py is kept as a thin
# backward-compatibility shim that imports from the package.
