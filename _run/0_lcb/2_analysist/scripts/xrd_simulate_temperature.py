from __future__ import annotations

__version__ = "1.1.0"

import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure

plt.rcParams.update({
    "font.size": 12, "font.family": "serif",
    "axes.linewidth": 1.0, "axes.edgecolor": "black",
    "figure.autolayout": True, "figure.dpi": 300,
})

TT_MIN_DEFAULT, TT_MAX_DEFAULT = 10.0, 90.0
TT_STEP = 0.02          # 2theta grid step (deg)
BROADEN_SIGMA = 0.15    # deg Gaussian broadening per reflection (instrument)
KB = 8.6173e-5          # eV/K (Boltzmann)
TEMPS_DEFAULT = [298.15, 348.60, 447.875, 547.15, 646.425]  # matches Stage-3 TEMPS
E_LABEL = r"$\Delta E$ (eV/atom)"


def xrd_temperature_description(leaf, composition, temps, e_max):
    """Self-describing 'description' embedded in xrd_temperature.json."""
    return {
        "kind": "Temperature-dependent simulated powder XRD of one fixed-"
                "composition AGOX leaf via a Boltzmann thermal-ensemble average",
        "schema": "0_lcb_xrd_simulate_temperature/v1",
        "leaf": leaf,
        "composition": composition,
        "e_max": e_max,
        "method": (
            "For every sampled DFT-relaxed structure read from the Stage-1 "
            "manifest, pymatgen XRDCalculator (Cu K-alpha, scaled=False true "
            "relative intensity) on a 2theta grid of step 0.02 deg, each "
            "reflection Gaussian-broadened with sigma 0.15 deg. Thermal pattern "
            "at T: I(2T;T) = sum_i w_i(T)*I_i(2T) / sum_i w_i(T), with "
            "w_i(T)=exp(-DeltaE_i/(kB*T)), DeltaE_i = per-atom relative energy "
            "(E_i-E_glob)/N from the manifest rel_energies, kB=8.6173e-5 eV/K."
        ),
        "energy_units": "rel_energies and mean_rel are eV/atom",
        "units": {
            "grid": "two-theta angle in degrees",
            "intensity": "true relative diffracted intensity (a.u.), weighted "
                         "mean over the sampled ensemble at that T (comparable "
                         "across T: not rescaled to max=1)",
            "T": "temperature in Kelvin",
            "mean_rel": "population-weighted mean relative energy <E>(T) in eV/atom",
        },
        "fields": {
            "series": "one entry per T: T (K), grid = 2theta (deg), "
                      "intensity = Boltzmann-averaged pattern at T, mean_rel = "
                      "population-weighted mean relative energy (eV/atom), "
                      "n = number of sampled structures contributing",
            "num_sampled": "total sampled structures read from the manifest",
            "e_max": "relative-energy cutoff (eV/atom) applied upstream "
                     "(xrd_extract_structures --e-max)",
        },
    }


def load_calc():
    return XRDCalculator(wavelength="CuKa")


def structure_pattern(calc, cif_path, manifest_dir, tt_min, tt_max, grid):
    """Return the Gaussian-broadened intensity array of one CIF on ``grid``."""
    full = cif_path if os.path.isabs(cif_path) else os.path.join(manifest_dir, cif_path)
    struct = Structure.from_file(full)
    pat = calc.get_pattern(struct, two_theta_range=(tt_min, tt_max), scaled=False)
    inten = np.zeros_like(grid)
    for x, y in zip(pat.x, pat.y):
        gi = int(round((x - tt_min) / TT_STEP))
        if 0 <= gi < len(grid):
            inten[gi] += y
    from scipy.ndimage import gaussian_filter1d
    return gaussian_filter1d(inten, sigma=BROADEN_SIGMA / TT_STEP)


def collect_from_manifest(manifest_path, tt_min, tt_max):
    """Flatten every window's sampled (cif, rel_energy) pairs; compute XRD once."""
    with open(manifest_path) as f:
        man = json.load(f)
    man_dir = os.path.dirname(os.path.abspath(manifest_path))
    grid = np.arange(tt_min, tt_max + TT_STEP, TT_STEP)
    calc = load_calc()
    rel_energies, patterns = [], []
    for w in man["windows"]:
        for cif, relE in zip(w.get("cifs", []), w.get("rel_energies", [])):
            patterns.append(structure_pattern(calc, cif, man_dir, tt_min, tt_max, grid))
            rel_energies.append(relE)
    if not patterns:
        raise SystemExit("manifest has no sampled structures")
    return man, grid, np.asarray(rel_energies), patterns


