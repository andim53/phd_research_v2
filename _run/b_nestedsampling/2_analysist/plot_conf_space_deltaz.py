#!/usr/bin/env python3
"""
Generate the conf_space.png landscape for a temperature-free nested-sampling run's
posterior structures, with the scatter colored by the Fe island height (delta Z).

Replicates the existing `analysis/posterior/conf_space.png` (Fingerprint-PCA
landscape + state-density panel) but colors the PCA scatter by the Fe island
height `delta_Z = max(Fe z) - min(Fe z)` (Angstrom) instead of leaving it
monochrome.

Reads the posterior structures from a run's `posterior_T{KKK}/*.xsf` files (the
per-temperature temperature-free posterior outputs), computes:
  - PC1 of the AGOX Fingerprint descriptors (structural axis of the landscape),
  - per-atom relative energy (E - E_min)/N_atoms (energy axis of the density panel),
  - delta_Z per structure (the color).
Fe atoms are identified by symbol 'Fe' in the structure.

Reuses the shared `plot_structure_landscape` function (the version that accepts
`s=`), which colors the scatter with `z_data` and draws a colorbar.

Run with the project env python (needs AGOX Fingerprint + ASE + the landscape
script on sys.path):

  /home/think/miniconda3/envs/agox_v2/bin/python plot_conf_space_deltaz.py \
      --xsf-dir /path/to/ns_output_tfree/posterior_T300 \
      --outdir  /path/to/outdir \
      --outname conf_space_deltaz.png
"""

from __future__ import annotations

__version__ = "1.1.0"

import argparse
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ase.io import read

# --- paths: make the AGOX landscape script importable -------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ANALYSIST = "/home/think/Desktop/research/2_analysist"
_NS_LANDSCAPE_REF = "/home/think/Desktop/research/2_analysist/1_result/1_no_prior_control/nested_sampling/scripts"
for _p in (_HERE, _ANALYSIST, os.path.join(_ANALYSIST, "scripts"), _NS_LANDSCAPE_REF):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agox.models.descriptors.fingerprint import Fingerprint
from scripts.plot_structure_landscape import plot_structure_landscape

MAX_PHYSICAL_E = 1e4  # eV; reject unphysical GPR predictions


# ---------------------------------------------------------------------------
def delta_z_fe(atoms) -> float:
    """Fe island height delta Z = max(Fe z) - min(Fe z), in Angstrom."""
    pos = atoms.get_positions()
    sym = atoms.get_chemical_symbols()
    fe = [i for i, s in enumerate(sym) if s == "Fe"]
    if not fe:
        return np.nan
    z = pos[fe, 2]
    return float(z.max() - z.min())


def load_structures(xsf_dir):
    """Load posterior_*.xsf from a directory, ordered by rank in the filename."""
    files = sorted(glob.glob(os.path.join(xsf_dir, "posterior_*.xsf")),
                   key=lambda p: int(os.path.basename(p).split("_")[1]))
    if not files:
        raise FileNotFoundError(f"No posterior_*.xsf in {xsf_dir}")
    return [read(p) for p in files], files


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
        description="conf_space.png colored by Fe island height (delta Z)")
    p.add_argument("--xsf-dir", required=True,
                   help="dir containing posterior_*.xsf (e.g. posterior_T300)")
    p.add_argument("--outdir", default=None,
                   help="output dir (default: parent of --xsf-dir)")
    p.add_argument("--outname", default="conf_space_deltaz.png",
                   help="output filename (default conf_space_deltaz.png)")
    args = p.parse_args()

    outdir = args.outdir or os.path.dirname(os.path.abspath(args.xsf_dir))
    os.makedirs(outdir, exist_ok=True)

    structs, files = load_structures(args.xsf_dir)
    print(f"Loaded {len(structs)} posterior structures from {args.xsf_dir}")

    # energies: GPR-predicted, stored in the xsf filename (E-<value>)
    Es = []
    for f in files:
        base = os.path.basename(f)
        # filename pattern: posterior_<rank>_w<w>_E<energy>.xsf
        try:
            E = float(base.split("_E")[1].replace(".xsf", ""))
        except (IndexError, ValueError):
            E = np.nan
        Es.append(E)
    Es = np.asarray(Es, float)

    # per-atom relative energies (energy axis for the density panel)
    n_atoms = len(structs[0])
    E_min = np.nanmin(Es)
    rel = (Es - E_min) / n_atoms

    # Fe island height (color)
    dz = np.array([delta_z_fe(s) for s in structs])
    print(f"  energy range: {np.nanmin(Es):.3f} .. {np.nanmax(Es):.3f} eV")
    print(f"  delta Z range: {np.nanmin(dz):.3f} .. {np.nanmax(dz):.3f} Angstrom")

    # structural axis: PC1 of Fingerprint descriptors
    X_eigen, _ = fit_pca(structs)

    # Energy axis for the state-density panel: match the reference conf_space.png
    # produced by run_analysis_indices.py with --e-max 0.8 (energy scale 0 -> 0.8 eV/atom,
    # 5 ticks). Same energy scale/thickness/labels as that reference density panel.
    e_limit = (0.0 - 0.1, 0.8, 5)

    out_path = os.path.join(outdir, args.outname)
    fig = plot_structure_landscape(
        X_eigen, rel, z_data=dz,       # <-- color the scatter by delta Z
        save_path=outdir,
        animate_scatter=False,
        figsize=(3, 3),
        wspace=0.1,
        fontsize=10,
        e_limit=e_limit,
        fill_density=True,
        dens_line_weight=0.9,
        show_limits=False,
        custom_peak_labels=None,
        cmap="viridis",                 # colormap for delta Z
        show_colorbar=True,
        cbar_pad=0.02,
        z_limit=(np.nanmin(dz), np.nanmax(dz), 5),
        black_seed_zero=True,
        s=5,
        normalize_density=False,
        density_x_label="State Density\n(config./eV)",
        plot_z_vs_e=False,
    )
    plt.close(fig)
    # plot_structure_landscape writes conf_space.png; rename to our output name
    default_out = os.path.join(outdir, "conf_space.png")
    if default_out != out_path and os.path.exists(default_out):
        os.replace(default_out, out_path)
    print(f"  -> colored landscape saved to {out_path}")


if __name__ == "__main__":
    main()
