#!/usr/bin/env python3
"""
GPR accuracy analysis vs energy range (project b_nestedsampling).

Trains the AGOX GPR surrogate on the combined multi-seed Fe/MgO dataset
(dataset/seed_*/1_db/db_*.db, 1297 structures) and reports how accurately it
predicts the energy of the structures as a function of the ENERGY RANGE.

"Energy range" = the structure's energy relative to the global minimum,
expressed per atom (eV/atom), binned into equal-width windows. For each bin we
report in-sample prediction accuracy on the training set:

    MAE  = mean |E_pred - E_DFT|            (eV/atom)
    RMSE = sqrt(mean (E_pred - E_DFT)^2)     (eV/atom)
    R^2  = 1 - SS_res / SS_tot               (per bin, on per-atom energy)

Also computes the overall (whole-set) metrics and writes a CSV + a matplotlib
plot of MAE / RMSE / R^2 vs the energy range.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]
"""

from __future__ import annotations

__version__ = "1.0.0"

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

import matplotlib
matplotlib.use("Agg")           # headless
import matplotlib.pyplot as plt

# AGOX imports
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

DATASET_DIR = os.path.join(_HERE, "dataset")
DB_PATTERN = "seed_*/1_db/db_*.db"


# =============================================================================
# Helpers
# =============================================================================
def load_all_seeds(dataset_dir: str, pattern: str):
    """Load and concatenate all structures/energies from every seed DB."""
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
    return structures, np.asarray(energies, dtype=float), db_paths


def build_gpr(traj, use_ray: bool = False):
    """Build the GPR surrogate (same AGOX recipe as main.py)."""
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


