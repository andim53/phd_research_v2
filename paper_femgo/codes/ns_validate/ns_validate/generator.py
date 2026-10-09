#!/usr/bin/env python3
"""Structure generator that places the mobile film species to realise a target
film height dZ.

``dZ`` is the **film height**: ``dZ = max(z_mobile) - z_substrate_top`` — the
height of the top mobile atom above the (fixed) substrate surface. Using the
fixed substrate as the reference (instead of ``max - min`` over the mobile set)
removes the "bottom atom drops toward the surface and inflates dZ" failure: dZ
depends on ``max(z_mobile)`` alone.

The mobile species is configurable (``mobile_symbols``): ``("Fe",)`` for Fe/MgO,
``("Fe","Co")`` for Fe-Co, ``("Fe","Co","B")`` for Fe-Co-B; every species not
listed is treated as the fixed substrate. With ``sample_ordering``, each
proposal additionally re-shuffles the mobile species labels across the fixed
in-plane sites (composition-preserving), so orderings are marginalised over.

Draws a target ``dZ_target`` and returns a candidate whose film height is
exactly ``dZ_target``:
  - the substrate is copied verbatim from a reference DB structure (fixed during
    relax, so identical across the whole pool);
  - the mobile atoms sit at the reference structure's in-plane (x, y) positions
    (adsorption sites). Only the z-heights are randomized: this keeps the
    candidate inside the GPR's training manifold (random in-plane placement
    drives the surrogate into catastrophic extrapolation);
  - the bottom mobile atom is seeded at ``z_contact`` (the measured adsorption
    height);
  - the top mobile atom is placed at ``z_substrate_top + dZ_target`` (so film
    height = dZ_target exactly);
  - the remaining mobile z-coords are drawn i.i.d. uniform in
    ``[z_contact, z_substrate_top + dZ_target]``, then argmin/argmax re-assigned
    to the extremes.
"""

from __future__ import annotations

__version__ = "1.3.0"

import numpy as np
from ase import Atoms
from ase.data import atomic_numbers


class DeltaZGenerator:
    """Generate film/MgO candidates with a prescribed film height (island height)
    for an arbitrary mobile-species set."""

    def __init__(
        self,
        reference: Atoms,
        mobile_symbols=("Fe",),
        z_contact: float = None,
        contact_gap: float = 2.08,
        in_plane_jitter: float = 0.0,
        sample_ordering: bool = False,
        rng: np.random.Generator = None,
    ):
        syms = np.asarray(reference.get_chemical_symbols())
        mobile_mask = np.isin(syms, list(mobile_symbols))
        self.mobile_indices = np.where(mobile_mask)[0]
        self.substrate_indices = np.where(~mobile_mask)[0]
        if len(self.mobile_indices) == 0:
            raise ValueError("No mobile atoms found in the reference structure.")
        if len(self.substrate_indices) == 0:
            raise ValueError("No substrate atoms found in the reference structure.")

        self.reference = reference
        self.cell = reference.get_cell().copy()
        self.pbc = reference.get_pbc()
        self.n_mobile = len(self.mobile_indices)

        # mobile in-plane adsorption sites = the reference structure's (x, y).
        self.mobile_sites_xy = reference.positions[self.mobile_indices, :2].copy()
        self.in_plane_jitter = float(in_plane_jitter)
        self.sample_ordering = bool(sample_ordering)

        # z_contact = adsorption height of the bottom mobile atom above the surface.
        sub_z = reference.positions[self.substrate_indices, 2]
        self.substrate_top_z = float(sub_z.max())
        if z_contact is None:
            z_contact = self.substrate_top_z + float(contact_gap)
        self.z_contact = float(z_contact)

        self.rng = rng or np.random.default_rng()

    def draw_target_dz(self, dz_min: float, dz_max: float) -> float:
        """Uniform draw of a target film height in [dz_min, dz_max]."""
        return float(self.rng.uniform(dz_min, dz_max))

    def __call__(self, dZ_target: float) -> Atoms:
        """Build a candidate with film height == dZ_target (island height)."""
        atoms = self.reference.copy()

        n = self.n_mobile
        top_z = self.substrate_top_z + dZ_target   # film height = dZ_target
        # Defensive: a dZ target below the contact gap is unphysical. Clamp so
        # rng.uniform below never gets high < low.
        top_z = max(top_z, self.z_contact)
        # z-heights: bottom at z_contact, top at top_z, rest uniform between.
        z = np.empty(n)
        z[0] = self.z_contact                       # bottom (argmin)
        z[1] = top_z                                 # top (argmax)
        if n > 2:
            z[2:] = self.rng.uniform(self.z_contact, top_z, n - 2)
        imin, imax = int(z.argmin()), int(z.argmax())
        z[imin] = self.z_contact
        z[imax] = top_z
        z = np.clip(z, self.z_contact, top_z)

        # in-plane: adsorption sites (+ optional jitter), NOT uniform random.
        xy = self.mobile_sites_xy.copy()
        if self.in_plane_jitter > 0:
            xy = xy + self.rng.uniform(-self.in_plane_jitter,
                                       self.in_plane_jitter, xy.shape)

        # optional: re-shuffle the mobile species labels across the fixed sites
        # (composition-preserving; marginalises over orderings).
        if self.sample_ordering:
            all_syms = list(atoms.get_chemical_symbols())
            mob_syms = [all_syms[i] for i in self.mobile_indices]
            self.rng.shuffle(mob_syms)
            numbers = atoms.get_atomic_numbers().copy()
            for i, sym in zip(self.mobile_indices, mob_syms):
                numbers[i] = atomic_numbers[sym]
            atoms.set_atomic_numbers(numbers)

        pos = atoms.positions.copy()
        pos[self.mobile_indices, 0] = xy[:, 0]
        pos[self.mobile_indices, 1] = xy[:, 1]
        pos[self.mobile_indices, 2] = z
        atoms.positions = pos
        return atoms

    def film_height(self, atoms: Atoms) -> float:
        """Film height = max(z_mobile) - z_substrate_top (the island-height axis)."""
        z = atoms.positions[self.mobile_indices, 2]
        return float(z.max() - self.substrate_top_z)

    def z_spread(self, atoms: Atoms) -> float:
        """Mobile z-spread (max - min)."""
        z = atoms.positions[self.mobile_indices, 2]
        return float(z.max() - z.min())