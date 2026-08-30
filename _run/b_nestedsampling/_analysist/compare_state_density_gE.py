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

__version__ = "2.6.0"

import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.ticker import AutoMinorLocator
from scipy.signal import find_peaks
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
DENSITY_LABEL = "State Density\n(config./eV)"  # matches run_analysis_indices.py density axis; unit on bottom line
SCATTER_LABEL = r"$\psi_{1d}(a.u.)$"           # matches run_analysis_indices.py scatter axis
E_LIMIT = (0.0 - 0.1, 0.8, 5)                 # energy axis 0 -> 0.8 eV/atom, 5 ticks


def load_dataset_structures(dataset_dir: str, start_iter: int = 10):
    """Load structures + DFT energies from dataset/seed_*/1_db/db_*.db, keeping only
    AGOX structures with iteration >= start_iter (mirrors run_analysis_indices.py /
    process_database.py's start_iter filter via get_all_structures_data()['iteration'])."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched in {dataset_dir}")
    structures, energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        atoms_list = [db.db_to_atoms(d) for d in kept]
        structures.extend(atoms_list)
        energies.extend(a.get_potential_energy() for a in atoms_list)
        print(f"  {os.path.basename(p)}: {len(atoms_list)}/{len(raw)} structures "
              f"(iteration >= {start_iter})")
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


def delta_z_fe(atoms) -> float:
    """Fe island height delta Z = max(Fe z) - min(Fe z), in Angstrom."""
    pos = atoms.get_positions()
    sym = atoms.get_chemical_symbols()
    fe = [i for i, s in enumerate(sym) if s == "Fe"]
    if not fe:
        return np.nan
    z = pos[fe, 2]
    return float(z.max() - z.min())


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

    # --- dataset structures + energies (AGOX start-iter filter >= 10) ---
    structs, energies = load_dataset_structures(dataset_dir, start_iter=10)
    print(f"  dataset: {len(structs)} structures (iteration >= 10), {len(structs[0])} atoms each")
    E_ref_ds = energies.min()
    E_rel_ds = (energies - E_ref_ds) / args.n_atoms

    # PCA scatter (Configurational Space panel)
    X_eigen, _ = fit_pca(structs)
    # delta Z (Fe island height) per dataset structure, for the scatter colorbar
    z_data = np.array([delta_z_fe(s) for s in structs])
    z_data = z_data - np.nanmin(z_data)   # relative delta Z (Angstrom)
    print(f"  delta Z range: {np.nanmin(z_data):.3f} .. {np.nanmax(z_data):.3f} Angstrom")

    # --- shared energy axis ---
    min_e, max_e, nticks = E_LIMIT[0], args.e_max, E_LIMIT[2]
    eticks = np.round(np.linspace(min_e, max_e, nticks), 1)
    energy_grid = np.linspace(min_e, max_e, 200)

    # --- dataset KDE (GPR+LCB panel; smooth) and NS weighted histogram + KDE ---
    ds_kde = gaussian_kde(E_rel_ds)
    ds_density = ds_kde.evaluate(energy_grid)
    # NS state density = prior-weight-weighted histogram of the ns_output samples.csv
    # energies (per-atom relative), config./eV — the NS state-density recipe.
    n_bins_ns = 50
    ns_hist, ns_edges = np.histogram(E_rel_ns, bins=n_bins_ns, weights=Ws)
    ns_centers = 0.5 * (ns_edges[:-1] + ns_edges[1:])
    ns_binw = ns_edges[1] - ns_edges[0]
    ns_density = ns_hist / ns_binw  # config./eV (histogram)
    # KDE smoothing of the same NS energies, weighted by prior_weight.
    ns_kde = gaussian_kde(E_rel_ns, weights=Ws)
    ns_kde_density = ns_kde.evaluate(energy_grid)

    # --- 3-panel figure, shared energy y-axis, formatted like reference conf_space.png ---
    # widths: PCA (Configurational Space) LARGE, both State Density panels THINNER
    # (matches the reference conf_space.png where the PCA scatter is the wide panel
    # and the density panel is thin).
    ratios = [2.5, 1, 1]
    fig, axes = plt.subplots(1, 3, figsize=(7, 3), sharey=True,
                             gridspec_kw={'width_ratios': ratios})
    fig.subplots_adjust(wspace=0.1)

    # Panel 1 (far left): Configurational Space (PCA scatter of dataset), colored by
    # delta Z (Fe island height) with a PuBu colorbar (like 71_conf_space.py).
    ax_scat = axes[0]
    vmin, vmax = np.nanmin(z_data), np.nanmax(z_data)
    sc = ax_scat.scatter(X_eigen, E_rel_ds, c=z_data, cmap="PuBu", s=5,
                         norm=mcolors.Normalize(vmin=vmin, vmax=vmax),
                         edgecolors="black", linewidth=0.5, alpha=0.8, zorder=2)
    cbar = fig.colorbar(sc, ax=ax_scat, pad=0.02)
    cbar.set_label(r"$\Delta z$ (Å)")
    cbar.set_ticks(np.linspace(vmin, vmax, 5))
    cbar.set_ticklabels([f"{t:.2f}" for t in np.linspace(vmin, vmax, 5)])
    ax_scat.set_xlabel(SCATTER_LABEL)
    ax_scat.xaxis.set_minor_locator(AutoMinorLocator())
    ax_scat.set_xlim(np.min(X_eigen) - 0.1, np.max(X_eigen) + 0.1)
    ax_scat.set_aspect("equal")   # square ratio for the PCA panel

    # Panel 2 (middle): dataset State Density (KDE) -> GPR+LCB
    ax_ds = axes[1]
    ax_ds.plot(ds_density, energy_grid, color="black", lw=0.9, zorder=4, label="GPR+LCB")
    ax_ds.fill_betweenx(energy_grid, 0, ds_density, color="black", alpha=0.12, zorder=3)
    # dashed lines at the GPR+LCB KDE peak(s) (like 36_find_density_peak.py), black
    ds_peaks, _ = find_peaks(ds_density, prominence=np.max(ds_density) * 0.05)
    for pk in ds_peaks:
        ax_ds.hlines(energy_grid[pk], 0, ds_density[pk], colors="black",
                     linestyles="--", alpha=0.5)
    # notes: flat and island at the reference energies (black text)
    for note_e, note_txt in [(0.255, "flat"), (0.074, "island")]:
        ax_ds.text(0.02, note_e, note_txt, color="black", fontsize=8,
                   ha="left", va="bottom")
    ax_ds.legend(loc="upper right", frameon=False, fontsize=9)
    ax_ds.set_xlabel(DENSITY_LABEL)

    # Panel 3 (far right): NS State Density — prior-weight-weighted histogram (barh,
    # x = density, y = energy) with KDE smoothing overlaid, NS only.
    ax_ns = axes[2]
    ax_ns.barh(ns_centers, ns_density, height=ns_binw * 0.9, color="tab:red",
               alpha=0.35, label="NS")
    ax_ns.plot(ns_kde_density, energy_grid, color="tab:red", lw=1.5, zorder=4)
    # additional black dashed line at the flat/island reference energies (NS panel)
    for note_e in (0.255, 0.074):
        ax_ns.axhline(note_e, color="black", linestyle="--", lw=1.0, alpha=0.6)
    ax_ns.legend(loc="upper right", frameon=False, fontsize=9)
    ax_ns.set_xlabel(DENSITY_LABEL)

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
    print(f"  NS hist peak at: {ns_centers[np.argmax(ns_density)]:.4f} eV/atom (abs g={ns_density.max():.3f})")
    print(f"Dataset (DFT)    : {len(structs)} structures")
    print(f"  DS KDE peak at : {energy_grid[np.argmax(ds_density)]:.4f} eV/atom (abs g={ds_density.max():.3f})")
    print(f"n_atoms          : {args.n_atoms}")
    print(f"energy y-axis    : [{min_e:.2f}, {max_e:.2f}] eV/atom ({nticks} ticks)")


if __name__ == "__main__":
    main()
