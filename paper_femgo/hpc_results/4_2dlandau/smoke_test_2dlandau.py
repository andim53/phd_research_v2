#!/usr/bin/env python3
"""
Cheap local smoke test for the 2D Landau sampler on a FAKE "GPR" surrogate.

Validates the real `WangLandau2DSampler` code path — DeltaZGenerator jump
proposal, dZ-ceiling GPR relax (FixAtoms + BoxConstraint), 2D Wang-Landau
acceptance, Torbrügge accessible-cell mapping, flat/island labelling, 2D
reweighting to <dZ(T)> and dF — with NO DFT and NO real AGOX surrogate.

The toy is a 2-Fe motif on a fixed Mg/O substrate (Fe are indices 0,1; the
substrate atoms sit at z=10.0, indices 2..5). The **dZ axis is the film height**
``h = z_Fe_top - z_substrate_top`` (substrate at 10.0; the top Fe atom is index
1, always >= the bottom by construction since dZ >= contact gap). The fake
energy is:
  - an *asymmetric double well in the film height* h (flat at hf, island at hi,
    island the global min via -m*h), so <dZ(T)> is genuinely T-dependent (the
    2D analogue of d_landauPlus's T-dependent-F check); and
  - a *weak harmonic in the mean Fe height* zbar = (z0+z1)/2, giving a second
    energy-varying degree of freedom per film height (a smooth, well-conditioned
    E-width per dZ).

Full-rank analytic forces (no argmax/argmin singularity, no quartic barrier),
so BFGS stays well-conditioned.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python smoke_test_2dlandau.py
"""

from __future__ import annotations

__version__ = "1.2.0"

import os
import sys

import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from landau_2d.wang_landau_2d import WangLandau2DSampler  # noqa: E402
from landau_2d.generator import DeltaZGenerator  # noqa: E402
from landau_2d.thermodynamics import reweight_2d  # noqa: E402


class Fake2DGPR(Calculator):
    """ASE Calculator: asymmetric double well in film height x harmonic in mean z.

    E(h, zbar) = A*(h-hf)^2*(h-hi)^2 - m*h + B*(zbar - zbar0)^2

    h = z1 - 10.0 (film height; atom 1 is the top Fe, substrate at 10.0),
    zbar = (z0+z1)/2 (mean Fe height). -m*h makes the island (large h) the
    global min; the B harmonic in zbar is the second DOF (smooth E-width per h).
    """

    implemented_properties = ["energy", "forces"]

    def __init__(self, hf=2.2, hi=4.5, A=1.0, m=0.1, zbar0=13.0, B=0.2):
        super().__init__()
        self.hf, self.hi, self.A, self.m = hf, hi, A, m
        self.zbar0, self.B = zbar0, B

    def _h(self, atoms):
        # film height: top Fe (index 1) above the substrate surface (z=10.0)
        return float(atoms.positions[1, 2] - 10.0)

    def _energy(self, atoms):
        h = self._h(atoms)
        zbar = 0.5 * (atoms.positions[0, 2] + atoms.positions[1, 2])
        e_h = (self.A * (h - self.hf) ** 2 * (h - self.hi) ** 2
               - self.m * h)
        return e_h + self.B * (zbar - self.zbar0) ** 2

    def calculate(self, atoms=None, properties=None, system_changes=None):
        super().calculate(atoms, properties, system_changes)
        a = self.atoms
        h = self._h(a)
        zbar = 0.5 * (a.positions[0, 2] + a.positions[1, 2])
        forces = np.zeros_like(a.positions)

        # dE/dh = A*2*(h-hf)(h-hi)(2h - hf - hi) - m
        dh = (self.A * 2 * (h - self.hf) * (h - self.hi)
              * (2 * h - self.hf - self.hi) - self.m)
        # dE/d(zbar) = 2 B (zbar - zbar0)
        dzbar = 2.0 * self.B * (zbar - self.zbar0)

        # h = z1 - 10 (dh/dz1 = 1, dh/dz0 = 0); zbar = (z0+z1)/2 (d/dz = 1/2)
        forces[1, 2] = -(dh + 0.5 * dzbar)
        forces[0, 2] = -(0.5 * dzbar)
        self.results = {"energy": self._energy(a), "forces": forces}

    def predict_energy(self, atoms):
        return self._energy(atoms)


def make_system():
    """2 mobile Fe (indices 0,1) on a 4-atom Mg/O substrate (indices 2..5, z=10)."""
    syms = ["Fe", "Fe", "Mg", "Mg", "O", "O"]
    cell = np.diag([8.0, 8.0, 30.0])
    pos = np.zeros((6, 3))
    pos[0] = [3.0, 3.0, 12.0]        # bottom Fe (z_contact = substrate + 2.0)
    pos[1] = [3.0, 4.0, 13.0]        # top Fe
    pos[2:6, :2] = [[2.5, 3.5], [3.5, 3.5], [3.0, 2.5], [3.0, 4.5]]
    pos[2:6, 2] = 10.0
    return Atoms(symbols=syms, positions=pos, cell=cell,
                 pbc=[True, True, False])


