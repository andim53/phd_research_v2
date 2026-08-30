#!/usr/bin/env python3
"""
Compare the nested-sampling (NS) state density g(E) against the dataset state
density, and show the dataset's configurational space — as a single 3-panel
figure that mirrors the reference `analysis_indices/conf_space.png` formatting:

  [Configurational Space] | [dataset State Density] | [NS State Density]

- Panel 1 (far left): Configurational Space — PCA scatter (Fingerprint PC1 vs
  per-atom relative energy) of the dataset structures, like the reference
  conf_space.png panel.
- Panel 2 (middle): dataset State Density — gaussian KDE of the dataset DFT
  energies (per-atom relative).
- Panel 3 (far right): NS State Density — gaussian KDE of the NS sample energies
  (per-atom relative). NS only (no GPR+LCB overlay).

All three panels share the same energy (y) axis, e_limit 0->0.8 eV/atom (5 ticks),
and the formatting matches the reference conf_space.png (serif, ticks-in, no grid,
energy y-label '$E_{i}-E_{glob}$ (eV/atom)', state-density x-label
'State Density (config./eV)', scatter x-label '$\\psi_{1d}(a.u.)$').

Usage (needs agox_v2 for Fingerprint + Database + scipy + matplotlib):
  /home/think/miniconda3/envs/agox_v2/bin/python compare_state_density_gE.py \
      --run b10_femgo_walk_emax04_exclworst_noxsf_novelty \
      --ns-output analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --n-atoms 75 [--e-max 0.8] [--simple] \
      --outname compare_state_density_gE.png
"""

from __future__ import annotations

__version__ = "2.0.0"

import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.stats import gaussian_kde

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint

import analyze_tfree_outputs as ato  # reuse load_samples

# --- Plotting style: same rcParams as run_analysis_indices.py (reference pipeline) ---
plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif",
    "axes.linewidth": 1.0,
    "axes.edgecolor": "black",
    "axes.facecolor": "white",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "axes.grid": False,
    "figure.autolayout": True,
    "figure.dpi": 300,
})

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"       # matches run_analysis_indices.py
DENSITY_LABEL = "State Density (config./eV)"  # matches run_analysis_indices.py density axis
SCATTER_LABEL = r"$\psi_{1d}(a.u.)$"           # matches run_analysis_indices.py scatter axis
E_LIMIT = (0.0 - 0.1, 0.8, 5)                 # energy axis 0 -> 0.8 eV/atom, 5 ticks


