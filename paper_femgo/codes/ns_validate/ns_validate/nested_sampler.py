#!/usr/bin/env python3
"""NestedSampler — 1D nested sampling of the inherent-structure DOS g_NS(E).

Independent validation of the 2D Wang-Landau DOS (spec 202610012020, v18).
Runs 1D nested sampling over the full (E, dZ) space on the SAME GPR surrogate
as 2dlandau, relaxing each live point to its basin minimum (inherent structure)
before binning, so NS produces an inherent-structure DOS g_NS(E) matching the
WL's definition.

Resampling (Option A, decided): the DeltaZGenerator is an independent proposal;
the energy-shell constraint is a rejection filter (accept only E_IS < E_removed).
dZ-retry: the proposal budget is ``dz_retry`` — each attempt draws a fresh dZ,
builds+relaxes+gate-checks, then applies the energy-shell filter. Fallback to the
best available point so NS does not stall.

Relaxation-quality gate: fmax=0.1 (empirical best); reject any structure not
reaching fmax<=0.1 within ``relax_steps`` (300) — do not bin it.

NS weights: w_i = alpha^(i-1) - alpha^i, alpha = (K-1)/K (Skilling / Partay).
"""

from __future__ import annotations

__version__ = "1.1.0"

import time
from typing import List, Optional

import numpy as np
from ase import Atoms

from .utils import K_B, _logsumexp


