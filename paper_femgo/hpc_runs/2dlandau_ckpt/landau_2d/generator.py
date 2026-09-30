#!/usr/bin/env python3
"""Structure generator that places Fe atoms to realise a target island height dZ.

``dZ`` is the **film height**: ``dZ = max(z_Fe) - z_substrate_top`` — the height
of the top Fe atom above the (fixed) MgO surface. Using the fixed substrate as
the reference (instead of ``max - min`` over Fe) removes the "bottom Fe drops
toward the surface and inflates dZ" failure: dZ depends on ``max(z_Fe)`` alone.

Draws a target ``dZ_target`` and returns a candidate whose film height is
exactly ``dZ_target``:
  - the substrate (Mg/O) is copied verbatim from a reference DB structure
    (fixed during relax, so identical across the whole pool);
  - the Fe atoms sit at the **substrate's adsorption sites** — the reference
    structure's Fe in-plane (x, y) positions (a 5x5 lattice of MgO(001) hollow
    sites). Only the z-heights are randomized: this keeps the candidate inside
    the GPR's training manifold (random in-plane placement drives the surrogate
    into catastrophic extrapolation — see the M3 real-GPR check);
  - the bottom Fe is seeded at ``z_contact`` (the measured adsorption height,
    ~12.08 A = 2.08 A above the MgO surface);
  - the top Fe is placed at ``z_substrate_top + dZ_target`` (so film height =
    dZ_target exactly);
  - the remaining Fe z-coords are drawn i.i.d. uniform in
    ``[z_contact, z_substrate_top + dZ_target]``, then argmin/argmax re-assigned
    to the extremes.
"""

from __future__ import annotations

__version__ = "1.2.1"

import numpy as np
from ase import Atoms


class DeltaZGenerator:
    """Generate Fe/MgO candidates with a prescribed Fe film height (island height)."""

    def __init__(
        self,
        reference: Atoms,
        fe_symbols=("Fe",),
        z_contact: float = None,
        contact_gap: float = 2.08,
        in_plane_jitter: float = 0.0,
        rng: np.random.Generator = None,
    ):
        syms = np.asarray(reference.get_chemical_symbols())
        fe_mask = np.isin(syms, list(fe_symbols))
        self.fe_indices = np.where(fe_mask)[0]
        self.substrate_indices = np.where(~fe_mask)[0]
        if len(self.fe_indices) == 0:
            raise ValueError("No Fe atoms found in the reference structure.")
        if len(self.substrate_indices) == 0:
            raise ValueError("No substrate atoms found in the reference structure.")

        self.reference = reference
        self.cell = reference.get_cell().copy()
        self.pbc = reference.get_pbc()
        self.n_fe = len(self.fe_indices)

        # Fe in-plane adsorption sites = the reference structure's Fe (x, y).
        self.fe_sites_xy = reference.positions[self.fe_indices, :2].copy()
        self.in_plane_jitter = float(in_plane_jitter)

        # z_contact = adsorption height of the bottom Fe above the MgO surface.
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

        n = self.n_fe
        top_z = self.substrate_top_z + dZ_target   # film height = dZ_target
        # Defensive: a dZ target below the contact gap is unphysical (flat
        # monolayer can't be thinner than z_contact). Clamp so rng.uniform
        # below never gets high < low.
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
        xy = self.fe_sites_xy.copy()
        if self.in_plane_jitter > 0:
            xy = xy + self.rng.uniform(-self.in_plane_jitter,
                                       self.in_plane_jitter, xy.shape)

        pos = atoms.positions.copy()
        pos[self.fe_indices, 0] = xy[:, 0]
        pos[self.fe_indices, 1] = xy[:, 1]
        pos[self.fe_indices, 2] = z
        atoms.positions = pos
        return atoms

    def fe_film_height(self, atoms: Atoms) -> float:
        """Film height = max(z_Fe) - z_substrate_top (the island-height axis)."""
        z = atoms.positions[self.fe_indices, 2]
        return float(z.max() - self.substrate_top_z)

    def fe_z_spread(self, atoms: Atoms) -> float:
        """Fe z-spread (max - min) — kept for flat/island labelling."""
        z = atoms.positions[self.fe_indices, 2]
        return float(z.max() - z.min())
