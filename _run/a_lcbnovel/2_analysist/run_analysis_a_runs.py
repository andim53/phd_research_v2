#!/usr/bin/env python3
"""
Single-seed AGOX analysis for the Novelty-LCB a-runs (e.g. a1_mgofe_Seed3_Iter300).

Sibling to `run_analysis_indices.py` (the multi-seed Fe/MgO runner ported from the
b_nestedsampling architecture), but dedicated to the per-seed a-runs whose output
lives under `<run>/output/seed_<N>/1_db/db_<N>.db`. It loads the run's seed DB(s)
directly and runs the same three stages:

  Stage 1 — Best-so-far progression plot (single seed; low-energy-window bullets +
            global ground-state .xsf export).
  Stage 2 — Landscape analysis & evaluation (scripts/plot_structure_landscape.py):
            PCA landscape (Fingerprint PC1) + per-atom KDE state density.
  Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z), vs T.

Produces, under <outdir>:
  progression_plots/progression_seed_split_<N>.png  (Stage 1 best-so-far progression)
  conf_space.png                          (Stage 2 landscape + state density)
  binding_probability_vs_temperature.png  (Stage 3 Boltzmann P(T))

Scoped to the single-seed a-runs in this project. Point --dataset at the run's
`output/` dir (which holds seed_*/1_db/db_*.db):

  idx a1 -> 2_analysist/a1_mgofe_Seed3_Iter300/output      (seed_3, 300 iterations)
  idx a10 -> 2_analysist/a10_mgofeb_Seed3_Iter500/output   (seed_3, 500 iterations)

The EMT benchmark dirs 73/74 have a flat benchmark_results/ layout that does NOT
fit the seed_*/1_db structure, so they are intentionally excluded here.

All arguments mirror the reference runner:
  --dataset        : path to the dir containing seed_*/1_db/db_*.db (required)
  --outdir         : output dir for the analysis figures (required)
  --e-max          : custom energy upper limit (eV/atom) for Stage 2 & Stage 3
  --normalize-density : normalize state-density panel to [0,1] (Stage 2 only)
  --start-iter     : keep only structures with AGOX iteration >= this (default 10)

Two-phase (extract / plot-from-json) mode:
  --extract        : read the DB and write a SINGLE self-describing JSON file
                     (analysis_data.json in --outdir) holding ALL raw data needed to
                     reproduce every plot. No plots are produced.
  --plot-from-json <file> : plot ONLY from that JSON file (the DB is not read) and
                     reproduce the same PNGs — identical to plotting directly from
                     the database. Each flag works on its own.

Run from /home/think/Desktop/research/_run/a_lcbnovel/2_analysist with the
agox_v2 conda env:
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_a_runs.py \
      --dataset a1_mgofe_Seed3_Iter300/output \
      --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
  ... --e-max 0.8
  ... --extract --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
  ... --plot-from-json a1_mgofe_Seed3_Iter300/analysis_a_runs/analysis_data.json \
      --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
"""

from __future__ import annotations

__version__ = "1.2.0"

