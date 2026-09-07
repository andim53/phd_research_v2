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

__version__ = "2.1.2"

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


def gs_compare_description(family):
    """Self-describing 'description' block embedded in the emitted xrd_plots.json.

    Lets a downstream AI agent interpret the file (method, units, per-field
    legend) without knowing this working directory.
    """
    return {
        "kind": "Ground-state powder-XRD comparison across dopant concentrations "
                "for one amorphous interstitial-alloy family",
        "schema": "0_lcb_xrd_groundstate_compare/v1",
        "family": family,
        "method": "pymatgen XRDCalculator (Cu K-alpha) per leaf's single "
                  "global-ground-state (rel-E = 0) structure, 2theta grid step "
                  "0.02 deg, each reflection Gaussian-broadened sigma 0.15 deg",
        "intensity_scaling": "scaled=False (true relative intensity)",
        "units": {
            "leaves[].grid": "two-theta angle in degrees",
            "leaves[].intensity": "true relative diffracted intensity (a.u.)",
            "leaves[].concentration_pct": "interstitial dopant concentration in "
                                          "atom percent",
            "leaves[].E_glob_eV": "global ground-state total energy in eV",
        },
        "fields": {
            "leaves": "one record per concentration leaf of the family: the "
                      "ground-state (lowest-energy, rel-E = 0) simulated powder "
                      "pattern plus composition (host/interstitial symbols, atom "
                      "counts), formula, concentration %, E_glob, and the two "
                      "crystallinity indices peak_fraction_ci / integrated_ci",
            "leaves[].peak_fraction_ci": "area in resolved-peak neighbourhoods / "
                                         "total area",
            "leaves[].integrated_ci": "(total - amorphous running-mean "
                                      "background)/total",
        },
    }


def simulate_pattern(calc, cif_path, tt_min, tt_max):
    """Simulate a structure's powder XRD on a common 2theta grid and Gaussian-broaden."""
    grid = np.arange(tt_min, tt_max + TT_STEP, TT_STEP)
    struct = Structure.from_file(cif_path)
    pat = calc.get_pattern(struct, two_theta_range=(tt_min, tt_max), scaled=False)
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


def _conc_key(l):
    """Return the concentration (%) from a leaf record, supporting both the
    element-agnostic 'concentration_pct' and legacy 'P_concentration_pct'."""
    return l.get("concentration_pct", l.get("P_concentration_pct", 0.0))


_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _formula_label(l, inter):
    """Legend label like 'Ta₅₄B₀ (0.0% B)' for a leaf record.

    ``inter`` is the comparison-wide interstitial symbol (e.g. 'B'), so even a
    pure-host leaf (0 interstitial) renders as, e.g., 'Ta₅₄B₀ (0.0% B)'.
    """
    host = l.get("host_symbol", "")
    nh = l.get("n_host", 0)
    ni = l.get("n_interstitial", 0)
    formula = f"{host}{str(nh).translate(_SUB)}"
    if inter:
        formula += f"{inter}{str(ni).translate(_SUB)}"
    inter_lab = inter or host
    return f"{formula} ({_conc_key(l):.1f}% {inter_lab})"


def plot_from_data(data, outdir, figsize=(8, 4.5)):
    """Draw both comparison PNGs from a data dict (live run or JSON)."""
    leaves = data["leaves"]
    family = data.get("family", "")
    fam_base = os.path.basename(family.rstrip("/")) if family else ""
    # interstitial symbol: use the first leaf that actually has one (a pure-host
    # first leaf, e.g. 7_fxg_0b Ta-only, must not mislabel the whole plot); fall
    # back to the host symbol if none have an interstitial.
    inter = next((l.get("interstitial_symbol") for l in leaves
                  if l.get("interstitial_symbol")), None) or "X"
    # --- Figure 1: overlaid ground-state XRD patterns ---
    w, h = figsize
    fig, ax = plt.subplots(figsize=(w, h))
    cmap = plt.get_cmap("tab10")
    ordered = sorted((l for l in leaves if l["grid"]),
                     key=lambda l: _conc_key(l))
    for i, l in enumerate(ordered):
        ax.plot(l["grid"], l["intensity"], lw=1.8,
                color=cmap(i % cmap.N), label=_formula_label(l, inter))
    # cmap = plt.get_cmap("viridis")
    # concs = [_conc_key(l) for l in leaves]
    # vmin, vmax = min(concs), max(concs)
    # for l in leaves:
    #     if not l["grid"]:
    #         continue
    #     color = cmap((_conc_key(l) - vmin) / (vmax - vmin + 1e-9)) \
    #         if vmax > vmin else "C0"
    #     ax.plot(l["grid"], l["intensity"], lw=1.1, color=color,
    #             label=_formula_label(l, inter))
    ax.set_xlabel(r"2$\theta$ (deg)"); ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(f"Ground-state XRD — {fam_base} (per {inter} concentration)")
    ax.legend(title=f"{inter} concentration", fontsize=8, ncol=2, loc="upper right")
    fig.savefig(os.path.join(outdir, "xrd_averaged_by_window.png"))
    plt.close(fig)

    # --- Figure 2: CI vs interstitial concentration ---
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [_conc_key(l) for l in leaves]
    ax.plot(xs, [l["peak_fraction_ci"] for l in leaves], "o-",
            label="peak-fraction CI")
    ax.plot(xs, [l["integrated_ci"] for l in leaves], "s--",
            label="integrated CI")
    ax.set_xlabel(f"{inter} concentration (%)"); ax.set_ylabel("Crystallinity index")
    ax.set_title(f"Ground-state crystallinity vs {inter} content ({fam_base})")
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
    parser.add_argument("--figsize", default="8,4.5",
                        help="overlay figure size 'W,H' in inches (default 8,4.5)")
    args = parser.parse_args()
    args.figsize = tuple(float(x) for x in args.figsize.split(","))

    if args.from_json:
        with open(os.path.join(args.from_json, "xrd_plots.json")) as f:
            data = json.load(f)
        os.makedirs(args.outdir, exist_ok=True)
        plot_from_data(data, args.outdir, figsize=args.figsize)
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
            "concentration_pct": _conc_key(l),
            "interstitial_symbol": l.get("interstitial_symbol", "X"),
            "host_symbol": l.get("host_symbol", ""),
            "n_host": l.get("n_host", 0),
            "n_interstitial": l.get("n_interstitial", 0),
            "formula": l["formula"],
            "E_glob_eV": l["E_glob_eV"],
            "grid": grid.tolist(),
            "intensity": inten.tolist(),
            "peak_fraction_ci": pf,
            "integrated_ci": ic,
        })
        inter = l.get("interstitial_symbol", "X")
        print(f"  {l['leaf']:6s} {l['formula']:10s} {inter}={_conc_key(l):.1f}%  "
              f"peak-fraction CI={pf:.3f}  integrated CI={ic:.3f}")

    data = {"family": man.get("family"), "leaves": leaves,
            "description": gs_compare_description(man.get("family"))}

    plot_from_data(data, args.outdir, figsize=args.figsize)

    if args.json:
        with open(os.path.join(args.outdir, "xrd_plots.json"), "w") as f:
            json.dump(data, f, indent=1)
        print(f"  -> xrd_plots.json written to "
              f"{os.path.join(args.outdir, 'xrd_plots.json')}")

    print(f"\nDONE. figures under {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
