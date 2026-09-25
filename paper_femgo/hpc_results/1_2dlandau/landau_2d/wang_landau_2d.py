#!/usr/bin/env python3
"""WangLandau2DSampler — 2D Wang-Landau sampling of g(E, dZ) on a GPR surrogate.

Generalises ``d_landauPlus``'s 1D basin-hopping Wang-Landau sampler to a **2D
histogram** over (E, dZ), where E is the GPR-relaxed energy and dZ the **film
height** = max(z_Fe) - z_substrate_top (the island height above the fixed MgO
surface). The proposal is a *generator-based jump move*, NOT a Markov
rattle-walk:

  1. draw a target dZ ~ U[dZ_min, dZ_max] (capped at the natural island height);
  2. generate a random structure at that dZ (``DeltaZGenerator``);
  3. relax it under a hard z-ceiling on the Fe atoms at
     z_substrate_top + dZ_target (GPR BFGS + FixAtoms(substrate));
  4. bin the relaxed structure's (E, dZ) and Wang-Landau-accept.

The resulting density of states is the **inherent-structure** (basin-minimum)
joint DOS g_IS(E, dZ). Flatness is a 2D check over *visited* cells only
(Torbrügge reference-histogram style): an initial pass maps the accessible
(E, dZ) region, and proposals landing in never-visited cells are rejected.

Wang-Landau acceptance ``ln(r) < ln_g[cur] - ln_g[trial]``, standard f->f/2
flatness, then the 1/t tail (Belardinelli & Pereyra 2007). The walk is
non-Markovian by design (Fort et al. 2015) — that is correct, not a bug.

The recovered g_IS is proposal-biased (generator reachability, not true basin
volume) — see the spec Assumption 1. Ensemble is reweightable.
"""

from __future__ import annotations

__version__ = "1.1.0"

from typing import List, Optional

import numpy as np
from ase import Atoms

from agox.utils.constraints.box_constraint import BoxConstraint


