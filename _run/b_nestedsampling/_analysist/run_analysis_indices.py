#!/usr/bin/env python3
"""
Unified AGOX analysis for the GPR+LCB-only dataset (e.g. b11 boron seed DBs).

Adapted from `_archive/_analysist/run_analysis_indices.py` for the b_nestedsampling
project's flat dataset layout. Instead of an index/folder map + Stage-1 DB
processing, this loads ALL seed databases directly (like main.py's load_all_seeds)
and runs the same analyses:

  Stage 1 — Best-so-far progression plot (per-seed, like process_database.py's
            plot_best_so_far -> progression_seed_split_<idx>.png).
  Stage 2 — Landscape analysis & evaluation (scripts/plot_structure_landscape.py):
            PCA landscape (Fingerprint PC1) + per-atom KDE state density.
  Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z), vs T.

Produces, under <outdir>:
  progression_plots/progression_seed_split_0.png   (Stage 1 best-so-far progression)
  conf_space.png                          (Stage 2 landscape + state density)
  binding_probability_vs_temperature.png  (Stage 3 Boltzmann P(T))

Usage (needs agox_v2 conda env for AGOX Fingerprint + ASE + scipy):
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
      --dataset b11_boron_walk_emax04_exclworst_noxsf_novelty/dataset \
      --outdir b11_boron_walk_emax04_exclworst_noxsf_novelty/analysis_indices \
      [--e-max 0.8] [--normalize-density]
"""

from __future__ import annotations

__version__ = "1.3.1"

import argparse
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from ase.io import write as ase_write
from scipy.stats import gaussian_kde

# --- paths: make the self-contained scripts/ importable ----------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from scripts.plot_structure_landscape import plot_structure_landscape

# ---------------------------------------------------------------------------
# Plotting style — same rcParams as the reference pipeline
# ---------------------------------------------------------------------------
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

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"
E_LIMIT_DEFAULT = (0.0 - 0.1, 1.5 + 0.1, 5)

# --- Temperatures & colours (mirrors the reference Stage 3) -----------------
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
COLORS_PLASMA = ['#0d0887', '#47039f', '#7301a8', '#9c176d', '#bd3752',
                 '#d8546a', '#ed7953', '#fb9f4a', '#fdca42', '#f0f928']


