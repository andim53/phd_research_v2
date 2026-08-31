#!/usr/bin/env python3
"""
Wang-Landau density-of-states sampling on an AGOX GPR surrogate.

Loads every structure from every seed database in the chosen dataset, trains a
single GPR surrogate on the combined structures, then runs the WangLandauSampler
to compute the density of states g(E) over relative energy per atom. From g(E)
it derives the partition function Z, free energy F = -k_B T ln Z and heat
capacity C_V at a set of temperatures.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]

    /home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --dataset dataset --n-bins 100 --e-max 0.40 --mc-steps 2000000 \
    --temperatures 100,200,300,500,1000 --output ./wl_output --rng 42

This script relies on:
  - the `wang_landau` package in this directory (imported as a package)
  - the AGOX / ASE stack installed in the agox_v2 conda env
"""

from __future__ import annotations

__version__ = "1.3.0"

import argparse
import os
import sys
from pathlib import Path

import numpy as np

# --- Make `wang_landau` importable from this directory ----------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import matplotlib
matplotlib.use("Agg")

from wang_landau.gpr_training import load_all_seeds, build_gpr, validate_gpr
from wang_landau.wang_landau_sampler import WangLandauSampler
from wang_landau.thermodynamics import (
    g_of_E_to_thermodynamics, heat_capacity_from_thermo)
from wang_landau.utils import K_B


# Available datasets: name -> (dir, glob pattern). Default = dataset.
DATASETS = {
    "dataset": ("dataset", "seed_*/1_db/db_*.db"),
    "dataset_boron3": ("dataset_boron3", "seed_*/1_db/db_*.db"),
    "dataset_boron": ("dataset_boron", "seed_*/1_db/db_*.db"),
}


