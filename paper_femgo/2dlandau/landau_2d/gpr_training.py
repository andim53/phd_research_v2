#!/usr/bin/env python3
"""Load AGOX seed databases, build/train the GPR surrogate, and validate it.

Verbatim reuse of ``_run/d_landauPlus/landau_plus/gpr_training.py`` (v1.0.0) —
the same ``data/femgo`` GO/GOFEE run, same ``seed_*/1_db/db_*.db`` glob
(deliberately excluding ``stop_16``), same Fingerprint/Repulsive GPR recipe.
The dataset dir is ``paper_femgo/data/femgo`` here.
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


def _ensure_ray_local():
    """Pre-initialise a small local Ray cluster if none is running.

    AGOX's ``GPR.__init__`` starts Ray unconditionally; on a memory-constrained
    local box Ray's auto-detected config underflows its 75 MB object-store
    minimum, so pre-start a deliberately small cluster. On HPC (SLURM/PJM) Ray
    is left to AGOX's own startup.
    """
    import os
    try:
        import ray
    except ImportError:
        return
    if ray.is_initialized():
        return
    if "SLURM_NTASKS" in os.environ or os.environ.get("PJM_JOBID", ""):
        return  # let AGOX size the cluster on HPC
    try:
        ray.init(num_cpus=2, object_store_memory=int(120e6),
                 _memory=int(300e6), include_dashboard=False,
                 _temp_dir=os.path.expanduser("~/tmp/ray_small"),
                 ignore_reinit_error=True, log_to_driver=False)
    except Exception as e:  # pragma: no cover - best effort
        print(f"[gpr_training] WARNING: local Ray pre-init failed ({e}); "
              f"AGOX will attempt its own startup")


def build_gpr(traj, use_ray=False):
    """Build and train the GPR surrogate (AGOX recipe from the dataset).

    Uses ``Fingerprint.from_atoms(traj[0])`` — the proven c_landausampling /
    d_landauPlus recipe (verified to reproduce the GO run's feature space).
    """
    _ensure_ray_local()
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
