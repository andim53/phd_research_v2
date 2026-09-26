#!/usr/bin/env python3
"""
Generate example structures at several film-height (dZ) bins — both as the
random generator produces them AND after GPR relaxation under the dZ ceiling —
and write each as an XSF file (VESTA-readable) for visual inspection. Also plots
the relaxation energy trajectory (E vs BFGS step, from the randomized candidate
down to the constrained minimum) for each target.

Output goes to paper_femgo/analysis/2dlandau_examples/:
  - gen_dz_<h>.xsf       : raw generated candidate (film height = h)
  - relax_dz_<h>.xsf     : same candidate after GPR relax (ceiling at h)
  - relax_energy.png     : E vs relaxation step for every target, overlaid
  - summary.csv          : target h vs relaxed film height, E, label

The dZ axis is the film height = max(z_Fe) - z_substrate_top, spanning
[contact_gap, natural_island_height].

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python make_examples.py [--n N]
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ase.io import write as ase_write

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJ = os.path.dirname(_HERE)          # paper_femgo
_DATA = os.path.join(_PROJ, "data", "femgo")
_OUTDIR = os.path.join(_PROJ, "analysis", "2dlandau_examples")

sys.path.insert(0, _HERE)

from landau_2d.gpr_training import load_all_seeds, build_gpr
from landau_2d.generator import DeltaZGenerator
from agox.utils.constraints.box_constraint import BoxConstraint
from ase.constraints import FixAtoms
import ase.optimize


def _strip_constraints(atoms):
    """Copy with no constraints (XSF doesn't serialize them)."""
    a = atoms.copy()
    a.set_constraint([])
    return a


def _relax(gpr, gen, atoms, dz_target, relax_steps):
    """Relax under the dZ ceiling; return (relaxed, [E0, E1, ...] per step)."""
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

    energies = [gpr.predict_energy(r)]

    def _cb(opt=None):
        energies.append(gpr.predict_energy(r))

    try:
        opt = ase.optimize.BFGS(r, logfile=None)
        opt.attach(_cb)
        opt.run(fmax=0.05, steps=relax_steps)
    except Exception as e:
        print(f"  [warn] relax failed for h={dz_target:.3f}: {e}")
    return r, energies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6,
                    help="number of example film-height targets (default 6)")
    ap.add_argument("--relax-steps", type=int, default=50,
                    help="BFGS steps per structure (default 50)")
    args = ap.parse_args()

    os.makedirs(_OUTDIR, exist_ok=True)

    structures, energies, _ = load_all_seeds(_DATA)
    gpr = build_gpr(structures, use_ray=False)
    gen = DeltaZGenerator(structures[0], z_contact=None, contact_gap=2.08,
                          rng=np.random.default_rng(0))

    dz_min = gen.z_contact - gen.substrate_top_z      # contact gap (~2.08)
    i_min = int(np.argmin(energies))
    dz_max = gen.fe_film_height(structures[i_min])     # natural island (~5.73)
    print(f"dZ range (film height): [{dz_min:.3f}, {dz_max:.3f}] A")

    targets = np.linspace(dz_min, dz_max, args.n)
    print(f"targets: {['%.3f' % t for t in targets]}")

    E_ref = energies.min()
    n_atoms = len(structures[0])
    rows = []
    traj = {}

    for h in targets:
        trial = gen(h)
        h_gen = gen.fe_film_height(trial)
        ase_write(os.path.join(_OUTDIR, f"gen_dz_{h:.2f}.xsf"),
                  _strip_constraints(trial))
        print(f"  gen h={h:.3f} -> film height {h_gen:.3f} A "
              f"(spread {gen.fe_z_spread(trial):.3f}), "
              f"E = {gpr.predict_energy(trial):.3f} eV")

        relaxed, es = _relax(gpr, gen, trial, h, args.relax_steps)
        traj[h] = es
        h_rel = gen.fe_film_height(relaxed)
        E_rel = gpr.predict_energy(relaxed)
        rel_eV = (E_rel - E_ref) / n_atoms
        lab = "flat" if gen.fe_z_spread(relaxed) < 1.0 else "island"
        ase_write(os.path.join(_OUTDIR, f"relax_dz_{h:.2f}.xsf"),
                  _strip_constraints(relaxed))
        print(f"  relax h={h:.3f} -> film height {h_rel:.3f} A "
              f"(spread {gen.fe_z_spread(relaxed):.3f}), "
              f"E = {E_rel:.3f} eV (rel {rel_eV:.4f}), {lab} "
              f"after {len(es)-1} steps")
        rows.append((h, h_gen, h_rel, E_rel, rel_eV, lab))

    # summary.csv
    with open(os.path.join(_OUTDIR, "summary.csv"), "w") as f:
        f.write("target_film_height_A,gen_film_height_A,relax_film_height_A,"
                "E_relaxed_eV,rel_eV_per_atom,label\n")
        for (h, hg, hr, E, rel, lab) in rows:
            f.write(f"{h:.4f},{hg:.4f},{hr:.4f},{E:.4f},{rel:.4f},{lab}\n")

    # --- relaxation energy trajectories -------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    cmap = plt.get_cmap("viridis")
    for k, h in enumerate(targets):
        es = traj[h]
        steps = np.arange(len(es))
        color = cmap(k / max(len(targets) - 1, 1))
        ax.plot(steps, es, marker="o", ms=3, lw=1.2, color=color,
                label=f"dZ = {h:.2f} A")
    ax.set_xlabel("BFGS step")
    ax.set_ylabel("GPR energy (eV)")
    ax.set_title("Relaxation under dZ ceiling (randomized -> constrained minimum)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(_OUTDIR, "relax_energy.png"), dpi=150)
    plt.close(fig)

    print(f"\nWrote {len(rows)*2} XSF files + summary.csv + relax_energy.png "
          f"to {_OUTDIR}")


if __name__ == "__main__":
    main()