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

Dataset parameters mirror the ns_output (`--e-max-per-atom 0.4`, n_atoms 82 for
boron) so the dataset curve reflects the same filtered pool the sampler used.

Usage (needs numpy + scipy + matplotlib + agox_v2 for the DB loader):
  /home/think/miniconda3/envs/agox_v2/bin/python compare_state_density_gE.py \
      --run b11_boron_walk_emax04_exclworst_noxsf_novelty \
      --ns-output analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_boron_iter20000 \
      --n-atoms 82 --e-max-per-atom 0.4 \
      --outname compare_state_density_gE.png
"""

from __future__ import annotations

__version__ = "1.0.1"

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
    p.add_argument("--e-max-per-atom", type=float, default=None,
                   help="relative eV/atom filter on the dataset (mirrors --e-max-per-atom). "
                        "Default None = keep all.")
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
    g_ns = hist_g / binw

    # --- dataset DFT energies + filter (mirror main.py) ---
    energies = load_dataset_energies(dataset_dir)
    if args.e_max_per_atom is not None:
        e_per_atom = energies / args.n_atoms
        keep = (e_per_atom - e_per_atom.min()) <= args.e_max_per_atom
        energies = energies[keep]
        print(f"  --e-max-per-atom {args.e_max_per_atom}: kept "
              f"{energies.size} / {e_per_atom.size} dataset structures")
    print(f"  dataset: {energies.size} structures")

    # --- dataset KDE g(E), relative to its OWN minimum ---
    E_rel_ds = (energies - energies.min()) / args.n_atoms
    kde = gaussian_kde(E_rel_ds)
    # KDE integrates to 1 (a normalized density); NS histogram integrates to
    # sum(Ws) ~= 1 (the consumed prior volume). Scale KDE so both integrate to 1.
    grid = np.linspace(0, max(E_rel_ns.max(), E_rel_ds.max()), 400)
    g_ds = kde(grid)

    # --- overlay plot ---
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(centers_ns, g_ns, width=binw * 0.9, alpha=0.5,
           label="NS g(E) (weighted histogram)")
    ax.plot(grid, g_ds, "r-", lw=2, label="GPR+LCB g(E) (Gaussian KDE)")
    ax.set_xlabel("E - E_min (eV/atom)"); ax.set_ylabel(r"$g(E)$ (config./eV)")
    ax.set_title("State density: NS samples vs dataset (KDE)")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout()

    out_path = os.path.join(out_dir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")

    # --- printed summary ---
    print("=" * 60)
    print("State-density comparison")
    print("=" * 60)
    print(f"NS samples       : {Es.size} (prior-volume weighted)")
    print(f"  g(E) peak at   : {centers_ns[np.argmax(g_ns)]:.4f} eV/atom (g={g_ns.max():.3f})")
    print(f"Dataset (DFT)    : {energies.size} structures")
    print(f"  KDE peak at    : {grid[np.argmax(g_ds)]:.4f} eV/atom (g={g_ds.max():.3f})")
    print(f"n_atoms          : {args.n_atoms}")
    print(f"NS E range       : [{E_rel_ns.min():.4f}, {E_rel_ns.max():.4f}] eV/atom (rel. own min)")
    print(f"DS E range       : [{E_rel_ds.min():.4f}, {E_rel_ds.max():.4f}] eV/atom (rel. own min)")


if __name__ == "__main__":
    main()
