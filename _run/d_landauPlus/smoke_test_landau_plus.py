#!/usr/bin/env python3
"""
Cheap local smoke test for the Landau-Plus sampler on a FAKE "GPR" surrogate.

Validates the real `LandauPlusSampler` code path — uniform-in-volume rattle,
mandatory GPR relax with FixAtoms + BoxConstraint, Wang-Landau accept, flat/
island labelling, ensemble collection, thermodynamics — with NO DFT and NO real
AGOX surrogate.

The toy is the minimal geometry that exercises every branch: 2 mobile Fe atoms
on a small fixed Mg/O substrate, with a fake energy that is an *asymmetric
double well in the Fe z-spread* (flat = small spread, metastable higher energy;
island = large spread, global minimum). Two mobile atoms, each carrying a real
force, keep BFGS well-conditioned (full rank) so the mandatory relax converges
fast — unlike the 25-Fe real motif where 23 atoms have zero force and the
Hessian becomes singular.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python smoke_test_landau_plus.py
"""

from __future__ import annotations

__version__ = "1.0.0"

import os
import sys

import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from landau_plus.wang_landau_sampler import LandauPlusSampler  # noqa: E402
from landau_plus.thermodynamics import (  # noqa: E402
    g_of_E_to_thermodynamics, heat_capacity_from_thermo)


class FakeDoubleWellGPR(Calculator):
    """ASE Calculator: per-atom double well in Fe z (2 mobile Fe atoms).

    Each Fe atom independently sits in a one-particle double well between a
    "flat" position zf and an "island" position zi, plus a coupling that lowers
    the energy when the two atoms separate (large spread = island = global
    min):

        E = A*[ (z0-zf)^2(z0-zi)^2 + (z1-zf)^2(z1-zi)^2 ] - m*(z1 - z0)

    Every mobile atom carries a smooth full-rank force (no argmax/argmin
    discontinuity), so BFGS is well-conditioned and the mandatory relax
    converges fast.
    """

    implemented_properties = ["energy", "forces"]

    def __init__(self, zf=12.3, zi=15.3, A=2.0, m=1.0):
        super().__init__()
        self.zf, self.zi = zf, zi
        self.A, self.m = A, m

    def _energy(self, atoms):
        z0, z1 = atoms.positions[0, 2], atoms.positions[1, 2]
        e0 = self.A * (z0 - self.zf) ** 2 * (z0 - self.zi) ** 2
        e1 = self.A * (z1 - self.zf) ** 2 * (z1 - self.zi) ** 2
        return e0 + e1 - self.m * (z1 - z0)

    def _spread(self, atoms):
        z = atoms.positions[:2, 2]
        return float(z.max() - z.min())

    def calculate(self, atoms=None, properties=None, system_changes=None):
        super().calculate(atoms, properties, system_changes)
        z0, z1 = self.atoms.positions[0, 2], self.atoms.positions[1, 2]
        E = self._energy(self.atoms)
        def de(z):
            return self.A * 2 * (z - self.zf) * (z - self.zi) * (2 * z - self.zf - self.zi)
        forces = np.zeros_like(self.atoms.positions)
        forces[0, 2] = -(de(z0) + self.m)   # -dE/dz0
        forces[1, 2] = -(de(z1) - self.m)   # -dE/dz1
        self.results = {"energy": E, "forces": forces}

    def predict_energy(self, atoms):
        return self._energy(atoms)


def make_db(n=40):
    """2 Fe (mobile) on a fixed Mg/O substrate; Fe spread spans [0.1, 3.4]."""
    from ase.constraints import FixAtoms
    syms = ["Fe", "Fe", "Mg", "Mg", "O", "O"]
    cell = np.diag([14.35, 14.35, 40.0])
    structures = []
    for spread in np.linspace(0.1, 3.4, n):
        pos = np.zeros((6, 3))
        pos[0] = [7.0, 7.0, 12.3]                 # bottom Fe
        pos[1] = [7.0, 8.0, 12.3 + spread]        # top Fe
        pos[2:6, :2] = [[6.5, 7.0], [7.5, 7.0], [7.0, 6.5], [7.0, 7.5]]
        pos[2:6, 2] = 10.0
        a = Atoms(symbols=syms, positions=pos, cell=cell, pbc=[True, True, False])
        a.set_constraint(FixAtoms(indices=[2, 3, 4, 5]))
        structures.append(a)
    fake = FakeDoubleWellGPR()
    energies = np.array([fake.predict_energy(a) for a in structures])
    return fake, structures, energies


