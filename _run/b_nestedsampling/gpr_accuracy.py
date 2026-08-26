#!/usr/bin/env python3
"""
GPR accuracy analysis vs energy range (project b_nestedsampling).

Trains the AGOX GPR surrogate on the combined multi-seed Fe/MgO dataset
(dataset/seed_*/1_db/db_*.db, 1297 structures) and reports how accurately it
predicts the energy of the structures as a function of the ENERGY RANGE.

"Energy range" = the structure's energy relative to the global minimum,
expressed per atom (eV/atom), binned into equal-width windows.

Two evaluation modes:

1. In-sample (default): trains one GPR on all structures and reports accuracy on
   the SAME training set. This reflects training-set fit (interpolation points).

2. Cross-validation (--cv): K-fold stratified by energy bin — each bin's
   structures are split across K folds so every fold trains on a spread of energy
   ranges. Each fold trains on K-1/K of the data and predicts the held-out 1/K.
   Held-out predictions are pooled across folds and reported per energy bin
   (a truthful out-of-sample generalization estimate), plus a fold-averaged
   summary.

Metrics (eV/atom, per bin and overall):

    MAE  = mean |E_pred - E_DFT|
    RMSE = sqrt(mean (E_pred - E_DFT)^2)
    R^2  = 1 - SS_res / SS_tot

Also writes a CSV + a matplotlib plot of MAE / RMSE / R^2 vs the energy range.

Optional uncertainty analysis (--uncertainty): reports the GPR's own predictive
uncertainty (posterior std from predict_energy_and_uncertainty), averaged per
energy bin, as a function of the energy range. In in-sample mode this is the std
of the single trained model on the training set; in CV mode it is the average std
of the held-out predictions pooled across folds. Writes
uncertainty_by_energy_range.csv and adds a mean_model_std column to the accuracy
CSV, plus per-bin model-std error bars on the plot.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py [options]
"""

from __future__ import annotations

