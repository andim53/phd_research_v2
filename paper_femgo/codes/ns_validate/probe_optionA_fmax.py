#!/usr/bin/env python3
"""Force-tolerance probe for Option A: does a more lenient fmax (0.1, 0.2)
let the GPR BFGS relax converge, given surrogate noise? Runs 5 trials at each
of two fmax tolerances and reports final force + convergence.

Run: /home/think/miniconda3/envs/agox_v2/bin/python probe_optionA_fmax.py
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
DZ_MIN, DZ_MAX = 2.08, 5.73
FMAX_TOLERANCES = [0.1, 0.2]

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

    for fmax_tol in FMAX_TOLERANCES:
        print("\n" + "=" * 70)
        print(f"fmax tolerance = {fmax_tol} eV/A : {N_TRIALS} x "
              f"{RELAX_STEPS}-step relax")
        print("=" * 70)
        # fresh dZ targets per tolerance so we see the tolerance effect, not the same trials
        gen.rng = np.random.default_rng(100 + int(fmax_tol * 100))
        for k in range(N_TRIALS):
            dz_target = gen.draw_target_dz(DZ_MIN, DZ_MAX)
            trial = gen(dz_target)
            trial.calc = gpr
            trial.set_constraint([])
            f0 = get_fmax(trial)

            z_floor = gen.substrate_top_z
            z_ceil = z_floor + dz_target
            cell = gen.cell.copy(); cell[2,2] = (z_ceil - z_floor) + 1e-6
            box = BoxConstraint(confinement_cell=cell,
                                confinement_corner=np.array([0.,0.,z_floor]),
                                indices=gen.fe_indices, pbc=[True,True,False])
            fix = FixAtoms(indices=list(map(int, gen.substrate_indices)))
            relaxed = trial.copy()
            relaxed.set_constraint([box, fix])
            relaxed.calc = gpr
            opt = BFGS(relaxed, logfile=None)
            try:
                opt.run(fmax=fmax_tol, steps=RELAX_STEPS)
            except Exception as e:
                print(f"  trial {k+1}: relax error {e}")
                continue
            fn = get_fmax(relaxed)
            E = float(gpr.predict_energy(relaxed))
            rel = (E - E_ref) / n_atoms
            n_steps = opt.nsteps if hasattr(opt, 'nsteps') else '?'
            converged = fn <= fmax_tol
            print(f"  trial {k+1}: f0={f0:8.4f} -> f_final={fn:8.4f} eV/A, "
                  f"rel={rel:7.4f} eV/atom, nsteps={n_steps}, "
                  f"{'CONVERGED' if converged else 'LEFT-OVER FORCE'}")

    print("\nDone.")

if __name__ == "__main__":
    main()
