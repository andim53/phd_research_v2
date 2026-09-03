#!/usr/bin/env python3
"""
Unified AGOX analysis runner for the _run/0_lcb project's GPR+LCB datasets.

Adapted from the b_nestedsampling analysis runner architecture
(/home/think/Desktop/research/_run/b_nestedsampling/2_analysist/run_analysis_indices.py),
originally re-hosted under _run/a_lcbnovel (Fe/MgO). This copy is **project-agnostic**
in its data loading (it globs `seed_*/1_db/db_*.db` and uses the per-structure atom
count dynamically), so it runs on any of the interstitial-alloy families that live
under `2_analysist/`:

  Family            Host   Interstitial   Leaf dataset dirs (each holds seed_*/1_db)
  ----------------  -----  -------------  ----------------------------------------------
  11_bTa            Ta     B              7_fxg_0b, 8_fxg_1b, 9_fxg_3b, 10_fxg_5b, 11_p_Ta10b
  15_bPt            Pt     B              1_pt0b, 2_pt1b, 3_pt3b, 4_p_pt10b
  16_bW             W      B              1_w0b, 2_w1b, 3_w3b, 4_p_w10b
  17_PPt            Pt     P              0_plus5cell/{0_PPt_4x4_20P,1_3x3_20P,...},
                                          1_plus0cell/{0_0P,...,3_30P}, 2_plus3cell/..., 3_plus10cell/...

The 3-stage pipeline:
  Stage 1 — Best-so-far progression plot (per-seed), plus bullet scatter on Seed 0
            and .xsf export of the low-energy window minima + global ground state.
  Stage 2 — Landscape analysis & evaluation (scripts/plot_structure_landscape.py):
            PCA landscape (Fingerprint PC1) + per-atom KDE state density.
  Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z), vs T.

Produces, under <outdir>:
  progression_plots/progression_seed_split_0.png   (Stage 1 best-so-far progression)
  conf_space.png                          (Stage 2 landscape + state density)
  binding_probability_vs_temperature.png  (Stage 3 Boltzmann P(T))

Point `--dataset` at ONE leaf dataset dir (a dir that directly contains
`seed_*/1_db/db_*.db`), and `--outdir` at the analysis output location. A per-family
README lives in each result dir explaining the exact invocation for its leaves.

All arguments:
  --dataset        : path to the dir containing seed_*/1_db/db_*.db (required)
  --outdir         : output dir for the analysis figures (required)
  --e-max          : custom energy upper limit (eV/atom) for ALL THREE graphs
                    (Stage 1 progression y-axis, Stage 2 landscape, Stage 3
                    binding probability). When set, every energy axis uses the
                    same window [-0.1, e_max] so graphs are directly comparable
                    across leaves/families.
  --normalize-density : normalize state-density panel to [0,1] (Stage 2 only)
  --start-iter     : keep only structures with AGOX iteration >= this (default 10)

Run from /home/think/Desktop/research/_run/0_lcb/2_analysist with the agox_v2 conda env:
  /home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
      --dataset 15_bPt/1_pt0b \
      --outdir 15_bPt/1_pt0b/analysis_indices
  ... (repeat --dataset/--outdir per leaf; add --e-max as needed per system)
"""

from __future__ import annotations

__version__ = "2.4.0"

import argparse
import glob
import json
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
# JSON data emission / re-plot helpers
# ---------------------------------------------------------------------------
# The three Stage JSON files (one per analysis PNG), written to --json-dir.
STAGE_JSON = {
    1: "stage1_progression.json",
    2: "stage2_landscape.json",
    3: "stage3_probability.json",
}


