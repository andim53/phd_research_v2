#!/usr/bin/env python3
"""
State-density / energy-landscape analysis for nested-sampling results.

Replicates the Stage-2 (landscape) and Stage-3 (Boltzmann probability) logic from
`_run/9_novelFilter/run_analysis_thresholds.py`, applied to the structures sampled
by `NestedSampler` and compared against the original training set (the 1297
combined-seed structures).

For each structure set it produces (using GPR-predicted energies, via
`gpr.predict_energy`):

  1. Landscape : PCA on AGOX Fingerprint descriptors + KDE state-density panel
                 -> conf_space.png   (per set)
  2. Boltzmann : P(E) = rho(E)*exp(-dE/kbT)/Z at the reference temperatures
                 -> binding_probability_vs_temperature.png   (per set)
  3. Comparison: one combined overlaid KDE state-density plot (training vs
                 posterior) on a common energy axis -> comparison_state_density.png

Paths: `_ANALYSIST` and its `scripts/` are inserted into sys.path so the shared
`plot_structure_landscape` function resolves.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from ase.io import read

# --- agox / ase / analysist paths ---------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ANALYSIST = "/home/think/Desktop/research/_analysist"
for _p in (_HERE, _ANALYSIST, os.path.join(_ANALYSIST, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agox.models.descriptors.fingerprint import Fingerprint
from scripts.plot_structure_landscape import plot_structure_landscape

# ---------------------------------------------------------------------------
# Shared plotting style (identical to the reference Stage-2/Stage-3 scripts)
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
    "ytick.major.width": 1.0,
    "axes.grid": False,
    "figure.autolayout": True,
    "figure.dpi": 300,
})

# Stage-3 temperatures / colours (from the reference script)
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
COLORS_PLASMA = ["#0d0887", "#47039f", "#7301a8", "#9c176d", "#bd3752",
                 "#d8546a", "#ed7953", "#fb9f4a", "#fdca42", "#f0f928"]

E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"

MAX_PHYSICAL_E = 1e4  # eV; reject GPR predictions with |E| above this


# ---------------------------------------------------------------------------
def _is_degenerate(rel):
    """True if a gaussian_kde on these relative energies would be singular
    (fewer than 2 distinct energy values)."""
    return len(np.unique(np.round(rel, 6))) < 2


def predict_energies(structures, gpr):
    """GPR-predicted absolute energies (eV) for a list of Atoms.

    Returns only the (structure, energy) pairs whose GPR prediction is physical
    (|E| < MAX_PHYSICAL_E), keeping arrays aligned.
    """
    keep_structs, keep_E = [], []
    for s in structures:
        E = gpr.predict_energy(s)
        if abs(E) < MAX_PHYSICAL_E:
            keep_structs.append(s)
            keep_E.append(E)
    return keep_structs, np.asarray(keep_E, dtype=float)


# ---------------------------------------------------------------------------
def fit_pca(structures):
    """Project a list of structures onto the top PCA eigenvector of their
    common (combined) Fingerprint covariance. Returns PC1 score array."""
    fp = Fingerprint.from_atoms(structures[0])
    data = np.array([fp.create_features(s).flatten() for s in structures])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    return Xc @ evecs[:, order[0]], fp


def make_landscape(structures, rel_energies, save_path, e_limit,
                   normalize_density=False):
    """One reference-style landscape plot (PCA scatter + state-density KDE).

    Parameters
    ----------
    structures : list of ase.Atoms
        Structures for the PCA scatter panel.
    rel_energies : np.ndarray
        Per-atom relative energies (eV/atom), same length as ``structures``.
    """
    X_eigen, _ = fit_pca(structures)

    os.makedirs(save_path, exist_ok=True)
    fig = plot_structure_landscape(
        X_eigen, rel_energies, z_data=None,
        save_path=save_path,
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
        s=5,
        normalize_density=normalize_density,
        density_x_label=("State Density\n(a.u.)" if normalize_density
                         else "State Density\n(config./eV)"),
        plot_z_vs_e=False,
    )
    plt.close(fig)
    print(f"  -> landscape saved to {save_path}/conf_space.png")


def make_probability(rel_energies, save_path, e_max=None):
    """Reference-style Boltzmann probability P(E) vs temperature.

    Parameters
    ----------
    rel_energies : np.ndarray
        Per-atom relative energies (eV/atom).
    """
    rel = rel_energies
    kde = gaussian_kde(rel)

    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for T, color in zip(TEMPS, COLORS_PLASMA):
        probs = calculate_boltzmann_probs(rel, kde, T)
        ax.scatter(rel, probs, color=color, s=5, alpha=0.5,
                   edgecolors="none", label=f"{T} K")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability P(E)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(0, 1 + 0.05)
    xmax = e_max if e_max is not None else rel.max() + 0.05
    ax.set_xlim(0, xmax)
    plt.tight_layout()

    os.makedirs(save_path, exist_ok=True)
    out_path = os.path.join(save_path, "binding_probability_vs_temperature.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability saved to {out_path}")


def calculate_boltzmann_probs(relative_energies, kde_model, T):
    """Pi = [rho(E)*exp(-dE/kbT)] / Z, normalised to a 0-1 peak (reference logic)."""
    kb = 8.6173e-5  # eV/K
    rho_i = kde_model.evaluate(relative_energies) + 1e-15
    relative_e = relative_energies - np.min(relative_energies)
    weights = np.exp(-relative_e / (kb * T))
    numerator = rho_i * weights
    Z = np.sum(numerator)
    probs = numerator / Z
    return probs / probs.max()


def make_comparison_density(train_rel, post_rel, save_path,
                            output_name="comparison_state_density.png"):
    """Overlay the training and posterior state-density KDE curves on a common
    per-atom-relative-energy axis (density-only panel, no PCA scatter)."""
    all_e = np.concatenate([train_rel, post_rel])
    e_max = all_e.max() + 0.05
    e_limit = (0.0 - 0.1, e_max + 0.1, 5)

    os.makedirs(save_path, exist_ok=True)
    fig = plot_structure_landscape(
        np.array([]), {  # energies handled as dataset dict; no scatter
            "Training": train_rel,
            "Posterior": post_rel,
        },
        save_path=save_path,
        plot_density_only=True,
        figsize=(3, 3),
        fontsize=10,
        e_limit=e_limit,
        fill_density=True,
        dens_line_weight=1.0,
        show_limits=False,
        density_cmap="viridis",
        black_seed_zero=True,
        normalize_density=False,
        density_x_label="State Density\n(config./eV)",
    )
    plt.close(fig)
    out = os.path.join(save_path, output_name)
    # plot_structure_landscape writes conf_space.png; rename to the comparison name
    if os.path.exists(os.path.join(save_path, "conf_space.png")):
        os.replace(os.path.join(save_path, "conf_space.png"), out)
    print(f"  -> comparison density saved to {out}")


# ---------------------------------------------------------------------------
def analyze_state_density(posterior_structures, training_structures, gpr,
                          output_dir, normalize_density=False, e_max=None):
    """Run the full state-density / landscape / probability analysis.

    Parameters
    ----------
    posterior_structures : list of ase.Atoms
        The posterior samples accumulated by the sampler (all discarded
        worst-points, not just the top-20 saved XSFs).
    training_structures : list of ase.Atoms
        The original combined-seed training set (1297 structures).
    gpr : agox GPR
        Trained surrogate; energies are recomputed with ``predict_energy``.
    output_dir : str
        Where to write the per-set analysis subfolders.
    normalize_density : bool
        Normalize each state-density panel to 0-1.
    e_max : float or None
        Common upper energy limit (eV/atom). If None, each set uses its own max.
    """
    out = os.path.abspath(output_dir)

    print("\n" + "=" * 70)
    print("State-density / landscape analysis of nested-sampling results")
    print("=" * 70)

    # GPR-predicted energies for both sets (same surrogate basis)
    post_structs, post_E = predict_energies(posterior_structures, gpr)
    train_structs, train_E = predict_energies(training_structures, gpr)
    print(f"\nPosterior: {len(post_structs)} physical / {len(posterior_structures)}")
    print(f"Training : {len(train_structs)} physical / {len(training_structures)}")
    print(f"Posterior E range: {post_E.min():.3f} .. {post_E.max():.3f} eV")
    print(f"Training  E range: {train_E.min():.3f} .. {train_E.max():.3f} eV")

    # Common reference so both sets are on the same energy scale
    common_min_e = min(post_E.min(), train_E.min())
    num_atoms = len(post_structs[0])
    post_rel = (post_E  - common_min_e) / num_atoms
    train_rel = (train_E - common_min_e) / num_atoms

    # ---- per-set landscape + probability ----------------------------------
    for name, structs, rel in [
        ("training", train_structs, train_rel),
        ("posterior", post_structs, post_rel),
    ]:
        print(f"\n=== {name} ===")
        print(f"  rel-E max = {rel.max():.4f} eV/atom")
        e_limit = (0.0 - 0.1,
                   (e_max if e_max is not None else rel.max()) + 0.1, 5)
        save_path = os.path.join(out, name)
        if _is_degenerate(rel):
            print("  WARNING: degenerate energy set (<2 distinct values); "
                  "skipping landscape/probability for this set.")
            continue
        make_landscape(structs, rel, save_path, e_limit,
                       normalize_density=normalize_density)
        make_probability(rel, save_path, e_max=e_max)

    # ---- combined comparison density panel ---------------------------------
    print("\n=== comparison (training vs posterior) ===")
    if _is_degenerate(train_rel) or _is_degenerate(post_rel):
        print("  WARNING: one or both energy sets are degenerate (<2 distinct "
              "values); skipping the comparison density panel.")
    else:
        make_comparison_density(train_rel, post_rel, out)

    print(f"\nAnalysis written to {out}")
    return out


# ---------------------------------------------------------------------------
# Standalone re-analysis from saved output (no GPR required)
# ---------------------------------------------------------------------------
def load_saved_run(run_output_dir: str):
    """Load a saved nested-sampling run's posterior samples + energies.

    Reads ``posterior_structures/posterior_*.xsf`` (all of them) and
    ``posterior_summary.csv`` (rank, energy_eV, weight, log_weight). The
    energies are the GPR-predicted values stored at save time, so this works
    without re-training / re-predicting.

    Returns
    -------
    structures : list of ase.Atoms
    energies   : np.ndarray  (eV), same order as ``structures``
    """
    run_dir = Path(run_output_dir)
    xsf_dir = run_dir / "posterior_structures"
    struct_files = sorted(glob.glob(str(xsf_dir / "posterior_*.xsf")))
    summary_path = run_dir / "posterior_summary.csv"
    if not struct_files:
        raise FileNotFoundError(f"No posterior_*.xsf in {xsf_dir}")
    if not summary_path.exists():
        raise FileNotFoundError(
            f"{summary_path} missing (need `posterior_summary.csv`) — re-run "
            f"the sampler's save() with the updated code.")

    # order by rank parsed from filename
    def _rank(p):
        return int(os.path.basename(p).split("_")[1])
    struct_files.sort(key=_rank)

    structs = [read(p) for p in struct_files]

    # read summary: rank,energy_eV,weight,log_weight
    energies = np.loadtxt(summary_path, delimiter=',', skiprows=1)
    util = np.atleast_2d(energies.reshape(-1, 4))
    e_arr = util[:, 1]

    print(f"[load_saved_run] {len(structs)} posterior structures, "
          f"E range {e_arr.min():.3f} .. {e_arr.max():.3f} eV")
    return structs, e_arr


def analyze_saved_output(run_output_dir: str, training_structures,
                         training_energies, output_dir,
                         normalize_density=False, e_max=None):
    """Re-run the state-density / landscape analysis on a saved run.

    Uses the posterior structures + stored GPR energies from ``run_output_dir``
    (written by ``NestedSampler.save``) and a separately-supplied training set
    with its own energies (e.g. the original 1297 DFT energies loaded from the
    databases). No GPR is required — this lets the analysis be re-run standalone.

    Parameters
    ----------
    run_output_dir : str
        Directory written by ``NestedSampler.save`` (contains
        ``posterior_structures/`` and ``posterior_summary.csv``).
    training_structures : list of ase.Atoms
        Original training / dataset structures.
    training_energies : np.ndarray
        Energies (eV) for ``training_structures`` (same order).
    output_dir : str
        Where to write the per-set analysis subfolders.
    """
    post_structs, post_E = load_saved_run(run_output_dir)
    train_structs = list(training_structures)
    train_E = np.asarray(training_energies, dtype=float)

    print("\n" + "=" * 70)
    print("Standalone state-density analysis of saved run")
    print(f"  run output  : {run_output_dir}")
    print("=" * 70)
    print(f"\nPosterior: {len(post_structs)} structures")
    print(f"Training : {len(train_structs)} structures")
    print(f"Posterior E range: {post_E.min():.3f} .. {post_E.max():.3f} eV")
    print(f"Training  E range: {train_E.min():.3f} .. {train_E.max():.3f} eV")

    # Same energy-normalisation as analyze_state_density
    common_min_e = min(post_E.min(), train_E.min())
    num_atoms = len(post_structs[0])
    post_rel = (post_E - common_min_e) / num_atoms
    train_rel = (train_E - common_min_e) / num_atoms

    out = os.path.abspath(output_dir)
    for name, structs, rel in [
        ("training", train_structs, train_rel),
        ("posterior", post_structs, post_rel),
    ]:
        print(f"\n=== {name} ===")
        print(f"  rel-E max = {rel.max():.4f} eV/atom")
        e_limit = (0.0 - 0.1,
                   (e_max if e_max is not None else rel.max()) + 0.1, 5)
        save_path = os.path.join(out, name)
        if _is_degenerate(rel):
            print("  WARNING: degenerate energy set (<2 distinct values); "
                  "skipping landscape/probability for this set.")
            continue
        make_landscape(structs, rel, save_path, e_limit,
                       normalize_density=normalize_density)
        make_probability(rel, save_path, e_max=e_max)

    # ---- combined comparison density panel ---------------------------------
    print("\n=== comparison (training vs posterior) ===")
    if _is_degenerate(train_rel) or _is_degenerate(post_rel):
        print("  WARNING: one or both energy sets are degenerate (<2 distinct "
              "values); skipping the comparison density panel.")
    else:
        make_comparison_density(train_rel, post_rel, out)

    print(f"\nAnalysis written to {out}")
    return out