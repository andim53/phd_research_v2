#!/usr/bin/env python3
"""
Analyze the outputs of a temperature-free nested-sampling run, from three CSVs:

  samples.csv            iteration, energy_eV, prior_weight   (discarded samples)
  final_live_energies.csv energy_eV                           (live set at termination)
  thermodynamics.csv     T_K, beta_eV-1, logZ, Z, F_eV        (per-temperature)

Produces a comprehensive analysis:
  1. samples.csv:
       - energy vs iteration (convergence / descent of the discarded samples)
       - prior_weight-weighted energy histogram (configurational state-density proxy
         g(E); the weights w_i = X_{i-1}-X_i are the prior-volume shells)
       - cumulative weighted evidence Z_wt = sum(prior_weight) vs iteration (sanity
         check against thermodynamics logZ)
  2. final_live_energies.csv:
       - live-energy distribution histogram
  3. thermodynamics.csv:
       - Z vs T, log Z vs T, F = -k_B T ln Z vs T, and heat capacity C_V(T) (numeric
         2nd derivative of logZ vs beta)
Plus a combined summary figure and a printed textual summary.

This is a GENERIC temperature-free analyzer: point --data at any run's output directory
containing those three CSVs (e.g. the b6_tfree_walk_emax04 or b7_boron_* run outputs).

Usage (only needs numpy + matplotlib, no AGOX):

  /home/think/miniconda3/envs/agox_v2/bin/python analyze_tfree_outputs.py \
      --data /path/to/ns_output_tfree \
      --outdir /path/to/analysis_out
"""

from __future__ import annotations

__version__ = "1.2.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

K_B = 8.617333262e-5  # eV/K

FILE_SAMPLES = "samples.csv"
FILE_LIVE = "final_live_energies.csv"
FILE_THERMO = "thermodynamics.csv"

COL_ITER, COL_E, COL_W = 0, 1, 2  # samples.csv columns
COL_T, COL_BETA, COL_LOGZ, COL_Z, COL_F = range(5)  # thermodynamics.csv columns

# rcParams matching `run_analysis_indices.py` (the reference pipeline style)
PIPELINE_RCPARAMS = {
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
}


def apply_pipeline_style():
    """Apply run_analysis_indices.py's rcParams so the plots match that style."""
    plt.rcParams.update(PIPELINE_RCPARAMS)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_samples(path: str):
    """samples.csv -> iterations, energies, prior_weights (1D arrays)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    d = np.loadtxt(path, delimiter=",", skiprows=1)
    if d.ndim == 1:
        d = d.reshape(1, -1)
    if d.shape[1] < 3:
        raise ValueError(f"{path}: expected >=3 columns, got {d.shape[1]}")
    return d[:, COL_ITER], d[:, COL_E], d[:, COL_W]


def load_live(path: str) -> np.ndarray:
    """final_live_energies.csv -> live energies (1D array)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    d = np.loadtxt(path, delimiter=",", skiprows=1)
    return np.atleast_1d(d).astype(float)