def _to_jsonable(obj):
    """Recursively convert numpy arrays / scalars to JSON-safe (list/float/int/bool)."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


def _color_to_hex(color) -> str:
    """Convert a matplotlib color (name, tuple, or 'C0') to a '#rrggbb' hex string
    for JSON-safe storage."""
    import matplotlib.colors as mcolors
    return mcolors.to_hex(color)


def _parse_seed_spec(spec):
    """Parse a --seeds CLI value ('0-4', '0,1,5', '0-2,7,10-12') into a set of ints.

    Returns None when spec is falsy (meaning: no subsetting / show all seeds).
    """
    if not spec:
        return None
    seeds = set()
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            seeds.update(range(int(lo.strip()), int(hi.strip()) + 1))
        else:
            seeds.add(int(part))
    return seeds


def _filter_progression_data(data, seeds):
    """Return a copy of a Stage-1 data dict with only the curves whose numeric
    seed index is in ``seeds`` (set of ints, or None = keep all).

    Axis limits are recomputed from the surviving curves; Seed-0 bullets + the
    global ground state (both anchored to Seed-0 x positions) are dropped when
    Seed 0 is not part of the subset, since their reference curve would be gone.
    """
    if not seeds:
        return data
    # Curves are stored in ascending seed order. Live runs tag each with "seed";
    # older JSONs lack the field, so fall back to the list index as the seed id.
    curves = [c for i, c in enumerate(data["curves"])
              if c.get("seed", i) in seeds]
    # Seed-0 bullets / global GS are meaningful only when Seed 0 is plotted.
    keep_markers = 0 in seeds
    bullets = data["bullets"] if keep_markers else []
    global_gs = data["global_gs"] if keep_markers else None
    max_x = max((len(c["x"]) for c in curves), default=0)
    return {
        "curves": curves,
        "bullets": bullets,
        "global_gs": global_gs,
        "e_max": data.get("e_max"),
        "max_y": data.get("max_y", 0),
        "max_x": max_x,
    }


def _write_stage_json(json_dir: str, stage: int, data: dict):
    """Write one stage's plot data to <json_dir>/<STAGE_JSON[stage]>, making json_dir."""
    os.makedirs(json_dir, exist_ok=True)
    path = os.path.join(json_dir, STAGE_JSON[stage])
    payload = {"stage": stage, "data": _to_jsonable(data)}
    with open(path, "w") as f:
        json.dump(payload, f, indent=1)
    print(f"  -> stage {stage} JSON written to {path}")


