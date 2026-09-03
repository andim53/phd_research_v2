#!/usr/bin/env python3
"""
Stage-1 helper — export .xsf structures by relative-energy-per-atom window.

Runs in the **agox_v2** env (AGOX + ASE). For one Ta-B (fxg) leaf (a dataset dir
holding seed_*/1_db/db_*.db), it loads every structure (iteration >= start_iter),
computes the relative energy per atom

    rel_e = (E - E_glob) / n_atoms,   E_glob = global min across the whole leaf

and, for each requested energy target, exports up to N .xsf files for the
lowest-rel-energy structures whose rel_e lies in the closed window

    [target - tol, target + tol].

"At least 3 (if any)" is honoured as: export up to N (default 3) structures per
window — all that fall in the window when fewer than N exist, none when the
window is empty.

Writes, under --outdir (suggested <leaf>/analysis_indices/rel_window_xsf/):
  relE_<target>_<seed>_iter<it>_rel<rel_e>.xsf   (one per exported structure)
  summary.json                                     (per-window counts + exported list)

Usage (agox_v2):
  PY=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY extract_rel_window_xsf.py --dataset 11_bTa/7_fxg_0b \
        --outdir 11_bTa/7_fxg_0b/analysis_indices/rel_window_xsf \
        --targets 0.01 0.1 0.15 --tol 0.005
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
    with AGOX iteration >= start_iter. Returns (atoms_list, energies, seed_labels,
    iterations)."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(
            f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    atoms_list, e_list, labels, iters = [], [], [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        for d in kept:
            atoms_list.append(db.db_to_atoms(d))
            e_list.append(atoms_list[-1].get_potential_energy())
            rel = os.path.relpath(p, dataset_dir)
            labels.append(rel.split(os.sep)[0])     # seed_0, seed_1, ...
            iters.append(int(d.get("iteration", 0)))
    return atoms_list, np.asarray(e_list, dtype=float), labels, iters


def main():
    parser = argparse.ArgumentParser(
        description="Export .xsf structures by relative-energy-per-atom window "
                    "(agox_v2, Ta-B fxg leaves).")
    parser.add_argument("--dataset", required=True,
                        help="leaf dataset dir holding seed_*/1_db/db_*.db")
    parser.add_argument("--outdir", required=True,
                        help="output dir (suggest <leaf>/analysis_indices/rel_window_xsf)")
    parser.add_argument("--targets", type=float, nargs="+", required=True,
                        help="relative-energy/atom targets (eV/atom), e.g. 0.01 0.1 0.15")
    parser.add_argument("--tol", type=float, default=0.005,
                        help="half-width of each window (eV/atom). Default 0.005.")
    parser.add_argument("--max-per-window", type=int, default=3,
                        help="max structures exported per window (lowest rel_e first). "
                             "Default 3.")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep structures with AGOX iteration >= this. Default 10.")
    args = parser.parse_args()

    print("=" * 70)
    print("Extract .xsf by relative-energy/atom window (agox_v2)")
    print(f"dataset : {args.dataset}")
    print(f"outdir  : {args.outdir}")
    print(f"targets : {args.targets}  tol=+/-{args.tol}")
    print(f"max-per-window : {args.max_per_window}  start_iter={args.start_iter}")
    print("=" * 70)

    atoms_list, energies, labels, iters = load_leaf(args.dataset,
                                                    start_iter=args.start_iter)
    if not atoms_list:
        raise SystemExit("No structures loaded.")
    natoms = len(atoms_list[0])
    e_glob = energies.min()
    rel = (energies - e_glob) / natoms

    os.makedirs(args.outdir, exist_ok=True)
    summary = {
        "dataset": os.path.basename(args.dataset.rstrip("/")),
        "n_atoms_per_struct": natoms,
        "n_structures_loaded": int(len(atoms_list)),
        "start_iter": args.start_iter,
        "E_glob_eV": float(e_glob),
        "tol": args.tol,
        "windows": {},
        "exported": [],
    }

    for tgt in args.targets:
        lo, hi = tgt - args.tol, tgt + args.tol
        in_win_total = np.where((rel >= lo) & (rel <= hi))[0]
        # sort by relative energy, keep the lowest up to max-per-window
        in_win = in_win_total[np.argsort(rel[in_win_total])][: args.max_per_window]
        files = []
        for gi in in_win:
            rel_e = float(rel[gi])
            seed = labels[gi]
            it = int(iters[gi])
            fname = f"relE_{tgt:.3f}_{seed}_iter{it}_rel{rel_e:.6f}.xsf"
            path = os.path.join(args.outdir, fname)
            ase_write(path, atoms_list[gi])
            files.append(fname)
            summary["exported"].append({
                "target": tgt, "rel_e": rel_e, "file": fname,
                "seed": seed, "iteration": it,
            })
            print(f"  tgt {tgt:.3f}: exported {fname}  (rel_e={rel_e:.6f} eV/atom)")
        summary["windows"][f"{tgt:.3f}"] = {
            "window": [lo, hi], "n_in_window_total": int(len(in_win_total)),
            "n_exported": len(files), "files": files,
        }
        if not files:
            print(f"  tgt {tgt:.3f}: no structure in [{lo}, {hi}] eV/atom")

    with open(os.path.join(args.outdir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(f"\nDone. Outputs under {os.path.abspath(args.outdir)}")
    print(f"summary -> {os.path.join(args.outdir, 'summary.json')}")


if __name__ == "__main__":
    main()
