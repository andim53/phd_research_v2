#!/usr/bin/env python3
"""Option-A reachability probe: run the DeltaZGenerator + 300-step GPR relax
5 times and report the inherent-structure energies reached, to check whether
the generator+relax stalls at the global minimum (i.e. reaches it too fast,
which would collapse NS live points to one energy).

Run: /home/think/miniconda3/envs/agox_v2/bin/python probe_optionA.py
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

def main():
    print("=" * 70)
    print("Loading dataset + training GPR (same recipe as 2dlandau)...")
    t0 = time.perf_counter()
    structures, energies, db_paths = load_all_seeds(DATA_DIR)
    print(f"  {len(structures)} structures, {len(db_paths)} DBs, "
          f"E range {energies.min():.4f}..{energies.max():.4f} eV")
    gpr = build_gpr(structures)
    E_ref = float(energies.min())
    n_atoms = len(structures[0])
    print(f"  GPR trained in {time.perf_counter()-t0:.1f}s; E_ref={E_ref:.4f} eV")

    gen = DeltaZGenerator(structures[0], z_contact=None, contact_gap=2.08,
                          rng=np.random.default_rng(42))
    print(f"  z_contact={gen.z_contact:.4f} A, substrate_top={gen.substrate_top_z:.4f} A")

    print("\n" + "=" * 70)
    print(f"Option-A probe: {N_TRIALS} independent generator+relax trials "
          f"({RELAX_STEPS} BFGS steps each)")
    print("=" * 70)
    results = []
    for k in range(N_TRIALS):
        dz_target = gen.draw_target_dz(DZ_MIN, DZ_MAX)
        trial = gen(dz_target)
        # relax under the dZ ceiling, same as WL _relax
        from ase.optimize import BFGS
        from ase.constraints import FixAtoms
        from agox.utils.constraints.box_constraint import BoxConstraint
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
        opt.run(fmax=0.05, steps=RELAX_STEPS)
        E = float(gpr.predict_energy(relaxed))
        rel = (E - E_ref) / n_atoms
        dz = gen.fe_film_height(relaxed)
        spread = gen.fe_z_spread(relaxed)
        results.append((dz_target, E, rel, dz, spread))
        print(f"  trial {k+1}: dZ_target={dz_target:.3f} A -> "
              f"E={E:9.4f} eV, rel={rel:7.4f} eV/atom, "
              f"dZ={dz:.3f} A, z-spread={spread:.3f} A")

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    rels = [r[2] for r in results]
    print(f"  rel energies reached: {[f'{r:.4f}' for r in rels]}")
    print(f"  min rel: {min(rels):.4f} eV/atom, max rel: {max(rels):.4f} eV/atom")
    print(f"  spread (max-min): {max(rels)-min(rels):.4f} eV/atom")
    print(f"  E_ref (global min) = {E_ref:.4f} eV -> rel 0.0000")
    print(f"  n trials at rel < 0.05: {sum(1 for r in rels if r < 0.05)}")
    print(f"  n trials at rel < 0.10: {sum(1 for r in rels if r < 0.10)}")
    print("\n  Interpretation: if all 5 trials land at ~the same low rel energy,")
    print("  the generator+relax reaches the global min too fast -> NS live points")
    print("  would collapse to one energy (stall). If they spread out, NS can explore.")

if __name__ == "__main__":
    main()
