#!/usr/bin/env python3
"""
Stage 2 — ground-state comparison plots (pymat_xrd).

Reads the Stage-1 ground-state manifest (xrd_groundstate_extract.py) that lists the
4 Pt-P 1_plus0cell leaves' rel-E=0 CIFs, simulates powder XRD for each ground-state
structure, and produces two comparison figures:

  xrd_averaged_by_window.png   : the 4 ground-state XRD patterns overlaid
                                 (one curve per P concentration)
  crystallinity_vs_energy.png  : peak-fraction & integrated CI of each ground
                                 state vs P concentration (%), since each is a
                                 single structure there is no energy axis.
  xrd_plots.json               : (with --json) all plotted arrays for re-plotting.

Runs in the **pymat_xrd** env (pymatgen + scipy + matplotlib). CI functions mirror
xrd_simulate_crystallinity.py (peak-fraction ±0.6 deg; integrated via 5-deg running
mean background).

Usage (pymat_xrd):
  PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
  $PY_X xrd_groundstate_compare.py --manifest <family>/xrd_gs_compare/manifest.json \
        --outdir <family>/xrd_gs_compare [--json]
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d, uniform_filter1d

from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure

plt.rcParams.update({
    "font.size": 12, "font.family": "serif",
    "axes.linewidth": 1.0, "axes.edgecolor": "black",
    "figure.autolayout": True, "figure.dpi": 300,
})

TT_MIN_DEFAULT, TT_MAX_DEFAULT = 10.0, 90.0
TT_STEP = 0.02
BROADEN_SIGMA = 0.15


def simulate_pattern(calc, cif_path, tt_min, tt_max):
    """Simulate a structure's powder XRD on a common 2theta grid and Gaussian-broaden."""
    grid = np.arange(tt_min, tt_max + TT_STEP, TT_STEP)
    struct = Structure.from_file(cif_path)
    pat = calc.get_pattern(struct, two_theta_range=(tt_min, tt_max))
    inten = np.zeros_like(grid)
    for x, y in zip(pat.x, pat.y):
        gi = int(round((x - tt_min) / TT_STEP))
        if 0 <= gi < len(grid):
            inten[gi] += y
    return grid, gaussian_filter1d(inten, sigma=BROADEN_SIGMA / TT_STEP)


def peak_fraction_ci(two_theta, inten, half_width_deg=0.6):
    total = np.trapezoid(inten, two_theta)
    if total <= 0:
        return 0.0
    peaks, _ = find_peaks(inten, prominence=0.02 * inten.max())
    if peaks.size == 0:
        return 0.0
    half = half_width_deg
    crit = np.zeros_like(two_theta, dtype=bool)
    for p in peaks:
        th = two_theta[p]
        crit |= (two_theta >= th - half) & (two_theta <= th + half)
    return float(np.trapezoid(np.where(crit, inten, 0.0), two_theta) / total)


def integrated_ci(two_theta, inten, bg_window_deg=5.0):
    total = np.trapezoid(inten, two_theta)
    if total <= 0:
        return 0.0
    halfwin = max(1, int(bg_window_deg / 2 / TT_STEP))
    bg = uniform_filter1d(inten, size=2 * halfwin + 1, mode="nearest")
    return float(np.trapezoid(np.maximum(inten - bg, 0.0), two_theta) / total)


