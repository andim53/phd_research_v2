#!/usr/bin/env python3
"""
Nested Sampling over the combined multi-seed Fe/MgO AGOX dataset.

Loads EVERY structure from every seed database in dataset/seed_*/1_db/db_*.db,
trains a single GPR surrogate on the combined 1297 structures, then runs the
NestedSampler from the `nested_sampling` package on the combined dataset.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py [options]

This script relies on:
  - the `nested_sampling` package in this directory (imported as a package)
  - the AGOX / ASE stack installed in the agox_v2 conda env
"""

from __future__ import annotations

import os
import sys
import glob
import argparse
from pathlib import Path

import numpy as np

# --- Make `nested_sampling` importable from this directory -------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# AGOX imports
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

# Nested sampling package
from nested_sampling.nested_sampler import NestedSampler
from nested_sampling.utils import K_B


# =============================================================================
# Parameters
# =============================================================================
DATASET_DIR = os.path.join(_HERE, "dataset")
DB_PATTERN = "seed_*/1_db/db_*.db"        # every seed in the dataset


# =============================================================================
# Helpers
# =============================================================================
def load_all_seeds(dataset_dir: str, pattern: str):
    """Load and concatenate all structures/energies from every seed DB.

    Returns
    -------
    structures : list of ase.Atoms
        All structures from all seeds (1297 total).
    energies : np.ndarray
        Potential energy of each structure (eV).
    db_paths : list of str
        Database files that were loaded.
    """
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, pattern)))
    if not db_paths:
        raise FileNotFoundError(
            f"No databases matched {os.path.join(dataset_dir, pattern)}"
        )

    structures = []
    energies = []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        print(f"  {os.path.relpath(p)}: {len(traj)} structures")

    energies = np.asarray(energies, dtype=float)
    return structures, energies, db_paths


def build_gpr(traj):
    """Build the GPR surrogate (AGOX recipe from dataset/main.py)."""
    descriptor = Fingerprint.from_atoms(traj[0])
    print(f"  Descriptor feature dim: {descriptor.create_features(traj[0]).shape[1]}")

    bk = 0.01
    kernel = (
        C(5000, (1, 1e5)) *
        (C(bk, (bk, bk)) * RBF() +
         C(1 - bk, (1 - bk, 1 - bk)) * RBF())
        + Noise(0.01, (0.01, 0.01))
    )

    gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
    print(f"  Training on {len(traj)} structures...")
    gpr.train(traj)
    print("  GPR training done.")
    return gpr


# =============================================================================
# Main
# =============================================================================
def main():
    p = argparse.ArgumentParser(
        description="Nested sampling on the combined multi-seed Fe/MgO dataset"
    )
    p.add_argument("--temp", type=float, default=300.0,
                   help="Temperature (K), default 300")
    p.add_argument("--n-live", type=int, default=50,
                   help="Number of live points, default 50")
    p.add_argument("--n-iters", type=int, default=300,
                   help="Nested sampling iterations, default 300")
    p.add_argument("--perturb", type=float, default=0.01,
                   help="Perturbation amplitude (A), default 0.01")
    p.add_argument("--output", default=os.path.join(_HERE, "ns_output_allseeds"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed for the sampler RNG")
    args = p.parse_args()

    # --- 1. Load the combined multi-seed dataset -----------------------------
    print("=" * 70)
    print("Loading combined dataset from all seeds")
    print(f"  Pattern: {DB_PATTERN}")
    structures, energies, db_paths = load_all_seeds(DATASET_DIR, DB_PATTERN)
    print(f"  Total: {len(structures)} structures, "
          f"{len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()}")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 2. Train GPR on the combined dataset --------------------------------
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures)

    # Sanity check the surrogate on a few training points
    print("\nValidation (first 5):")
    print("  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)")
    for i in range(min(5, len(structures))):
        Ed = energies[i]
        Eg = gpr.predict_energy(structures[i])
        print(f"  {i:3d}  {Ed:10.4f}  {Eg:10.4f}  {Eg-Ed:10.4f}")

    # --- 3. Run nested sampling ----------------------------------------------
    beta = 1.0 / (K_B * args.temp)
    print(f"\nbeta = {beta:.6f} eV^-1  (T = {args.temp} K)")
    print(f"perturb = {args.perturb} A")

    sampler = NestedSampler(
        gpr=gpr,
        db_structures=structures,
        db_energies=energies,
        n_live=args.n_live,
        beta=beta,
        temperature=args.temp,
        perturb=args.perturb,
        rng=np.random.default_rng(args.rng),
    )

    sampler.initialize()
    sampler.run(n_iterations=args.n_iters, progress_every=20)
    sampler.save(args.output)

    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
