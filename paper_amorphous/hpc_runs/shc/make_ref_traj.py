"""make_ref_traj.py — build the 0%-P crystalline reference traj for Run B.

Writes the GLOBAL-MINIMUM structure of the +0 cell 0% P leaf
(data/17_PPt/1_plus0cell/0_0P) as an ASE traj `ref_0P_gmin.traj` (spec G2/G5/m4).
Composition Pt108 (fcc Pt). Lowest energy across that leaf's seeds.

Runs in **agox_v2** (AGOX read; read-only on data/17_PPt). May also be run on the HPC
in gpaw_env. Does NOT relax — it snapshots the db global minimum as the SHC reference.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python make_ref_traj.py \
      --out ref_0P_gmin.traj
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import os
from pathlib import Path

from agox.databases import Database


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leaf", default="data/17_PPt/1_plus0cell/0_0P")
    ap.add_argument("--out", default="ref_0P_gmin.traj")
    args = ap.parse_args()

    dbs = sorted(glob.glob(os.path.join(args.leaf, "seed_*/1_db/db_*.db")))
    if not dbs:
        raise SystemExit(f"no seed dbs under {args.leaf}")

    best = None
    best_db = None
    best_e = None
    for dbp in dbs:
        db = Database(filename=dbp)
        db.restore_to_memory()
        for a in db.get_all_candidates():
            e = a.get_potential_energy()
            if best_e is None or e < best_e:
                best, best_e, best_db = a, e, dbp

    if best is None:
        raise SystemExit("no candidate found")

    from ase.io import write
    write(args.out, best)
    print(f"wrote {args.out}")
    print(f"  formula={best.get_chemical_formula()} atoms={len(best)}")
    print(f"  energy_E_v={best_e:.4f}  source_db={best_db}")


if __name__ == "__main__":
    main()