def bin_metrics(dE, err, bin_width, n_atoms):
    """Compute MAE/RMSE/R^2 per equal-width bin of dE (eV/atom).

    dE, err : np.ndarray of per-atom values (eV/atom)
    Returns list of dicts (one per bin) + dict of overall metrics.
    """
    dE = np.asarray(dE, dtype=float)
    err = np.asarray(err, dtype=float)
    lo, hi = 0.0, float(dE.max())
    n_bins = max(1, int(np.ceil((hi - lo) / bin_width)))
    edges = np.linspace(lo, hi, n_bins + 1)
    edges[-1] += 1e-6          # include the max point in the last bin

    rows = []
    for b in range(n_bins):
        e0, e1 = edges[b], edges[b + 1]
        m = (dE >= e0) & (dE < e1)
        n = int(m.sum())
        if n == 0:
            continue
        e = err[m]
        mae = float(np.mean(np.abs(e)))
        rmse = float(np.sqrt(np.mean(e ** 2)))
        ss_res = float(np.sum(e ** 2))
        ss_tot = float(np.sum((dE[m] - dE[m].mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        rows.append({
            "bin_lo_eV_per_atom": float(e0),
            "bin_hi_eV_per_atom": float(e1),
            "n_structures": n,
            "MAE_eV_per_atom": mae,
            "RMSE_eV_per_atom": rmse,
            "R2": r2,
        })

    # overall (whole set)
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    ss_res = float(np.sum(err ** 2))
    ss_tot = float(np.sum((dE - dE.mean()) ** 2))
    overall = {
        "n_structures": len(dE),
        "MAE_eV_per_atom": mae,
        "RMSE_eV_per_atom": rmse,
        "R2": 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
    }
    return rows, overall, edges, n_bins


# =============================================================================
# Main
# =============================================================================
def main():
    p = argparse.ArgumentParser(
        description="GPR accuracy (MAE/RMSE/R^2) vs energy range (Fe/MgO)")
    p.add_argument("--bin-width", type=float, default=0.1,
                   help="Energy-bin width (eV/atom). Default 0.1 (auto ~7 bins "
                        "over the ~0.675 eV/atom range).")
    p.add_argument("--output", default=os.path.join(_HERE, "gpr_accuracy_out"),
                   help="Output directory")
    p.add_argument("--use-ray", action="store_true",
                   help="Use AGOX Ray for GPR training (default: single-process "
                        "use_ray=False)")
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Load dataset
    print("=" * 70)
    print("Loading combined dataset from all seeds")
    structures, energies, db_paths = load_all_seeds(DATASET_DIR, DB_PATTERN)
    n_atoms = len(structures[0])
    print(f"  Total: {len(structures)} structures, {len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()} "
          f"({n_atoms} atoms)")

    # 2. Train GPR
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures, use_ray=args.use_ray)

    # 3. Predict energies (in-sample) and per-atom errors
    print("\nPredicting energies on the training set...")
    E_pred = np.array([gpr.predict_energy(a) for a in structures])
    E_DFT = np.asarray([a.get_potential_energy() for a in structures])
    # per-atom values (eV/atom), consistent with the energy-range axis
    dE_per_atom = (E_DFT - E_DFT.min()) / n_atoms
    err_per_atom = (E_pred - E_DFT) / n_atoms

    # 4. Bin + metrics
    rows, overall, edges, n_bins = bin_metrics(
        dE_per_atom, err_per_atom, args.bin_width, n_atoms)

    print("\n" + "=" * 70)
    print(f"GPR accuracy vs energy range  (bin width = {args.bin_width:.3f} "
          f"eV/atom, {n_bins} bins, metrics in eV/atom)")
    print("=" * 70)
    hdr = (f"{'bin_lo':>8} {'bin_hi':>8} {'n':>6} "
           f"{'MAE':>10} {'RMSE':>10} {'R2':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['bin_lo_eV_per_atom']:8.3f} {r['bin_hi_eV_per_atom']:8.3f} "
              f"{r['n_structures']:6d} "
              f"{r['MAE_eV_per_atom']:10.4f} {r['RMSE_eV_per_atom']:10.4f} "
              f"{r['R2']:8.3f}")
    print("-" * len(hdr))
    print(f"{'OVERALL':>24} {overall['n_structures']:6d} "
          f"{overall['MAE_eV_per_atom']:10.4f} "
          f"{overall['RMSE_eV_per_atom']:10.4f} {overall['R2']:8.3f}")

    # 5. Save CSV
    csv_path = out / "gpr_accuracy_by_energy_range.csv"
    with open(csv_path, "w") as f:
        f.write("bin_lo_eV_per_atom,bin_hi_eV_per_atom,n_structures,"
                "MAE_eV_per_atom,RMSE_eV_per_atom,R2\n")
        for r in rows:
            f.write(f"{r['bin_lo_eV_per_atom']:.6f},{r['bin_hi_eV_per_atom']:.6f},"
                    f"{r['n_structures']},{r['MAE_eV_per_atom']:.8f},"
                    f"{r['RMSE_eV_per_atom']:.8f},{r['R2']:.8f}\n")
    print(f"\nSaved CSV: {csv_path}")

    # 6. Plot
    centers = [(r['bin_lo_eV_per_atom'] + r['bin_hi_eV_per_atom']) / 2
               for r in rows]
    mae = [r['MAE_eV_per_atom'] for r in rows]
    rmse = [r['RMSE_eV_per_atom'] for r in rows]
    r2 = [r['R2'] for r in rows]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.set_xlabel("Energy above minimum (eV/atom)")
    ax1.set_ylabel("Error (eV/atom)")
    ax1.plot(centers, mae, "-o", color="tab:blue", label="MAE")
    ax1.plot(centers, rmse, "-s", color="tab:orange", label="RMSE")
    ax1.axhline(overall["MAE_eV_per_atom"], ls="--", color="tab:blue", alpha=0.5,
                label=f"Overall MAE = {overall['MAE_eV_per_atom']:.3f}")
    ax1.axhline(overall["RMSE_eV_per_atom"], ls="--", color="tab:orange",
                alpha=0.5, label=f"Overall RMSE = {overall['RMSE_eV_per_atom']:.3f}")

    ax2 = ax1.twinx()
    ax2.set_ylabel("R²")
    ax2.plot(centers, r2, "-^", color="tab:green", label="R²")
    ax2.set_ylim(-1, 1.05)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best", fontsize=8)

    fig.suptitle(f"GPR accuracy vs energy range (Fe/MgO, {len(structures)} "
                 f"structures, {n_atoms} atoms)")
    fig.tight_layout()
    plot_path = out / "gpr_accuracy_by_energy_range.png"
    fig.savefig(plot_path, dpi=150)
    print(f"Saved plot: {plot_path}")

    # 7. Overall summary (JSON-like print)
    print("\nOVERALL (whole set, eV/atom): "
          f"MAE={overall['MAE_eV_per_atom']:.4f} "
          f"RMSE={overall['RMSE_eV_per_atom']:.4f} "
          f"R2={overall['R2']:.4f}")
    print(f"\nDone. Outputs in {out}")


if __name__ == "__main__":
    main()
