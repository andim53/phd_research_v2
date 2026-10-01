#!/usr/bin/env python3
"""Probe for M1: in the dZ region BETWEEN flat and natural island height, do
300-step GPR BFGS relaxes (under the dZ ceiling) converge to final max-force
below the 0.1 eV/A inherent-structure threshold, or do they stall (leftover
force) and thus get thrown out by the proposed stall-drop logic?

If they stall, the in-between cells would be dropped from the accessible map
and never sampled. If they converge below 0.1, the in-between region IS
sampleable (and the ceiling masks the z-growth residual, per M1).

Run: /home/think/miniconda3/envs/agox_v2/bin/python probe_inbetween_fmax.py
"""
import os, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "landau_2d"))

import matplotlib
matplotlib.use("Agg")

from landau_2d.gpr_training import load_all_seeds, build_gpr
from landau_2d.generator import DeltaZGenerator

DATA_DIR = os.path.join(_HERE, "..", "..", "data", "femgo")
N_TRIALS = 5
RELAX_STEPS = 300
FMAX_THRESH = 0.1
FLAT_SPREAD = 1.0
# in-between targets: flat ~2.08 (contact gap) .. natural island ~5.73
DZ_TARGETS = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]


def get_fmax(atoms):
    f = atoms.get_forces()
    return float(np.abs(f).max())


def main():
    print("=" * 70)
    print("Loading dataset + training GPR...")
    t0 = time.perf_counter()
    structures, energies, db_paths = load_all_seeds(DATA_DIR)
    gpr = build_gpr(structures)
    E_ref = float(energies.min())
    n_atoms = len(structures[0])
    print(f"  GPR trained in {time.perf_counter()-t0:.1f}s; E_ref={E_ref:.4f} eV")

    gen = DeltaZGenerator(structures[0], z_contact=None, contact_gap=2.08,
                          rng=np.random.default_rng(7))
    print(f"  z_contact={gen.z_contact:.4f} A, substrate_top={gen.substrate_top_z:.4f} A")

    from ase.optimize import BFGS
    from ase.constraints import FixAtoms
    from agox.utils.constraints.box_constraint import BoxConstraint

    print("\n" + "=" * 70)
    print(f"In-between dZ probe: {N_TRIALS} trials x {RELAX_STEPS} steps, "
          f"fmax threshold = {FMAX_THRESH} eV/A")
    print("=" * 70)

    for dz_target in DZ_TARGETS:
        gen.rng = np.random.default_rng(1000 + int(dz_target * 100))
        n_pass = 0
        n_stall = 0
        print(f"\n--- dZ target = {dz_target:.2f} A ---")
        for k in range(N_TRIALS):
            trial = gen(dz_target)
            trial.calc = gpr
            trial.set_constraint([])
            f0 = get_fmax(trial)

            z_floor = gen.substrate_top_z
            z_ceil = z_floor + dz_target
            cell = gen.cell.copy(); cell[2, 2] = (z_ceil - z_floor) + 1e-6
            box = BoxConstraint(confinement_cell=cell,
                                confinement_corner=np.array([0., 0., z_floor]),
                                indices=gen.fe_indices, pbc=[True, True, False])
            fix = FixAtoms(indices=list(map(int, gen.substrate_indices)))
            relaxed = trial.copy()
            relaxed.set_constraint([box, fix])
            relaxed.calc = gpr
            opt = BFGS(relaxed, logfile=None)
            try:
                opt.run(fmax=FMAX_THRESH, steps=RELAX_STEPS)
            except Exception as e:
                print(f"  trial {k+1}: relax error {e}")
                continue
            fn = get_fmax(relaxed)
            E = float(gpr.predict_energy(relaxed))
            rel = (E - E_ref) / n_atoms
            n_steps = opt.nsteps if hasattr(opt, 'nsteps') else '?'
            h_rel = gen.fe_film_height(relaxed)
            spread = gen.fe_z_spread(relaxed)
            lab = "flat" if spread < FLAT_SPREAD else "island"
            passed = fn <= FMAX_THRESH
            n_pass += passed
            n_stall += (not passed)
            print(f"  trial {k+1}: f0={f0:8.4f} -> f_final={fn:8.4f} eV/A, "
                  f"rel={rel:7.4f} eV/atom, h={h_rel:5.3f} A, spread={spread:5.3f} "
                  f"({lab}), nsteps={n_steps}, "
                  f"{'PASS<0.1' if passed else 'STALL>0.1'}")
        print(f"  => {n_pass}/{N_TRIALS} pass (f_final<={FMAX_THRESH}), "
              f"{n_stall}/{N_TRIALS} stall (would be dropped)")

    print("\nDone.")
    print("Interpretation: if most in-between trials STALL, the stall-drop "
          "logic would make the in-between region inaccessible (never sampled). "
          "If they PASS, the region is sampleable and the ceiling masks the "
          "z-growth residual (M1 confirmed).")


if __name__ == "__main__":
    main()
