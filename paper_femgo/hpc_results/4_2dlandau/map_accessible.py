#!/usr/bin/env python3
"""Map the accessible (E, dZ) cells on the real GPR — a longer reference pass.

Trains the real GPR once, then runs N proposal steps (draw target dZ -> generate
on adsorption sites -> GPR relax under the dZ ceiling -> bin (E, dZ)), and
reports:
  - the accessible-cell count (and fraction of the 35x12 grid),
  - the per-dZ E-spread (min/max rel E in each visited dZ column),
  - the dZ bins actually reachable.

This answers "how many cells are actually accessible / what does the band look
like" without running the full WL production.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python map_accessible.py [--n N] [--relax-steps S]
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from landau_2d.gpr_training import load_all_seeds, build_gpr
from landau_2d.generator import DeltaZGenerator

DATA_DIR = os.path.join(_HERE, "..", "data", "femgo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120,
                    help="number of proposals (default 120)")
    ap.add_argument("--relax-steps", type=int, default=100,
                    help="BFGS steps per proposal (default 100, production)")
    ap.add_argument("--n-e-bins", type=int, default=35)
    ap.add_argument("--e-max", type=float, default=0.7)
    ap.add_argument("--n-dz-bins", type=int, default=12)
    args = ap.parse_args()

    structures, energies, _ = load_all_seeds(DATA_DIR)
    print(f"loaded {len(structures)} structures")
    gpr = build_gpr(structures, use_ray=False)
    gen = DeltaZGenerator(structures[0], z_contact=None, contact_gap=2.08,
                          rng=np.random.default_rng(0))
    E_ref = energies.min()
    n_atoms = len(structures[0])

    # dZ range = film height [flat ~ contact gap, natural island height]
    dz_min = gen.z_contact - gen.substrate_top_z      # = contact gap
    i_min = int(np.argmin(energies))
    dz_max = gen.fe_film_height(structures[i_min])
    print(f"dZ range (film height): [{dz_min:.3f}, {dz_max:.3f}] A")

    e_width = args.e_max / args.n_e_bins
    dz_width = (dz_max - dz_min) / args.n_dz_bins

    from agox.utils.constraints.box_constraint import BoxConstraint
    from ase.constraints import FixAtoms
    import ase.optimize

    def relax(atoms, dz_target):
        z_floor = gen.substrate_top_z
        z_ceil = z_floor + dz_target
        cell = gen.cell.copy()
        cell[2, 2] = (z_ceil - z_floor) + 1e-6
        box = BoxConstraint(confinement_cell=cell,
                            confinement_corner=np.array([0.0, 0.0, z_floor]),
                            indices=gen.fe_indices, pbc=[True, True, False])
        fix = FixAtoms(indices=list(map(int, gen.substrate_indices)))
        r = atoms.copy()
        r.set_constraint([box, fix])
        r.calc = gpr
        try:
            opt = ase.optimize.BFGS(r, logfile=None)
            opt.run(fmax=0.05, steps=args.relax_steps)
        except Exception as e:
            print(f"  relax failed: {e}")
        return r

    t0 = time.time()
    rel_E = []
    dZ = []
    rng = np.random.default_rng(1)
    for k in range(args.n):
        target = float(rng.uniform(dz_min, dz_max))
        trial = gen(target)
        r = relax(trial, target)
        E = gpr.predict_energy(r)
        rel = (E - E_ref) / n_atoms
        dz = gen.fe_film_height(r)
        if np.isfinite(rel) and abs(E) < 1e4 and rel <= 5 * args.e_max:
            rel_E.append(rel)
            dZ.append(dz)
    rel_E = np.asarray(rel_E)
    dZ = np.asarray(dZ)
    print(f"\n{args.n} proposals, {len(rel_E)} physical, in {time.time()-t0:.1f}s")

    # bin and count
    i = np.minimum((rel_E / e_width).astype(int), args.n_e_bins - 1)
    j = np.minimum(((dZ - dz_min) / dz_width).astype(int), args.n_dz_bins - 1)
    occupied = set(zip(i.tolist(), j.tolist()))
    n_cells = len(occupied)
    n_grid = args.n_e_bins * args.n_dz_bins
    print(f"accessible cells: {n_cells} / {n_grid} "
          f"({100.0*n_cells/n_grid:.1f}%)")
    print(f"distinct E bins reached: {len(set(i.tolist()))} / {args.n_e_bins}")
    print(f"distinct dZ bins reached: {len(set(j.tolist()))} / {args.n_dz_bins}")

    # per-dZ column E-spread
    print("\ndZ-bin  center(A)  n    E_min      E_max      spread(eV/atom)")
    for jj in range(args.n_dz_bins):
        m = j == jj
        if not m.any():
            continue
        center = dz_min + dz_width * (jj + 0.5)
        print(f"  {jj:2d}     {center:5.2f}    {m.sum():3d}  "
              f"{rel_E[m].min():9.4f}  {rel_E[m].max():9.4f}  "
              f"{rel_E[m].max()-rel_E[m].min():9.4f}")

    print("\noverall rel E: min %.4f  max %.4f eV/atom"
          % (rel_E.min(), rel_E.max()))
    print("overall dZ  : min %.4f  max %.4f A" % (dZ.min(), dZ.max()))


if __name__ == "__main__":
    main()