def _read_stage_json(json_dir: str, stage: int) -> dict:
    """Load a stage's plot data JSON as a plain dict (its 'data' member)."""
    path = os.path.join(json_dir, STAGE_JSON[stage])
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing stage-{stage} JSON: {path}")
    with open(path) as f:
        payload = json.load(f)
    return payload["data"]




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
def _progression_data(dataset_dir, start_iter=10, e_max=None, outdir=None):
    """Compute + return the Stage-1 plotting data (per-seed best-so-far curves,
    Seed-0 bullet coordinates, ground-state info, axis limits) as a JSON-safe dict.

    When ``outdir`` is given, also writes the Seed-0 window-minimum + global
    ground-state .xsf structures under <outdir>/progression_plots (side output
    needing the DB; not reproduced from JSON)."""
    seed_data, _, _ = load_all_seeds_by_seed(dataset_dir, start_iter=start_iter)
    curves = []          # per-seed: {name, x, best_so_far, color, lw, is_seed0}
    bullets = []         # Seed-0 window minima: {x, rel_e}
    gs = None            # {x, rel_e} global ground-state bullet, if any
    max_y, max_x = 0, 0
    sorted_seed_names = list(seed_data.keys())
    cmap = plt.get_cmap("tab10")
    seed0_structs = None
    seed0_rel_e = None
    seed0_n = 0

    for i, s_name in enumerate(sorted_seed_names):
        s_structs, s_energies = seed_data[s_name]
        if not s_structs:
            continue
        e_min = s_energies.min()
        s_rel_e_atom = np.asarray([(e - e_min) / len(a)
                                   for e, a in zip(s_energies, s_structs)])
        if e_max is not None:
            mask = s_rel_e_atom <= e_max
            s_rel_e_atom = s_rel_e_atom[mask]
            s_structs = [a for a, m in zip(s_structs, mask) if m]
        if len(s_rel_e_atom) == 0:
            continue
        if i == 0:
            seed0_structs = s_structs
            seed0_rel_e = s_rel_e_atom
            seed0_n = len(s_rel_e_atom)
        s_best_so_far = np.minimum.accumulate(s_rel_e_atom)
        if i == 0:
            current_color, linewidth, is_seed0 = "black", 2.0, True
        else:
            current_color, linewidth, is_seed0 = cmap((i - 1) % 10), 1.5, False
        curves.append({
            "name": s_name,
            "seed": i,                  # numeric seed index, for --seeds subsetting
            "x": list(range(len(s_best_so_far))),
            "best_so_far": s_best_so_far.tolist(),
            "color": _color_to_hex(current_color),
            "lw": linewidth,
            "is_seed0": is_seed0,
        })
        max_y = max(max_y, float(np.max(s_rel_e_atom)))
        max_x = max(max_x, len(s_best_so_far))

    # Seed-0 bullets + ground state (needs structures for .xsf side output)
    if seed0_structs is not None and seed0_n > 0:
        global_min_e = min((energies.min() for _, (_, energies) in seed_data.items()
                            if len(energies) > 0), default=None)
        gs_struct = None
        if global_min_e is not None:
            for _, (s_structs, s_energies) in seed_data.items():
                if len(s_energies) > 0:
                    gs_struct = s_structs[int(s_energies.argmin())]
                    break
        windows = [(0, 20), (20, 40), (40, 60), (60, 80)]
        plot_dir = None
        if outdir is not None:
            plot_dir = os.path.join(outdir, "progression_plots")
            os.makedirs(plot_dir, exist_ok=True)
        for (wlo, whi) in windows:
            idxs = [j for j in range(seed0_n) if wlo <= j < whi]
            if not idxs:
                continue
            jmin = idxs[int(np.argmin(seed0_rel_e[idxs]))]
            bullets.append({"x": int(jmin), "rel_e": float(seed0_rel_e[jmin])})
            if plot_dir is not None and seed0_structs is not None:
                ase_write(os.path.join(plot_dir, f"seed0_min_w{wlo}-{whi}.xsf"),
                          seed0_structs[jmin])
        if global_min_e is not None and gs_struct is not None:
            seed0_min_abs = min((energies.min() for _, (_, energies) in seed_data.items()
                                 if len(energies) > 0), default=global_min_e)
            gs_rel = (global_min_e - seed0_min_abs) / len(gs_struct)
            gs_x = seed0_n - 1
            if len(seed0_rel_e) > 0:
                gs_x = int(np.argmin(np.abs(seed0_rel_e - gs_rel)))
            gs = {"x": gs_x, "rel_e": float(gs_rel)}
            if plot_dir is not None and gs_struct is not None:
                ase_write(os.path.join(plot_dir, "global_gs.xsf"), gs_struct)

    return {
        "curves": curves,
        "bullets": bullets,
        "global_gs": gs,
        "e_max": e_max,
        "max_y": max_y,
        "max_x": max_x,
    }


