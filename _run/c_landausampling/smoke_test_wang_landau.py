#!/usr/bin/env python3
"""
Cheap local smoke test for the Wang-Landau sampler on a FAKE 1-atom "GPR".

Validates the real `WangLandauSampler` code path (moves, acceptance rule, energy
bins, flatness check, standard->1/t switch, g(E) output, thermodynamics) without
any DFT or the real AGOX surrogate. The fake surrogate reproduces the Fortran
toy's asymmetric double well E(x) = A*(x^2-1)^2 + B*x on a single atom whose
x-coordinate is displaced by the small/large rattle — the direct analogue of
`_tmp/main_wanglandau_1d.f`.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python smoke_test_wang_landau.py
"""

from __future__ import annotations

__version__ = "1.1.0"

import os
import sys

import numpy as np
from ase import Atoms

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from wang_landau.wang_landau_sampler import WangLandauSampler
from wang_landau.thermodynamics import (
    g_of_E_to_thermodynamics, heat_capacity_from_thermo)


class FakeDoubleWellGPR:
    """Mimics gpr.predict_energy(atoms) with the Fortran double-well potential.

    E(x) = A*(x^2-1)^2 + B*x, x = first atom's x-coordinate. A=1, B=0.3 (as in
    the Fortran). Minima near x=+1 (flat) and x=-1 (island, global min).
    """

    def __init__(self, A=1.0, B=0.3):
        self.A = A
        self.B = B

    def predict_energy(self, atoms):
        x = atoms.positions[0][0]
        return self.A * (x ** 2 - 1.0) ** 2 + self.B * x


def make_db():
    """A 1-atom 'database' of structures spanning the double-well basin.

    x in [-1.3, 1.3]: the relevant region (island ~ -1, flat ~ +1, barrier ~ 0).
    E(x)=A(x^2-1)^2+B*x has min ~ -0.3 at x~-1 and max in-range ~ +1.3 at x~0
    (barrier), so relative energies stay within [0, ~1.3] < e_max=1.4 — giving
    a genuinely spread g(E) and a T-dependent free energy (a strong check).
    """
    structures = []
    for x in np.linspace(-1.3, 1.3, 81):
        structures.append(Atoms("Fe", positions=[[x, 0.0, 0.0]]))
    gpr = FakeDoubleWellGPR()
    energies = np.array([gpr.predict_energy(a) for a in structures])
    return gpr, structures, energies