def plot_from_data(data, outdir):
    """Draw both comparison PNGs from a data dict (live run or JSON)."""
    leaves = data["leaves"]
    # --- Figure 1: overlaid ground-state XRD patterns ---
    fig, ax = plt.subplots(figsize=(8, 4.5))
    cmap = plt.get_cmap("viridis")
    concs = [l["P_concentration_pct"] for l in leaves]
    vmin, vmax = min(concs), max(concs)
    for l in leaves:
        if not l["grid"]:
            continue
        color = cmap((l["P_concentration_pct"] - vmin) / (vmax - vmin + 1e-9)) \
            if vmax > vmin else "C0"
        ax.plot(l["grid"], l["intensity"], lw=1.1, color=color,
                label=f"{l['leaf']} ({l['P_concentration_pct']:.0f}%P)")
    ax.set_xlabel(r"2$\theta$ (deg)"); ax.set_ylabel("Intensity (a.u.)")
    ax.set_title("Ground-state XRD — Pt–P 1_plus0cell (per P concentration)")
    ax.legend(title="P concentration", fontsize=8, ncol=2, loc="upper right")
    fig.savefig(os.path.join(outdir, "xrd_averaged_by_window.png"))
    plt.close(fig)

    # --- Figure 2: CI vs P concentration ---
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [l["P_concentration_pct"] for l in leaves]
    ax.plot(xs, [l["peak_fraction_ci"] for l in leaves], "o-",
            label="peak-fraction CI")
    ax.plot(xs, [l["integrated_ci"] for l in leaves], "s--",
            label="integrated CI")
    ax.set_xlabel("P concentration (%)"); ax.set_ylabel("Crystallinity index")
    ax.set_title("Ground-state crystallinity vs P content (1_plus0cell)")
    ax.set_xlim(0, max(xs) + 5 if xs else 40)
    ax.set_ylim(0, 1)
    ax.legend()
    fig.savefig(os.path.join(outdir, "crystallinity_vs_energy.png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Ground-state XRD + CI comparison for Pt-P 1_plus0cell (pymat_xrd).")
    parser.add_argument("--manifest", default=None,
                        help="Stage-1 ground-state manifest.json (required for a full run; "
                             "ignored with --from-json)")
    parser.add_argument("--outdir", required=True,
                        help="output dir for the comparison figures")
    parser.add_argument("--json", action="store_true",
                        help="also write xrd_plots.json")
    parser.add_argument("--from-json", default=None,
                        help="re-draw both PNGs from xrd_plots.json in this dir")
    args = parser.parse_args()

    if args.from_json:
        with open(os.path.join(args.from_json, "xrd_plots.json")) as f:
            data = json.load(f)
        os.makedirs(args.outdir, exist_ok=True)
        plot_from_data(data, args.outdir)
        print(f"\nDONE. Re-plotted ground-state PNGs from "
              f"{os.path.join(args.from_json, 'xrd_plots.json')}")
        return

    if not args.manifest:
        parser.error("--manifest is required for a full run (or use --from-json)")

    with open(args.manifest) as f:
        man = json.load(f)
    man_dir = os.path.dirname(os.path.abspath(args.manifest))
    os.makedirs(args.outdir, exist_ok=True)

    print("=" * 70)
    print("Ground-state XRD + CI comparison (pymat_xrd)")
    print(f"family out: {man.get('family')}")
    print(f"2theta [{TT_MIN_DEFAULT},{TT_MAX_DEFAULT}] deg")
    print("=" * 70)

    calc = XRDCalculator(wavelength="CuKa")
    leaves = []
    for l in man["leaves"]:
        cif_full = l["cif"] if os.path.isabs(l["cif"]) else os.path.join(man_dir, l["cif"])
        grid, inten = simulate_pattern(calc, cif_full, TT_MIN_DEFAULT, TT_MAX_DEFAULT)
        pf = peak_fraction_ci(grid, inten)
        ic = integrated_ci(grid, inten)
        leaves.append({
            "leaf": l["leaf"],
            "P_concentration_pct": l["P_concentration_pct"],
            "formula": l["formula"],
            "E_glob_eV": l["E_glob_eV"],
            "grid": grid.tolist(),
            "intensity": inten.tolist(),
            "peak_fraction_ci": pf,
            "integrated_ci": ic,
        })
        print(f"  {l['leaf']:6s} {l['formula']:10s} P={l['P_concentration_pct']:.1f}%  "
              f"peak-fraction CI={pf:.3f}  integrated CI={ic:.3f}")

    data = {"family": man.get("family"), "leaves": leaves}

    plot_from_data(data, args.outdir)

    if args.json:
        with open(os.path.join(args.outdir, "xrd_plots.json"), "w") as f:
            json.dump(data, f, indent=1)
        print(f"  -> xrd_plots.json written to "
              f"{os.path.join(args.outdir, 'xrd_plots.json')}")

    print(f"\nDONE. figures under {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()