class WangLandau2DSampler:
    """2D Wang-Landau flat-histogram sampling of g(E, dZ) on a GPR surrogate."""

    def __init__(
        self,
        gpr,
        generator,
        E_ref: float,
        n_atoms: int,
        n_e_bins: int = 35,
        e_min: float = 0.0,
        e_max: float = 0.7,
        e_reject: Optional[float] = None,
        n_dz_bins: int = 12,
        dz_min: float = 2.08,
        dz_max: float = 5.73,
        relax_steps: int = 100,
        flat_island_spread_aa: float = 1.0,
        flatness_criterion: float = 0.80,
        check_interval: int = 5000,
        n_stages_standard: int = 14,
        reference_steps: int = 2000,
        rng: np.random.Generator = None,
    ):
        self.gpr = gpr
        self.gen = generator
        self.E_ref = float(E_ref)
        self.n_atoms = int(n_atoms)

        # Energy bins over relative energy per atom (eV/atom above train min).
        self.n_e_bins = int(n_e_bins)
        self.e_min = float(e_min)
        self.e_max = float(e_max)
        self.e_width = (self.e_max - self.e_min) / self.n_e_bins
        self.e_centers_rel = self.e_min + self.e_width * (
            np.arange(self.n_e_bins) + 0.5)

        # dZ bins over film height (Angstrom), = max(z_Fe) - z_substrate_top.
        self.n_dz_bins = int(n_dz_bins)
        self.dz_min = float(dz_min)
        self.dz_max = float(dz_max)
        self.dz_width = (self.dz_max - self.dz_min) / self.n_dz_bins
        self.dz_centers = self.dz_min + self.dz_width * (
            np.arange(self.n_dz_bins) + 0.5)

        self.relax_steps = int(relax_steps)

        if e_reject is not None and float(e_reject) > self.e_max:
            self.e_reject = float(e_reject)
        else:
            self.e_reject = 5.0 * self.e_max
        print(f"[WL2D] extrapolation guard: reject rel E > {self.e_reject:.4f} "
              f"eV/atom")

        self.flat_island_spread_aa = float(flat_island_spread_aa)

        # Wang-Landau state: 2D arrays [E bin, dZ bin].
        self.flatness_criterion = float(flatness_criterion)
        self.check_interval = int(check_interval)
        self.n_stages_standard = int(n_stages_standard)
        self.reference_steps = int(reference_steps)
        self.rng = rng or np.random.default_rng()
        self.ln_g = np.zeros((self.n_e_bins, self.n_dz_bins))
        self.H = np.zeros((self.n_e_bins, self.n_dz_bins), dtype=int)
        self.accessible = np.zeros((self.n_e_bins, self.n_dz_bins), dtype=bool)
        self.ln_f = 1.0
        self.stage = 0
        self.switched_to_1_over_t = False
        self.step_at_switch = 0
        self.step = 0

        # Current walker bin (i, j) — the "cur" state of the jump walk.
        self.bin_current = (-1, -1)

        # Ensemble of accepted (relaxed) structures.
        self.ensemble_structs: List[Atoms] = []
        self.ensemble_rows = []   # (E_total, E_rel, dZ, i, j, label)

        print(f"[WL2D] E bins={self.n_e_bins} over [{e_min}, {e_max}] "
              f"(width {self.e_width:.4f})")
        print(f"[WL2D] dZ bins={self.n_dz_bins} over [{dz_min}, {dz_max}] "
              f"(width {self.dz_width:.4f})")
        print(f"[WL2D] relax {self.relax_steps} BFGS steps; "
              f"flatness {self.flatness_criterion}; 1/t after "
              f"{self.n_stages_standard} halvings")

    # -- Helpers --------------------------------------------------------------

    def rel_energy(self, atoms: Atoms) -> float:
        """Relative energy per atom above the training minimum (eV/atom)."""
        E = self.gpr.predict_energy(atoms)
        return (E - self.E_ref) / self.n_atoms

    def fe_axis(self, atoms: Atoms) -> float:
        """Film height max(z_Fe) - z_substrate_top — the dZ axis."""
        return self.gen.fe_film_height(atoms)

    def fe_z_spread(self, atoms: Atoms) -> float:
        """Fe z-spread (max - min) — kept for flat/island labelling."""
        return self.gen.fe_z_spread(atoms)

    def get_e_bin(self, rel: float) -> int:
        """0-indexed E bin; -1 if below floor. Above e_max caps to top bin."""
        if rel < self.e_min:
            return -1
        b = int((rel - self.e_min) / self.e_width)
        return min(b, self.n_e_bins - 1)

    def get_dz_bin(self, dz: float) -> int:
        """0-indexed dZ bin; clamp into [0, n_dz_bins-1]."""
        b = int((dz - self.dz_min) / self.dz_width)
        return min(max(b, 0), self.n_dz_bins - 1)

    def label(self, atoms: Atoms) -> str:
        """Label by Fe z-spread (flat monolayer < threshold <= island)."""
        return "flat" if self.fe_z_spread(atoms) < self.flat_island_spread_aa \
            else "island"

    # -- Relax ----------------------------------------------------------------

    def _ceiling_box(self, dZ_target: float) -> BoxConstraint:
        """Hard z-ceiling on the Fe atoms at substrate_top + dZ_target.

        dZ is the *film height* (max(z_Fe) - z_substrate_top), so the ceiling
        sits at ``z_substrate_top + dZ_target``. The box bottom sits at the
        substrate surface (Fe cannot penetrate it). Because the sampling range
        is capped at the natural island height, the ceiling always binds: for
        every target below the natural island the Fe want to be taller, so
        ``max(z_Fe)`` presses against the ceiling and dZ = target holds.
        In-plane x/y are periodic (unclamped); only z is bounded.
        """
        z_floor = self.gen.substrate_top_z
        z_ceil = z_floor + dZ_target
        cell = self.gen.cell.copy()
        cell[2, 2] = (z_ceil - z_floor) + 1e-6
        corner = np.array([0.0, 0.0, z_floor])
        box = BoxConstraint(confinement_cell=cell, confinement_corner=corner,
                            indices=self.gen.fe_indices,
                            pbc=[True, True, False])
        return box

    def _relax(self, atoms: Atoms, dZ_target: float) -> Atoms:
        """Relax under the dZ ceiling: FixAtoms(substrate) + BoxConstraint(Fe)."""
        import ase.optimize
        from ase.constraints import FixAtoms

        relaxed = atoms.copy()
        box = self._ceiling_box(dZ_target)
        fix = FixAtoms(indices=list(map(int, self.gen.substrate_indices)))
        relaxed.set_constraint([box, fix])
        relaxed.calc = self.gpr
        try:
            opt = ase.optimize.BFGS(relaxed, logfile=None)
            opt.run(fmax=0.05, steps=self.relax_steps)
        except Exception as e:
            print(f"[WL2D] relax failed ({e}); using unrelaxed trial")
            return atoms
        return relaxed

    # -- Wang-Landau bookkeeping ---------------------------------------------

    def _visit(self, i: int, j: int):
        self.ln_g[i, j] += self.ln_f
        self.H[i, j] += 1

    def _check_flatness(self) -> bool:
        # flatness over visited cells only (Torbrügge reference-histogram style)
        visited = self.H > 0
        if not visited.any():
            return False
        mean_H = self.H[visited].mean()
        min_H = self.H[visited].min()
        return min_H > self.flatness_criterion * mean_H

    def _maybe_refine(self):
        if not self.switched_to_1_over_t:
            if self.step % self.check_interval == 0:
                if self._check_flatness():
                    self.ln_f /= 2.0
                    self.H[:] = 0
                    self.stage += 1
                    print(f"  stage {self.stage}: ln_f = {self.ln_f:.6e} "
                          f"(flat at step {self.step})")
            if self.stage >= self.n_stages_standard:
                self.switched_to_1_over_t = True
                self.step_at_switch = self.step
                self.H[:] = 0
                print(f"  Switching to 1/t algorithm at step {self.step} "
                      f"(after {self.stage} standard halvings)")
        else:
            self.ln_f = 1.0 / max(self.step - self.step_at_switch, 1)

    # -- Proposal -------------------------------------------------------------

    def _propose(self):
        """One jump move: draw dZ -> generate -> relax -> bin.

        Returns (relaxed_atoms, e_bin, dz_bin, rel_E, dz); bins -1 if out of
        range (E below floor).
        """
        dz_target = self.gen.draw_target_dz(self.dz_min, self.dz_max)
        trial = self.gen(dz_target)
        trial = self._relax(trial, dz_target)
        E = self.gpr.predict_energy(trial)
        rel = (E - self.E_ref) / self.n_atoms if np.isfinite(E) else float("nan")
        dz = self.fe_axis(trial)
        if not np.isfinite(rel) or abs(E) > 1e4:
            return trial, -1, -1, float("nan"), dz
        e_bin = self.get_e_bin(rel)
        dz_bin = self.get_dz_bin(dz)
        return trial, e_bin, dz_bin, rel, dz

    # -- Initialisation & run --------------------------------------------------

    def _reference_pass(self):
        """Torbrügge-style initial pass: map the accessible (E, dZ) region."""
        print(f"[WL2D] reference pass: {self.reference_steps} proposals to map "
              f"accessible (E, dZ) cells...")
        for _ in range(self.reference_steps):
            _, e_bin, dz_bin, rel, _ = self._propose()
            if e_bin >= 0 and np.isfinite(rel):
                self.accessible[e_bin, dz_bin] = True
        n_acc = int(self.accessible.sum())
        print(f"[WL2D] accessible cells mapped: {n_acc} / "
              f"{self.n_e_bins * self.n_dz_bins}")

    def initialize(self):
        """Set ``cur`` to the first accepted structure's bin."""
        self._reference_pass()
        # walker starts at the first proposal that lands in an accessible cell
        for _ in range(100):
            trial, e_bin, dz_bin, rel, dz = self._propose()
            if e_bin >= 0 and np.isfinite(rel):
                self.bin_current = (e_bin, dz_bin)
                self._record(trial, rel, dz, e_bin, dz_bin)
                print(f"[WL2D] init: rel E = {rel:.4f} eV/atom (E bin "
                      f"{e_bin}), dZ = {dz:.3f} A (dZ bin {dz_bin}) "
                      f"({self.label(trial)})")
                return
        raise RuntimeError("Could not initialise the walker inside the "
                           "accessible region.")

    def _record(self, atoms: Atoms, rel: float, dz: float, i: int, j: int):
        self.ensemble_structs.append(atoms.copy())
        E = float(self.gpr.predict_energy(atoms))
        self.ensemble_rows.append(
            (E, float(rel), float(dz), i, j, self.label(atoms)))

    def run(self, n_steps: int, progress_every: int = 5000):
        print(f"\nWL-2D: {n_steps} MC steps, grid {self.n_e_bins}x"
              f"{self.n_dz_bins}, ln_f_init=1.0")
        print("=" * 60)
        for _ in range(n_steps):
            self.step += 1
            trial, e_bin, dz_bin, rel, dz = self._propose()

            # extrapolation / out-of-range / never-visited -> revisit cur
            reject = (e_bin < 0 or not np.isfinite(rel)
                      or rel > self.e_reject
                      or not self.accessible[e_bin, dz_bin])
            if reject:
                self._visit(*self.bin_current)
                self._maybe_refine()
                continue

            # Wang-Landau acceptance
            r = self.rng.random()
            ci, cj = self.bin_current
            if np.log(r) < self.ln_g[ci, cj] - self.ln_g[e_bin, dz_bin]:
                self.bin_current = (e_bin, dz_bin)
                self._record(trial, rel, dz, e_bin, dz_bin)

            self._visit(*self.bin_current)
            self._maybe_refine()

            if self.step % progress_every == 0:
                visited = int((self.H > 0).sum())
                n_acc = int(self.accessible.sum())
                print(f"  step {self.step:9d}  stage {self.stage:2d}  "
                      f"ln_f {self.ln_f:.3e}  visited {visited}/{n_acc}")

        print(f"\nTotal MC steps = {self.step}, stages reached = {self.stage}")
        print(f"  accepted ensemble size = {len(self.ensemble_structs)}")
        print(f"  accessible cells = {int(self.accessible.sum())}")
        if self.switched_to_1_over_t:
            print("Used the 1/t algorithm for the final stage.")
        else:
            print("NOTE: standard f->f/2 scheme; did not reach the 1/t switch.")

    # -- Results --------------------------------------------------------------

    def g_of_E_dZ(self):
        """Return (e_centers_rel, dz_centers, ln_g, H, accessible)."""
        return (self.e_centers_rel.copy(), self.dz_centers.copy(),
                self.ln_g.copy(), self.H.copy(), self.accessible.copy())
