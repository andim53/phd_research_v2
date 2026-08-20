#!/usr/bin/env python3
"""
Novel structure filtering for a partition-function representation.

Loads every structure from every AGOX seed database, builds a fingerprint
descriptor, and greedily filters the combined set down to a *distinct* (novel)
subset: no two kept structures are "alike", where likeness is measured by the
minimum Euclidean distance in descriptor feature space (the same novelty
measure used by ``NoveltyLCBAcquisitor`` in ``_run/6_lcbnovel_benchmark``).

The filtered subset is a representation of the energy landscape in which each
basin / local minimum appears exactly once, so it can be used to evaluate the
canonical partition function without double counting near-duplicate structures:

    Z(T) = sum_i exp(-beta * E_i)   over the DISTINCT structures only

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python run_filter.py [options]
"""

from __future__ import annotations

import glob
import os
from collections import Counter

import numpy as np

# AGOX / ASE imports
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint


# Boltzmann constant in eV/K
K_B = 8.617333262e-5  # eV/K


# =============================================================================
# Loading
# =============================================================================
def load_all_seeds(dataset_dir: str, pattern: str = "seed_*/1_db/db_*.db"):
    """Load and concatenate all structures/energies from every seed DB.

    Returns
    -------
    structures : list of ase.Atoms
        All structures from all seeds.
    energies : np.ndarray
        Potential energy of each structure (eV).
    db_paths : list of str
        Database files that were loaded.
    origins : list of str
        Per-structure source database path (relative), aligned with structures.
    """
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, pattern)))
    if not db_paths:
        raise FileNotFoundError(
            f"No databases matched {os.path.join(dataset_dir, pattern)}"
        )

    structures, energies, origins = [], [], []
    for p in db_paths:
        rel = os.path.relpath(p, dataset_dir)
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        origins.extend([rel] * len(traj))
        print(f"  {rel}: {len(traj)} structures")

    energies = np.asarray(energies, dtype=float)
    return structures, energies, db_paths, origins


def verify_uniform_composition(structures) -> str:
    """Return the single chemical formula if all structures share it, else raise."""
    comps = Counter(tuple(a.get_chemical_symbols()) for a in structures)
    natoms = set(len(a) for a in structures)
    if len(comps) != 1 or len(natoms) != 1:
        raise ValueError(
            f"Dataset is NOT uniform: {len(comps)} distinct compositions, "
            f"{natoms} atom counts. Cannot use one global descriptor."
        )
    formula = structures[0].get_chemical_formula()
    n = list(comps.values())[0]
    print(f"  Composition: {formula} ({n} structures, {len(structures[0])} atoms)")
    return formula


def build_features(descriptor, structures) -> np.ndarray:
    """Feature matrix (n, d) for all structures (raw, not normalised).

    Uses the raw Euclidean fingerprint distance, matching the novelty measure
    in ``_run/6_lcbnovel_benchmark/novelty_lcb`` (where distinct local minima
    are ~1-6 apart in raw units and near-duplicate relaxations are much closer).
    """
    return np.vstack(
        [descriptor.get_features(a).ravel() for a in structures]
    )


