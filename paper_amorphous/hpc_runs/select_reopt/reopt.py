"""reopt.py — Run A (stage 2): DFT re-optimization of the selected amorphous minima.

Runs on the HPC node in the **gpaw_env** conda env (has BOTH gpaw and agox — see spec
M2). Reads the XSF structures chosen by filter_select.py (Run A stage 1, written under
<selroot>/selected/<leaf>/<rank>.xsf), re-relaxes each with real GPAW DFT to a strict
fmax, then writes one ASE trajectory of relaxed minima per leaf:
    opt_novel_<leaf>.traj
plus a per-structure summary JSON/CSV.

GPAW settings are taken VERBATIM from the source Pt-P runs'
data/17_PPt/<family>/<leaf>/main.py (G1):
    mode lcao, basis dzp, xc PBE, symmetry off, nbands 'nao',
    occupations fermi-dirac width 0.05, mixer pulay {beta 0.05, nmaxold 5, weight 100},
    convergence {energy 1e-4, density 1e-3, eigenstates 1e-3}, maxiter 100.
This is a bulk amorphous cell with NO frozen substrate — all atoms are mobile
(FixAtoms not applied).

Usage (HPC, gpaw_env):
  python reopt.py --selroot <sel_outdir> --outdir ./reopt_out [--fmax 0.05]
Writes:
  opt_novel_<leaf>.traj        ASE traj of relaxed minima per leaf
  reopt_summary_<leaf>.json    provenance + final forces/energies
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import json
import os
from pathlib import Path

import numpy as np


# GPAW settings verbatim from data/17_PPt/<leaf>/main.py
DFT = dict(
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    symmetry="off",
    nbands="nao",
    occupations={"name": "fermi-dirac", "width": 0.05},
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    maxiter=100,
    kpts=(1, 1, 1),
)


def relax_one(atoms, fmax, directory):
    """GPAW relaxation to strict fmax, all atoms mobile. Returns relaxed Atoms."""
    from ase.optimize import BFGS
    from gpaw import GPAW

    calc = GPAW(txt=os.path.join(directory, "relax.txt"), **DFT)
    atoms.calc = calc
    opt = BFGS(atoms, logfile=os.path.join(directory, "bfgs.log"))
    opt.run(fmax=fmax)
    return atoms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selroot", default=None,
                    help="filter_select.py --outdir (default: this dir's ./out_select_reopt)")
    ap.add_argument("--outdir", default=None,
                    help="output dir (default: this dir's ./out_select_reopt)")
    ap.add_argument("--fmax", type=float, default=0.05)
    ap.add_argument("--leaf", default=None, help="restrict to one leaf key")
    args = ap.parse_args()

    # Standalone: default to this dir's output (all in-dir).
    here = os.path.dirname(os.path.abspath(__file__))
    if args.selroot is None:
        args.selroot = os.path.join(here, "out_select_reopt")
    if args.outdir is None:
        args.outdir = os.path.join(here, "out_select_reopt")

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    from ase.io import read as ase_read
    from ase.io import write as ase_write

    # find per-leaf chosen XSFs
    selroots = sorted(glob.glob(os.path.join(args.selroot, "selected", "*")))
    for sel_dir in selroots:
        leaf = os.path.basename(sel_dir)
        if args.leaf and leaf != args.leaf:
            continue
        xsfs = sorted(glob.glob(os.path.join(sel_dir, "*.xsf")))
        if not xsfs:
            print(f"[{leaf}] no XSF, skipping")
            continue
        relaxed_list = []
        summary = []
        for rank, x in enumerate(xsfs, start=1):
            atoms = ase_read(x)
            work = Path(args.outdir) / leaf / str(rank)
            work.mkdir(parents=True, exist_ok=True)
            try:
                relaxed = relax_one(atoms, args.fmax, str(work))
                F = np.asarray(relaxed.get_forces())
                n = np.linalg.norm(F, axis=1)
                s = {
                    "leaf": leaf, "rank": rank,
                    "formula": relaxed.get_chemical_formula(),
                    "energy_eV": relaxed.get_potential_energy(),
                    "max_force_eV_per_A": float(n.max()),
                    "mean_force_eV_per_A": float(n.mean()),
                }
                relaxed_list.append(relaxed)
                summary.append(s)
                print(f"[{leaf}] rank {rank}: E={s['energy_eV']:.3f} "
                      f"maxF={s['max_force_eV_per_A']:.3f}")
            except Exception as e:  # noqa: BLE001 — report & continue per structure
                summary.append({"leaf": leaf, "rank": rank, "error": str(e)})
                print(f"[{leaf}] rank {rank}: FAILED {e}")
        if relaxed_list:
            traj = Path(args.outdir) / f"opt_novel_{leaf}.traj"
            ase_write(str(traj), relaxed_list)
            with open(Path(args.outdir) / f"reopt_summary_{leaf}.json", "w") as f:
                json.dump({
                    "leaf": leaf,
                    "description": {
                        "kind": "Run A stage-2: DFT re-opt of novel+low-force selected "
                                "amorphous Pt-P minima to strict fmax (GPAW lcao/dzp/PBE).",
                        "method": "BFGS/GPAW, all atoms mobile, fmax from --fmax",
                        "units": "energy eV; forces eV/A",
                    },
                    "relaxed": summary,
                }, f, indent=2)


if __name__ == "__main__":
    main()
