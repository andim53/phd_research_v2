#!/usr/bin/env python3
"""
Force filter + nested novel filter on the ORIGINAL raw AGOX dataset.

Motivation
----------
The raw AGOX database (dataset/seed_*/1_db/db_*.db) holds structures with
single-point DFT energies but LARGE residual forces (the original run's
evaluator used only ~1 DFT step, fmax=0.05/steps=1), so most structures are
NOT converged local minima. A *force filter* keeps only structures whose
residual forces are small, i.e. the ones closest to being genuine minima.
Then a *novel filter* (fingerprint distinctness, fixed threshold) is applied
INSIDE the force filter so each force threshold yields distinct minima only.

Force metric
------------
max|F| over the 25 MOBILE Fe atoms only. The 50-atom MgO substrate is held
fixed by the original run's constraints and naturally carries large forces, so
it is EXCLUDED from the force measure (only the relaxable Fe atoms count).

Pipeline (per force threshold)
------------------------------
1. Load ALL raw structures (dataset/seed_*/1_db/db_*.db).
2. Force filter: keep structures with max|Fe force| < force_threshold.
   Swept across FORCE_THRESHOLDS.
3. Novel filter inside: on the force-surviving structures, run the greedy
   fingerprint distinctness filter (energy-ordered, fixed novel threshold).
4. Write each force threshold to <outdir>/force_<v>/ (novel_structures/,
   novel_structures_summary.csv, filter_summary.txt) and a
   force_comparison.csv at the top level.
5. The landscape/probability analysis is run SEPARATELY by
   run_analysis_thresholds.py (point it at <outdir> with --prefix force_).

Run (agox_v2 env):
    /home/think/miniconda3/envs/agox_v2/bin/python run_force_novel_filter.py [options]
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

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from ase.io import write

from novel_filter.filter import (
    filter_novel,
    nearest_neighbour_distances,
    verify_uniform_composition,
)

# ---------------------------------------------------------------------------
DATASET_DIR = os.path.join(_HERE, "dataset")
DB_PATTERN = "seed_*/1_db/db_*.db"

# Default force sweep (eV/A, on the mobile Fe atoms)
FORCE_THRESHOLDS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
# Fixed novel threshold applied inside each force threshold
NOVEL_THRESHOLD = 1.0


# ---------------------------------------------------------------------------
def load_raw_structures(dataset_dir: str, pattern: str):
    """Load all raw structures + energies + forces from every seed DB.

    Returns
    -------
    structures : list of ase.Atoms
    energies   : np.ndarray
    forces     : np.ndarray, shape (n, n_atoms, 3)  (may be nan if unavailable)
    origins    : list of str (source DB path per structure)
    """
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, pattern)))
    if not db_paths:
        raise FileNotFoundError(f"No databases matched {os.path.join(dataset_dir, pattern)}")

    structures, energies, forces, origins = [], [], [], []
    for p in db_paths:
        rel = os.path.relpath(p, dataset_dir)
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        origins.extend([rel] * len(traj))
        for a in traj:
            try:
                forces.append(a.get_forces())
            except Exception:
                forces.append(np.full((len(a), 3), np.nan))
    energies = np.asarray(energies, dtype=float)
    forces = np.asarray(forces, dtype=float)
    return structures, energies, forces, origins


def fe_forces(atoms, forces):
    """Return the force magnitude (max |F|) over the mobile Fe atoms only."""
    fe_idx = [i for i, s in enumerate(atoms.get_chemical_symbols()) if s == "Fe"]
    if not fe_idx:
        return np.nan
    return np.abs(forces[fe_idx]).max()


def build_features(descriptor, structures) -> np.ndarray:
    return np.vstack([descriptor.get_features(a).ravel() for a in structures])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default=DATASET_DIR,
                   help="Dataset dir containing seed_*/1_db/db_*.db")
    p.add_argument("--force-thresholds", default=",".join(map(str, FORCE_THRESHOLDS)),
                   help=f"Comma-separated force thresholds (eV/A). Default {FORCE_THRESHOLDS}")
    p.add_argument("--novel-threshold", type=float, default=NOVEL_THRESHOLD,
                   help=f"Novel (fingerprint) threshold applied inside each force "
                        f"threshold. Default {NOVEL_THRESHOLD}")
    p.add_argument("--outdir", default=os.path.join(_HERE, "force_output"),
                   help="Output dir; each force threshold writes force_<v>/ subfolder")
    p.add_argument("--rng", type=int, default=42, help="RNG seed")
    args = p.parse_args()

    force_thresholds = [float(x) for x in args.force_thresholds.replace(" ", "").split(",") if x]
    print("Force threshold sweep:", force_thresholds)
    print(f"Novel threshold inside: {args.novel_threshold}")

    # --- 1. Load raw dataset ------------------------------------------------
    print("=" * 70)
    print("Loading RAW dataset")
    structures, energies, forces, origins = load_raw_structures(args.dataset, DB_PATTERN)
    print(f"  Total: {len(structures)} structures")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")
    formula = verify_uniform_composition(structures)
    print(f"  Composition: {formula}")

    # --- 2. Per-structure force measure (mobile Fe only) --------------------
    fe_fmax = np.array([fe_forces(a, f) for a, f in zip(structures, forces)])
    print(f"\nMax|Fe force|: min={np.nanmin(fe_fmax):.3f}  "
          f"median={np.nanmedian(fe_fmax):.3f}  max={np.nanmax(fe_fmax):.3f} eV/A")
    print("  (substrate Mg/O forces excluded; only mobile Fe atoms count)")

    # --- 3. Descriptor (uniform composition already verified) --------------
    descriptor = Fingerprint.from_atoms(structures[0])
    all_features = build_features(descriptor, structures)
    print(f"  Descriptor feature dim: {all_features.shape[1]}")

    # --- 4. Per force threshold: force filter -> novel filter -> save ------
    order = np.argsort(energies, kind="stable")
    os.makedirs(args.outdir, exist_ok=True)
    comparison = []

    for fthr in force_thresholds:
        name = f"force_{fthr:g}"
        print(f"\n=== {name} (Fe force < {fthr} eV/A, novel thr {args.novel_threshold}) ===")

        # Force filter: keep structures with max Fe force below threshold
        mask = ~np.isnan(fe_fmax) & (fe_fmax < fthr)
        idx_pass = np.where(mask)[0]
        n_pass = len(idx_pass)
        print(f"  force filter: kept {n_pass}/{len(structures)} "
              f"({n_pass/len(structures)*100:.1f}%)")

        if n_pass == 0:
            print("  -> no structures survive force filter, skipping")
            comparison.append((fthr, 0, 0, np.nan, np.nan))
            continue

        # Subset features/energies to survivors, reorder by energy
        sub_idx = idx_pass[np.argsort(energies[idx_pass], kind="stable")]
        sub_features = all_features[sub_idx]

        # Novel filter inside (fixed threshold)
        kept_rel, min_dist = filter_novel(
            sub_features, np.arange(len(sub_idx)), args.novel_threshold
        )
        kept_global = sub_idx[kept_rel]   # indices into the full arrays
        E_kept = energies[kept_global]
        print(f"  novel filter inside: kept {len(kept_global)} distinct / {n_pass} survivors")

        # Write to force_<v>/
        out_dir = os.path.join(args.outdir, name)
        ns_dir = os.path.join(out_dir, "novel_structures")
        os.makedirs(ns_dir, exist_ok=True)

        with open(os.path.join(out_dir, "novel_structures_summary.csv"), "w") as fh:
            fh.write("rank,dataset_index,energy_eV,source,max_F_eV_per_Ang\n")
            for rank, gi in enumerate(kept_global):
                fname = f"novel_{rank:04d}_E{E_kept[rank]:.3f}.xsf"
                write(os.path.join(ns_dir, fname), structures[gi])
                fh.write(f"{rank},{gi},{energies[gi]:.6f},{origins[gi]},"
                         f"{fe_fmax[gi]:.6f}\n")

        with open(os.path.join(out_dir, "filter_summary.txt"), "w") as fh:
            fh.write(f"force_threshold_eV_per_Ang  : {fthr}\n")
            fh.write(f"novel_threshold             : {args.novel_threshold}\n")
            fh.write(f"input_structures            : {len(structures)}\n")
            fh.write(f"force_filter_survivors      : {n_pass}\n")
            fh.write(f"novel_distinct_kept         : {len(kept_global)}\n")

        print(f"  kept E range: {E_kept.min():.4f} .. {E_kept.max():.4f} eV")
        comparison.append((fthr, n_pass, len(kept_global), E_kept.min(), E_kept.max()))

    # --- 5. Cross-force-threshold comparison --------------------------------
    comp_path = os.path.join(args.outdir, "force_comparison.csv")
    with open(comp_path, "w") as fh:
        fh.write("force_threshold_eV_per_Ang,force_filter_survivors,novel_distinct_kept,"
                 "kept_E_min_eV,kept_E_max_eV\n")
        for fthr, n_pass, n_kept, emin, emax in comparison:
            emin_s = f"{emin:.6f}" if not np.isnan(emin) else ""
            emax_s = f"{emax:.6f}" if not np.isnan(emax) else ""
            fh.write(f"{fthr},{n_pass},{n_kept},{emin_s},{emax_s}\n")
    print(f"\nCross-force-threshold summary: {comp_path}")
    print("\nNow run the analysis on the force_<v>/ sets:")
    print("  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py "
          f"--outdir {args.outdir} --prefix force_")
    print("Done.")


if __name__ == "__main__":
    main()
