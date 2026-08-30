#!/usr/bin/env python3
"""
Compare the nested-sampling state density g(E) from a temperature-free run's
`samples.csv` (prior-weight-weighted histogram, exactly as `state_density_gE.png`
in `analyze_tfree_outputs.py`) against a gaussian-KDE state density computed
directly from the run's DATASET (the seed DB structures' DFT energies).

Produces a single overlay plot: the NS weighted-histogram g(E) and the dataset
KDE g(E), both in per-atom relative-energy units `(E - min)/n_atoms`, each
referenced to its OWN minimum so the density SHAPES are compared on the same
eV/atom axis.

Dataset parameters: the KDE is built on ALL dataset structures (no energy
filter); only the PLOT is clipped to the NS g(E) E-E_min max so both curves
share the same eV/atom range. n_atoms 82 for boron.

Usage (needs numpy + scipy + matplotlib + agox_v2 for the DB loader):
  /home/think/miniconda3/envs/agox_v2/bin/python compare_state_density_gE.py \
      --run b11_boron_walk_emax04_exclworst_noxsf_novelty \
      --ns-output analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000 \
      --n-atoms 82 \
      --outname compare_state_density_gE.png
"""

from __future__ import annotations

__version__ = "1.4.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

import analyze_tfree_outputs as ato  # reuse load_samples + the NS g(E) recipe


def load_dataset_energies(dataset_dir: str):
    """Load + filter dataset DFT energies, mirroring main.py's load_all_seeds."""
    import glob
    from agox.databases import Database
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched in {dataset_dir}")
    energies = []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        energies.extend(a.get_potential_energy() for a in traj)
    return np.asarray(energies, dtype=float)


def main():
    p = argparse.ArgumentParser(description="Overlay NS g(E) with dataset-KDE g(E)")
    p.add_argument("--run", required=True,
                   help="b11 run dir name under _analysist/ (contains dataset/ and the "
                        "analysis_<ns_output> dir)")
    p.add_argument("--ns-output", required=True,
                   help="analysis_<ns_output_name> dir name (the one holding samples.csv "
                        "under the run's ns_output dir and state_density_gE.png)")
    p.add_argument("--n-atoms", type=int, default=82,
                   help="atoms per structure (boron Fe25Mg25O25B7 = 82). Default 82.")
    p.add_argument("--outname", default="compare_state_density_gE.png",
                   help="output filename (written next to the NS analysis dir)")
    args = p.parse_args()

    _HERE = os.path.dirname(os.path.abspath(__file__))
    run_dir = os.path.join(_HERE, args.run)
    dataset_dir = os.path.join(run_dir, "dataset")
    out_dir = os.path.join(run_dir, args.ns_output)          # analysis dir (writes PNG here)
    # samples.csv lives in the ns_output dir: the analysis dir name is "analysis_<ns_output_name>",
    # so the ns_output dir is the same name minus the leading "analysis_" prefix.
    ns_name = args.ns_output
    if ns_name.startswith("analysis_"):
        ns_name = ns_name[len("analysis_"):]
    ns_dir = os.path.join(run_dir, ns_name)
    if not os.path.isdir(ns_dir):
        raise FileNotFoundError(f"ns_output dir not found: {ns_dir}")

    # --- NS weighted-histogram g(E) (exact recipe from state_density_gE.png) ---
    iters, Es, Ws = ato.load_samples(os.path.join(ns_dir, "samples.csv"))
    rel_min = Es.min()
    E_rel_ns = (Es - rel_min) / args.n_atoms
    n_bins = 50
    hist_g, edges_g = np.histogram(E_rel_ns, bins=n_bins, weights=Ws)
    centers_ns = 0.5 * (edges_g[:-1] + edges_g[1:])
    binw = edges_g[1] - edges_g[0]
    g_ns_abs = hist_g / binw            # absolute config./eV
    peak_ns = g_ns_abs.max()
    g_ns = g_ns_abs / peak_ns           # peak-normalized (=1) for shape comparison

    # --- dataset DFT energies (ALL structures, no energy filter) ---
    energies = load_dataset_energies(dataset_dir)
    print(f"  dataset: {energies.size} structures (all, unfiltered)")

    # --- dataset KDE g(E), relative to its OWN minimum ---
    E_rel_ds = (energies - energies.min()) / args.n_atoms
    kde = gaussian_kde(E_rel_ds)
    # KDE integrates to 1 (a normalized density); NS histogram integrates to
    # sum(Ws) ~= 1 (the consumed prior volume).
    # Plot x-range is capped at the NS g(E) E-E_min max so both curves share the
    # same max; the full-dataset KDE (which may extend further) is only drawn up to it.
    grid = np.linspace(0, E_rel_ns.max(), 400)
    g_ds_abs = kde(grid)
    peak_ds = g_ds_abs.max()
    g_ds = g_ds_abs / peak_ds           # peak-normalized (=1) for shape comparison

    # --- overlay plot (both peak-normalized to 1 so shapes are comparable) ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.bar(centers_ns, g_ns, width=binw * 0.9, alpha=0.5,
           label=f"NS g(E) (weighted hist; peak {peak_ns:.1f} config./eV)")
    ax.plot(grid, g_ds, "r-", lw=2,
            label=f"GPR+LCB g(E) (Gaussian KDE; peak {peak_ds:.3f} config./eV)")
    ax.set_xlabel("E - E_min (eV/atom)")
    ax.set_ylabel(r"$g(E)$ / $g(E)_{max}$  (peak-normalized)")
    ax.set_title("State density shape: NS samples vs dataset (KDE)\npeak-normalized")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    fig.tight_layout()

    out_path = os.path.join(out_dir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")

    # --- printed summary ---
    print("=" * 60)
    print("State-density comparison (peak-normalized)")
    print("=" * 60)
    print(f"NS samples       : {Es.size} (prior-volume weighted)")
    print(f"  g(E) peak at   : {centers_ns[np.argmax(g_ns_abs)]:.4f} eV/atom (abs g={peak_ns:.3f})")
    print(f"Dataset (DFT)    : {energies.size} structures")
    print(f"  KDE peak at    : {grid[np.argmax(g_ds_abs)]:.4f} eV/atom (abs g={peak_ds:.3f})")
    print(f"n_atoms          : {args.n_atoms}")
    print(f"NS E range       : [{E_rel_ns.min():.4f}, {E_rel_ns.max():.4f}] eV/atom (rel. own min)")
    print(f"DS E range       : [{E_rel_ds.min():.4f}, {E_rel_ds.max():.4f}] eV/atom (rel. own min)")


if __name__ == "__main__":
    main()