def thermal_average(rel_energies, patterns, T):
    """I(T) = sum_i w_i(T)*I_i / sum_i w_i(T); also returns <E>(T) and w sum."""
    w = np.exp(-rel_energies / (KB * T))
    Z = w.sum()
    num = np.zeros_like(patterns[0])
    for wi, pi in zip(w, patterns):
        num += wi * pi
    mean_rel = float((w * rel_energies).sum() / Z) if Z > 0 else float("nan")
    return num / Z, mean_rel, len(w)


def plot_from_data(data, outdir, figsize=(8, 4.5)):
    """Draw xrd_by_temperature.png from a plots-data dict (overlay per T)."""
    leaf = data["leaf"]
    w, h = figsize
    fig, ax = plt.subplots(figsize=(w, h))
    tab10 = plt.get_cmap("tab10")
    for i, s in enumerate(data["series"]):
        ax.plot(s["grid"], s["intensity"], lw=1.8,
                color=tab10(i % tab10.N), label=f"{s['T']:g} K")
    ax.set_xlabel(r"2$\theta$ (deg)"); ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(f"{leaf} — temperature-dependent XRD (Boltzmann average)")
    ax.legend(title="T", fontsize=9, ncol=2, loc="upper right")
    ax.set_xlim(data["xlim"])
    fig.savefig(os.path.join(outdir, "xrd_by_temperature.png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Stage 2 (pymat_xrd): temperature-dependent powder XRD via "
                    "Boltzmann thermal-ensemble average over a leaf's sampled "
                    "structures (reads a Stage-1 manifest).")
    parser.add_argument("--manifest", required=True,
                        help="path to Stage-1 manifest.json (xrd_extract_structures.py)")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--2theta-min", type=float, default=TT_MIN_DEFAULT)
    parser.add_argument("--2theta-max", type=float, default=TT_MAX_DEFAULT)
    parser.add_argument("--temps", type=float, nargs="*", default=None,
                        help="temperatures in K; default matches Stage-3 TEMPS "
                             f"{TEMPS_DEFAULT}")
    parser.add_argument("--json", action="store_true",
                        help="also write xrd_temperature.json (self-describing)")
    parser.add_argument("--figsize", default="8,4.5",
                        help="figure size 'W,H' in inches (default 8,4.5)")
    args = parser.parse_args()
    args.figsize = tuple(float(x) for x in args.figsize.split(","))

    temps = list(args.temps) if args.temps else list(TEMPS_DEFAULT)
    os.makedirs(args.outdir, exist_ok=True)
    man, grid, rel_energies, patterns = collect_from_manifest(
        args.manifest, getattr(args, "2theta_min"), getattr(args, "2theta_max"))
    leaf = man["leaf"]
    composition = man.get("composition", {})
    e_max = man.get("e_max")

    print("=" * 70)
    print("XRD Stage 2 (pymat_xrd) — temperature-dependent XRD (Boltzmann average)")
    print(f"leaf: {leaf}  comp={composition}  n_sampled={len(patterns)}")
    print(f"T(K): {temps}")
    print("=" * 70)

    series = []
    for T in temps:
        iten, mean_rel, n = thermal_average(rel_energies, patterns, T)
        series.append({"T": T,
                       "grid": grid.tolist(),
                       "intensity": iten.tolist(),
                       "mean_rel": mean_rel,
                       "n": n})
        print(f"  T={T:8.3f} K   <E>(T)={mean_rel:+.4f} eV/atom   (n={n})")

    data = {"leaf": leaf, "composition": composition,
            "e_max": e_max, "num_sampled": len(patterns),
            "xlim": [getattr(args, "2theta_min"), getattr(args, "2theta_max")],
            "series": series}
    plot_from_data(data, args.outdir, figsize=args.figsize)

    if args.json:
        out = dict(data)
        out["description"] = xrd_temperature_description(leaf, composition,
                                                         temps, e_max)
        jp = os.path.join(args.outdir, "xrd_temperature.json")
        with open(jp, "w") as f:
            json.dump(out, f, indent=1)
        print(f"  -> xrd_temperature.json written to {jp}")

    print(f"\nDONE. figures under {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
