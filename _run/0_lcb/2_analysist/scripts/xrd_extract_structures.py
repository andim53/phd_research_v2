#!/usr/bin/env python3
"""
Stage 1 — XRD crystallinity: structure extraction & energy-window binning.

Runs in the **agox_v2** env (AGOX + ASE, NO pymatgen). For one 11_bTa leaf
(dataset dir holding seed_*/1_db/db_*.db), it loads every structure, computes
the relative energy per atom (E - E_glob)/n_atoms, bins the structures into
energy windows, and writes the sampled structures of each window as CIF files
(plus a manifest JSON). A later stage (pymat_xrd env) reads these CIFs and
simulates powder XRD.

Writes, under --outdir:
  manifest.json        : window metadata (label, lo/hi, n_total, n_sampled,
                         composition) + a "cifs" list of relative CIF paths.
  windows/<win_label>/ : sampled <seed>_<idx>.cif files (deterministic stride).

Usage (agox_v2):
  PY_A=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY_A xrd_extract_structures.py --dataset 11_bTa/7_fxg_0b \
        --outdir 11_bTa/7_fxg_0b/xrd_out --e-max 0.5
"""
from __future__ import annotations

__version__ = "1.1.0"

import argparse
import glob
import json
import os

import numpy as np
from collections import Counter

from agox.databases import Database
from ase.io import write as ase_write


def load_leaf(dataset_dir: str, start_iter: int = 10):
    """All structures + DFT energies from dataset_dir/seed_*/1_db/db_*.db,
    iteration >= start_iter. Returns list[atoms], np energies, per-structure
    dict of metadata labels."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(
            f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    atoms_list, e_list, labels = [], [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        for d in kept:
            a = db.db_to_atoms(d)
            atoms_list.append(a)
            e_list.append(a.get_potential_energy())
            # seed label for provenance: seed dir name
            rel = os.path.relpath(p, dataset_dir)          # e.g. seed_3/1_db/db_3.db
            seed = rel.split(os.sep)[0]
            labels.append(seed)
    return atoms_list, np.asarray(e_list, dtype=float), labels


def _window_label(lo, hi, bin_width):
    """Return a distinct string label for an energy window [lo, hi).

    Uses enough decimals (derived from bin_width) so fine bins (e.g. 0.005 eV/atom)
    don't collapse to identical labels under a fixed %.2f.
    """
    ndec = _label_decimals(bin_width)
    return f"{lo:.{ndec}f}_{hi:.{ndec}f}"


def _label_decimals(bin_width):
    """Number of decimals needed to distinguish bins of the given width."""
    import math
    return max(2, -int(math.floor(math.log10(bin_width))))


def main():
    parser = argparse.ArgumentParser(
        description="XRD stage 1 (agox_v2): extract + energy-window-bin a 11_bTa "
                    "leaf's structures, writing windowed CIF files + manifest.")
    parser.add_argument("--dataset", required=True,
                        help="leaf dataset dir holding seed_*/1_db/db_*.db")
    parser.add_argument("--outdir", required=True,
                        help="output dir (e.g. <leaf>/xrd_out)")
    parser.add_argument("--e-max", type=float, default=0.5,
                        help="upper relative-energy/atom window (eV/atom); "
                             "structures above this are dropped (bad/unrelaxed). "
                             "Default 0.5.")
    parser.add_argument("--bin-width", type=float, default=0.1,
                        help="energy-window width (eV/atom). Default 0.1.")
    parser.add_argument("--max-per-window", type=int, default=150,
                        help="max structures sampled per window (deterministic "
                             "stride). Default 150.")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep structures with AGOX iteration >= this. Default 10.")
    args = parser.parse_args()

    print("=" * 70)
    print("XRD Stage 1 (agox_v2) — structure extraction + energy binning")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    print(f"e_max={args.e_max} bin_width={args.bin_width} "
          f"max_per_window={args.max_per_window} start_iter={args.start_iter}")
    print("=" * 70)

    atoms_list, energies, labels = load_leaf(args.dataset, start_iter=args.start_iter)
    if not atoms_list:
        raise SystemExit("No structures loaded.")
    natoms = len(atoms_list[0])
    e_glob = energies.min()
    rel = (energies - e_glob) / natoms

    # composition (assumed uniform across the leaf)
    comp = Counter(atoms_list[0].get_chemical_symbols())
    nB = comp.get("B", 0)
    nTa = comp.get("Ta", 0)

    print(f"leaf: {natoms} atoms/struct, comp={dict(comp)}, n_structures="
          f"{len(atoms_list)}, E_glob={e_glob:.3f} eV")
    print(f"relE/atom: min={rel.min():.3f} median={np.median(rel):.3f} "
          f"p90={np.percentile(rel, 90):.3f} max={rel.max():.3f}")

    # keep only structures within the energy window of interest
    keep = rel <= args.e_max
    print(f"dropped {int((~keep).sum())}/{len(rel)} structures above e_max="
          f"{args.e_max} eV/atom")
    idx_all = np.where(keep)[0]

    # energy windows [lo, hi)
    edges = np.arange(0.0, args.e_max + 1e-9, args.bin_width)
    if edges[-1] < args.e_max - 1e-9:
        edges = np.append(edges, args.e_max)
    win_dir = os.path.join(args.outdir, "windows")
    os.makedirs(win_dir, exist_ok=True)

    windows = []
    for w in range(len(edges) - 1):
        lo, hi = edges[w], edges[w + 1]
        m = (rel[idx_all] >= lo) & (rel[idx_all] < hi)
        idx = idx_all[m]
        label = _window_label(lo, hi, args.bin_width)
        ndec = _label_decimals(args.bin_width)
        n_total = int(idx.size)
        # deterministic stride sample (keep the lowest-energy member first)
        order = np.argsort(rel[idx])
        idx = idx[order]
        n_sampled = min(n_total, args.max_per_window)
        stride = np.linspace(0, n_total - 1, n_sampled).astype(int) if n_total else []
        picked = idx[stride] if n_total else []
        cif_paths = []
        for j, gi in enumerate(picked):
            fname = os.path.join("windows", label,
                                 f"{labels[gi]}_s{j:04d}.cif")
            full = os.path.join(args.outdir, fname)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            ase_write(full, atoms_list[gi], format="cif")
            cif_paths.append(fname)
        windows.append({
            "label": label, "lo": lo, "hi": hi,
            "n_total": n_total, "n_sampled": n_sampled,
            "cifs": cif_paths,
            "rel_energies": [round(float(rel[gi]), 4) for gi in picked],
        })
        print(f"  window [{lo:.{ndec}f},{hi:.{ndec}f}): {n_total} total -> {n_sampled} CIFs")

    manifest = {
        "leaf": os.path.basename(os.path.normpath(args.dataset)),
        "natoms": natoms, "composition": dict(comp),
        "nTa": nTa, "nB": nB,
        "e_glob": float(e_glob),
        "e_max": args.e_max, "bin_width": args.bin_width,
        "windows": windows,
    }
    mpath = os.path.join(args.outdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDONE. manifest -> {mpath}")


if __name__ == "__main__":
    main()