def main():
    p = argparse.ArgumentParser(
        description="Wang-Landau density of states on a GPR surrogate")
    p.add_argument("--dataset", default="dataset",
                   choices=list(DATASETS),
                   help="Which dataset dir to sample (default dataset). "
                        "Choices: dataset (Fe/MgO), dataset_boron3 (B3), "
                        "dataset_boron (B7).")
    p.add_argument("--n-bins", type=int, default=40,
                   help="Number of energy bins, default 40")
    p.add_argument("--e-min", type=float, default=0.0,
                   help="Lower bin edge (eV/atom rel), default 0.0")
    p.add_argument("--e-max", type=float, default=0.40,
                   help="Upper bin edge (eV/atom rel), i.e. barrier+margin, "
                        "default 0.40")
    p.add_argument("--small-step", type=float, default=0.05,
                   help="Small Gaussian displacement scale (A), default 0.05")
    p.add_argument("--large-step", type=float, default=0.20,
                   help="Large Gaussian displacement scale (A), default 0.20 "
                        "(reduced from 0.40 to avoid GPR-extrapolation escapes)")
    p.add_argument("--e-reject", type=float, default=None,
                   help="Relative energy (eV/atom) above which a trial is treated "
                        "as an unphysical GPR extrapolation and REJECTED (revisits "
                        "current bin) instead of being capped into the top bin. "
                        "Default = 5*e_max; set <= e_max to disable.")
    p.add_argument("--perturb-symbols", default="Fe",
                   help="Symbol(s) of atoms to rattle, comma-separated; "
                        "default 'Fe'")
    p.add_argument("--flatness-criterion", type=float, default=0.80,
                   help="Flatness threshold, default 0.80")
    p.add_argument("--check-interval", type=int, default=5000,
                   help="Flatness check interval (MC steps), default 5000")
    p.add_argument("--n-stages-standard", type=int, default=14,
                   help="Standard-scheme halvings before switching to 1/t, "
                        "default 14")
    p.add_argument("--swap-prob", type=float, default=0.0,
                   help="Probability of choosing a swap (permutation) move "
                        "instead of a rattle on each MC step. Swap exchanges "
                        "positions of two atoms of DIFFERENT species within "
                        "the mobile set, then rattles them. Requires >=2 "
                        "mobile species; disabled (no-op) otherwise. "
                        "Default 0.0 (off).")
    p.add_argument("--max-swaps", type=int, default=1,
                   help="Max number of swaps per swap move; each swap move "
                        "performs a random 1..max swaps (mirrors the reference "
                        "GlobalPermutationGenerator). Default 1.")
    p.add_argument("--swap-rattle", type=float, default=0.05,
                   help="Gaussian displacement (A) applied to the two swapped "
                        "atoms after a swap. Default 0.05.")
    p.add_argument("--mc-steps", type=int, default=2000000,
                   help="Number of Wang-Landau MC steps, default 2000000")
    p.add_argument("--temperatures", default="100,200,300,500,1000",
                   help="Comma-separated temperatures (K) for thermodynamics "
                        "post-processing")
    p.add_argument("--start-from-top", action="store_true",
                   default=False,
                   help="Initialize the walker at the TOP of the tracked window "
                        "[e_min, e_max) (pick the highest-rel-energy DB structure "
                        "strictly inside the window; the 'flat' analogue). Default "
                        "off: start from the global minimum and walk up.")
    p.add_argument("--start-from-min", action="store_true",
                   help="Explicitly initialize the walker from the GLOBAL MINIMUM "
                        "(lowest-energy DB structure, rel E ~ 0) and let the walk "
                        "ascend. This is the default behaviour; provided for "
                        "clarity/explicitness.")
    p.add_argument("--output", default=os.path.join(_HERE, "wl_output"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed for the sampler RNG")
    p.add_argument("--use-ray", action="store_true",
                   help="Enable Ray in GPR training (default: single-process)")
    args = p.parse_args()

    # --- 1. Load the chosen dataset -----------------------------------------
    ds_dir, ds_pat = DATASETS[args.dataset]
    print("=" * 70)
    print(f"Loading dataset '{args.dataset}' ({ds_dir})")
    structures, energies, db_paths = load_all_seeds(
        os.path.join(_HERE, ds_dir), ds_pat)
    print(f"  Total: {len(structures)} structures, {len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()} "
          f"({len(structures[0])} atoms)")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 2. Train the GPR surrogate ------------------------------------------
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures, use_ray=args.use_ray)
    validate_gpr(gpr, structures, energies)

    # --- 3. Run Wang-Landau --------------------------------------------------
    print("\nRunning Wang-Landau sampling...")
    temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
    sampler = WangLandauSampler(
        gpr=gpr,
        db_structures=structures,
        db_energies=energies,
        n_bins=args.n_bins,
        e_min=args.e_min,
        e_max=args.e_max,
        e_reject=args.e_reject,
        small_step=args.small_step,
        large_step=args.large_step,
        perturb_symbols=args.perturb_symbols,
        flatness_criterion=args.flatness_criterion,
        check_interval=args.check_interval,
        n_stages_standard=args.n_stages_standard,
        swap_prob=args.swap_prob,
        max_swaps=args.max_swaps,
        swap_rattle=args.swap_rattle,
        rng=np.random.default_rng(args.rng),
    )
    # Initialize: --start-from-top picks the top of the tracked window; otherwise
    # (default, or --start-from-min) start from the global minimum and walk up.
    start_from_top = args.start_from_top and not args.start_from_min
    sampler.initialize(start_from_top=start_from_top)
    sampler.run(n_steps=args.mc_steps,
                progress_every=max(args.check_interval, 1))

    # --- 4. Save g(E) + thermodynamics ---------------------------------------
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    sampler.save(str(output_dir))

    bin_centers_rel, ln_g = sampler.g_of_E()
    therm_rows = g_of_E_to_thermodynamics(
        bin_centers_rel, ln_g, sampler.E_ref, sampler.n_atoms, temps)
    np.savetxt(output_dir / "thermodynamics.csv",
               np.asarray(therm_rows, dtype=float), delimiter=',',
               header='T_K,beta_eV-1,logZ,Z,F_eV', comments='')
    print("\nThermodynamics (from normalised g(E)):")
    print("  T(K)   beta(eV^-1)   logZ      Z          F(eV)")
    for (T, beta, logZ, Z, F) in therm_rows:
        print(f"  {T:6.1f}  {beta:11.6f}  {logZ:9.4f}  {Z:9.4e}  {F:9.4f}")

    cv = heat_capacity_from_thermo(therm_rows)
    if cv:
        np.savetxt(output_dir / "heat_capacity.csv",
                   np.asarray(cv, dtype=float), delimiter=',',
                   header='T_K,C_V_eV_per_K', comments='')
        print("\nHeat capacity C_V (needs >=3 temperatures):")
        for (T, c) in cv:
            print(f"  T = {T:6.1f} K:  C_V = {c:9.4f} eV/K")

    _plot_g_of_E(bin_centers_rel, ln_g, output_dir)

    print(f"\nDone. Results written to {output_dir}")


def _plot_g_of_E(bin_centers_rel, ln_g, output_dir):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(bin_centers_rel, ln_g, "o-", ms=3)
    ax.set_xlabel(r"$(E - E_{\mathrm{min}})/N$  (eV/atom)")
    ax.set_ylabel(r"$\ln g(E)$")
    ax.set_title("Wang-Landau density of states $g(E)$")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "g_of_E.png", dpi=150)
    plt.close(fig)
    print(f"  Wrote g_of_E.png to {output_dir}")


if __name__ == "__main__":
    main()
