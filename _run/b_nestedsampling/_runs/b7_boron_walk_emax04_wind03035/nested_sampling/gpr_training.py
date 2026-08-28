#!/usr/bin/env python3
"""Train a GPR model from an AGOX database."""

from __future__ import annotations

__version__ = "1.0.0"

import os
import sys

import numpy as np

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.environments import Environment

from .utils import K_B


# =============================================================================
# GPR training
# =============================================================================

def train_gpr(db_path: str):
    """Load DB, train GPR, return (gpr, structures, energies).

    Parameters
    ----------
    db_path : str
        Path to the .db file.

    Returns
    -------
    gpr : GPR
        Trained GPR model.
    structures : list of Atoms
        Trajectory from the database.
    energies : np.ndarray
        Potential energies (one per structure).
    """
    print(f"Loading database: {db_path}")
    db = Database(filename=db_path)
    db.restore_to_memory()
    traj = db.restore_to_trajectory()
    print(f"  {len(traj)} structures")

    energies = np.array([a.get_potential_energy() for a in traj
                         if hasattr(a, 'get_potential_energy')])
    print(f"  Energy range: {energies.min():.4f} to {energies.max():.4f} eV")
    print(f"  (mean={energies.mean():.4f}, std={energies.std():.4f})")

    # Descriptor
    print("\nCreating Fingerprint descriptor (from_atoms)...")
    descriptor = Fingerprint.from_atoms(traj[0])
    print(f"  Feature dim: {descriptor.create_features(traj[0]).shape[1]}")

    # Kernel (AGOX default from main.py)
    bk = 0.01
    kernel = (
        C(5000, (1, 1e5)) *
        (C(bk, (bk, bk)) * RBF() +
         C(1 - bk, (1 - bk, 1 - bk)) * RBF())
        + Noise(0.01, (0.01, 0.01))
    )

    gpr = GPR(descriptor=descriptor, kernel=kernel, database=db, prior=Repulsive())

    print(f"\nTraining on {len(traj)} structures...")
    gpr.train(traj)
    print("  Done.")

    print("\nValidation (first 5):\n  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)")
    for i in range(min(5, len(traj))):
        Ed = energies[i]
        Eg = gpr.predict_energy(traj[i])
        print(f"  {i:3d}  {Ed:10.4f}  {Eg:10.4f}  {Eg-Ed:10.4f}")

    return gpr, traj, energies