def main():
    ref = make_system()
    fake = Fake2DGPR()
    gen = DeltaZGenerator(ref, z_contact=12.0, in_plane_jitter=0.0,
                          rng=np.random.default_rng(0))

    # contact gap = 2.0 (z_contact 12 - substrate 10); film-height range
    dz_min = gen.z_contact - gen.substrate_top_z   # 2.0
    dz_max = 5.0

    e_island = fake.predict_energy(gen(dz_max))
    e_flat = fake.predict_energy(gen(dz_min))
    print(f"E island(film height {dz_max}) = {e_island:.4f} eV")
    print(f"E flat(film height {dz_min})   = {e_flat:.4f} eV")

    ok = True
    sampler = WangLandau2DSampler(
        gpr=fake, generator=gen, E_ref=-2.0, n_atoms=6,
        n_e_bins=20, e_min=0.0, e_max=0.7, e_reject=None,
        n_dz_bins=10, dz_min=dz_min, dz_max=dz_max,
        relax_steps=30, flat_island_spread_aa=1.0,
        flatness_criterion=0.80, check_interval=300,
        n_stages_standard=3, reference_steps=300,
        rng=np.random.default_rng(7),
    )

    # --- (1) generator realises the target film height ----------------------
    for target in [2.2, 3.0, 4.5]:
        a = gen(target)
        h = gen.fe_film_height(a)
        if abs(h - target) > 1e-6:
            print(f"[SMOKE] FAIL: generator film height {h:.4f} != target {target}")
            ok = False
    print("[SMOKE] generator realises target film height exactly")

    # --- (2) relax descends in energy, ceiling holds max Fe z -----------------
    trial = gen(3.0)
    E_before = fake.predict_energy(trial)
    relaxed = sampler._relax(trial, 3.0)
    E_after = fake.predict_energy(relaxed)
    zmax_after = relaxed.positions[gen.fe_indices, 2].max()
    z_ceil = gen.substrate_top_z + 3.0
    print(f"[SMOKE] relax: E {E_before:.4f} -> {E_after:.4f} eV, "
          f"max z {zmax_after:.3f} <= ceil {z_ceil:.3f}")
    if E_after > E_before + 1e-9:
        print("[SMOKE] FAIL: relaxation raised the energy")
        ok = False
    if zmax_after > z_ceil + 1e-3:
        print(f"[SMOKE] FAIL: ceiling leaked, max z {zmax_after:.3f} > "
              f"{z_ceil:.3f}")
        ok = False

    # --- (3) short WL run: 2D histogram non-trivial --------------------------
    sampler.initialize()
    sampler.run(n_steps=2000, progress_every=1000)
    e_centers, dz_centers, ln_g, H, accessible = sampler.g_of_E_dZ()
    visited = int((H > 0).sum())
    n_acc = int(accessible.sum())
    print(f"[SMOKE] visited {visited} cells, accessible {n_acc}, "
          f"ensemble {len(sampler.ensemble_structs)}")
    if visited < 2:
        print("[SMOKE] FAIL: fewer than 2 cells visited (collapsed histogram)")
        ok = False
    if np.ptp(ln_g[accessible]) < 1e-4:
        print("[SMOKE] FAIL: ln_g constant (sampler did not move)")
        ok = False

    # --- (4) reweighting: T-dependent <dZ(T)> --------------------------------
    temps = [100, 200, 300, 500, 1000]
    rows = reweight_2d(
        sampler.ensemble_rows, ln_g, e_centers, dz_centers,
        0.0, sampler.e_width, sampler.dz_min, sampler.dz_width,
        sampler.n_atoms, temps, flat_island_spread_aa=1.0)
    means = [r["mean_dZ_A"] for r in rows]
    print("[SMOKE] <dZ(T)> vs T:")
    for r in rows:
        print(f"  T={r['T_K']:6.1f} K  <dZ>={r['mean_dZ_A']:.4f} A  "
              f"std={r['std_dZ_A']:.4f}  dF={r['dF_flat_island_eV']:.4f} eV")
    if np.ptp(means) < 1e-3:
        print("[SMOKE] FAIL: <dZ(T)> constant across T (degenerate 2D DOS)")
        ok = False
    if not all(np.isfinite(r["dF_flat_island_eV"]) for r in rows):
        print("[SMOKE] FAIL: non-finite dF_flat_island")
        ok = False

    print("\n[SMOKE] RESULT: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())