def main():
    gpr, structures, energies = make_db()
    print(f"E island(spread~3.4) = "
          f"{gpr.predict_energy(structures[-1]):.4f} eV (global min)")
    print(f"E flat(spread~0.1)  = "
          f"{gpr.predict_energy(structures[0]):.4f} eV (metastable)")

    ok = True
    sampler = LandauPlusSampler(
        gpr=gpr,
        db_structures=structures,
        db_energies=energies,
        n_bins=40,
        e_min=0.0,
        e_max=1.2,          # spans both wells (relative energies)
        rattle=1.5,
        relax_steps=20,
        perturb_symbols="Fe",
        flat_island_spread_aa=1.0,
        flatness_criterion=0.80,
        check_interval=150,
        n_stages_standard=3,
        rng=np.random.default_rng(7),
    )

    # --- (0) label() unit check: spread < 1 -> flat, >= 1 -> island ----------
    a_flat = structures[0].copy()          # spread 0.1 -> flat
    a_island = structures[-1].copy()       # spread 3.4 -> island
    if sampler.label(a_flat) != "flat":
        print("[SMOKE] FAIL: label(spread=0.1) != flat")
        ok = False
    if sampler.label(a_island) != "island":
        print("[SMOKE] FAIL: label(spread=3.4) != island")
        ok = False
    print(f"[SMOKE] label: spread 0.1 -> {sampler.label(a_flat)}, "
          f"spread 3.4 -> {sampler.label(a_island)}")

    # --- (1) relaxation descends in energy (basin-hopping works) -------------
    trial = structures[1].copy()           # near flat well, unrelaxed
    E_before = gpr.predict_energy(trial)
    sampler.x_current = trial
    rel = sampler._relax(trial)
    E_after = gpr.predict_energy(rel)
    print(f"[SMOKE] relax: E {E_before:.4f} -> {E_after:.4f} eV "
          f"(spread {sampler.fe_z_spread(trial):.3f} -> "
          f"{sampler.fe_z_spread(rel):.3f})")
    if E_after > E_before + 1e-9:
        print("[SMOKE] FAIL: relaxation raised the energy")
        ok = False

    # --- (2) short WL run: g(E) non-trivial, thermodynamics finite -------------
    sampler.initialize()
    sampler.run(n_steps=800, progress_every=400)
    bin_centers_rel, ln_g = sampler.g_of_E()
    visited = int((sampler.H > 0).sum())
    print(f"[SMOKE] visited bins: {visited}/{sampler.n_bins}; "
          f"ensemble: {len(sampler.ensemble_structs)}")
    if np.ptp(ln_g) < 1e-4:
        print("[SMOKE] FAIL: ln_g constant (sampler did not move)")
        ok = False

    temps = [100, 200, 300, 500, 1000]
    rows = g_of_E_to_thermodynamics(bin_centers_rel, ln_g,
                                    sampler.E_ref, sampler.n_atoms, temps)
    Fs = [r[4] for r in rows]
    for (T, beta, logZ, Z, F) in rows:
        if not (np.isfinite(logZ) and np.isfinite(F)):
            print(f"[SMOKE] FAIL: non-finite thermodynamics at T={T}")
            ok = False
        print(f"  T={T:6.1f} K  logZ={logZ:9.4f}  F={F:9.4f} eV")
    if np.ptp(Fs) < 1e-6:
        print("[SMOKE] FAIL: F constant across T (delta-like g(E))")
        ok = False
    cv = heat_capacity_from_thermo(rows)
    print(f"[SMOKE] heat capacity points: {len(cv)}")

    # --- (3) save path + ensemble labels --------------------------------------
    sampler.save("/tmp/lp_smoke_output")
    labels = {r[3] for r in sampler.ensemble_rows}
    print(f"[SMOKE] ensemble labels seen: {labels}")
    print("[SMOKE] save() wrote outputs OK")

    print("\n[SMOKE] RESULT: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())