def load_dataset_structures(dataset_dir: str):
    """Load structures + DFT energies from dataset/seed_*/1_db/db_*.db (mirrors main.py)."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched in {dataset_dir}")
    structures, energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
    return structures, np.asarray(energies, dtype=float)


def fit_pca(structures):
    """PC1 of the AGOX Fingerprint descriptors (structural landscape axis)."""
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    return Xc @ evecs[:, order[0]], fp


def main():
    p = argparse.ArgumentParser(
        description="3-panel figure: Config Space | dataset State Density | NS State Density")
    p.add_argument("--run", required=True,
                   help="run dir name under _analysist/ (contains dataset/ and the "
                        "analysis_<ns_output> dir)")
    p.add_argument("--ns-output", required=True,
                   help="analysis_<ns_output_name> dir name (holds the ns_output samples.csv "
                        "and receives the output PNG)")
    p.add_argument("--n-atoms", type=int, default=82,
                   help="atoms per structure (boron = 82, Fe/MgO = 75). Default 82.")
    p.add_argument("--e-max", type=float, default=0.8,
                   help="max E - E_glob (eV/atom) for the shared energy y-axis. Default 0.8 "
                        "(matches the reference conf_space.png).")
    p.add_argument("--simple", action="store_true",
                   help="simplified version: no title; short legend labels.")
    p.add_argument("--outname", default="compare_state_density_gE.png",
                   help="output filename (written next to the NS analysis dir)")
    args = p.parse_args()

    _HERE = os.path.dirname(os.path.abspath(__file__))
    run_dir = os.path.join(_HERE, args.run)
    dataset_dir = os.path.join(run_dir, "dataset")
    out_dir = os.path.join(run_dir, args.ns_output)   # analysis dir (writes PNG here)
    # samples.csv lives in the ns_output dir: analysis_<name> -> <name>
    ns_name = args.ns_output
    if ns_name.startswith("analysis_"):
        ns_name = ns_name[len("analysis_"):]
    ns_dir = os.path.join(run_dir, ns_name)
    if not os.path.isdir(ns_dir):
        raise FileNotFoundError(f"ns_output dir not found: {ns_dir}")

    # --- NS sample energies (per-atom relative) ---
    iters, Es, Ws = ato.load_samples(os.path.join(ns_dir, "samples.csv"))
    E_ref_ns = Es.min()
    E_rel_ns = (Es - E_ref_ns) / args.n_atoms
    print(f"  NS samples: {Es.size}, E range [{E_rel_ns.min():.4f}, {E_rel_ns.max():.4f}] eV/atom")

    # --- dataset structures + energies ---
    structs, energies = load_dataset_structures(dataset_dir)
    print(f"  dataset: {len(structs)} structures, {len(structs[0])} atoms each")
    E_ref_ds = energies.min()
    E_rel_ds = (energies - E_ref_ds) / args.n_atoms

    # PCA scatter (Configurational Space panel)
    X_eigen, _ = fit_pca(structs)

    # --- shared energy axis ---
    min_e, max_e, nticks = E_LIMIT[0], args.e_max, E_LIMIT[2]
    eticks = np.round(np.linspace(min_e, max_e, nticks), 1)
    energy_grid = np.linspace(min_e, max_e, 200)

    # --- dataset KDE and NS KDE (smooth, matching the reference density style) ---
    ds_kde = gaussian_kde(E_rel_ds)
    ds_density = ds_kde.evaluate(energy_grid)
    ns_kde = gaussian_kde(E_rel_ns)
    ns_density = ns_kde.evaluate(energy_grid)

    # --- 3-panel figure, shared energy y-axis, formatted like reference conf_space.png ---
    # widths: scatter (1), dataset density (2.5), NS density (2.5); figsize proportional to (3,3).
    ratios = [1, 2.5, 2.5]
    fig, axes = plt.subplots(1, 3, figsize=(6, 3), sharey=True,
                             gridspec_kw={'width_ratios': ratios})
    fig.subplots_adjust(wspace=0.1)

    # Panel 1 (far left): Configurational Space (PCA scatter of dataset)
    ax_scat = axes[0]
    ax_scat.scatter(X_eigen, E_rel_ds, c="white", s=5, edgecolors="black",
                    linewidth=0.5, alpha=0.8, zorder=2)
    ax_scat.set_xlabel(SCATTER_LABEL)
    ax_scat.xaxis.set_minor_locator(AutoMinorLocator())
    ax_scat.set_xlim(np.min(X_eigen) - 0.1, np.max(X_eigen) + 0.1)

    # Panel 2 (middle): dataset State Density (KDE)
    ax_ds = axes[1]
    ax_ds.plot(ds_density, energy_grid, color="black", lw=0.9, zorder=4)
    ax_ds.fill_betweenx(energy_grid, 0, ds_density, color="black", alpha=0.12, zorder=3)
    ax_ds.set_xlabel(DENSITY_LABEL)

    # Panel 3 (far right): NS State Density (KDE, NS only)
    ax_ns = axes[2]
    ax_ns.plot(ns_density, energy_grid, color="tab:red", lw=0.9, zorder=4)
    ax_ns.fill_betweenx(energy_grid, 0, ns_density, color="tab:red", alpha=0.12, zorder=3)
    ax_ns.set_xlabel(DENSITY_LABEL)
    if not args.simple:
        ax_ns.set_title("NS State Density", fontsize=10)

    # shared energy y-axis styling on the left panel
    axes[0].set_ylabel(E_LABEL)
    for ax in axes:
        ax.set_ylim(min_e, max_e)
        ax.set_yticks(eticks)
        ax.yaxis.set_minor_locator(AutoMinorLocator())

    out_path = os.path.join(out_dir, args.outname)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved -> {out_path}")

    # --- printed summary ---
    print("=" * 60)
    print("3-panel state-density comparison")
    print("=" * 60)
    print(f"NS samples       : {Es.size}")
    print(f"  NS KDE peak at : {energy_grid[np.argmax(ns_density)]:.4f} eV/atom (abs g={ns_density.max():.3f})")
    print(f"Dataset (DFT)    : {len(structs)} structures")
    print(f"  DS KDE peak at : {energy_grid[np.argmax(ds_density)]:.4f} eV/atom (abs g={ds_density.max():.3f})")
    print(f"n_atoms          : {args.n_atoms}")
    print(f"energy y-axis    : [{min_e:.2f}, {max_e:.2f}] eV/atom ({nticks} ticks)")


if __name__ == "__main__":
    main()