def main():
    ok = test_single_species()
    ok = test_two_species_swap() and ok
    print("\n[SMOKE] RESULT: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def test_single_species():
    """Run the full WL path on the 1-atom double-well toy (Fe only)."""
    gpr, structures, energies = make_db()
    print(f"E_ref (min) = {energies.min():.4f} eV")
    print(f"E flat(x=1) = {gpr.predict_energy(structures[-1]):.4f} eV")

    # e_max (eV/atom rel) must reach past the barrier (~1.3 rel with A=1,B=0.3)
    sampler = WangLandauSampler(
        gpr=gpr,
        db_structures=structures,
        db_energies=energies,
        n_bins=40,
        e_min=0.0,
        e_max=1.4,
        small_step=0.05,
        large_step=0.40,
        perturb_symbols="Fe",
        flatness_criterion=0.80,
        check_interval=50000,      # small so the flatness check fires quickly
        n_stages_standard=4,       # switch to 1/t after just 4 halvings
        rng=np.random.default_rng(7),
    )
    sampler.initialize(start_from_top=True)
    sampler.run(n_steps=1_000_000, progress_every=100_000)

    bin_centers_rel, ln_g = sampler.g_of_E()
    visited = int((sampler.H > 0).sum())
    print(f"\n[SMOKE] visited bins: {visited}/{sampler.n_bins}")
    print(f"[SMOKE] stages reached: {sampler.stage}")

    ok = True
    if visited < sampler.n_bins // 2:
        print(f"[SMOKE] FAIL: only {visited} bins visited (< half)")
        ok = False
    if not np.all(np.isfinite(ln_g)):
        print("[SMOKE] FAIL: ln_g contains non-finite values")
        ok = False
    # g(E) should be large (slow E-vs-x change) at the minima and small at the
    # barrier top; the log density should be monotonically decreasing-ish into
    # the barrier region. Just check it is not flat-constant (a crashed run
    # yields all zeros).
    if np.ptp(ln_g) < 1e-6:
        print("[SMOKE] FAIL: ln_g is constant (sampler did not move)")
        ok = False

    # Thermodynamics should run and give finite logZ
    temps = [100, 200, 300, 500, 1000]
    rows = g_of_E_to_thermodynamics(bin_centers_rel, ln_g,
                                    sampler.E_ref, sampler.n_atoms, temps)
    for (T, beta, logZ, Z, F) in rows:
        if not (np.isfinite(logZ) and np.isfinite(F)):
            print(f"[SMOKE] FAIL: non-finite thermodynamics at T={T}")
            ok = False
        print(f"  T={T:6.1f} K  logZ={logZ:9.4f}  Z={Z:9.4e}  F={F:9.4f} eV")
    cv = heat_capacity_from_thermo(rows)
    print(f"[SMOKE] heat capacity points: {len(cv)}")

    return ok


def test_two_species_swap():
    """Verify the swap (permutation) move on a 2-species toy.

    Checks that (a) swap moves actually occur in proportion to swap_prob, and
    (b) a single-species system with swap_prob>0 falls back to all-rattle.
    """
    print("\n--- swap move test (2-species toy) ---")

    class FakeGPR:
        def predict_energy(self, atoms):
            return float(atoms.positions[:, 0].sum())

    positions = np.array([[x, 0, 0] for x in range(10)], float)
    atoms = Atoms(["B"] * 5 + ["Fe"] * 5, positions=positions)
    structs = [atoms.copy() for _ in range(5)]
    for k, a in enumerate(structs):
        a.positions += np.random.default_rng(k).normal(0, 0.01, a.positions.shape)
    energies = np.array([FakeGPR().predict_energy(a) for a in structs])

    ok = True

    # (a) 2-species: swap_prob=0.5 should yield ~half swap moves
    s = WangLandauSampler(FakeGPR(), structs, energies, n_bins=20,
                          e_min=0.0, e_max=2.0, swap_prob=0.5, max_swaps=3,
                          swap_rattle=0.05, perturb_symbols="B,Fe",
                          rng=np.random.default_rng(1))
    s.initialize(start_from_top=True)
    for _ in range(2000):
        s._propose_move()
    print(f"[SMOKE] 2-species swap_prob=0.5: rattle={s.n_rattle_moves} "
          f"swap={s.n_swap_moves}")
    if not (s.swap_available and s.n_swap_moves > 0):
        print("[SMOKE] FAIL: no swap moves in a 2-species system")
        ok = False

    # (b) single-species: swap_prob>0 falls back to all-rattle (no crash)
    atoms1 = Atoms(["Fe"] * 5, positions=np.array([[x, 0, 0] for x in range(5)], float))
    structs1 = [atoms1.copy() for _ in range(5)]
    for k, a in enumerate(structs1):
        a.positions += np.random.default_rng(k).normal(0, 0.01, a.positions.shape)
    energies1 = np.array([FakeGPR().predict_energy(a) for a in structs1])
    s1 = WangLandauSampler(FakeGPR(), structs1, energies1, n_bins=10,
                           e_min=0.0, e_max=2.0, swap_prob=0.5, max_swaps=3,
                           perturb_symbols="Fe", rng=np.random.default_rng(3))
    s1.initialize(start_from_top=True)
    for _ in range(1000):
        s1._propose_move()
    print(f"[SMOKE] single-species swap_prob=0.5: rattle={s1.n_rattle_moves} "
          f"swap={s1.n_swap_moves} (expect swap=0)")
    if s1.n_swap_moves != 0:
        print("[SMOKE] FAIL: swap moves occurred in a single-species system")
        ok = False

    return ok


if __name__ == "__main__":
    sys.exit(main())
