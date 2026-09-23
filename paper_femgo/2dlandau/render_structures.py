#!/usr/bin/env python3
"""
Render the generated/relaxed example structures as 3D PNGs with the user's
custom per-element coloring (Fe=green, Mg=orange, O=red), and write a VESTA
project (.vesta) file per structure that embeds the same colors, so VESTA opens
it pre-colored.

Reads the XSF files written by make_examples.py from analysis/2dlandau_examples/.

For each relaxed (and generated) structure it writes:
  - <name>.png   : ball-and-stick 3D render (matplotlib, custom colors)
  - <name>.vesta : VESTA project with per-element colors + stick/ball style

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python render_structures.py
"""

from __future__ import annotations

__version__ = "2.0.0"

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'codes'))
from vesta_writer import write_vesta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read as ase_read
from ase.geometry import get_distances

_PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTDIR = os.path.join(_PROJ, "analysis", "2dlandau_examples")

# User's custom colors (from data/femgo/main.py custom_colors)
COLORS = {"Fe": "#4C9F38", "Mg": "#FF7F0E", "O": "#D62728"}
# covalent radii (Angstrom) for sphere sizing
RADII = {"Fe": 1.32, "Mg": 1.41, "O": 0.66}
# bond cutoffs (Angstrom) per element pair, ball-and-stick
BOND_CUT = 3.0


def _element(atom):
    return atom.symbol


def _render(atoms, out_png, title):
    """Ball-and-stick 3D render using matplotlib."""
    pos = atoms.positions
    syms = [a.symbol for a in atoms]

    # fixed view direction (tilted, looking down the island)
    # rotate positions: look slightly from +x/+y and below
    elev, azim = 24.0, 32.0
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")

    # depth = distance along the view axis (for sphere sizing / fade)
    azr, elr = np.deg2rad(azim), np.deg2rad(elev)
    view = np.array([np.cos(elr) * np.sin(azr),
                     np.cos(elr) * np.cos(azr),
                     np.sin(elr)])
    depth = pos @ view
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-9)

    # --- bonds (stick) -----------------------------------------------------
    # neighbor list with a generous cutoff, drawn once per pair
    n = len(pos)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(pos[i] - pos[j])
            cut = BOND_CUT
            if d < cut:
                ax.plot([pos[i, 0], pos[j, 0]],
                        [pos[i, 1], pos[j, 1]],
                        [pos[i, 2], pos[j, 2]],
                        color="#888888", lw=1.0, alpha=0.55, zorder=1)

    # --- atoms (balls) ------------------------------------------------------
    # project to view coords to sort far-to-near so near atoms draw on top
    # (simple painter's algorithm by depth)
    order = np.argsort(depth)[::-1]   # far first
    for idx in order:
        s = syms[idx]
        c = COLORS.get(s, "#555555")
        r = RADII.get(s, 1.0)
        d = depth[idx]
        # sphere size: scale radius to marker area; fade far atoms
        size = (r * 28) ** 2 * (1.0 - 0.35 * d)
        alpha = 0.95 - 0.35 * d
        ax.scatter(pos[idx, 0], pos[idx, 1], pos[idx, 2],
                   s=size, color=c, alpha=alpha, edgecolors="none",
                   depthshade=True, zorder=2)

    # legend (one proxy per element)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", linestyle="none",
                      markerfacecolor=COLORS[e], markersize=9,
                      label=e) for e in ("Fe", "Mg", "O")]
    ax.legend(handles=handles, loc="upper right", fontsize=10)

    # equal aspect + clean axes
    mn, mx = pos.min(axis=0), pos.max(axis=0)
    ctr = 0.5 * (mn + mx)
    span = (mx - mn).max() * 0.55
    ax.set_xlim(ctr[0] - span, ctr[0] + span)
    ax.set_ylim(ctr[1] - span, ctr[1] + span)
    ax.set_zlim(ctr[2] - span, ctr[2] + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=12)

    fig.tight_layout()
    fig.savefig(out_png, dpi=200, transparent=False)
    plt.close(fig)
    print(f"  rendered {os.path.basename(out_png)}")


def main():
    patterns = sorted(glob.glob(os.path.join(_OUTDIR, "relax_dz_*.xsf")))
    if not patterns:
        print("No relax_dz_*.xsf found — run make_examples.py first.")
        return 1
    for xsf in patterns:
        base = os.path.splitext(os.path.basename(xsf))[0]
        atoms = ase_read(xsf)
        h = float(base.split("_dz_")[1])
        _render(atoms, os.path.join(_OUTDIR, base + ".png"),
                f"Relaxed structure, dZ = {h:.2f} A")
        write_vesta(atoms, os.path.join(_OUTDIR, base + ".vesta"),
                    f"2dlandau {base}", darken_fe=False)
    print(f"\nDone. Files in {_OUTDIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())