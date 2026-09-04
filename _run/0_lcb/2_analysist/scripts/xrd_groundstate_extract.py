#!/usr/bin/env python3
"""
Stage 1 — ground-state comparison: extract each 1_plus0cell Pt-P leaf's global
ground-state structure (rel-E = 0) as a CIF.

Runs in the **agox_v2** env (AGOX + ASE). For a family of leaves (dataset dirs),
each holding seed_*/1_db/db_*.db, it loads every structure (iteration >= 10),
finds the single structure at the leaf's global minimum energy (rel-E = 0), and
writes it as a CIF into the leaf's output dir.

Writes, under each leaf's --outdir (suggested <leaf>/xrd_gs_compare/):
  groundstate.cif        : the rel-E=0 structure
  groundstate.json       : leaf metadata (composition, E_glob, concentration %)

Usage (agox_v2):
  PY=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY xrd_groundstate_extract.py --family 17_PPt/1_plus0cell \
        --outdir 17_PPt/1_plus0cell/xrd_gs_compare
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import json
import os

import numpy as np

from agox.databases import Database
from ase.io import write as ase_write


def load_leaf(dataset_dir: str, start_iter: int = 10):
    """All structures + energies + iterations from dataset_dir/seed_*/1_db/db_*.db
    with AGOX iteration >= start_iter."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(
            f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    atoms_list, e_list = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        for d in raw:
            if d.get("iteration", 0) >= start_iter:
                a = db.db_to_atoms(d)
                atoms_list.append(a)
                e_list.append(a.get_potential_energy())
    return atoms_list, np.asarray(e_list, dtype=float)


def main():
    parser = argparse.ArgumentParser(
        description="Extract each Pt-P 1_plus0cell leaf's global ground-state (rel-E=0) "
                    "CIF (agox_v2).")
    parser.add_argument("--family", required=True,
                        help="family dir holding the concentration leaf subdirs "
                             "(e.g. 17_PPt/1_plus0cell)")
    parser.add_argument("--leaves", nargs="*", default=None,
                        help="concentration leaf names (e.g. 0_0P 1_10P 2_20P 3_30P); "
                             "default: all [0-9]* subdirs holding seed_*/1_db")
    parser.add_argument("--outdir", required=True,
                        help="shared output dir under the family "
                             "(e.g. 17_PPt/1_plus0cell/xrd_gs_compare)")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep structures with AGOX iteration >= this. Default 10.")
    args = parser.parse_args()

    if args.leaves:
        leaf_dirs = [os.path.join(args.family, l) for l in args.leaves]
    else:
        leaf_dirs = sorted(glob.glob(os.path.join(args.family, "[0-9]*")))

    print("=" * 70)
    print("Ground-state extraction (agox_v2)")
    print(f"family  : {args.family}")
    print(f"outdir  : {args.outdir}")
    print(f"leaves  : {[os.path.basename(d) for d in leaf_dirs]}")
    print("=" * 70)

    os.makedirs(args.outdir, exist_ok=True)
    manifest = []
    for ld in leaf_dirs:
        if not os.path.isdir(ld):
            print(f"  skip (not a dir): {ld}")
            continue
        atoms_list, energies = load_leaf(ld, start_iter=args.start_iter)
        if not atoms_list:
            print(f"  [{os.path.basename(ld)}] no structures -> skip")
            continue
        eg = energies.min()
        i = int(np.argmin(energies))          # first index attaining the global min
        gs = atoms_list[i]
        comp = gs.get_chemical_formula()
        from collections import Counter
        c = Counter(gs.get_chemical_symbols())
        n_atoms = len(gs)
        nP = c.get("P", 0); nPt = c.get("Pt", 0)
        conc = 100.0 * nP / (nPt + nP) if (nPt + nP) else 0.0
        leaf_out = os.path.join(args.outdir, os.path.basename(ld))
        os.makedirs(leaf_out, exist_ok=True)
        ase_write(os.path.join(leaf_out, "groundstate.cif"), gs)
        rec = {
            "leaf": os.path.basename(ld),
            "composition": dict(c),
            "formula": comp,
            "n_atoms": n_atoms,
            "nPt": nPt, "nP": nP,
            "P_concentration_pct": float(conc),
            "E_glob_eV": float(eg),
            "cif": os.path.join(os.path.basename(ld), "groundstate.cif"),
        }
        with open(os.path.join(leaf_out, "groundstate.json"), "w") as f:
            json.dump(rec, f, indent=1)
        manifest.append(rec)
        print(f"  {os.path.basename(ld):6s} {comp:12s} E_glob={eg:.3f}  "
              f"P={conc:.1f}%  -> {rec['cif']}")

    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump({"family": args.family, "leaves": manifest}, f, indent=1)
    print(f"\nDone. {len(manifest)} ground-state CIFs under {args.outdir}")
    print(f"manifest -> {os.path.join(args.outdir, 'manifest.json')}")


if __name__ == "__main__":
    main()