#!/usr/bin/env python3
"""Load AGOX seed databases, build/train the GPR surrogate, and validate it.

Adapted from `c_landausampling/wang_landau/gpr_training.py`. The dataset is the
`data/femgo` GO/GOFEE run: seed databases under ``seed_*/1_db/db_*.db``. The
``stop_*`` database (``stop_16``) is deliberately EXCLUDED by the glob pattern
(it is a final/restart snapshot, not part of the seed set).
"""

from __future__ import annotations

__version__ = "1.0.0"

import glob
import os

import numpy as np

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive


def load_all_seeds(dataset_dir: str, pattern: str = "seed_*/1_db/db_*.db"):
    """Load and concatenate all structures/energies from every seed DB.

    Returns
    -------
    structures : list of ase.Atoms
    energies : np.ndarray (eV)
    db_paths : list of str
    """
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, pattern)))
    if not db_paths:
        raise FileNotFoundError(
            f"No databases matched {os.path.join(dataset_dir, pattern)}")

    structures, energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        print(f"  {os.path.relpath(p)}: {len(traj)} structures")

    return structures, np.asarray(energies, dtype=float), db_paths


def build_gpr(traj, use_ray=False):
    """Build and train the GPR surrogate (AGOX recipe from the dataset).

    Uses ``Fingerprint.from_atoms(traj[0])``, the proven c_landausampling recipe
    (verified to reproduce the GO run's feature space on this dataset — the
    ``Fingerprint(environment=...)`` of the original search differs only in
    environment plumbing, not the radial/angular fingerprint features).
    """
    descriptor = Fingerprint.from_atoms(traj[0])
    print(f"  Descriptor feature dim: "
          f"{descriptor.create_features(traj[0]).shape[1]}")

    bk = 0.01
    kernel = (
        C(5000, (1, 1e5)) *
        (C(bk, (bk, bk)) * RBF() +
         C(1 - bk, (1 - bk, 1 - bk)) * RBF())
        + Noise(0.01, (0.01, 0.01))
    )

    gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(),
              use_ray=use_ray)
    print(f"  Training on {len(traj)} structures...")
    gpr.train(traj)
    print("  GPR training done.")
    return gpr


def validate_gpr(gpr, structures, energies, n_show=5):
    """Print GPR-vs-DFT deltas on the first ``n_show`` training structures."""
    print("\nValidation (first %d):" % n_show)
    print("  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)")
    for i in range(min(n_show, len(structures))):
        Ed = energies[i]
        Eg = gpr.predict_energy(structures[i])
        print(f"  {i:3d}  {Ed:10.4f}  {Eg:10.4f}  {Eg - Ed:10.4f}")