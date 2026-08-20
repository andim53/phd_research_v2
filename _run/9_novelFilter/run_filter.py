#!/usr/bin/env python3
"""
Filter the combined multi-seed Fe/MgO AGOX dataset down to a distinct (novel)
subset for a partition-function representation.

Loads EVERY structure from every seed database in dataset/seed_*/1_db/db_*.db,
computes fingerprint features, and greedily keeps only structures that are
structurally novel (minimum Euclidean distance in descriptor space > threshold)
relative to all already-kept structures. Structures are processed lowest-energy
first, so the lowest-energy member of each structural basin is kept as its
single representative (no double counting).

Also evaluates the canonical partition function Z(T) = sum_i exp(-beta E_i) over
the DISTINCT subset.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python run_filter.py [options]

This script relies on:
  - the `novel_filter` package in this directory (imported as a package)
  - the AGOX / ASE stack installed in the agox_v2 conda env
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

# --- Make `novel_filter` importable from this directory ---------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from novel_filter.filter import (
    build_features,
    filter_novel,
    load_all_seeds,
    nearest_neighbour_distances,
    partition_function,
    save_novel_subset,
    verify_uniform_composition,
)
from agox.models.descriptors.fingerprint import Fingerprint


# =============================================================================
# Parameters
# =============================================================================
DATASET_DIR = os.path.join(_HERE, "dataset")
DB_PATTERN = "seed_*/1_db/db_*.db"


# =============================================================================
# Main
# =============================================================================
def parse_thresholds(arg: str, single: float) -> list[float]:
    """Resolve the threshold list from --thresholds / --threshold."""
    if arg:
        return [float(x) for x in arg.replace(" ", "").split(",") if x]
    return [single]


def main():
    p = argparse.ArgumentParser(
        description="Filter multi-seed AGOX dataset to distinct (novel) structures "
                    "for a partition-function representation"
    )
    p.add_argument("--thresholds", type=str, default=None,
                   help="Comma-separated list of thresholds to sweep, e.g. "
                        "'0.5,1.0,1.5,2.0'. Each threshold writes its OWN output "
                        "folder containing all kept .xsf structures. If omitted, "
                        "only --threshold is used.")
    p.add_argument("--threshold", type=float, default=1.0,
                   help="Single threshold used when --thresholds is not given. "
                        "Min raw Euclidean fingerprint distance from all kept "
                        "structures to be considered novel (matches novelty_lcb; "
                        "distinct Fe/MgO minima are typically >1.0 apart, "
                        "near-duplicate relaxations much closer; larger = fewer, "
                        "more diverse). Default 1.0")
    p.add_argument("--temp", type=float, default=300.0,
                   help="Temperature (K) for the partition function, default 300")
    p.add_argument("--output", default=os.path.join(_HERE, "novel_output"),
                   help="Output directory (each threshold gets a thr_<v>/ subfolder)")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed (used only for tie handling / reproducibility)")
    args = p.parse_args()

    thresholds = parse_thresholds(args.thresholds, args.threshold)
    print("Threshold sweep:", thresholds)

    # --- 1. Load the combined multi-seed dataset -----------------------------
    print("=" * 70)
    print("Loading combined dataset from all seeds")
    print(f"  Pattern: {DB_PATTERN}")
    structures, energies, db_paths, origins = load_all_seeds(DATASET_DIR, DB_PATTERN)
    print(f"  Total: {len(structures)} structures, {len(db_paths)} databases")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 2. Uniform-composition pre-check + descriptor -----------------------
    verify_uniform_composition(structures)
    descriptor = Fingerprint.from_atoms(structures[0])
    dim = descriptor.create_features(structures[0]).shape[1]
    print(f"  Descriptor feature dim: {dim}")

    # --- 3. Feature matrix ---------------------------------------------------
    print("\nComputing fingerprint features...")
    features = build_features(descriptor, structures)

    # --- 4. Nearest-neighbour distance stats (guides threshold choice) -------
    print("Computing nearest-neighbour distances...")
    nn = nearest_neighbour_distances(features)
    print(f"  NN distance: min={nn.min():.4f}  median={np.median(nn):.4f}  "
          f"max={nn.max():.4f}")
    for t in thresholds:
        print(f"  fract < {t:.2f}: {(nn < t).mean() * 100:.1f}% of structures "
              f"have a near-twin within threshold")

    # --- 5+6. Per-threshold filtering + saving -------------------------------
    order = np.argsort(energies, kind="stable")   # lowest energy processed first
    comparison_rows = []

    for thr in thresholds:
        print(f"\n--- Threshold {thr:.4f} ---")
        kept_idx, min_kept_dist = filter_novel(features, order, thr)
        E_kept = np.asarray([energies[i] for i in kept_idx], dtype=float)

        Z, log_Z, weights, log_weights = partition_function(E_kept, args.temp)

        print(f"  kept {len(kept_idx)} novel / {len(structures)} total "
              f"(removed {len(structures) - len(kept_idx)} duplicates)")
        print(f"  kept E range: {E_kept.min():.4f} .. {E_kept.max():.4f} eV")
        print(f"  partition function over {len(kept_idx)} distinct structures "
              f"at {args.temp:.0f} K: Z = {Z:.6e}  (log Z = {log_Z:.4f})")

        # Each threshold gets its own subfolder with ALL kept .xsf files.
        out_dir = os.path.join(args.output, f"thr_{thr:g}")
        save_novel_subset(out_dir, structures, energies, origins, kept_idx,
                          min_kept_dist, thr, args.temp)

        comparison_rows.append((thr, len(kept_idx),
                                len(structures) - len(kept_idx),
                                E_kept.min(), E_kept.max(),
                                log_Z, Z))

    # --- 7. Cross-threshold comparison summary -------------------------------
    comp_path = os.path.join(args.output, "threshold_comparison.csv")
    os.makedirs(args.output, exist_ok=True)
    with open(comp_path, "w") as fh:
        fh.write("threshold,n_kept,n_removed,kept_E_min_eV,kept_E_max_eV,log_Z,Z\n")
        for row in comparison_rows:
            thr, nk, nr, emin, emax, lz, z = row
            fh.write(f"{thr},{nk},{nr},{emin:.6f},{emax:.6f},{lz:.4f},{z:.6e}\n")
    print(f"\nCross-threshold summary written to {comp_path}")
    for row in comparison_rows:
        thr, nk, nr, emin, emax, lz, z = row
        print(f"  thr={thr:6.2f}  kept={nk:5d}  removed={nr:5d}  "
              f"E=[{emin:.3f},{emax:.3f}]  log_Z={lz:8.4f}  Z={z:.3e}")
    print("\nDone.")


if __name__ == "__main__":
    main()
