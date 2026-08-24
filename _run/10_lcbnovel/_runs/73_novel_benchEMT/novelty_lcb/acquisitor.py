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
from functools import partial
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

# Module-level LCB acquisition surface used for surrogate relaxation.
# These are *free functions* so that the calculator passed to
# ParallelRelaxPostprocess pickles cleanly (bound methods would drag the
# acquisitor's sqlite database connection into the object graph).

def lcb_acquisition_energy(E, sigma, kappa=1.0):
    """LCB energy surface used for surrogate relaxation (to minimise)."""
    return E - kappa * sigma


def lcb_acquisition_force(E, F, sigma, sigma_force, kappa=1.0):
    """Force surface corresponding to :func:`lcb_acquisition_energy`."""
    return F - kappa * sigma_force


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
    target_energy : float, optional
        Centre of the energy window (eV). Only used in the **centered** mode
        (when ``energy_above_min`` is ``None``). Default ``None`` (no constraint).
    delta_E : float, optional
        Half-width of the energy window (eV). Only used in the **centered** mode.
        Default 0.5.
    energy_above_min : float, optional
        If given (not ``None``), enables the **auto global-minimum** mode: the window
        becomes ``(-inf, E_min + energy_above_min]`` (or the per-atom equivalent when
        ``per_atom=True``), where ``E_min`` is the live lowest DFT energy currently in
        the database (recomputed each acquisition round). No prior calibration /
        regular-LCB run is needed. Candidates with predicted energy above the cap are
        excluded; energies below ``E_min`` are allowed so a new, lower global minimum
        can still be discovered. When ``None``, falls back to the centered
        ``target_energy ± delta_E`` mode. Default ``None``.
    per_atom : bool, optional
        If ``True`` and ``energy_above_min`` is set, the window is computed in energy
        per atom (eV/atom): both the candidate predicted energy ``E`` and the global
        minimum ``E_min`` are divided by the number of atoms ``N`` before comparing,
        so ``energy_above_min`` is interpreted as eV per atom. This makes the window
        scale-independent of system size and lets values like 0.5-2 eV/atom be chosen
        directly. Requires every candidate to have the same atom count ``N`` (true for
        this fixed-composition Fe/MgO dataset). Default ``False`` (total eV).
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
        target_energy: Optional[float] = None,
        delta_E: float = 0.5,
        novelty_weight: float = 1.0,
        kappa: float = 1.0,
        energy_above_min: Optional[float] = None,
        per_atom: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.model = model
        self.descriptor = descriptor
        self.target_energy = target_energy
        self.delta_E = delta_E
        self.novelty_weight = novelty_weight
        self.kappa = kappa
        self.energy_above_min = energy_above_min
        self.per_atom = per_atom

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
    #  Global-minimum energy (for auto window mode)                       #
    # ------------------------------------------------------------------ #

    def _global_min_energy(self) -> Optional[float]:
        """Live lowest DFT energy currently stored in the database (eV).

        Returns ``None`` if the database has no finite-energy candidates yet.
        """
        candidates = self.database.get_all_candidates()
        if not candidates:
            return None
        energies = []
        for c in candidates:
            try:
                e = c.get_potential_energy()
            except Exception:
                continue
            if e is not None and np.isfinite(e):
                energies.append(e)
        if not energies:
            return None
        return float(min(energies))

    def _n_atoms(self) -> int:
        """Number of atoms in a candidate (assumed uniform across the DB).

        Uses the template/candidate length; falls back to 1 if unavailable so the
        per-atom comparison degenerates gracefully to total-energy.
        """
        try:
            cands = self.database.get_all_candidates()
            if cands and len(cands) > 0:
                return len(cands[0])
        except Exception:
            pass
        return 1

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
            if self.energy_above_min is not None:
                # Auto global-minimum mode: window = (-inf, E_min + X].
                # E_min is the live lowest DFT energy in the DB. No lower bound,
                # so a new, lower global minimum can still be discovered.
                e_min = self._global_min_energy()
                if e_min is None:
                    # No minima yet: no cap (search freely until the first one).
                    in_window = True
                elif self.per_atom:
                    # Per-atom mode: divide both candidate E and E_min by N,
                    # so energy_above_min is in eV/atom.
                    n = self._n_atoms()
                    in_window = (E / n) <= (e_min / n) + self.energy_above_min
                    if not in_window:
                        continue  # values[i] stays +inf → excluded
                else:
                    # Total-energy mode (default).
                    in_window = E <= e_min + self.energy_above_min
                    if not in_window:
                        continue  # values[i] stays +inf → excluded
            elif self.target_energy is not None:
                # Centered mode: window = [target - delta_E, target + delta_E].
                lo = self.target_energy - self.delta_E
                hi = self.target_energy + self.delta_E
                in_window = lo <= E <= hi
                if not in_window:
                    continue  # values[i] stays +inf → excluded
            else:
                # No window constraint.
                in_window = True

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
            cand.add_meta_information("in_window", in_window)

        return values

    # ------------------------------------------------------------------ #
    #  Acquisition calculator (for surrogate relaxation)                 #
    # ------------------------------------------------------------------ #

    def get_acquisition_calculator(self):
        """Return an ASE calculator for the acquisition surface.

        This is consumed by :class:`agox.postprocessors.ParallelRelaxPostprocess`
        (and friends) to pre-relax candidates on the cheap surrogate before
        the expensive DFT evaluation.

        The novelty bonus is the *discrete* minimum Euclidean distance to the
        database in descriptor space, which is not differentiable w.r.t. atomic
        positions, so it cannot contribute a well-defined force.  We therefore
        relax candidates on the uncertainty-weighted lower-confidence-bound
        surface ``E - kappa*sigma`` (the LCB part of Novelty-LCB), whose energy
        and force gradients come analytically from the GPR model.

        IMPORTANT: the acquisition functions are passed as ``functools.partial``
        objects over *module-level* functions that close over only the scalar
        ``kappa``.  Bound methods (``self._acquisition_energy``) would capture the
        whole acquisitor instance -- including its sqlite-backed ``database`` --
        into the calculator's pickle graph, which breaks Ray ``ray.put``
        serialization (``cannot pickle 'sqlite3.Connection' object``).
        """
        from agox.acquisitors.LCB import LowerConfidenceBoundCalculator

        return LowerConfidenceBoundCalculator(
            self.model,
            partial(lcb_acquisition_energy, kappa=self.kappa),
            partial(lcb_acquisition_force, kappa=self.kappa),
        )

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