def load_thermo(path: str):
    """thermodynamics.csv -> (T, beta, logZ, Z, F) 1D arrays."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    d = np.loadtxt(path, delimiter=",", skiprows=1)
    if d.ndim == 1:
        d = d.reshape(1, -1)
    if d.shape[1] < 5:
        raise ValueError(f"{path}: expected >=5 columns, got {d.shape[1]}")
    return tuple(d[:, c] for c in range(5))


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------
def heat_capacity(T, beta, logZ):
    """C_V = k_B beta^2 d^2(lnZ)/d(beta)^2 via numpy.gradient (needs >=3 points)."""
    dlogZ = np.gradient(logZ, beta)
    d2logZ = np.gradient(dlogZ, beta)
    return K_B * beta**2 * d2logZ


E_LABEL = r"$E_{i}-E_{glob}$ (eV/atom)"  # matches run_analysis_indices.py


def make_analysis(data_dir, outdir, n_atoms=75, relative_energy=False):
    os.makedirs(outdir, exist_ok=True)

    # --- load ---
    iters, Es, Ws = load_samples(os.path.join(data_dir, FILE_SAMPLES))
    live = load_live(os.path.join(data_dir, FILE_LIVE))
    T, beta, logZ, Z, F = load_thermo(os.path.join(data_dir, FILE_THERMO))

    # If relative-energy mode, convert energies to (E - E_ref)/n_atoms (eV/atom),
    # matching run_analysis_indices.py's relative-energy convention and axis label.
    E_ref = Es.min()
    if relative_energy:
        Es_plot = (Es - E_ref) / n_atoms
        live_plot = (live - E_ref) / n_atoms
        energy_xlabel = E_LABEL
    else:
        Es_plot, live_plot = Es, live
        energy_xlabel = "energy (eV)"

    # --- 1a. energy vs iteration (convergence) ---
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(iters, Es_plot, ".", ms=3, alpha=0.4, label="discarded samples")
    ax.plot(iters, np.cumsum(Ws * Es_plot) / np.cumsum(Ws), "r-", lw=1.5,
            label="weighted running mean")
    ax.set_xlabel("iteration"); ax.set_ylabel(energy_xlabel)
    ax.set_title("Discarded-sample energy vs iteration")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "samples_energy_vs_iter.png"), dpi=300)
    plt.close(fig)

    # --- 1b. prior_weight-weighted energy histogram (state-density proxy g(E)) ---
    n_bins = 50
    hist, edges = np.histogram(Es_plot, bins=n_bins, weights=Ws)
    centers = 0.5 * (edges[:-1] + edges[1:])
    binw = edges[1] - edges[0]
    g = hist / binw  # per-unit-energy density
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(centers, g, width=binw * 0.9, alpha=0.6, label="weighted g(E) proxy")
    ax.set_xlabel(energy_xlabel); ax.set_ylabel("g(E) (config./eV)")
    ax.set_title("Prior-weight-weighted energy histogram (state-density proxy)")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "samples_weighted_histogram.png"), dpi=300)
    plt.close(fig)

    # --- 1c. cumulative weighted evidence Z_wt vs iteration ---
    cum = np.cumsum(Ws)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(iters, np.log(cum), "b-", label=r"$\log \Sigma_i w_i$ (from samples)")
    if T.size > 0 and logZ.size > 0:
        ax.axhline(logZ[-1], color="r", ls="--", lw=1.2,
                   label=f"logZ from thermo.csv @T={T[-1]:.0f}K")
    ax.set_xlabel("iteration"); ax.set_ylabel(r"$\log(\Sigma w_i)$")
    ax.set_title("Cumulative weighted evidence (sanity vs thermo logZ)")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "samples_cumulative_Z.png"), dpi=300)
    plt.close(fig)

    # --- 2. final live-energy distribution ---
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(live_plot, bins=30, color="green", alpha=0.6)
    ax.axvline(live_plot.min(), color="k", ls="--", lw=1.2, label=f"min={live_plot.min():.3f}")
    ax.axvline(live_plot.max(), color="orange", ls="--", lw=1.2, label=f"max={live_plot.max():.3f}")
    ax.set_xlabel(energy_xlabel); ax.set_ylabel("count")
    ax.set_title("Final live-point energy distribution")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "live_energy_hist.png"), dpi=300)
    plt.close(fig)

    # --- 3. thermodynamics Z/logZ/F + C_V ---
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].plot(T, Z, "o-"); axes[0].set(xlabel="T (K)", ylabel="Z")
    axes[0].set_title("Partition function Z")
    axes[1].plot(T, logZ, "o-"); axes[1].set(xlabel="T (K)", ylabel="log Z")
    axes[1].set_title("Log evidence log Z")
    axes[2].plot(T, F, "s-"); axes[2].set(xlabel="T (K)", ylabel=r"$F=-k_B T\ln Z$ (eV)")
    axes[2].set_title("Free energy F")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "thermodynamics_Z_F.png"), dpi=300)
    plt.close(fig)

    if T.size >= 3:
        Cv = heat_capacity(T, beta, logZ)
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(T, Cv, "^-")
        ax.set(xlabel="T (K)", ylabel=r"$C_V$ (eV/K)")
        ax.set_title("Heat capacity (numeric 2nd deriv of logZ vs beta)")
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "thermodynamics_Cv.png"), dpi=300)
        plt.close(fig)
    else:
        Cv = np.array([])
        print("  (heat capacity skipped: need >=3 temperatures)")

    # --- 4. configurational state density g(E) from samples (weighted histogram) ---
    # g(E) in eV/atom RELATIVE to E_ref (the minimum sample energy), units config./eV.
    rel_min = Es.min()                     # E_ref (min sample energy)
    E_rel = (Es - rel_min) / n_atoms       # eV/atom above the min
    n_bins_g = 50
    hist_g, edges_g = np.histogram(E_rel, bins=n_bins_g, weights=Ws)
    centers_g = 0.5 * (edges_g[:-1] + edges_g[1:])
    binw_g = edges_g[1] - edges_g[0]
    g_of_E = hist_g / binw_g               # config./eV (per-atom relative energy units)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(centers_g, g_of_E, width=binw_g * 0.9, alpha=0.6,
           label=r"$g(E)$ (weighted histogram)")
    ax.set_xlabel(E_LABEL if relative_energy else "E - E_ref (eV/atom)")
    ax.set_ylabel(r"$g(E)$ (config./eV)")
    ax.set_title("Configurational state density $g(E)$ from samples.csv")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "state_density_gE.png"), dpi=300)
    plt.close(fig)

    # --- 5. Z(T) from g(E) Laplace-transform consistency check vs thermodynamics.csv ---
    # Z_from_g(beta) = sum_E g(E) exp(-beta_per_atom * E_rel) * dE.
    # Use PER-ATOM beta (beta/n_atoms) to match the per-atom relative energies E_rel.
    # Note: thermodynamics.csv logZ is computed per-SYSTEM (evaluate() with absolute
    # energies and E_ref shift + live-set correction), so this comparison is a SHAPE /
    # trend check of logZ vs T, not an exact numerical match (a constant log-offset is
    # expected from the E_ref/normalization/live-set differences).
    if T.size > 0 and logZ.size > 0:
        beta_atom = beta / n_atoms
        Z_from_g = np.array([
            np.sum(g_of_E * np.exp(-beta_atom[i] * centers_g) * binw_g)
            for i in range(T.size)
        ])
        # compare logZ from thermo.csv vs log(Z_from_g), with a constant-shift fit
        logZ_from_g = np.log(np.maximum(Z_from_g, 1e-300))
        # offset = mean(logZ_thermo - logZ_from_g); report the shifted residual
        if T.size >= 2:
            offset = np.mean(logZ - logZ_from_g)
            residual = logZ - (logZ_from_g + offset)
        else:
            offset = 0.0
            residual = np.array([0.0])
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(T, logZ, "o-", label="logZ (thermodynamics.csv)")
        ax.plot(T, logZ_from_g + offset, "s--",
                label=r"$\log Z_{from g(E)}$ (shifted by const. offset)")
        ax.set_xlabel("T (K)"); ax.set_ylabel("log Z")
        ax.set_title("Consistency check: log Z(T) trend from g(E) vs thermodynamics.csv")
        ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "state_density_Z_consistency.png"), dpi=300)
        plt.close(fig)
    else:
        Z_from_g = np.array([])
        logZ_from_g = np.array([])
        offset = 0.0
        residual = np.array([])
        print("  (consistency check skipped: no thermodynamics.csv rows)")

    # --- combined summary ---
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].plot(iters, Es_plot, ".", ms=2, alpha=0.3)
    axes[0, 0].set(xlabel="iter", ylabel=energy_xlabel); axes[0, 0].set_title("samples energy")
    axes[0, 1].bar(centers, g, width=binw * 0.9, alpha=0.6)
    axes[0, 1].set(xlabel=energy_xlabel, ylabel="g(E)"); axes[0, 1].set_title("weighted g(E) proxy")
    axes[1, 0].hist(live_plot, bins=30, color="green", alpha=0.6)
    axes[1, 0].set(xlabel=energy_xlabel, ylabel="count"); axes[1, 0].set_title("final live")
    axes[1, 1].plot(T, logZ, "o-")
    axes[1, 1].set(xlabel="T (K)", ylabel="log Z"); axes[1, 1].set_title("log Z vs T")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "tfree_analysis_summary.png"), dpi=300)
    plt.close(fig)

    # --- printed summary ---
    print("=" * 60)
    print("Temperature-free NS analysis")
    print("=" * 60)
    print(f"discarded samples : {iters.size}")
    print(f"  energy range    : {Es.min():.4f} .. {Es.max():.4f} eV")
    print(f"  weighted mean E : {np.average(Es, weights=Ws):.4f} eV")
    print(f"final live points : {live.size}")
    print(f"  live range      : {live.min():.4f} .. {live.max():.4f} eV")
    print(f"thermodynamics   : {T.size} temperatures")
    for i in range(T.size):
        print(f"  T={T[i]:8.1f} K  logZ={logZ[i]:10.4f}  Z={Z[i]:.4e}  F={F[i]:.4f} eV"
              + (f"  Cv={Cv[i]:.4f}" if Cv.size else ""))
    total_w = Ws.sum()
    print(f"total prior weight sum(w_i) = {total_w:.6e}  (should ~= final X ~= exp(-iters/n_live))")
    print(f"state density g(E): {n_bins_g} bins in E-E_ref (eV/atom) ["
          f"{E_rel.min():.4f} .. {E_rel.max():.4f}]; peak g = {g_of_E.max():.4f} at "
          f"{centers_g[np.argmax(g_of_E)]:.4f} eV/atom")
    if Z_from_g.size:
        print("Z(T) consistency (trend from g(E) vs thermodynamics.csv):")
        print(f"  const. log-offset = {offset:.4f}; residual (logZ_thermo - shifted logZ_from_g):")
        for i in range(T.size):
            print(f"  T={T[i]:8.1f} K  logZ_thermo={logZ[i]:9.4f}  "
                  f"logZ_from_g+off={logZ_from_g[i]+offset:9.4f}  resid={residual[i]:+.4f}")
    print(f"outputs written to: {os.path.abspath(outdir)}")


def main():
    p = argparse.ArgumentParser(
        description="Analyze a temperature-free nested-sampling run's outputs "
                    "(samples.csv, final_live_energies.csv, thermodynamics.csv)")
    p.add_argument("--data", required=True,
                   help="dir containing samples.csv, final_live_energies.csv, thermodynamics.csv")
    p.add_argument("--outdir", default=None,
                   help="output dir for plots (default: <data>/analysis/analyze_tfree)")
    p.add_argument("--n-atoms", type=int, default=75,
                   help="number of atoms per structure, for the per-atom relative "
                        "energy (eV/atom) units of the state density g(E). Default 75 "
                        "(Fe/MgO). Only scales the x-axis units.")
    p.add_argument("--style-pipeline", action="store_true",
                   help="apply run_analysis_indices.py's rcParams (serif font, ticks-in "
                        "on top/right, no grid, dpi 300) to all resulting plots.")
    p.add_argument("--relative-energy", action="store_true",
                   help="plot energy axes as RELATIVE energy (E - E_ref)/n_atoms (eV/atom), "
                        "using run_analysis_indices.py's axis title "
                        r"'$E_{i}-E_{glob}$ (eV/atom)'. Default off = absolute eV.")
    args = p.parse_args()

    if args.style_pipeline:
        apply_pipeline_style()

    outdir = args.outdir or os.path.join(args.data, "analysis", "analyze_tfree")
    make_analysis(args.data, outdir, n_atoms=args.n_atoms,
                  relative_energy=args.relative_energy)


if __name__ == "__main__":
    main()