class NestedSampler:
    """1D nested sampling of the inherent-structure DOS g_NS(E)."""

    def __init__(
        self,
        gpr,
        generator,
        E_ref: float,
        n_atoms: int,
        n_live: int = 50,
        n_iterations: int = 300,
        e_min: float = 0.0,
        e_max: float = 0.7,
        n_e_bins: int = 35,
        relax_steps: int = 300,
        fmax: float = 0.1,
        dz_min: float = 2.08,
        dz_max: float = 5.73,
        dz_retry: int = 5,
        progress_every: int = 20,
        rng: np.random.Generator = None,
    ):
        self.gpr = gpr
        self.gen = generator
        self.E_ref = float(E_ref)
        self.n_atoms = int(n_atoms)

        self.n_live = int(n_live)
        self.n_iterations = int(n_iterations)
        self.alpha = (self.n_live - 1) / self.n_live

        # Energy bins over relative energy per atom (eV/atom above train min).
        self.n_e_bins = int(n_e_bins)
        self.e_min = float(e_min)
        self.e_max = float(e_max)
        self.e_width = (self.e_max - self.e_min) / self.n_e_bins
        self.e_centers_rel = self.e_min + self.e_width * (
            np.arange(self.n_e_bins) + 0.5)

        self.relax_steps = int(relax_steps)
        self.fmax = float(fmax)
        self.dz_min = float(dz_min)
        self.dz_max = float(dz_max)
        self.dz_retry = int(dz_retry)
        self.progress_every = int(progress_every)
        self.rng = rng or np.random.default_rng()

        # NS state
        self.live_structures: List[Atoms] = []
        self.live_energies: List[float] = []
        self.live_rel: List[float] = []
        self.live_dz: List[float] = []
        self.iteration = 0

        # Removed (discarded) points -> DOS
        self.removed_energies: List[float] = []   # E_total (eV)
        self.removed_rel: List[float] = []        # rel eV/atom
        self.removed_weights: List[float] = []    # NS weight w_i

        # Acceptance diagnostics
        self.n_relax_gate_pass = 0
        self.n_relax_gate_fail = 0
        self.n_energy_shell_pass = 0
        self.n_energy_shell_fail = 0
        self.n_fallback = 0

        print(f"[NS] 1D nested sampling: n_live={self.n_live}, "
              f"n_iterations={self.n_iterations}, alpha={self.alpha:.4f}")
        print(f"[NS] E bins={self.n_e_bins} over [{e_min}, {e_max}] "
              f"(width {self.e_width:.4f})")
        print(f"[NS] relax {self.relax_steps} BFGS steps, fmax={self.fmax}; "
              f"dz_retry {self.dz_retry}")

    # -- Helpers --------------------------------------------------------------

    def rel_energy(self, atoms: Atoms) -> float:
        E = self.gpr.predict_energy(atoms)
        return (E - self.E_ref) / self.n_atoms

    def get_e_bin(self, rel: float) -> int:
        if rel < self.e_min:
            return -1
        b = int((rel - self.e_min) / self.e_width)
        return min(b, self.n_e_bins - 1)

    # -- Relax (with quality gate) -------------------------------------------

    def _relax(self, atoms: Atoms, dZ_target: float):
        """Relax under the dZ ceiling; return (relaxed, converged_bool)."""
        from ase.optimize import BFGS
        from ase.constraints import FixAtoms
        from agox.utils.constraints.box_constraint import BoxConstraint

        z_floor = self.gen.substrate_top_z
        z_ceil = z_floor + dZ_target
        cell = self.gen.cell.copy()
        cell[2, 2] = (z_ceil - z_floor) + 1e-6
        box = BoxConstraint(confinement_cell=cell,
                            confinement_corner=np.array([0.0, 0.0, z_floor]),
                            indices=self.gen.fe_indices, pbc=[True, True, False])
        fix = FixAtoms(indices=list(map(int, self.gen.substrate_indices)))

        relaxed = atoms.copy()
        relaxed.set_constraint([box, fix])
        relaxed.calc = self.gpr
        try:
            opt = BFGS(relaxed, logfile=None)
            opt.run(fmax=self.fmax, steps=self.relax_steps)
        except Exception as e:
            print(f"[NS] relax failed ({e}); treating as gate-fail")
            return atoms, False
        f = np.abs(relaxed.get_forces()).max()
        converged = float(f) <= self.fmax
        return relaxed, converged

    # -- Proposal (Option A + dZ-retry) --------------------------------------

    def _propose(self, E_boundary: float):
        """Draw a candidate below E_boundary, or None if the cap is exhausted.

        Order (m9): for each of up to ``dz_retry`` attempts, draw a fresh dZ ->
        build + relax + gate-check -> energy-shell filter (E_IS < E_boundary).
        If no attempt passes the energy shell, fall back to the best (lowest-E)
        gate-passing structure seen (m10).
        """
        best = None
        best_rel = float("inf")
        for _ in range(self.dz_retry):
            dz_target = self.gen.draw_target_dz(self.dz_min, self.dz_max)
            trial = self.gen(dz_target)
            relaxed, converged = self._relax(trial, dz_target)
            if converged:
                self.n_relax_gate_pass += 1
                E = float(self.gpr.predict_energy(relaxed))
                rel = (E - self.E_ref) / self.n_atoms
                if rel < best_rel:
                    best = relaxed
                    best_rel = rel
                if E < E_boundary:
                    self.n_energy_shell_pass += 1
                    return relaxed, E, rel
                self.n_energy_shell_fail += 1
            else:
                self.n_relax_gate_fail += 1
        # cap exhausted -> fallback to best available (m10)
        if best is not None:
            self.n_fallback += 1
            E = float(self.gpr.predict_energy(best))
            rel = (E - self.E_ref) / self.n_atoms
            return best, E, rel
        return None

    # -- Initialize ----------------------------------------------------------

    def initialize(self):
        """Draw n_live live points from the prior (no energy constraint)."""
        print(f"[NS] initializing {self.n_live} live points...")
        t0 = time.perf_counter()
        while len(self.live_structures) < self.n_live:
            dz_target = self.gen.draw_target_dz(self.dz_min, self.dz_max)
            for _ in range(self.dz_retry):
                trial = self.gen(dz_target)
                relaxed, converged = self._relax(trial, dz_target)
                if converged:
                    self.n_relax_gate_pass += 1
                    E = float(self.gpr.predict_energy(relaxed))
                    rel = (E - self.E_ref) / self.n_atoms
                    self.live_structures.append(relaxed)
                    self.live_energies.append(E)
                    self.live_rel.append(rel)
                    self.live_dz.append(self.gen.fe_film_height(relaxed))
                    break
                else:
                    self.n_relax_gate_fail += 1
        print(f"[NS] initialized {len(self.live_structures)} live points in "
              f"{time.perf_counter()-t0:.1f}s")

    # -- Step ----------------------------------------------------------------

    def step(self):
        """One NS iteration: remove worst, record, replace."""
        worst_idx = int(np.argmax(self.live_energies))
        E_worst = self.live_energies[worst_idx]
        rel_worst = self.live_rel[worst_idx]

        # NS weight: w_i = alpha^(i-1) - alpha^i
        w = self.alpha ** self.iteration - self.alpha ** (self.iteration + 1)
        self.removed_energies.append(E_worst)
        self.removed_rel.append(rel_worst)
        self.removed_weights.append(w)

        # Replace worst with a point below E_worst
        new = self._propose(E_worst)
        if new is None:
            # fallback: keep the worst (do not shrink) — NS stalls gracefully
            self.n_fallback += 1
            return
        relaxed, E, rel = new
        self.live_structures[worst_idx] = relaxed
        self.live_energies[worst_idx] = E
        self.live_rel[worst_idx] = rel
        self.live_dz[worst_idx] = self.gen.fe_film_height(relaxed)
        self.iteration += 1

    # -- Run -----------------------------------------------------------------

    def run(self):
        print(f"\nNS: {self.n_iterations} iterations, {self.n_live} live, "
              f"alpha={self.alpha:.4f}")
        print("=" * 60)
        t0 = time.perf_counter()
        for it in range(self.n_iterations):
            self.step()
            if (it + 1) % self.progress_every == 0:
                E_min = min(self.live_energies)
                rel_min = (E_min - self.E_ref) / self.n_atoms
                print(f"  iter {it+1:5d}  live E_min={E_min:9.4f} eV "
                      f"(rel {rel_min:7.4f})  removed={len(self.removed_energies)}")
        print(f"NS done in {time.perf_counter()-t0:.1f}s; "
              f"{len(self.removed_energies)} removed points")

    # -- Results --------------------------------------------------------------

    def g_of_E(self):
        """Return (e_centers_rel, ln_g, H, accessible) for the NS DOS.

        g_NS(E) = sum of NS weights of removed points in each energy bin,
        normalized to a density (divide by bin width). ln_g in log space.
        """
        ln_g = np.full(self.n_e_bins, -np.inf)
        H = np.zeros(self.n_e_bins, dtype=int)
        for rel, w in zip(self.removed_rel, self.removed_weights):
            b = self.get_e_bin(rel)
            if b < 0:
                continue
            H[b] += 1
            # accumulate in log space
            if ln_g[b] == -np.inf:
                ln_g[b] = np.log(w)
            else:
                ln_g[b] = np.logaddexp(ln_g[b], np.log(w))
        # density: divide by bin width
        ln_g = ln_g - np.log(self.e_width)
        accessible = np.isfinite(ln_g)
        return self.e_centers_rel.copy(), ln_g, H, accessible

    def acceptance_report(self) -> dict:
        return {
            "n_live": self.n_live,
            "n_iterations": self.iteration,
            "relax_gate_pass": self.n_relax_gate_pass,
            "relax_gate_fail": self.n_relax_gate_fail,
            "energy_shell_pass": self.n_energy_shell_pass,
            "energy_shell_fail": self.n_energy_shell_fail,
            "fallback": self.n_fallback,
            "relax_gate_pass_rate": (
                self.n_relax_gate_pass /
                max(self.n_relax_gate_pass + self.n_relax_gate_fail, 1)),
            "energy_shell_pass_rate": (
                self.n_energy_shell_pass /
                max(self.n_energy_shell_pass + self.n_energy_shell_fail, 1)),
        }
