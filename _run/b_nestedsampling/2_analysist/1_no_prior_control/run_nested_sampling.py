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
from nested_sampling.state_density import analyze_state_density, analyze_saved_output


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

    gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(),
              use_ray=True)
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
    p.add_argument("--perturb-symbols", default="Fe",
                   help="Symbol(s) of atoms to perturb (deposition layer), "
                        "default 'Fe'; all other atoms stay fixed")
    p.add_argument("--output", default=os.path.join(_HERE, "ns_output_allseeds"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed for the sampler RNG")
    p.add_argument("--analysis-dir", default=None,
                   help="Directory for the state-density/landscape analysis "
                        "outputs (default: <--output>/analysis)")
    p.add_argument("--no-analysis", action="store_true",
                   help="Skip the state-density / landscape analysis that runs "
                        "automatically after sampling")
    p.add_argument("--analyze-only", default=None, metavar="RUN_OUTPUT_DIR",
                   help="Re-run the state-density / landscape analysis on an "
                        "already-finished run's output directory (must contain "
                        "posterior_structures/ and posterior_summary.csv). "
                        "Skips data loading, GPR training and sampling. "
                        "Requires --output for the analysis destination.")
    args = p.parse_args()

    # --- 0. Standalone re-analysis of a saved run ----------------------------
    if args.analyze_only:
        analysis_dir = args.analysis_dir or os.path.join(args.output, "analysis")
        print("=" * 70)
        print("Standalone analysis of a saved nested-sampling run")
        print(f"  run output   : {args.analyze_only}")
        print(f"  analysis dir : {analysis_dir}")
        print("=" * 70)
        # training set (structures + DFT energies) for comparison
        structures, energies, _ = load_all_seeds(DATASET_DIR, DB_PATTERN)
        print(f"  Training set: {len(structures)} structures")
        analyze_saved_output(
            run_output_dir=args.analyze_only,
            training_structures=structures,
            training_energies=energies,
            output_dir=analysis_dir,
            normalize_density=False,
            e_max=None,
        )
        print("\nDone (standalone analysis).")
        return

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
        perturb_symbols=args.perturb_symbols,
        rng=np.random.default_rng(args.rng),
    )

    sampler.initialize()
    sampler.run(n_iterations=args.n_iters, progress_every=20)
    sampler.save(args.output)

    # --- 4. State-density / landscape analysis -------------------------------
    if not args.no_analysis:
        analysis_dir = args.analysis_dir or os.path.join(args.output, "analysis")
        print("\nRunning state-density / landscape analysis of results...")
        analyze_state_density(
            posterior_structures=sampler.posterior_samples,
            training_structures=structures,
            gpr=gpr,
            output_dir=analysis_dir,
            normalize_density=False,
            e_max=None,
        )
    else:
        print("\nSkipping state-density analysis (--no-analysis).")

    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
