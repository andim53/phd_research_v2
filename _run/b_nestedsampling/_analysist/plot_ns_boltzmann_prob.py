#!/usr/bin/env python3
"""
Plot the Boltzmann probability P(E) vs per-atom relative energy for a
temperature-free nested-sampling (NS) run, using the NS result.

For each temperature T (100, 200, 300, 500, 1000 K) the probability on a smooth
energy grid E is

    P(E, T) = g(E) * exp(-beta*(E - E_ref)) / Z(T)

where:
  - g(E)   = the KDE-smoothed NS state density (prior-weight-weighted gaussian
             KDE of the samples.csv energies), same as the NS g(E) smoothed with
             KDE in compare_state_density_gE.py,
  - beta   = 1/(k_B T),
  - E_ref  = min sample energy (per-atom relative energy = (E - E_ref)/n_atoms),
  - Z(T)   = sum_E g(E) * exp(-beta*(E - E_ref))  (partition function from g(E)).

This multiplies by g(E) and divides by the total Z from g(E), matching the
reference `analysis_indices/binding_probability_vs_temperature.png` (which uses
rho(E) = gaussian KDE) but with the NS KDE-smoothed g(E) as rho. Energies are
plotted as per-atom relative energy (E - E_ref)/n_atoms.

Usage (needs numpy + scipy + matplotlib + agox_v2 for load_samples):
  /home/think/miniconda3/envs/agox_v2/bin/python plot_ns_boltzmann_prob.py \
      --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outdir  b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outname binding_probability_vs_temperature.png \
      --n-atoms 75
"""

from __future__ import annotations

__version__ = "1.6.0"

import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects
from scipy.integrate import trapezoid
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde

import analyze_tfree_outputs as ato  # reuse load_samples

# --- Plotting style: same rcParams as the reference pipeline ---
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

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"   # matches the other analyses
K_B = 8.617333262e-5                       # eV/K


def load_dataset_energies(dataset_dir: str):
    """Load + filter dataset DFT energies from seed DBs (mirrors compare_state_density_gE.py)."""
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


def load_dataset_structures(dataset_dir: str, start_iter: int = 10):
    """Load dataset structures + energies with AGOX iteration >= start_iter (mirrors
    compare_state_density_gE.py), needed for the PCA delta-Z island/flat detection."""
    from agox.databases import Database
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
    return structures, np.asarray(energies, dtype=float)


def delta_z_fe(atoms) -> float:
    """Fe island height delta Z = max(Fe z) - min(Fe z), in Angstrom (mirrors
    compare_state_density_gE.py). Uses only Fe atoms."""
    pos = atoms.get_positions()
    sym = atoms.get_chemical_symbols()
    fe = [i for i, s in enumerate(sym) if s == "Fe"]
    if not fe:
        return np.nan
    z = pos[fe, 2]
    return float(z.max() - z.min())


def delta_z_island_flat(structures, energies, n_atoms, e_max=0.8):
    """Locate island/flat energies from the actual PCA delta-Z data:
    bin the dataset structures by per-atom relative energy and compute the mean relative
    delta-Z in each bin; island = low-energy bin (< 0.1 eV/atom) with HIGHEST mean delta-Z;
    flat = ~0.2 eV/atom region (0.15-0.30) bin with LOWEST mean delta-Z. Mirrors
    compare_state_density_gE.py --delta-z-lines."""
    e_rel = (np.asarray(energies, dtype=float) - np.asarray(energies).min()) / n_atoms
    z_data = np.array([delta_z_fe(s) for s in structures])
    z_data = z_data - np.nanmin(z_data)          # relative delta Z (Angstrom)
    nz_bins = 60
    dz_bins = np.linspace(0, e_max, nz_bins)
    dz_centers = 0.5 * (dz_bins[:-1] + dz_bins[1:])
    ok = ~np.isnan(z_data)
    E_bin, Z_bin = e_rel[ok], z_data[ok]
    mean_dz = np.full(len(dz_centers), np.nan)
    for k in range(len(dz_centers)):
        sel = (E_bin >= dz_bins[k]) & (E_bin < dz_bins[k + 1])
        if sel.sum() > 0:
            mean_dz[k] = Z_bin[sel].mean()
    # island: within E < 0.1 eV/atom, highest mean delta-Z
    low_mask = dz_centers < 0.1
    if low_mask.sum() and np.isfinite(np.where(low_mask, mean_dz, np.nan)).any():
        k_island = int(np.nanargmax(np.where(low_mask, mean_dz, -np.inf)))
        island_e = float(dz_centers[k_island])
        island_dz = float(mean_dz[k_island])
    else:
        island_e, island_dz = 0.074, np.nan
    # flat: near ~0.2 eV/atom (0.15-0.30), lowest mean delta-Z
    flat_mask = (dz_centers >= 0.15) & (dz_centers <= 0.30)
    if flat_mask.sum() and np.isfinite(np.where(flat_mask, mean_dz, np.nan)).any():
        k_flat = int(np.nanargmin(np.where(flat_mask, mean_dz, np.inf)))
        flat_e = float(dz_centers[k_flat])
        flat_dz = float(mean_dz[k_flat])
    else:
        flat_e, flat_dz = 0.255, np.nan
    return island_e, island_dz, flat_e, flat_dz


