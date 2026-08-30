#!/usr/bin/env python3
"""
Plot the thermodynamics of a temperature-free nested-sampling run.

Reads the ``thermodynamics.csv`` written by ``main.py`` post-processing in
temperature-free mode (columns: T_K, beta_eV-1, logZ, Z, F_eV; one row per
temperature) and produces:

  * Z vs T            (linear Z, one panel)
  * log Z vs T        (robust log-evidence, one panel)
  * F = -k_B T ln Z   (free energy vs T, one panel)
  * C_V vs T          (heat capacity vs T, one panel, --cv flag)

Heat capacity is estimated from the numerically stable log-evidence via
    C_V = k_B * beta^2 * d^2(ln Z)/d(beta)^2,
where beta = 1/(k_B T).  The second derivative is taken on the (beta, lnZ)
curve with numpy.gradient; it needs >= 3 temperature points to be meaningful.

Run with the project env python (only needs numpy + matplotlib, no AGOX):

    /home/think/miniconda3/envs/agox_v2/bin/python scripts/plot_thermodynamics.py \
        --input  ns_output_tfree/thermodynamics.csv \
        --output thermodynamics_Z_F.png \
        --cv

By default Z, log Z and F panels are drawn in one figure. Add --cv for a second
figure with the heat capacity.
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe; set before pyplot import
import matplotlib.pyplot as plt

K_B = 8.617333262e-5  # eV / K

# Columns of thermodynamics.csv (written by main.py temperature-free post-processing)
COL_T, COL_BETA, COL_LOGZ, COL_Z, COL_F = range(5)


def load_thermodynamics(path: str) -> np.ndarray:
    """Load thermodynamics.csv -> (T, beta, logZ, Z, F) columns as a 2D array."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Run a temperature-free NS run first "
            f"(main.py --temperature-free ...) to produce thermodynamics.csv.")
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    if data.ndim == 1:                      # single temperature row
        data = data.reshape(1, -1)
    if data.shape[1] < 5:
        raise ValueError(
            f"{path}: expected >=5 columns (T,beta,logZ,Z,F), got {data.shape[1]}")
    return data


def heat_capacity(T, beta, logZ) -> np.ndarray:
    """C_V = k_B * beta^2 * d^2(ln Z)/d(beta)^2, via numpy.gradient on (beta, lnZ)."""
    dlogZ = np.gradient(logZ, beta)
    d2logZ = np.gradient(dlogZ, beta)
    return K_B * beta**2 * d2logZ


def plot_main(data: np.ndarray, out_path: str):
    """Z vs T, log Z vs T, and F vs T panels in one figure."""
    T, beta, logZ, Z, F = [data[:, c] for c in (COL_T, COL_BETA, COL_LOGZ, COL_Z, COL_F)]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].plot(T, Z, "o-")
    axes[0].set(xlabel="T (K)", ylabel="Z")
    axes[0].set_title("Partition function")
    axes[1].plot(T, logZ, "o-")
    axes[1].set(xlabel="T (K)", ylabel="log Z")
    axes[1].set_title("Log evidence")
    axes[2].plot(T, F, "s-")
    axes[2].set(xlabel="T (K)", ylabel=r"$F = -k_B T \ln Z$ (eV)")
    axes[2].set_title("Free energy")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> {out_path}")


def plot_cv(data: np.ndarray, out_path: str):
    """Heat capacity C_V(T) panel (needs >=3 temperature points)."""
    T, beta, logZ = [data[:, c] for c in (COL_T, COL_BETA, COL_LOGZ)]
    if T.size < 3:
        print(f"  WARNING: heat capacity needs >=3 temperature points "
              f"(have {T.size}); skipping C_V plot.")
        return
    Cv = heat_capacity(T, beta, logZ)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(T, Cv, "^-")
    ax.set(xlabel="T (K)", ylabel=r"$C_V$ (eV/K)")
    ax.set_title("Heat capacity (numeric 2nd deriv. of ln Z vs beta)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> {out_path}")


def main():
    p = argparse.ArgumentParser(
        description="Plot thermodynamics (Z, log Z, F, optional C_V) from a "
                    "temperature-free nested-sampling run's thermodynamics.csv")
    p.add_argument("--input", required=True,
                   help="path to thermodynamics.csv (T,beta,logZ,Z,F per row)")
    p.add_argument("--output", default="thermodynamics_Z_F.png",
                   help="output PNG for the Z/logZ/F figure (default "
                        "thermodynamics_Z_F.png)")
    p.add_argument("--cv", action="store_true",
                   help="also write a heat-capacity C_V(T) figure "
                        "(default: thermodynamics_Cv.png)")
    p.add_argument("--cv-output", default="thermodynamics_Cv.png",
                   help="output PNG for the C_V figure (default "
                        "thermodynamics_Cv.png)")
    args = p.parse_args()

    data = load_thermodynamics(args.input)
    plot_main(data, args.output)
    if args.cv:
        plot_cv(data, args.cv_output)


if __name__ == "__main__":
    main()