__version__ = "1.2.0"

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
# Cross-validation helpers
# =============================================================================
def stratify_folds(dE, n_folds, rng):
    """Assign each structure to a fold, stratified by energy bin.

    Structures are binned by dE (eV/atom) and, within each bin, assigned to folds
    round-robin on a shuffled order, so every fold sees a spread of energy ranges.
    Returns an np.ndarray of fold ids (0..n_folds-1).
    """
    dE = np.asarray(dE, dtype=float)
    n = len(dE)
    folds = np.empty(n, dtype=int)
    lo, hi = 0.0, float(dE.max())
    n_bins = max(1, int(np.ceil((hi - lo) / 0.1)))
    edges = np.linspace(lo, hi, n_bins + 1)
    edges[-1] += 1e-6
    for b in range(n_bins):
        e0, e1 = edges[b], edges[b + 1]
        idx = np.where((dE >= e0) & (dE < e1))[0]
        perm = rng.permutation(idx)
        for k, i in enumerate(perm):
            folds[i] = k % n_folds
    return folds


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
    p.add_argument("--cv", action="store_true",
                   help="Use K-fold cross-validation (stratified by energy bin) "
                        "instead of in-sample evaluation. Held-out predictions "
                        "are pooled across folds for a truthful out-of-sample "
                        "accuracy estimate.")
    p.add_argument("--cv-folds", type=int, default=5,
                   help="Number of CV folds (default 5).")
    p.add_argument("--uncertainty", action="store_true",
                   help="Also report the GPR's own predictive uncertainty "
                        "(posterior std from predict_energy_and_uncertainty), "
                        "averaged per energy bin. Writes "
                        "uncertainty_by_energy_range.csv and adds a "
                        "mean_model_std column to the accuracy CSV + error bars "
                        "on the plot.")
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

    # 2. Evaluate
    if args.cv:
        print(f"\n=== Cross-validation ({args.cv_folds}-fold, stratified by energy bin) ===")
        E_DFT = np.asarray([a.get_potential_energy() for a in structures])
        dE_per_atom = (E_DFT - E_DFT.min()) / n_atoms
        rng = np.random.default_rng(42)
        folds = stratify_folds(dE_per_atom, args.cv_folds, rng)

        # pooled held-out predictions + per-fold metrics
        pooled_dE, pooled_err = [], []
        pooled_std = [] if args.uncertainty else None
        fold_metrics = []
        for f in range(args.cv_folds):
            tr_idx = np.where(folds != f)[0]
            te_idx = np.where(folds == f)[0]
            tr = [structures[i] for i in tr_idx]
            print(f"\n  Fold {f+1}/{args.cv_folds}: train {len(tr_idx)}, "
                  f"test {len(te_idx)}")
            gpr = build_gpr(tr, use_ray=args.use_ray)
            for i in te_idx:
                if pooled_std is not None:
                    e_pred, unc = gpr.predict_energy_and_uncertainty(structures[i])
                    pooled_std.append(np.asarray(unc).ravel()[0] / n_atoms)
                else:
                    e_pred = gpr.predict_energy(structures[i])
                pooled_dE.append(dE_per_atom[i])
                pooled_err.append((e_pred - E_DFT[i]) / n_atoms)
            # per-fold overall error
            fe = np.array([(gpr.predict_energy(structures[i]) - E_DFT[i])
                           / n_atoms for i in te_idx])
            fold_metrics.append(float(np.mean(np.abs(fe))))
        pooled_dE = np.array(pooled_dE)
        pooled_err = np.array(pooled_err)
        if pooled_std is not None:
            pooled_std = np.array(pooled_std)

        # pooled per-bin metrics
        rows, overall, edges, n_bins = bin_metrics(
            pooled_dE, pooled_err, args.bin_width, n_atoms)
        title = (f"GPR accuracy vs energy range  "
                 f"{args.cv_folds}-fold CV (pooled held-out), bin width = "
                 f"{args.bin_width:.3f} eV/atom, {n_bins} bins, metrics in eV/atom")
        csv_name = f"gpr_accuracy_by_energy_range_cv{args.cv_folds}folds.csv"
        plot_name = f"gpr_accuracy_by_energy_range_cv{args.cv_folds}folds.png"
        fold_mean = float(np.mean(fold_metrics))
        fold_std = float(np.std(fold_metrics))
        print(f"\n  Per-fold overall MAE (eV/atom): "
              f"{[f'{x:.4f}' for x in fold_metrics]}")
        print(f"  Fold-averaged overall MAE = {fold_mean:.4f} +/- {fold_std:.4f} "
              f"eV/atom")
        # CSV (pooled) + a fold-averaged summary row appended
        csv_path = out / csv_name
        _write_csv(csv_path, rows)
        with open(out / f"cv_fold_summary_{args.cv_folds}folds.csv", "w") as f:
            f.write("fold,overall_MAE_eV_per_atom\n")
            for k, m in enumerate(fold_metrics):
                f.write(f"{k+1},{m:.8f}\n")
            f.write(f"mean,{fold_mean:.8f}\n")
            f.write(f"std,{fold_std:.8f}\n")
        print(f"  Saved CSV: {csv_path}")
    else:
        # --- in-sample (default) ---
        print("\nTraining GPR on combined dataset...")
        gpr = build_gpr(structures, use_ray=args.use_ray)
        print("\nPredicting energies on the training set...")
        E_pred = np.array([gpr.predict_energy(a) for a in structures])
        E_DFT = np.asarray([a.get_potential_energy() for a in structures])
        dE_per_atom = (E_DFT - E_DFT.min()) / n_atoms
        err_per_atom = (E_pred - E_DFT) / n_atoms
        std_per_atom = None
        if args.uncertainty:
            print("  Computing model uncertainty (predict_energy_and_uncertainty)...")
            std_pts = []
            for a in structures:
                _, unc = gpr.predict_energy_and_uncertainty(a)
                std_pts.append(np.asarray(unc).ravel()[0] / n_atoms)
            std_per_atom = np.array(std_pts)
        rows, overall, edges, n_bins = bin_metrics(
            dE_per_atom, err_per_atom, args.bin_width, n_atoms)
        title = (f"GPR accuracy vs energy range  (in-sample, bin width = "
                 f"{args.bin_width:.3f} eV/atom, {n_bins} bins, "
                 f"metrics in eV/atom)")
        csv_path = out / "gpr_accuracy_by_energy_range.csv"
        _write_csv(csv_path, rows)
        plot_name = "gpr_accuracy_by_energy_range.png"
        print(f"  Saved CSV: {csv_path}")

    # 3. Uncertainty analysis (if requested)
    std_per_bin = None
    overall_std = None
    if args.uncertainty:
        # unify (dE, model-std) point arrays across modes
        if args.cv:
            dE_pts, std_pts = pooled_dE, pooled_std
        else:
            dE_pts, std_pts = dE_per_atom, std_per_atom
        std_per_bin = bin_mean_std(dE_pts, std_pts, edges, n_bins)
        overall_std = float(np.mean(std_pts))

        # separate uncertainty CSV
        unc_path = out / "uncertainty_by_energy_range.csv"
        with open(unc_path, "w") as f:
            f.write("bin_lo_eV_per_atom,bin_hi_eV_per_atom,"
                    "mean_model_std_eV_per_atom\n")
            for k, r in enumerate(rows):
                f.write(f"{r['bin_lo_eV_per_atom']:.6f},"
                        f"{r['bin_hi_eV_per_atom']:.6f},{std_per_bin[k]:.8f}\n")
        print(f"  Saved uncertainty CSV: {unc_path}")
        print(f"  Overall mean model std = {overall_std:.4f} eV/atom")

        # add mean_model_std column to the accuracy CSV (rewrite)
        acc_header = ("bin_lo_eV_per_atom,bin_hi_eV_per_atom,n_structures,"
                      "MAE_eV_per_atom,RMSE_eV_per_atom,R2,"
                      "mean_model_std_eV_per_atom\n")
        with open(csv_path, "w") as f:
            f.write(acc_header)
            for k, r in enumerate(rows):
                f.write(f"{r['bin_lo_eV_per_atom']:.6f},"
                        f"{r['bin_hi_eV_per_atom']:.6f},{r['n_structures']},"
                        f"{r['MAE_eV_per_atom']:.8f},"
                        f"{r['RMSE_eV_per_atom']:.8f},{r['R2']:.8f},"
                        f"{std_per_bin[k]:.8f}\n")

    # 4. Print table
    print("\n" + "=" * 70)
    print(title)
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

    # 5. Plot
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

    # uncertainty: per-bin mean model std as error bars on MAE (if requested)
    if std_per_bin is not None:
        ax1.errorbar(centers, mae, yerr=std_per_bin, fmt="none", ecolor="tab:red",
                     capsize=3, alpha=0.6, label="Model std (1σ)")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best", fontsize=8)

    mode_tag = f"{args.cv_folds}-fold CV" if args.cv else "in-sample"
    fig.suptitle(f"GPR accuracy vs energy range ({mode_tag}; Fe/MgO, "
                 f"{len(structures)} structures, {n_atoms} atoms)")
    fig.tight_layout()
    plot_path = out / plot_name
    fig.savefig(plot_path, dpi=150)
    print(f"  Saved plot: {plot_path}")

    # 6. Overall summary
    print("\nOVERALL (eV/atom): "
          f"MAE={overall['MAE_eV_per_atom']:.4f} "
          f"RMSE={overall['RMSE_eV_per_atom']:.4f} "
          f"R2={overall['R2']:.4f}")
    if std_per_bin is not None:
        print(f"  mean model std = {overall_std:.4f} eV/atom")
    print(f"\nDone. Outputs in {out}")


def _write_csv(csv_path, rows):
    """Write per-bin metrics CSV."""
    with open(csv_path, "w") as f:
        f.write("bin_lo_eV_per_atom,bin_hi_eV_per_atom,n_structures,"
                "MAE_eV_per_atom,RMSE_eV_per_atom,R2\n")
        for r in rows:
            f.write(f"{r['bin_lo_eV_per_atom']:.6f},{r['bin_hi_eV_per_atom']:.6f},"
                    f"{r['n_structures']},{r['MAE_eV_per_atom']:.8f},"
                    f"{r['RMSE_eV_per_atom']:.8f},{r['R2']:.8f}\n")


def bin_mean_std(dE, std, edges, n_bins):
    """Per-bin mean of a per-point quantity (e.g. model std), aligned with bin_metrics rows."""
    dE = np.asarray(dE, dtype=float)
    std = np.asarray(std, dtype=float)
    means = []
    for b in range(n_bins):
        e0, e1 = edges[b], edges[b + 1]
        m = (dE >= e0) & (dE < e1)
        if int(m.sum()) == 0:
            means.append(float("nan"))
        else:
            means.append(float(np.mean(std[m])))
    return means


if __name__ == "__main__":
    main()