def main():
    p = argparse.ArgumentParser(
        description="Plot NS Boltzmann probability P(E) vs relative energy at several T")
    p.add_argument("--ns-output", required=True,
                   help="ns_output dir containing samples.csv (the NS run's output)")
    p.add_argument("--dataset", default=None,
                   help="dataset dir (contains seed_*/1_db/db_*.db) to compute the "
                        "KDE state density and find the flat/island peaks. If omitted, "
                        "the flat/island dashed lines are not drawn.")
    p.add_argument("--delta-z-lines", action="store_true",
                   help="locate the island/flat dashed lines from the dataset PCA delta-Z "
                        "data (bin dataset structures by per-atom energy; island = low-energy "
                        "bin < 0.1 eV/atom with highest mean delta-Z; flat = 0.15-0.30 eV/atom "
                        "bin with lowest mean delta-Z), like compare_state_density_gE.py "
                        "--delta-z-lines. Default off: use the dataset KDE peaks.")
    p.add_argument("--outdir", required=True,
                   help="output dir for the PNG")
    p.add_argument("--outname", default="binding_probability_vs_temperature.png",
                   help="output filename (default binding_probability_vs_temperature.png)")
    p.add_argument("--n-atoms", type=int, default=75,
                   help="atoms per structure, for the per-atom relative energy (eV/atom). "
                        "Default 75 (Fe/MgO).")
    p.add_argument("--temperatures", type=float, nargs="+",
                   default=[100, 200, 300, 500, 1000],
                   help="temperatures (K) to plot. Default 100 200 300 500 1000.")
    p.add_argument("--area-norm", action="store_true",
                   help="normalize each temperature curve so its area (integral over energy) "
                        "= 1 via the trapezoidal rule (like Making_Prob_area_norm.py), "
                        "instead of peak-normalizing. y-label 'Probability Density (Area = 1)'.")
    p.add_argument("--linewidth", type=float, default=1.6,
                   help="line thickness of the P(E) temperature curves. Default 1.6.")
    p.add_argument("--figsize", type=float, default=5,
                   help="figure size in inches (square: width=height=this value). "
                        "Default 5.")
    p.add_argument("--legend-loc", default="upper right",
                   help="legend location (matplotlib loc string, e.g. 'upper left'). "
                        "Default 'upper right'.")
    p.add_argument("--legend-label", default="{T} K {ref}",
                   help="legend label format template. Placeholders: {T} = temperature, "
                        "{ref} = [N] reference marker (empty if none). "
                        "Default '{T} K {ref}'.")
    p.add_argument("--annotate-critical", action="store_true",
                   help="annotate each temperature curve with its [N] reference marker "
                        "(critical fabrication temperatures).")
    args = p.parse_args()

    # --- [N] reference map for the critical fabrication temperatures (from the
    # b10 iter20000 DISCUSSION.md section 9 temperature discussion) ---
    CRITICAL_REF = {
        298.0: "[1]",    # Fe/FeCo deposition, no heating (Scheike 2022)
        573.0: "[2]",    # CoFeB/MgO annealing 473-573 K (Marnitz 2015)
        623.0: "[3]",    # CoFeB/MgO optimization point (Kim 2023)
        673.0: "[4]",    # CoFeB/MgO annealing limit (Lv 2019)
        773.0: "[5]",    # In situ barrier crystallization / oxidation (Narayananellore 2017)
    }

    # --- load NS samples (energy_eV + prior_weight) ---
    iters, Es, Ws = ato.load_samples(os.path.join(args.ns_output, "samples.csv"))
    print(f"  NS samples: {Es.size}")

    E_ref = Es.min()
    rel = (Es - E_ref) / args.n_atoms           # per-atom relative energy (eV/atom)

    # --- KDE-smoothed NS state density g(E) (prior-weight-weighted) ---
    ns_kde = gaussian_kde(rel, weights=Ws)       # same as the NS g(E) KDE in compare_state_density_gE.py
    grid = np.linspace(0, rel.max() + 0.02, 400)
    gE = ns_kde.evaluate(grid)                   # config./eV

    # --- flat/island energies (dataset KDE peaks by default, or PCA delta-Z with flag) ---
    flat_e, island_e = None, None
    if args.dataset is not None and args.delta_z_lines:
        # PCA delta-Z-derived (like compare_state_density_gE.py --delta-z-lines)
        structs, ds_energies = load_dataset_structures(args.dataset, start_iter=10)
        island_e, island_dz, flat_e, flat_dz = delta_z_island_flat(
            structs, ds_energies, args.n_atoms, e_max=0.8)
        print(f"  [--delta-z-lines] dataset: {len(structs)} structures (iteration >= 10)")
        print(f"  delta-Z-derived island = {island_e:.3f} eV/atom (mean dZ {island_dz:.3f} A) | "
              f"flat = {flat_e:.3f} eV/atom (mean dZ {flat_dz:.3f} A)")
    elif args.dataset is not None:
        # dataset KDE peaks (default)
        ds_energies = load_dataset_energies(args.dataset)
        ds_rel = (ds_energies - ds_energies.min()) / args.n_atoms
        ds_kde = gaussian_kde(ds_rel)
        ds_grid = np.linspace(0, ds_rel.max() + 0.02, 400)
        ds_density = ds_kde.evaluate(ds_grid)
        ds_peaks, _ = find_peaks(ds_density, prominence=np.max(ds_density) * 0.05)
        peak_es = np.sort(ds_grid[ds_peaks])     # ascending energy
        if len(peak_es) >= 2:
            island_e, flat_e = peak_es[0], peak_es[1]   # lowest = island, next = flat
        elif len(peak_es) == 1:
            island_e = peak_es[0]
        print(f"  dataset KDE peaks (eV/atom): {peak_es.round(4).tolist()}")
        print(f"  island={island_e:.4f}, flat={flat_e:.4f}" if flat_e is not None
              else f"  island={island_e:.4f} (no flat peak)")

    fig, ax = plt.subplots(figsize=(args.figsize, args.figsize))
    # colors: a perceptually ordered set for the temperatures
    colors = ["#0d0887", "#47039f", "#7301a8", "#9c176d", "#bd3752",
              "#d8546a", "#ed7953", "#fb9f4a", "#fdca42", "#f0f928"]

    print("=" * 60)
    print("NS Boltzmann probability (g(E) * exp(-beta*E) / Z from g(E))")
    print("=" * 60)
    max_display = 0.0
    for i, T in enumerate(args.temperatures):
        beta = 1.0 / (K_B * T)
        # P(E,T) = g(E)*exp(-beta*(E-E_ref))/Z, Z = sum_E g(E)*exp(-beta*(E-E_ref))
        log_num = np.log(np.maximum(gE, 1e-300)) - beta * (grid - grid.min())
        log_Z = np.log(np.sum(np.exp(log_num)))
        probs = np.exp(log_num - log_Z)          # P(E,T), normalized over the grid
        # Normalize for display: peak-normalize (default) OR area-normalize (--area-norm)
        if args.area_norm:
            area = trapezoid(probs, grid)
            probs_plot = probs / area if area > 0 else probs   # area (integral) = 1
        else:
            probs_plot = probs / probs.max()     # peak = 1
        max_display = max(max_display, probs_plot.max())
        # legend label via the configurable template: {T}=bare temperature, {ref}=[N] marker (or empty)
        ref = CRITICAL_REF[T] if (args.annotate_critical and T in CRITICAL_REF) else ""
        label = args.legend_label.format(T=f"{T}", ref=ref)
        ax.plot(grid, probs_plot, color=colors[i % len(colors)],
                lw=args.linewidth, label=label)
        print(f"  T={T:6.1f} K  Z={np.exp(log_Z):.4e}  max P={probs.max():.3e}")

    # dashed vertical lines at the flat/island energies (black, white outline)
    for note_e, note_txt in [(flat_e, "flat"), (island_e, "island")]:
        if note_e is not None:
            ln = ax.axvline(note_e, color="black", linestyle="--", lw=1.2, alpha=0.6)
            ln.set_path_effects([patheffects.withStroke(linewidth=2.5, foreground="white")])
            t = ax.text(note_e, 0.05, note_txt, color="black", fontsize=8,
                        ha="left", va="bottom", rotation=90)
            t.set_path_effects([patheffects.withStroke(linewidth=2, foreground="white")])

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability Density (Area = 1)" if args.area_norm
                  else "Probability P(E) (peak-normalized)")
    # Auto-scale the y-axis to the tallest curve in area-norm mode (peaks can be >>1);
    # keep the 0-1.05 headroom for the default peak-normalized mode.
    if args.area_norm:
        ax.set_ylim(0, 1.05 * max_display)
    else:
        ax.set_ylim(0, 1.05)
    ax.set_xlim(0, grid.max())
    leg = ax.legend(frameon=False, loc=args.legend_loc, fontsize=9)
    # white outline on the legend text (patheffects.withStroke)
    for t in leg.get_texts():
        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground="white")])

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")
    print(f"  n_atoms = {args.n_atoms}; temperatures = {args.temperatures}")


if __name__ == "__main__":
    main()
