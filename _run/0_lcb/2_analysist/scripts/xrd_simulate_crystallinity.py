#!/usr/bin/env python3
"""
Stage 2 — XRD crystallinity: powder-XRD simulation + crystallinity index.

Runs in the **pymat_xrd** env (pymatgen + numpy/scipy/matplotlib, NO ase/AGOX).
Reads the manifest.json + windowed CIF files written by Stage 1
(xrd_extract_structures.py, run in agox_v2), simulates powder XRD for every
sampled structure in each energy window, averages the intensity per window, and
computes a crystallinity index (CI) per window.

Crystallinity metrics (both reported):
  - "peak-fraction" CI = area under resolved crystalline peaks / total area of
    the averaged pattern. Peaks are found with scipy find_peaks; each peak's
    neighbourhood extends +/-half_width in 2theta.
  - "integrated" CI   = (total - amorphous background)/total, where the
    background is a broad-running mean of the pattern (amorphous halo).

Writes, under --outdir:
  xrd_averaged_by_window.png    : overlaid window-averaged patterns
  crystallinity_vs_energy.png   : CI vs window (peak-fraction & integrated)
  crystallinity.csv             : per-window CI + count
  xrd_plots.json                : (with --json) all plotted arrays — per-window
                                  averaged 2theta grid + intensity + CI rows —
                                  for faithful re-plotting
Prints the per-window CI table to stdout for the DISCUSSION.

Usage (pymat_xrd):
  PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
  $PY_X xrd_simulate_crystallinity.py --manifest <leaf>/xrd_out/manifest.json \
        --outdir <leaf>/xrd_out [--json]
  $PY_X xrd_simulate_crystallinity.py --from-json <leaf>/xrd_out <leaf>/xrd_out
"""
from __future__ import annotations

__version__ = "1.2.0"

import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure


plt.rcParams.update({
    "font.size": 12, "font.family": "serif",
    "axes.linewidth": 1.0, "axes.edgecolor": "black",
    "figure.autolayout": True, "figure.dpi": 300,
})

TT_MIN_DEFAULT, TT_MAX_DEFAULT = 10.0, 90.0
TT_STEP = 0.02  # 2theta grid step for resampling/averaging
BROADEN_SIGMA = 0.15  # deg — Gaussian broaden each delta to mimic instrument
# energy-axis title shared with the analysis progression/landscape plots
E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"


def load_calc():
    return XRDCalculator(wavelength="CuKa")


def average_pattern(calc, cif_paths, manifest_dir, tt_min, tt_max):
    """Resample each structure's XRD onto a common 2theta grid, broaden, average."""
    grid = np.arange(tt_min, tt_max + TT_STEP, TT_STEP)
    accum = np.zeros_like(grid)
    n = 0
    for cif in cif_paths:
        full = cif if os.path.isabs(cif) else os.path.join(manifest_dir, cif)
        struct = Structure.from_file(full)
        pat = calc.get_pattern(struct, two_theta_range=(tt_min, tt_max))
        # scatter each delta onto nearest grid point then Gaussian-broaden
        inten = np.zeros_like(grid)
        for x, y in zip(pat.x, pat.y):
            gi = int(round((x - tt_min) / TT_STEP))
            if 0 <= gi < len(grid):
                inten[gi] += y
        from scipy.ndimage import gaussian_filter1d
        inten = gaussian_filter1d(inten, sigma=BROADEN_SIGMA / TT_STEP)
        accum += inten
        n += 1
    if n == 0:
        raise ValueError("no CIFs to average")
    return grid, accum / n


def peak_fraction_ci(two_theta, inten, half_width_deg=0.6):
    """CI = area in resolved-peak neighbourhoods / total area."""
    total = np.trapezoid(inten, two_theta)
    if total <= 0:
        return 0.0
    peaks, _ = find_peaks(inten, prominence=0.02 * inten.max())
    if peaks.size == 0:
        return 0.0
    half = half_width_deg
    # union of [peak-half, peak+half] intervals
    crit = np.zeros_like(two_theta, dtype=bool)
    for p in peaks:
        th = two_theta[p]
        crit |= (two_theta >= th - half) & (two_theta <= th + half)
    return float(np.trapezoid(np.where(crit, inten, 0.0), two_theta) / total)


def integrated_ci(two_theta, inten, bg_window_deg=5.0):
    """CI = (total - amorphous background)/total; background = wide running mean."""
    total = np.trapezoid(inten, two_theta)
    if total <= 0:
        return 0.0
    halfwin = max(1, int(bg_window_deg / 2 / TT_STEP))
    bg = uniform_filter1d(inten, size=2 * halfwin + 1, mode="nearest")
    return float(np.trapezoid(np.maximum(inten - bg, 0.0), two_theta) / total)