def _plot_progression_from_data(data, outdir, seeds=None):
    """Draw the Stage-1 progression PNG from a data dict (from a live run or JSON).

    ``seeds`` optionally restricts the plotted curves to the given numeric seed
    indices (set of ints) — see ``_filter_progression_data``. The legend is placed
    inside the axes (upper-left) when few curves are shown, else outside to the
    right with the saved figure auto-sized so the legend is never clipped.
    """
    from matplotlib.ticker import AutoMinorLocator
    print("\n[STAGE 1] Best-so-far progression plot")
    data = _filter_progression_data(data, seeds)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    max_y = data.get("max_y", 0)
    max_x = data.get("max_x", 0)
    for c in data["curves"]:
        ax.plot(c["x"], c["best_so_far"], label=c["name"], lw=c["lw"],
                color=c["color"], zorder=50 if c["is_seed0"] else 1)
    ax.set_xlabel("Evaluated Candidates")
    ax.set_ylabel(E_LABEL)
    ax.set_xlim(0, max_x)
    e_max = data.get("e_max")
    if e_max is not None:
        ax.set_ylim(-0.1, e_max)
    else:
        ax.set_ylim(0, max_y * 1.1)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="both", top=False, right=False,
                   labeltop=False, labelright=False)
    n_curves = len(data["curves"])
    if n_curves <= 6:
        # few curves: legend inside, upper-left (Seed 0 is black + topmost, so
        # anchors first and never runs off the small figure)
        ax.legend(loc="upper left", fontsize=9, ncol=1, frameon=True,
                  borderaxespad=0.4)
        tight_bbox = None
    else:
        # many curves: keep the legend outside, right; savefig auto-grows the
        # canvas (bbox_inches="tight") so the legend is never clipped.
        ax.legend(loc="upper left", fontsize=8, ncol=1, frameon=True,
                  bbox_to_anchor=(1.02, 1), borderaxespad=0.)
        tight_bbox = "tight"
    # Seed-0 window-minimum bullets (black fill / white ring)
    for b in data["bullets"]:
        ax.plot(b["x"], b["rel_e"], "o", ms=7, zorder=60,
                mfc="black", mec="white", mew=1.2)
    # global ground-state star
    if data.get("global_gs"):
        ax.plot(data["global_gs"]["x"], data["global_gs"]["rel_e"], "*", ms=14,
                zorder=61, mfc="red", mec="white", mew=1.2)
    plot_dir = os.path.join(outdir, "progression_plots")
    os.makedirs(plot_dir, exist_ok=True)
    out_path = os.path.join(plot_dir, "progression_seed_split_0.png")
    plt.savefig(out_path, dpi=300, bbox_inches=tight_bbox)
    plt.close(fig)
    print(f"  -> progression plot saved to {out_path}")
    return out_path


def step1_progression(dataset_dir, outdir, start_iter=10, e_max=None,
                      json_dir=None, seeds=None):
    """Stage 1: emit JSON (if json_dir), write xsf side-output, draw the PNG."""
    data = _progression_data(dataset_dir, start_iter=start_iter, e_max=e_max,
                             outdir=outdir)
    if json_dir:
        _write_stage_json(json_dir, 1, data)
    return _plot_progression_from_data(data, outdir, seeds=seeds)


# ---------------------------------------------------------------------------
# Stage 2 — Landscape analysis (PCA + state density)
# ---------------------------------------------------------------------------
def _landscape_data(structures, energies, e_max=None, normalize_density=False):
    """Return the Stage-2 plot inputs (PCA X_eigen, rel energies, e_limit, and the
    fixed kwargs passed to plot_structure_landscape) as a JSON-safe dict."""
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms

    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    X_eigen = Xc @ evecs[:, order[0]]

    e_limit = (0.0 - 0.1, e_max, 5) if e_max is not None else E_LIMIT_DEFAULT
    density_x_label = ("State Density\n(a.u.)" if normalize_density
                       else "State Density\n(config./eV)")

    return {
        "X_eigen": X_eigen,
        "rel": rel,
        "e_limit": list(e_limit),
        "normalize_density": bool(normalize_density),
        "density_x_label": density_x_label,
        "num_atoms": num_atoms,
        "params": {
            "figsize": [3, 3], "wspace": 0.1, "fontsize": 10,
            "fill_density": True, "dens_line_weight": 0.9, "show_limits": False,
            "custom_peak_labels": None, "cmap": "PuBu", "show_colorbar": False,
            "cbar_pad": 0.02, "z_limit": [5.85, 0, 5], "black_seed_zero": True,
            "s": 15, "plot_z_vs_e": False, "animate_scatter": False,
            "plot_density_only": False,
        },
    }