# ---------------------------------------------------------------------------
# Data loading — all seed DBs -> structures + DFT energies
# ---------------------------------------------------------------------------
def load_all_seeds(dataset_dir: str, start_iter: int = 10):
    """Load every structure/energy from dataset/seed_*/1_db/db_*.db, keeping only
    structures with AGOX iteration >= start_iter (inclusive), mirroring
    process_database.py's start_iter filter (get_all_structures_data()['iteration'])."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    structures, energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        # mirror process_database.py: read raw structure dicts, filter by iteration
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        atoms_list = [db.db_to_atoms(d) for d in kept]
        structures.extend(atoms_list)
        energies.extend(a.get_potential_energy() for a in atoms_list)
        print(f"  {os.path.relpath(p)}: {len(atoms_list)}/{len(raw)} structures "
              f"(iteration >= {start_iter})")
    energies = np.asarray(energies, dtype=float)
    return structures, energies


def load_all_seeds_by_seed(dataset_dir: str, start_iter: int = 10):
    """Load per-seed structures + energies from dataset/seed_*/1_db/db_*.db,
    filtered by iteration >= start_iter. Returns an ordered dict
    {seed_label: (structures, energies)} plus the flattened structures/energies."""
    from collections import OrderedDict
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    seed_data = OrderedDict()
    all_structs, all_energies = [], []
    for i, p in enumerate(db_paths):
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        atoms_list = [db.db_to_atoms(d) for d in kept]
        e_list = np.asarray([a.get_potential_energy() for a in atoms_list], dtype=float)
        seed_data[f"Seed {i}"] = (atoms_list, e_list)
        all_structs.extend(atoms_list)
        all_energies.extend(e_list)
        print(f"  {os.path.relpath(p)}: {len(atoms_list)}/{len(raw)} structures "
              f"(iteration >= {start_iter})")
    return seed_data, all_structs, np.asarray(all_energies, dtype=float)


# ---------------------------------------------------------------------------
# Stage 1 — Best-so-far progression plot (per-seed)
# ---------------------------------------------------------------------------
def step1_progression(dataset_dir, outdir, start_iter=10, e_max=None):
    """Per-seed best-so-far relative-energy-per-atom progression plot, mirroring
    _archive/_analysist/scripts/process_database.py's plot_best_so_far (the source
    of progression_seed_split_<idx>.png). Seed 0 is highlighted in bold black on top.

    If e_max is given (eV/atom), each seed's structures are filtered to those with
    relative-energy-per-atom <= e_max (i.e. (E - seed_min)/n_atoms <= e_max), matching
    the --e-max energy cap used in Stage 2/3."""
    print("\n[STAGE 1] Best-so-far progression plot")
    from matplotlib.ticker import AutoMinorLocator

    seed_data, _, _ = load_all_seeds_by_seed(dataset_dir, start_iter=start_iter)

    # Capture Seed 0's filtered structures/energies for the bullet scatter + xsf export
    seed0_structs = None
    seed0_rel_e = None
    seed0_n = 0

    fig, ax = plt.subplots(figsize=(6, 3.5))
    max_y, max_x = 0, 0
    sorted_seed_names = list(seed_data.keys())
    cmap = plt.get_cmap("tab10")
    for i, s_name in enumerate(sorted_seed_names):
        s_structs, s_energies = seed_data[s_name]
        if not s_structs:
            continue
        # relative energy per atom within this seed (mirrors calculate_relative_energy)
        e_min = s_energies.min()
        s_rel_e_atom = np.asarray([(e - e_min) / len(a) for e, a in zip(s_energies, s_structs)])
        # apply the 0.8 eV/atom energy filter (relative to the seed min, per atom)
        if e_max is not None:
            mask = s_rel_e_atom <= e_max
            s_rel_e_atom = s_rel_e_atom[mask]
            s_structs = [a for a, m in zip(s_structs, mask) if m]
        if len(s_rel_e_atom) == 0:
            continue
        # remember Seed 0's filtered data (index 0 in sorted_seed_names) for bullets/xsf
        if i == 0:
            seed0_structs = s_structs
            seed0_rel_e = s_rel_e_atom
            seed0_n = len(s_rel_e_atom)
        s_best_so_far = np.minimum.accumulate(s_rel_e_atom)  # progressive minimum
        # highlight Seed 0 in bold black on top (reference styling)
        if i == 0:
            current_color, linewidth, zorder = "black", 2.0, 50
        else:
            current_color, linewidth, zorder = cmap((i - 1) % 10), 1.5, 1
        ax.plot(range(len(s_best_so_far)), s_best_so_far,
                label=s_name, lw=linewidth, color=current_color, zorder=zorder)
        max_y = max(max_y, np.max(s_rel_e_atom))
        max_x = max(max_x, len(s_best_so_far))

    ax.set_xlabel("Evaluated Candidates")
    ax.set_ylabel(r"$E_{i}-E_{glob}$ (eV/atom)")
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y * 1.1)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="both", top=False, right=False,
                   labeltop=False, labelright=False)
    ax.legend(loc="upper left", fontsize=9, ncol=1, frameon=True,
              bbox_to_anchor=(1.02, 1), borderaxespad=0.)
    plt.tight_layout()

    # --- Bullet scatter on Seed 0: lowest-energy candidate in each evaluated-candidate
    # window (0-20, 20-40, 40-60, 60-80), plus the global ground state. Save each as xsf. ---
    plot_dir = os.path.join(outdir, "progression_plots")
    os.makedirs(plot_dir, exist_ok=True)
    if seed0_structs is not None:
        # global minimum across ALL data (for the ground-state bullet)
        global_min_e = min(
            (energies.min() for _, (_, energies) in seed_data.items() if len(energies) > 0),
            default=None)
        gs_struct = None
        if global_min_e is not None:
            for s_name, (s_structs, s_energies) in seed_data.items():
                if len(s_energies) > 0:
                    gi = int(s_energies.argmin())
                    gs_struct = s_structs[gi]
                    break

        windows = [(0, 20), (20, 40), (40, 60), (60, 80)]
        saved = []
        for (wlo, whi) in windows:
            idxs = [j for j in range(seed0_n) if wlo <= j < whi]
            if not idxs:
                continue
            jmin = idxs[int(np.argmin(seed0_rel_e[idxs]))]  # lowest-energy candidate in window
            # bullet at (candidate_index, rel_energy_per_atom) on Seed 0: black fill, white outline
            ax.plot(jmin, seed0_rel_e[jmin], "o", ms=7, zorder=60,
                    mfc="black", mec="white", mew=1.2)
            # save the structure
            fname = os.path.join(plot_dir, f"seed0_min_w{wlo}-{whi}.xsf")
            ase_write(fname, seed0_structs[jmin])
            saved.append(fname)
        # global ground state bullet (lowest across all data), plotted at its seed-0 candidate
        # position if it is in Seed 0, else at the last candidate with its rel energy
        if global_min_e is not None and gs_struct is not None:
            # ground-state rel-energy-per-atom relative to seed0's absolute minimum
            seed0_min_abs = min(
                (energies.min() for _, (_, energies) in seed_data.items()
                 if len(energies) > 0), default=global_min_e)
            gs_rel = (global_min_e - seed0_min_abs) / len(gs_struct)
            # locate the nearest seed-0 candidate index to the ground-state energy
            gs_x = seed0_n - 1
            if len(seed0_rel_e) > 0:
                gs_x = int(np.argmin(np.abs(seed0_rel_e - gs_rel)))
            ax.plot(gs_x, gs_rel, "*", ms=14, zorder=61,
                    mfc="red", mec="white", mew=1.2)
            fname = os.path.join(plot_dir, "global_gs.xsf")
            ase_write(fname, gs_struct)
            saved.append(fname)
        if saved:
            print(f"  -> saved {len(saved)} xsf structures:")
            for f in saved:
                print(f"     {f}")
    plt.tight_layout()

    out_path = os.path.join(plot_dir, "progression_seed_split_0.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> progression plot saved to {out_path}")


# ---------------------------------------------------------------------------
# Stage 2 — Landscape analysis (PCA + state density)
# ---------------------------------------------------------------------------
def step2_landscape(structures, energies, outdir, e_max=None, normalize_density=False):
    print("\n[STAGE 2] Landscape analysis")
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms

    # PCA via Fingerprint descriptors
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    os.makedirs(outdir, exist_ok=True)

    if e_max is not None:
        e_limit = (0.0 - 0.1, e_max, 5)
    else:
        e_limit = E_LIMIT_DEFAULT

    density_x_label = ("State Density\n(a.u.)" if normalize_density
                       else "State Density\n(config./eV)")

    fig = plot_structure_landscape(
        X_eigen, rel, z_data=None,
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
        cmap="PuBu",
        show_colorbar=False,
        cbar_pad=0.02,
        z_limit=(5.85, 0, 5),
        black_seed_zero=True,
        s=15,
        normalize_density=normalize_density,
        density_x_label=density_x_label,
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {outdir}/conf_space.png")


# ---------------------------------------------------------------------------
# Stage 3 — Boltzmann probability vs temperature
# ---------------------------------------------------------------------------
def calculate_boltzmann_probs(energies, kde_model, T):
    """Normalized Pi = rho(E)*exp(-dE/kbT)/Z, then scaled so peak = 1."""
    kb = 8.6173e-5  # eV/K
    rho_i = kde_model.evaluate(energies) + 1e-15
    relative_e = energies - np.min(energies)
    weights = np.exp(-relative_e / (kb * T))
    numerator = rho_i * weights
    Z = np.sum(numerator)
    probs = numerator / Z
    return probs / probs.max()


def step3_probability(structures, energies, outdir, e_max=None):
    print("\n[STAGE 3] Boltzmann probability analysis")
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms
    kde = gaussian_kde(rel)

    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(rel, kde, T)
        ax.scatter(rel, probs, color=color, s=15, alpha=0.5,
                   edgecolors="none", label=f"{T} K")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(0, 1 + 0.05)
    ax.set_xlim(0, e_max if e_max is not None else rel.max() + 0.05)
    plt.tight_layout()

    out_path = os.path.join(outdir, "binding_probability_vs_temperature.png")
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AGOX analysis (Stage 2 landscape + Stage 3 Boltzmann P(T)) "
                    "for the GPR+LCB-only dataset (e.g. b11 boron seed DBs)")
    parser.add_argument("--dataset", required=True,
                        help="path to the dataset dir containing seed_*/1_db/db_*.db")
    parser.add_argument("--outdir", required=True,
                        help="output dir for the analysis figures")
    parser.add_argument("--e-max", type=float, default=None,
                        help="custom upper energy limit (eV/atom) for the Stage 2 "
                             "landscape and Stage 3 probability plots. Default = "
                             "each stage's default.")
    parser.add_argument("--normalize-density", action="store_true",
                        help="normalize the Stage 2 state-density panel to [0,1]")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep only structures with AGOX iteration >= this value "
                             "(inclusive), mirroring process_database.py's start_iter. "
                             "Default 10.")
    args = parser.parse_args()

    print("=" * 70)
    print("AGOX ANALYSIS PIPELINE (GPR+LCB-only dataset)")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    if args.e_max is not None:
        print(f"e-max  : {args.e_max} eV/atom")
    if args.normalize_density:
        print("normalize-density: True")
    print(f"start-iter : {args.start_iter} (iteration >= {args.start_iter})")
    print("=" * 70)

    structures, energies = load_all_seeds(args.dataset, start_iter=args.start_iter)
    print(f"\nTotal: {len(structures)} structures, {len(structures[0])} atoms each "
          f"(iteration >= {args.start_iter})")

    os.makedirs(args.outdir, exist_ok=True)
    step1_progression(args.dataset, args.outdir, start_iter=args.start_iter, e_max=args.e_max)
    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max)

    print(f"\nDONE. Outputs under: {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