# =============================================================================
# Novelty filtering
# =============================================================================
def filter_novel(
    features: np.ndarray,
    order: np.ndarray,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Greedily select a distinct (novel) subset of structures.

    Process the structures in ``order`` (typically ascending energy so the
    lowest-energy member of each basin is kept as its representative).  A
    structure is kept iff its minimum Euclidean distance in feature space to
    every previously-kept structure is strictly greater than ``threshold``.

    Parameters
    ----------
    features : np.ndarray, shape (n, d)
        Raw (un-normalised) fingerprint feature matrix.
    order : np.ndarray, shape (n,)
        Indices into ``features`` giving the processing order.
    threshold : float
        Minimum distance a structure must be from all kept structures to be
        considered novel.  Larger -> fewer, more diverse structures.

    Returns
    -------
    kept_idx : np.ndarray
        Indices of the selected novel structures.
    min_kept_dist : np.ndarray
        For each selected structure, its minimum distance to the kept set at
        the time it was added (i.e. distance to the nearest other kept point).
    """
    kept_idx = []
    kept_feats = []          # list of feature vectors kept so far
    min_kept_dist = []

    for idx in order:
        f = features[idx]
        if kept_feats:
            K = np.vstack(kept_feats)
            dmin = float(np.linalg.norm(K - f, axis=1).min())
            if dmin <= threshold:
                continue
            min_kept_dist.append(dmin)
        else:
            min_kept_dist.append(np.inf)  # first structure is always novel
        kept_idx.append(int(idx))
        kept_feats.append(f)

    return np.asarray(kept_idx, dtype=int), np.asarray(min_kept_dist, dtype=float)


def nearest_neighbour_distances(features: np.ndarray) -> np.ndarray:
    """Distance of each structure to its nearest neighbour (chunked, memory-safe)."""
    n = features.shape[0]
    nn = np.full(n, np.inf)
    # chunked pairwise to avoid materialising an n x n matrix
    chunk = 128
    for start in range(0, n, chunk):
        block = features[start:start + chunk]                 # (c, d)
        # squared distance to all points
        d2 = (block**2).sum(1, keepdims=True) + (features**2).sum(1) \
             - 2.0 * block @ features.T                       # (c, n)
        np.fill_diagonal(d2[:, start:start + chunk], np.inf)  # ignore self
        d2 = np.maximum(d2, 0.0)
        nn[start:start + chunk] = np.sqrt(d2).min(1)
    return nn


# =============================================================================
# Partition function over the distinct set
# =============================================================================
def partition_function(energies: np.ndarray, temperature: float):
    """Canonical partition function and Boltzmann weights over the distinct set.

    Works entirely in log space for numerical stability (energies ~ -400 eV,
    beta ~ 40, so raw exp(beta*E) would overflow/underflow).  Returns Z, log_Z,
    normalised weights, and the corresponding log weights.
    """
    beta = 1.0 / (K_B * temperature)
    E_ref = energies.min()
    log_w = -beta * (energies - E_ref)          # log Boltzmann weight, up to norm
    m = log_w.max()
    logsum = m + np.log(np.exp(log_w - m).sum())   # stable log of the sum
    log_Z = logsum
    log_weights = log_w - logsum                   # normalised log weights
    weights = np.exp(log_weights)                  # may underflow to 0 for hot tails
    Z = np.exp(log_Z)
    return float(Z), float(log_Z), weights, log_weights


# =============================================================================
# Saving
# =============================================================================
def save_novel_subset(
    out_dir: str,
    structures,
    energies,
    origins,
    kept_idx,
    min_kept_dist,
    threshold,
    temperature,
):
    """Write the filtered novel structures (.xsf) and a summary CSV."""
    from pathlib import Path
    from ase.io import write

    out = Path(out_dir)
    (out / "novel_structures").mkdir(parents=True, exist_ok=True)

    rows = []
    for rank, i in enumerate(kept_idx):
        E = energies[i]
        # energy-ranked xsf files (kept_idx is already energy-ascending by order)
        write(out / "novel_structures" / f"novel_{rank:04d}_E{E:.3f}.xsf",
              structures[i])
        rows.append((rank, i, E, origins[i], min_kept_dist[rank]))

    # CSV summary (mixed types: rank,idx,energy,source-string,min_dist)
    with open(out / "novel_structures_summary.csv", "w") as fh:
        fh.write("rank,dataset_index,energy_eV,source,min_dist_to_kept\n")
        for rank, i, E, src, dmin in rows:
            fh.write(f"{rank},{i},{E:.6f},{src},{dmin:.6f}\n")

    # Partition function over the distinct set
    E_kept = np.asarray([energies[i] for i in kept_idx], dtype=float)
    Z, log_Z, weights, log_weights = partition_function(E_kept, temperature)
    np.savetxt(
        out / "partition_function.csv",
        np.column_stack([np.arange(len(kept_idx)),
                         E_kept,
                         weights,
                         log_weights]),
        delimiter=",",
        header="rank,energy_eV,boltzmann_weight,log_boltzmann_weight",
        comments="",
    )
    with open(out / "filter_summary.txt", "w") as fh:
        fh.write(f"threshold                : {threshold:.4f}\n")
        fh.write(f"temperature [K]          : {temperature:.1f}\n")
        fh.write(f"input structures         : {len(structures)}\n")
        fh.write(f"novel (distinct) kept    : {len(kept_idx)}\n")
        fh.write(f"removed as duplicates    : {len(structures)-len(kept_idx)}\n")
        fh.write(f"partition function Z({temperature:.0f} K) = {Z:.6e}\n")
        fh.write(f"log Z                    : {log_Z:.4f}\n")

    print(f"\nResults written to {out}")
    print(f"  novel_structures_summary.csv ({len(kept_idx)} rows)")
    print(f"  partition_function.csv")
    print(f"  filter_summary.txt")