def _plot_landscape_from_data(data, outdir):
    """Draw the Stage-2 landscape PNG from a data dict (live run or JSON).

    Re-calls plot_structure_landscape with the stored inputs (deterministic, so the
    PNG reproduces faithfully). Also returns the computed arrays if the upstream
    function returns them.
    """
    import matplotlib.pyplot as _plt
    p = data["params"]
    os.makedirs(outdir, exist_ok=True)
    X_eigen = np.asarray(data["X_eigen"])
    rel = np.asarray(data["rel"])
    result = plot_structure_landscape(
        X_eigen, rel, z_data=None,
        save_path=outdir,
        animate_scatter=p["animate_scatter"],
        figsize=tuple(p["figsize"]), wspace=p["wspace"], fontsize=p["fontsize"],
        plot_density_only=p["plot_density_only"],
        e_limit=tuple(data["e_limit"]), fill_density=p["fill_density"],
        dens_line_weight=p["dens_line_weight"], show_limits=p["show_limits"],
        custom_peak_labels=p["custom_peak_labels"],
        cmap=p["cmap"], show_colorbar=p["show_colorbar"], cbar_pad=p["cbar_pad"],
        z_limit=tuple(p["z_limit"]), black_seed_zero=p["black_seed_zero"],
        s=p["s"], normalize_density=data["normalize_density"],
        density_x_label=data["density_x_label"],
        plot_z_vs_e=p["plot_z_vs_e"], return_data=True,
    )
    if isinstance(result, dict):
        arrays = result
        _plt.close(arrays.pop("figure", None))
    else:
        arrays = {}
        _plt.close(result)
    print(f"  -> landscape saved to {outdir}/conf_space.png")
    return arrays


def step2_landscape(structures, energies, outdir, e_max=None,
                    normalize_density=False, json_dir=None):
    """Stage 2: draw conf_space.png AND capture its plotted arrays into JSON."""
    data = _landscape_data(structures, energies, e_max=e_max,
                           normalize_density=normalize_density)
    arrays = _plot_landscape_from_data(data, outdir)
    # fold the computed curve arrays into the JSON payload (literal dump of the plot)
    if arrays:
        data["plot_arrays"] = arrays
    if json_dir:
        _write_stage_json(json_dir, 2, data)
    return data


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


def _probability_data(structures, energies, e_max=None):
    """Return the Stage-3 plotting data (relative energies, KDE rel grid, per-T
    probabilities, temps, colors, axis windows) as a JSON-safe dict."""
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms
    kde = gaussian_kde(rel)
    series = []
    for T, color in zip(TEMPS, COLORS_PLASMA):
        series.append({
            "T": T,
            "color": color,
            "rel": rel.tolist(),
            "probs": calculate_boltzmann_probs(rel, kde, T).tolist(),
        })
    e_lim = (-0.1, e_max) if e_max is not None else (0.0, float(rel.max()) + 0.05)
    return {
        "num_atoms": num_atoms,
        "series": series,
        "e_max": e_max,
        "xlim": list(e_lim),
        "ylim": [0.0, 1.05],
    }


def _plot_probability_from_data(data, outdir):
    """Draw the Stage-3 Boltzmann P(T) PNG from a data dict (live run or JSON)."""
    print("\n[STAGE 3] Boltzmann probability analysis")
    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for s in data["series"]:
        ax.scatter(s["rel"], s["probs"], color=s["color"], s=15, alpha=0.5,
                   edgecolors="none", label=f"{s['T']} K")
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(*data["ylim"])
    ax.set_xlim(*data["xlim"])
    plt.tight_layout()

    out_path = os.path.join(outdir, "binding_probability_vs_temperature.png")
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")
    return out_path


def step3_probability(structures, energies, outdir, e_max=None, json_dir=None):
    """Stage 3: emit JSON (if json_dir), then draw the Boltzmann P(T) PNG."""
    data = _probability_data(structures, energies, e_max=e_max)
    if json_dir:
        _write_stage_json(json_dir, 3, data)
    return _plot_probability_from_data(data, outdir)


