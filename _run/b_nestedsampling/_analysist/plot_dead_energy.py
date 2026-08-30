#!/usr/bin/env python3
"""
Plot the NS 'dead energy' curve: the highest-energy discarded sample at each
nested-sampling iteration, dead_E(Iter), vs iteration.

This mirrors the Fortran reference `_tmp/nested_sampling_windowed_fixed.f`, where
`dead_E(iter) = walkers_E(idx_worst)` records the worst (highest-energy) walker's
energy at each iteration. In the AGOX nested-sampling output, `samples.csv` stores
one discarded sample per iteration, and the `energy_eV` column is exactly this
dead_E(Iter) trace.

Produces a single plot of dead_E(Iter) vs iteration (the discarded-sample energy
descent curve), styled like the other analyses.

Usage (needs numpy + matplotlib + agox_v2 for load_samples):
  /home/think/miniconda3/envs/agox_v2/bin/python plot_dead_energy.py \
      --ns-output b10_femgo_walk_emax04_exclworst_noxsf_novelty/ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outdir  b10_femgo_walk_emax04_exclworst_noxsf_novelty/analysis_ns_output_tfree_walk_emax04_exclworst_noxsf_novelty_iter20000 \
      --outname dead_energy_vs_iteration.png
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

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


def main():
    p = argparse.ArgumentParser(
        description="Plot NS dead_E(Iter) (highest-energy discarded sample) vs iteration")
    p.add_argument("--ns-output", required=True,
                   help="ns_output dir containing samples.csv (the NS run's output)")
    p.add_argument("--outdir", required=True,
                   help="output dir for the PNG")
    p.add_argument("--outname", default="dead_energy_vs_iteration.png",
                   help="output filename (default dead_energy_vs_iteration.png)")
    args = p.parse_args()

    # --- load NS samples: iteration, energy_eV (= dead_E), prior_weight ---
    iters, Es, Ws = ato.load_samples(os.path.join(args.ns_output, "samples.csv"))
    print(f"  NS samples (iterations): {Es.size}")

    # dead_E(Iter) = the discarded (highest-energy) sample's energy at each iteration
    dead_E = Es

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(iters, dead_E, ".", ms=3, alpha=0.4, label="dead_E(Iter)")
    # weighted running mean to show the descent trend
    ax.plot(iters, np.cumsum(Ws * dead_E) / np.cumsum(Ws), "r-", lw=1.5,
            label="weighted running mean")
    ax.set_xlabel("iteration")
    ax.set_ylabel(r"$E_{dead}$ (eV)")
    ax.set_title("NS dead energy vs iteration")
    # x-axis: evenly spaced ticks with thousands separators (large iteration counts)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=8)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, args.outname)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")

    # --- printed summary ---
    print("=" * 60)
    print("NS dead energy trace")
    print("=" * 60)
    print(f"iterations : {dead_E.size}")
    print(f"dead_E range: {dead_E.min():.4f} .. {dead_E.max():.4f} eV")
    print(f"  (highest-energy discarded sample at iter 0: {dead_E[0]:.4f} eV)")
    print(f"  (final dead_E at iter {dead_E.size-1}: {dead_E[-1]:.4f} eV)")


if __name__ == "__main__":
    main()