# ---------------------------------------------------------------------------
# Plot-from-data helpers (shared by a live run and --from-json)
# ---------------------------------------------------------------------------
def plot_patterns_from_data(data, outdir):
    """Draw xrd_averaged_by_window.png from a plots-data dict."""
    leaf = data["leaf"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    cmap = plt.get_cmap("viridis")
    centers = [w["center"] for w in data["windows"] if w["grid"]]
    vmin, vmax = min(centers), max(centers)
    for w in data["windows"]:
        if not w["grid"]:
            continue
        color = cmap((w["center"] - vmin) / (vmax - vmin + 1e-9)) if vmax > vmin else "C0"
        ax.plot(w["grid"], w["intensity"], lw=1.1, color=color, label=w["label"])
    ax.set_xlabel(r"2$\theta$ (deg)"); ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(f"{leaf} — averaged XRD per energy window (eV/atom)")
    ax.legend(title="window [eV/atom]", fontsize=8, ncol=2, loc="upper left")
    fig.savefig(os.path.join(outdir, "xrd_averaged_by_window.png"))
    plt.close(fig)


def plot_ci_from_data(data, outdir):
    """Draw crystallinity_vs_energy.png from a plots-data dict."""
    leaf = data["leaf"]
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [r["center"] for r in data["rows"]]
    ax.plot(xs, [r["peak_fraction_ci"] for r in data["rows"]], "o-",
            label="peak-fraction CI")
    ax.plot(xs, [r["integrated_ci"] for r in data["rows"]], "s--",
            label="integrated CI")
    ax.set_xlabel(E_LABEL); ax.set_ylabel("Crystallinity index")
    ax.set_title(f"{leaf}")
    ax.set_xlim(0, data.get("e_max", 0.5))
    ax.legend()
    fig.savefig(os.path.join(outdir, "crystallinity_vs_energy.png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="XRD stage 2 (pymat_xrd): simulate + average powder XRD per "
                    "energy window and compute crystallinity indices.")
    parser.add_argument("--manifest", default=None,
                        help="path to Stage-1 manifest.json (required for a full "
                             "run; ignored with --from-json)")
    parser.add_argument("--outdir", required=True,
                        help="output dir for figures + crystallinity.csv")
    parser.add_argument("--2theta-min", type=float, default=TT_MIN_DEFAULT)
    parser.add_argument("--2theta-max", type=float, default=TT_MAX_DEFAULT)
    parser.add_argument("--json", action="store_true",
                        help="also write xrd_plots.json with every plotted array "
                             "(per-window 2theta grid + intensity + CI rows) for "
                             "faithful re-plotting via --from-json")
    parser.add_argument("--from-json", default=None,
                        help="skip simulation; read xrd_plots.json from this dir and "
                             "re-draw both PNGs into --outdir")
    args = parser.parse_args()

    # --- from-json mode: replot both XRD PNGs from stored arrays -----------
    if args.from_json:
        jp = os.path.join(args.from_json, "xrd_plots.json")
        with open(jp) as f:
            data = json.load(f)
        os.makedirs(args.outdir, exist_ok=True)
        plot_patterns_from_data(data, args.outdir)
        plot_ci_from_data(data, args.outdir)
        print(f"\nDONE. Re-plotted XRD PNGs from {jp} -> {os.path.abspath(args.outdir)}")
        return

    if not args.manifest:
        parser.error("--manifest is required for a full run (or use --from-json)")

    with open(args.manifest) as f:
        man = json.load(f)
    leaf = man["leaf"]
    man_dir = os.path.dirname(os.path.abspath(args.manifest))
    os.makedirs(args.outdir, exist_ok=True)

    print("=" * 70)
    print("XRD Stage 2 (pymat_xrd) — powder XRD + crystallinity index")
    print(f"leaf: {leaf}  comp={man['composition']}  e_glob={man['e_glob']:.3f} eV")
    print(f"2theta [{getattr(args,'2theta_min'):g},{getattr(args,'2theta_max'):g}] deg")
    print("=" * 70)

    calc = load_calc()
    rows = []
    patterns = []
    for w in man["windows"]:
        if w["n_sampled"] == 0:
            continue
        grid, avg = average_pattern(calc, w["cifs"], man_dir,
                                    getattr(args, "2theta_min"),
                                    getattr(args, "2theta_max"))
        pf = peak_fraction_ci(grid, avg)
        ic = integrated_ci(grid, avg)
        center = (w["lo"] + w["hi"]) / 2
        rows.append({"window": w["label"], "center": center,
                     "n": w["n_sampled"], "peak_fraction_ci": pf,
                     "integrated_ci": ic})
        patterns.append({"label": w["label"], "center": center,
                         "grid": grid.tolist(), "intensity": avg.tolist()})
        print(f"  window {w['label']:10s} n={w['n_sampled']:4d}  "
              f"peak-fraction CI={pf:.3f}  integrated CI={ic:.3f}")

    if not rows:
        raise SystemExit("no populated windows")

    data = {
        "leaf": leaf,
        "e_max": man["e_max"],
        "composition": man["composition"],
        "rows": rows,
        "windows": patterns,
    }

    # ---- figures (shared plot-from-data helpers) ----
    plot_patterns_from_data(data, args.outdir)
    plot_ci_from_data(data, args.outdir)

    # ---- CSV ----
    import csv
    csv_path = os.path.join(args.outdir, "crystallinity.csv")
    with open(csv_path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader(); wr.writerows(rows)

    # ---- optional JSON dump ----
    if args.json:
        jp = os.path.join(args.outdir, "xrd_plots.json")
        with open(jp, "w") as f:
            json.dump(data, f, indent=1)
        print(f"  -> xrd_plots.json written to {jp}")

    print(f"\nDONE. figures + {csv_path} under {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