# ---------------------------------------------------------------------------
# Re-plot from JSON
# ---------------------------------------------------------------------------
def replot_from_json(json_dir, outdir, seeds=None):
    """Read the three Stage JSON files under json_dir and re-draw all PNGs under outdir.

    Stages 1 and 3 store final curve arrays (faithful literal dump); Stage 2 stores the
    plot inputs + params and re-runs plot_structure_landscape to reproduce conf_space.png.
    ``seeds`` optionally restricts the Stage-1 progression plot to given seed indices.
    """
    os.makedirs(outdir, exist_ok=True)
    d1 = _read_stage_json(json_dir, 1)
    _plot_progression_from_data(d1, outdir, seeds=seeds)
    d2 = _read_stage_json(json_dir, 2)
    # If a literal plot_arrays dump exists (from a live run), fold it back into the data
    # so conf_space.png is reproduced from stored inputs (arrays are informational).
    _plot_landscape_from_data(d2, outdir)
    d3 = _read_stage_json(json_dir, 3)
    _plot_probability_from_data(d3, outdir)
    print(f"\nRe-plotted all 3 graphs from JSON {json_dir} -> {outdir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AGOX analysis (Stage 2 landscape + Stage 3 Boltzmann P(T)) "
                    "for the GPR+LCB-only dataset (e.g. 71/72 Novelty-LCB seed DBs)")
    parser.add_argument("--dataset", default=None,
                        help="path to the dataset dir containing seed_*/1_db/db_*.db. "
                             "Required for a full run; ignored when --from-json is used.")
    parser.add_argument("--outdir", required=True,
                        help="output dir for the analysis figures")
    parser.add_argument("--e-max", type=float, default=None,
                        help="custom energy upper limit (eV/atom); when set, ALL "
                             "three graphs (progression, landscape, probability) "
                             "share the energy window [-0.1, e_max]. Default = "
                             "each stage's auto/default window.")
    parser.add_argument("--normalize-density", action="store_true",
                        help="normalize the Stage 2 state-density panel to [0,1]")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep only structures with AGOX iteration >= this value "
                             "(inclusive), mirroring process_database.py's start_iter. "
                             "Default 10.")
    parser.add_argument("--seeds", default=None,
                        help="(Stage 1 progression only) restrict the plotted curves "
                             "to these seed indices, e.g. '0-4' or '0,1,5'. Applies to "
                             "both live runs and --from-json replots. Default: all seeds.")
    parser.add_argument("--json-dir", default=None,
                        help="emit each stage's plotting data as JSON (one file per "
                             "graph) into this dir, in addition to drawing the PNGs. "
                             "Default: <outdir>/analysis_json when --json-dir omitted.")
    parser.add_argument("--from-json", default=None,
                        help="skip DB loading and instead read the stage JSON files "
                             "from this dir, re-drawing all 3 PNGs into --outdir.")
    args = parser.parse_args()
    seeds = _parse_seed_spec(args.seeds)

    # --- from-json mode: no DB access --------------------------------------
    if args.from_json:
        print("=" * 70)
        print("AGOX ANALYSIS — replot from JSON")
        print(f"from-json : {args.from_json}")
        print(f"outdir    : {args.outdir}")
        print(f"seeds     : {args.seeds or 'all'}")
        print("=" * 70)
        replot_from_json(args.from_json, args.outdir, seeds=seeds)
        return

    if not args.dataset:
        parser.error("--dataset is required for a full run (or use --from-json)")

    json_dir = args.json_dir or os.path.join(args.outdir, "analysis_json")

    print("=" * 70)
    print("AGOX ANALYSIS PIPELINE (GPR+LCB-only dataset)")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    print("json-dir:", json_dir)
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
    step1_progression(args.dataset, args.outdir, start_iter=args.start_iter,
                      e_max=args.e_max, json_dir=json_dir, seeds=seeds)
    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density,
                    json_dir=json_dir)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir)

    print(f"\nDONE. Outputs under: {os.path.abspath(args.outdir)}")
    print(f"JSON data under: {os.path.abspath(json_dir)}")


if __name__ == "__main__":
    main()
