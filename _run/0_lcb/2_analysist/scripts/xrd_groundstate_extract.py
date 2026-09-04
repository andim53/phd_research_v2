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

__version__ = "2.0.0"

import argparse
import glob
import json
import os

import numpy as np

from agox.databases import Database
from ase.io import write as ase_write


def detect_host_interstitial(counts):
    """Given a {element: count} Counter, return
    (host_symbol, interstitial_symbol, interstitial_symbols, concentration_pct).

    Host = majority species; everything else is treated as interstitial (summed).
    interstitial_symbol is the single minority element when there is exactly one,
    else None; concentration_pct = 100 * n_inter / total."""
    host = max(counts, key=lambda k: counts[k])
    inter_symbols = sorted(k for k in counts if k != host)
    n_host = counts[host]
    n_inter = sum(counts[k] for k in inter_symbols)
    conc = 100.0 * n_inter / (n_host + n_inter) if (n_host + n_inter) else 0.0
    inter_symbol = inter_symbols[0] if len(inter_symbols) == 1 else None
    return host, inter_symbol, inter_symbols, float(conc)


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
        host_sym, inter_sym, inter_symbols, conc = detect_host_interstitial(c)
        leaf_out = os.path.join(args.outdir, os.path.basename(ld))
        os.makedirs(leaf_out, exist_ok=True)
        ase_write(os.path.join(leaf_out, "groundstate.cif"), gs)
        inter_label = inter_sym if inter_sym is not None else "+".join(inter_symbols)
        rec = {
            "leaf": os.path.basename(ld),
            "composition": dict(c),
            "formula": comp,
            "n_atoms": n_atoms,
            "host_symbol": host_sym,
            "interstitial_symbol": inter_label,
            "interstitial_symbols": inter_symbols,
            "n_host": int(c[host_sym]),
            "n_interstitial": int(sum(c[k] for k in inter_symbols)),
            "concentration_pct": float(conc),
            "E_glob_eV": float(eg),
            "cif": os.path.join(os.path.basename(ld), "groundstate.cif"),
        }
        with open(os.path.join(leaf_out, "groundstate.json"), "w") as f:
            json.dump(rec, f, indent=1)
        manifest.append(rec)
        print(f"  {os.path.basename(ld):6s} {comp:12s} E_glob={eg:.3f}  "
              f"{(inter_label + '=') if inter_label else ''}{conc:.1f}%  "
              f"-> {rec['cif']}")

    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump({"family": args.family, "leaves": manifest}, f, indent=1)
    print(f"\nDone. {len(manifest)} ground-state CIFs under {args.outdir}")
    print(f"manifest -> {os.path.join(args.outdir, 'manifest.json')}")


if __name__ == "__main__":
    main()