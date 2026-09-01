#!/usr/bin/env python3
"""
Plot the prior-weight-weighted state-density histogram g(E) from nested sampling,
comparing the impact of the number of iterations (1,000 / 5,000 / 10,000 / 20,000).

This mirrors the `samples_weighted_histogram.png` recipe from
`analyze_tfree_outputs.py`: g(E) is a prior-weight-weighted histogram of the
discarded-sample energies, divided by the bin width (config./eV), plotted vs
per-atom relative energy (E - E_min)/n_atoms.

All iteration counts are read from the SAME long run (the iter20000 ns_output),
by taking the first N samples (and their prior weights) for N = 1000, 5000,
10000, 20000. A single shared global minimum (the iter20000 run's E_min =
-436.888 eV) is used as E_ref for all iterations so the curves are directly
comparable on the same eV/atom axis.

Usage (needs numpy + matplotlib + agox_v2 for load_samples):
  /home/think/miniconda3/envs/agox_v2/bin/python plot_ns_histogram_iterations.py \
      --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outdir  b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_indices \
      --outname ns_histogram_state_density_iterations.png \
      --n-atoms 75
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects

import analyze_tfree_outputs as ato  # reuse load_samples

# --- Plotting style: same rcParams as the other analyses ---
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
DENSITY_LABEL = "State Density (config./eV)"


def main():
    p = argparse.ArgumentParser(
        description="Prior-weight-weighted state-density histogram g(E) vs number of NS iterations")
    p.add_argument("--ns-output", required=True,
                   help="ns_output dir containing samples.csv (the long iter20000 run)")
    p.add_argument("--outdir", required=True,
                   help="output dir for the PNG")
    p.add_argument("--outname", default="ns_histogram_state_density_iterations.png",
                   help="output filename")
    p.add_argument("--n-atoms", type=int, default=75,
                   help="atoms per structure, for per-atom relative energy. Default 75 (Fe/MgO).")
    p.add_argument("--iterations", type=int, nargs="+",
                   default=[1000, 5000, 10000, 20000],
                   help="iteration counts to compare (taken as first-N samples). "
                        "Default 1000 5000 10000 20000.")
    p.add_argument("--bins", type=int, default=50,
                   help="number of histogram bins. Default 50.")
    args = p.parse_args()

    # --- load the full iter20000 samples ---
    iters, Es, Ws = ato.load_samples(os.path.join(args.ns_output, "samples.csv"))
    print(f"  loaded {Es.size} samples from {args.ns_output}")

    # Shared global minimum (the full run's min) as E_ref for all iterations
    E_min = Es.min()
    print(f"  shared global E_min = {E_min:.4f} eV (E_ref for all iterations)")

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#0d0887", "#47039f", "#9c176d", "#ed7953"]   # perceptually ordered

    print("=" * 60)
    print("State-density histogram vs number of iterations")
    print("=" * 60)
    for i, N in enumerate(args.iterations):
        if N > Es.size:
            print(f"  WARNING: {N} > available samples {Es.size}; clipping to {Es.size}")
            N = Es.size
        # first N samples and their prior weights
        EsN, WsN = Es[:N], Ws[:N]
        rel = (EsN - E_min) / args.n_atoms                  # per-atom relative energy
        hist, edges = np.histogram(rel, bins=args.bins, weights=WsN)
        centers = 0.5 * (edges[:-1] + edges[1:])
        binw = edges[1] - edges[0]
        gE = hist / binw                                    # config./eV
        peak_i = centers[np.argmax(gE)]
        ax.plot(centers, gE, color=colors[i % len(colors)], lw=1.8,
                label=f"{N:,} iters (peak {peak_i:.3f} eV/atom)")
        print(f"  {N:>6,} iters: n_samples={N}, sum(w)={WsN.sum():.4f}, "
              f"g(E) peak {gE.max():.2f} config./eV at {peak_i:.4f} eV/atom")

    ax.set_xlabel(E_LABEL)
    ax.set_ylabel(DENSITY_LABEL)
    ax.set_title("NS state density g(E) vs number of iterations")
    ax.legend(fontsize=8, frameon=False, loc="upper right")

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")


if __name__ == "__main__":
    main()
