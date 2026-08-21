#!/usr/bin/env python3
"""
Save, for each threshold, the pair of kept structures that are separated by
~the threshold distance.

The novelty filter keeps structures whose minimum fingerprint distance to the
kept set is STRICTLY greater than the threshold.  Consequently the closest pair
among the kept structures of a threshold sits just ABOVE the threshold value —
that pair is "separated by (about) the threshold."  This script finds, for each
threshold folder, the pair whose fingerprint distance is closest to the
threshold, and saves those two structures as XSF files.

Output layout (into --outdir/example_pairs/):
    example_pairs/
    ├── pairs_summary.csv                     # threshold, pair idx, distance, energies
    ├── thr_0.25/
    │   ├── pair_A_rank<i>_E<e>.xsf           # structure i of the closest pair
    │   └── pair_B_rank<j>_E<e>.xsf           # structure j of the closest pair
    ├── thr_0.5/ ...
    └── thr_2/ ...

Run with the agox_v2 conda env (needs the AGOX Fingerprint descriptor):
    /home/think/miniconda3/envs/agox_v2/bin/python save_example_pairs.py [options]
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ase.io import read, write
from agox.models.descriptors.fingerprint import Fingerprint


# ---------------------------------------------------------------------------
def threshold_from_name(name: str) -> float:
    """Parse the threshold value out of a folder name like 'thr_0.25' / 'thr_1'."""
    return float(name[len("thr_"):])


def load_threshold_set(thr_dir: str):
    """Rank-ordered structures + energies for one threshold folder."""
    ns_dir = os.path.join(thr_dir, "novel_structures")
    struct_files = sorted(glob.glob(os.path.join(ns_dir, "novel_*.xsf")),
                          key=lambda p: int(os.path.basename(p).split("_")[1]))
    if not struct_files:
        raise FileNotFoundError(f"No novel_*.xsf in {ns_dir}")
    structures = [read(f) for f in struct_files]

    csv_path = os.path.join(thr_dir, "novel_structures_summary.csv")
    energies = {}
    with open(csv_path) as fh:
        next(fh)  # header
        for line in fh:
            parts = line.strip().split(",")
            energies[int(parts[0])] = float(parts[2])
    e_arr = np.array([energies[r] for r in range(len(structures))], dtype=float)
    return structures, e_arr


def closest_pair(features: np.ndarray) -> tuple[int, int, float]:
    """Indices (i, j), i<j, of the two structures with the smallest distance."""
    n = features.shape[0]
    best_dist = np.inf
    best_pair = (0, 1)
    # chunked to avoid a full n x n matrix on the largest threshold
    chunk = 200
    for start in range(0, n, chunk):
        block = features[start:start + chunk]
        d2 = ((block**2).sum(1, keepdims=True) + (features**2).sum(1)
              - 2.0 * block @ features.T)
        np.maximum(d2, 0.0, out=d2)
        # mask self and the lower triangle to avoid double counting
        for i in range(d2.shape[0]):
            gi = start + i
            d2[i, :gi + 1] = np.inf
        idx = np.argmin(d2)
        i_blk, j = np.unravel_index(idx, d2.shape)
        dist = np.sqrt(d2[i_blk, j])
        if dist < best_dist:
            best_dist = dist
            best_pair = (start + i_blk, j)
    return best_pair[0], best_pair[1], float(best_dist)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default=os.path.join(_HERE, "novel_output"),
                   help="Run output dir containing thr_<v>/ folders (default novel_output)")
    p.add_argument("--dest", default=None,
                   help="Where to write example_pairs/ (default <--outdir>/example_pairs)")
    args = p.parse_args()

    thr_names = sorted(
        d for d in os.listdir(args.outdir)
        if d.startswith("thr_") and os.path.isdir(os.path.join(args.outdir, d))
    )
    if not thr_names:
        raise SystemExit(f"No thr_<v>/ folders under {args.outdir!r}")

    dest = args.dest or os.path.join(args.outdir, "example_pairs")
    os.makedirs(dest, exist_ok=True)

    summary = []
    for name in thr_names:
        thr = threshold_from_name(name)
        thr_dir = os.path.join(args.outdir, name)
        print(f"\n=== {name} (threshold {thr}) ===")
        structures, energies = load_threshold_set(thr_dir)

        fp = Fingerprint.from_atoms(structures[0])
        features = np.array([fp.get_features(s).ravel() for s in structures])
        i, j, dist = closest_pair(features)
        Ei, Ej = energies[i], energies[j]

        print(f"  {len(structures)} structures")
        print(f"  closest pair: rank {i} (E={Ei:.4f}) <-> rank {j} (E={Ej:.4f})")
        print(f"  distance = {dist:.4f}  (threshold = {thr:.4f})")

        # save the two XSF files
        out_dir = os.path.join(dest, name)
        os.makedirs(out_dir, exist_ok=True)
        write(os.path.join(out_dir, f"pair_A_rank{i}_E{Ei:.3f}.xsf"), structures[i])
        write(os.path.join(out_dir, f"pair_B_rank{j}_E{Ej:.3f}.xsf"), structures[j])

        summary.append((name, thr, i, j, Ei, Ej, dist))

    # summary CSV
    sum_path = os.path.join(dest, "pairs_summary.csv")
    with open(sum_path, "w") as fh:
        fh.write("threshold_folder,threshold,idx_A,idx_B,energy_A_eV,energy_B_eV,pair_distance\n")
        for name, thr, i, j, Ei, Ej, dist in summary:
            fh.write(f"{name},{thr},{i},{j},{Ei:.6f},{Ej:.6f},{dist:.6f}\n")

    print(f"\nExample pairs written to {dest}/")
    for name, thr, i, j, Ei, Ej, dist in summary:
        print(f"  {name}: dist={dist:.4f} (thr={thr:.2f}), A=rank{i} E{Ei:.3f}, B=rank{j} E{Ej:.3f}")


if __name__ == "__main__":
    main()