import argparse
import glob
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime

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
def _seed_label_from_path(db_path: str) -> str:
    """Extract the human-readable seed label from a db path like
    .../seed_3/1_db/db_3.db -> 'Seed 3' (falls back to 'Seed' if undetermined)."""
    m = re.search(r"seed_(\d+)", os.path.basename(os.path.dirname(os.path.dirname(db_path))))
    return f"Seed {m.group(1)}" if m else "Seed"


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
    {seed_label: (structures, energies)} plus the flattened structures/energies.
    Labels use the actual seed number (e.g. 'Seed 3'), not a positional index."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    seed_data = OrderedDict()
    all_structs, all_energies = [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        atoms_list = [db.db_to_atoms(d) for d in kept]
        e_list = np.asarray([a.get_potential_energy() for a in atoms_list], dtype=float)
        seed_data[_seed_label_from_path(p)] = (atoms_list, e_list)
        all_structs.extend(atoms_list)
        all_energies.extend(e_list)
        print(f"  {os.path.relpath(p)}: {len(atoms_list)}/{len(raw)} structures "
              f"(iteration >= {start_iter})")
    return seed_data, all_structs, np.asarray(all_energies, dtype=float)


def compute_pca(structures):
    """PCA projection (Fingerprint PC1) of the structures onto the leading
    eigenvector — the X_eigen array consumed by Stage 2's landscape plot."""
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    return Xc @ evecs[:, order[0]]


def fingerprint_matrix(structures):
    """(n, d) matrix of flattened Fingerprint feature vectors for a list of ASE
    atoms, using the same descriptor + create_features call as compute_pca."""
    if len(structures) == 0:
        return np.zeros((0, 0))
    fp = Fingerprint.from_atoms(structures[0])
    return np.array([fp.create_features(s).flatten() for s in structures])


def compute_novelty_metrics(structures, threshold=0.1):
    """Fingerprint-novelty summary of a structure set for the report/JSON.

    distinct / duplication: greedy count matching the repo's is_distinct semantics
    (novelty_lcb/utils.py, default threshold 0.1) — a structure is a NEW distinct
    representative iff its minimum Euclidean fingerprint distance to every
    already-accepted distinct representative exceeds `threshold`; otherwise it is a
    duplicate. variety / difference: distribution of all pairwise fingerprint
    Euclidean distances.

    Returns a JSON-serialisable dict (empty-safe)."""
    n = len(structures)
    empty = {
        "n_structures": 0, "n_distinct": 0, "n_duplicates": 0,
        "fraction_duplicates": None, "threshold": threshold,
        "pairwise_fingerprint_distance": {
            "n_pairs": 0, "mean": None, "median": None, "std": None,
            "min": None, "max": None,
        },
    }
    if n == 0:
        return empty
    F = fingerprint_matrix(structures)
    reps = [F[0]]
    for i in range(1, n):
        d = np.linalg.norm(np.asarray(reps) - F[i], axis=1).min()
        if d > threshold:
            reps.append(F[i])
    n_distinct = len(reps)
    if n > 1:
        from scipy.spatial.distance import pdist
        pw = pdist(F, metric="euclidean")
        pw_stats = {
            "n_pairs": int(len(pw)),
            "mean": float(pw.mean()), "median": float(np.median(pw)),
            "std": float(pw.std()), "min": float(pw.min()), "max": float(pw.max()),
        }
    else:
        pw_stats = {
            "n_pairs": 0, "mean": 0.0, "median": 0.0,
            "std": 0.0, "min": 0.0, "max": 0.0,
        }
    return {
        "n_structures": n,
        "n_distinct": n_distinct,
        "n_duplicates": n - n_distinct,
        "fraction_duplicates": round((n - n_distinct) / n, 6),
        "threshold": threshold,
        "pairwise_fingerprint_distance": pw_stats,
    }


# ---------------------------------------------------------------------------
# Stage 1 — Best-so-far progression plot (single seed)
# ---------------------------------------------------------------------------
def step1_progression(seed_data, outdir, num_atoms, e_max=None, export_xsf=True):
    """Single-seed best-so-far relative-energy-per-atom progression plot, mirroring
    the multi-seed runner's Stage 1 but labelled with the actual seed number. Each
    seed's best-so-far curve is drawn (typically one for the a-runs), with bullets on
    the low-energy candidate windows (0-20, 20-40, 40-60, 60-80) and the global
    ground state exported as .xsf.

    seed_data is an OrderedDict {label: (structures_or_None, energies)}. When
    structures are None (plot-from-json mode) the .xsf exports are skipped
    (export_xsf=False) but the PNG is reproduced identically.

    If e_max is given (eV/atom), each seed's structures are filtered to those with
    relative-energy-per-atom <= e_max (i.e. (E - seed_min)/n_atoms <= e_max), matching
    the --e-max energy cap used in Stage 2/3."""
    print("\n[STAGE 1] Best-so-far progression plot (single seed)")
    from matplotlib.ticker import AutoMinorLocator

    # Capture the first seed's filtered structures/energies for the bullets + xsf export
    first_structs = None
    first_rel_e = None
    first_n = 0
    first_label = None

    fig, ax = plt.subplots(figsize=(6, 3.5))
    max_y, max_x = 0, 0
    sorted_seed_names = list(seed_data.keys())
    cmap = plt.get_cmap("tab10")
    for i, s_name in enumerate(sorted_seed_names):
        s_structs, s_energies = seed_data[s_name]
        if len(s_energies) == 0:
            continue
        # relative energy per atom within this seed (mirrors calculate_relative_energy)
        e_min = s_energies.min()
        s_rel_e_atom = np.asarray([(e - e_min) / num_atoms for e in s_energies])
        # apply the energy filter (relative to the seed min, per atom)
        if e_max is not None:
            mask = s_rel_e_atom <= e_max
            s_rel_e_atom = s_rel_e_atom[mask]
            s_structs = [a for a, m in zip(s_structs, mask) if m] if s_structs else None
        if len(s_rel_e_atom) == 0:
            continue
        # remember the first seed's filtered data for bullets/xsf
        if first_structs is None and s_structs is not None:
            first_structs = s_structs
        if first_rel_e is None:
            first_rel_e = s_rel_e_atom
            first_n = len(s_rel_e_atom)
            first_label = s_name
        s_best_so_far = np.minimum.accumulate(s_rel_e_atom)  # progressive minimum
        # highlight the (single) seed in bold black on top
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

    # --- Bullet scatter on the first seed: lowest-energy candidate in each evaluated-
    # candidate window (0-20, 20-40, 40-60, 60-80), plus the global ground state. ---
    plot_dir = os.path.join(outdir, "progression_plots")
    os.makedirs(plot_dir, exist_ok=True)
    if first_rel_e is not None:
        # global minimum across ALL data (for the ground-state bullet)
        global_min_e = min(
            (energies.min() for _, (_, energies) in seed_data.items() if len(energies) > 0),
            default=None)
        gs_struct = None
        if global_min_e is not None and export_xsf:
            for s_name, (s_structs, s_energies) in seed_data.items():
                if len(s_energies) > 0 and s_structs is not None:
                    gi = int(s_energies.argmin())
                    gs_struct = s_structs[gi]
                    break

        windows = [(0, 20), (20, 40), (40, 60), (60, 80)]
        saved = []
        for (wlo, whi) in windows:
            idxs = [j for j in range(first_n) if wlo <= j < whi]
            if not idxs:
                continue
            jmin = idxs[int(np.argmin(first_rel_e[idxs]))]  # lowest-energy candidate in window
            # bullet at (candidate_index, rel_energy_per_atom): black fill, white outline
            ax.plot(jmin, first_rel_e[jmin], "o", ms=7, zorder=60,
                    mfc="black", mec="white", mew=1.2)
            # save the structure
            if export_xsf and first_structs is not None:
                fname = os.path.join(plot_dir, f"seed0_min_w{wlo}-{whi}.xsf")
                ase_write(fname, first_structs[jmin])
                saved.append(fname)
        # global ground state bullet, plotted at its nearest first-seed candidate position
        if global_min_e is not None:
            # ground-state rel-energy-per-atom relative to the first seed's absolute minimum
            first_min_abs = min(
                (energies.min() for _, (_, energies) in seed_data.items()
                 if len(energies) > 0), default=global_min_e)
            gs_rel = (global_min_e - first_min_abs) / num_atoms
            # locate the nearest first-seed candidate index to the ground-state energy
            gs_x = first_n - 1
            if len(first_rel_e) > 0:
                gs_x = int(np.argmin(np.abs(first_rel_e - gs_rel)))
            ax.plot(gs_x, gs_rel, "*", ms=14, zorder=61,
                    mfc="red", mec="white", mew=1.2)
            if export_xsf and gs_struct is not None:
                fname = os.path.join(plot_dir, "global_gs.xsf")
                ase_write(fname, gs_struct)
                saved.append(fname)
        if saved:
            print(f"  -> saved {len(saved)} xsf structures:")
            for f in saved:
                print(f"     {f}")
    plt.tight_layout()

    seed_tag = first_label.replace(" ", "") if first_label else "0"
    out_path = os.path.join(plot_dir, f"progression_seed_split_{seed_tag}.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> progression plot saved to {out_path}")


# ---------------------------------------------------------------------------
# Stage 2 — Landscape analysis (PCA + state density)
# ---------------------------------------------------------------------------
def step2_landscape(structures, energies, outdir, num_atoms, e_max=None,
                    normalize_density=False, x_eigen=None):
    print("\n[STAGE 2] Landscape analysis")
    rel = (energies - energies.min()) / num_atoms

    # PCA via Fingerprint descriptors (or reuse a precomputed projection)
    if x_eigen is None:
        x_eigen = compute_pca(structures)

    os.makedirs(outdir, exist_ok=True)

    if e_max is not None:
        e_limit = (0.0 - 0.1, e_max, 5)
    else:
        e_limit = E_LIMIT_DEFAULT

    density_x_label = ("State Density\n(a.u.)" if normalize_density
                       else "State Density\n(config./eV)")

    fig = plot_structure_landscape(
        x_eigen, rel, z_data=None,
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


def step3_probability(energies, outdir, num_atoms, e_max=None):
    print("\n[STAGE 3] Boltzmann probability analysis")
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
# Extract / plot-from-json helpers
# ---------------------------------------------------------------------------
def extract_json(dataset_dir, outdir, start_iter=10, e_max=None):
    """Read the DB and write a single self-describing JSON file holding ALL raw
    data needed to reproduce every plot (progression, landscape, Boltzmann P(T)).
    The JSON is independent and AI-readable: clear structure, named fields, and
    enough context to interpret each value without the database."""
    seed_data, all_structs, all_energies = load_all_seeds_by_seed(dataset_dir, start_iter=start_iter)
    num_atoms = len(all_structs[0])

    seeds = []
    for s_name, (s_structs, s_energies) in seed_data.items():
        e_min = s_energies.min()
        s_rel = np.asarray([(e - e_min) / num_atoms for e in s_energies])
        seeds.append({
            "label": s_name,
            "n_structures": int(len(s_energies)),
            "energies_eV": [float(x) for x in s_energies],
            "rel_energy_per_atom_eV": [float(x) for x in s_rel],
            "best_so_far_eV_per_atom": [float(x) for x in np.minimum.accumulate(s_rel)],
            "novelty": compute_novelty_metrics(s_structs),
        })

    rel = (all_energies - all_energies.min()) / num_atoms
    x_eigen = compute_pca(all_structs)

    payload = {
        "schema_version": "1.1",
        "runner": os.path.basename(__file__),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dataset": dataset_dir,
        "start_iter": int(start_iter),
        "e_max": e_max,
        "num_atoms": int(num_atoms),
        "description": (
            "Self-describing analysis data extracted from the AGOX database. "
            "'seeds' holds per-seed absolute DFT energies (eV) and relative energy "
            "per atom (eV/atom, relative to that seed's minimum), the best-so-far "
            "progression, and a 'novelty' block (distinct/duplicate counts + "
            "pairwise fingerprint-distance stats, see compute_novelty_metrics). "
            "'global' holds the flattened relative energies, the PCA projection "
            "(x_eigen) used by the Stage 2 landscape, and the run-level 'novelty' "
            "across all seeds. All three plots can be reproduced from this file "
            "alone via --plot-from-json."
        ),
        "seeds": seeds,
        "global": {
            "n_structures": int(len(all_energies)),
            "rel_energy_per_atom_eV": [float(x) for x in rel],
            "x_eigen": [float(x) for x in x_eigen],
            "novelty": compute_novelty_metrics(all_structs),
        },
    }

    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "analysis_data.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  -> extracted analysis data to {out_path}")
    return out_path

def plot_from_json(json_path, outdir, e_max=None, normalize_density=False):
    """Plot ONLY from the given JSON file (the DB is not read), reproducing the
    same PNGs as plotting directly from the database."""
    with open(json_path) as f:
        payload = json.load(f)
    num_atoms = int(payload["num_atoms"])

    seed_data = OrderedDict()
    for s in payload["seeds"]:
        seed_data[s["label"]] = (None, np.asarray(s["energies_eV"], dtype=float))

    rel = np.asarray(payload["global"]["rel_energy_per_atom_eV"], dtype=float)
    x_eigen = np.asarray(payload["global"]["x_eigen"], dtype=float)
    # Stage 2/3 only consume rel = (E - Emin)/N; passing rel*N as "energies"
    # reproduces the identical rel (rel.min() == 0), so no absolute energies needed.
    energies = rel * num_atoms

    os.makedirs(outdir, exist_ok=True)
    step1_progression(seed_data, outdir, num_atoms, e_max=e_max, export_xsf=False)
    step2_landscape(None, energies, outdir, num_atoms,
                    e_max=e_max, normalize_density=normalize_density, x_eigen=x_eigen)
    step3_probability(energies, outdir, num_atoms, e_max=e_max)

    print(f"\nDONE. Outputs under: {os.path.abspath(outdir)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Single-seed AGOX analysis (Stage 2 landscape + Stage 3 Boltzmann "
                    "P(T)) for the Novelty-LCB a-runs (e.g. a1_mgofe_Seed3_Iter300)")
    parser.add_argument("--dataset", default=None,
                            help="path to the run output dir containing seed_*/1_db/db_*.db "
                                 "(not needed with --plot-from-json)")
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
    parser.add_argument("--extract", action="store_true",
                        help="read the DB and write a single self-describing JSON file "
                             "(analysis_data.json in --outdir) with ALL raw data needed "
                             "to reproduce every plot. No plots are produced.")
    parser.add_argument("--plot-from-json", metavar="JSON", default=None,
                        help="plot ONLY from the given JSON file (the DB is not read) "
                             "and reproduce the same PNGs. Each flag works on its own.")
    args = parser.parse_args()

    if args.extract and args.plot_from_json:
        parser.error("--extract and --plot-from-json are mutually exclusive")
    if args.dataset is None and not args.plot_from_json:
        parser.error("--dataset is required (unless --plot-from-json is used)")

    print("=" * 70)
    print("SINGLE-SEED AGOX ANALYSIS (Novelty-LCB a-runs)")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    if args.e_max is not None:
        print(f"e-max  : {args.e_max} eV/atom")
    if args.normalize_density:
        print("normalize-density: True")
    print(f"start-iter : {args.start_iter} (iteration >= {args.start_iter})")
    print("=" * 70)

    # --- Extract-only mode: DB -> JSON, no plots ---------------------------
    if args.extract:
        extract_json(args.dataset, args.outdir, start_iter=args.start_iter, e_max=args.e_max)
        print(f"\nDONE. JSON under: {os.path.abspath(args.outdir)}")
        return

    # --- Plot-from-json mode: JSON -> PNGs, no DB read ----------------------
    if args.plot_from_json:
        if not os.path.isfile(args.plot_from_json):
            parser.error(f"--plot-from-json file not found: {args.plot_from_json}")
        plot_from_json(args.plot_from_json, args.outdir,
                       e_max=args.e_max, normalize_density=args.normalize_density)
        return

    # --- Full pipeline mode: DB -> PNGs -------------------------------------
    structures, energies = load_all_seeds(args.dataset, start_iter=args.start_iter)
    print(f"\nTotal: {len(structures)} structures, {len(structures[0])} atoms each "
          f"(iteration >= {args.start_iter})")
    num_atoms = len(structures[0])

    os.makedirs(args.outdir, exist_ok=True)
    seed_data, _, _ = load_all_seeds_by_seed(args.dataset, start_iter=args.start_iter)
    step1_progression(seed_data, args.outdir, num_atoms,
                      e_max=args.e_max, export_xsf=True)
    step2_landscape(structures, energies, args.outdir, num_atoms,
                    e_max=args.e_max, normalize_density=args.normalize_density)
    step3_probability(energies, args.outdir, num_atoms, e_max=args.e_max)

    print(f"\nDONE. Outputs under: {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
