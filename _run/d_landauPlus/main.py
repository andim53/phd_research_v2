#!/usr/bin/env python3
"""
Landau-Plus: inherent-structure (basin-hopping) Wang-Landau sampling of the
Fe/MgO flat<->island transition on an AGOX GPR surrogate. No DFT anywhere.

Loads every seed database in data/femgo, trains a single GPR surrogate on the
combined structures, then runs the LandauPlusSampler (basin-hopping Markov WL
walk initialised at the flat reference) to compute the inherent-structure
density of states g(E) and from it Z, F, C_V at a set of temperatures, plus the
reweightable ensemble of accepted (relaxed) structures.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]

IMPORTANT: the flat/island weight is rattle-amplitude (delta) sensitive. Test
multiple --rattle values before trusting the flat/island ratio.
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os
import sys
from pathlib import Path

import numpy as np

# --- Make `landau_plus` importable from this directory ----------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import matplotlib
matplotlib.use("Agg")

from landau_plus.gpr_training import load_all_seeds, build_gpr, validate_gpr
from landau_plus.wang_landau_sampler import LandauPlusSampler
from landau_plus.thermodynamics import (
    g_of_E_to_thermodynamics, heat_capacity_from_thermo)

DATA_DIR = os.path.join(_HERE, "data", "femgo")


def main():
    p = argparse.ArgumentParser(
        description="Landau-Plus basin-hopping Wang-Landau sampling on a GPR "
                    "surrogate (no DFT)")
    p.add_argument("--dataset", default=DATA_DIR,
                   help="Dataset dir holding seed_*/1_db/db_*.db "
                        f"(default {DATA_DIR})")
    p.add_argument("--n-bins", type=int, default=50,
                   help="Number of energy bins, default 50")
    p.add_argument("--e-min", type=float, default=0.0,
                   help="Lower bin edge (eV/atom rel), default 0.0")
    p.add_argument("--e-max", type=float, default=0.75,
                   help="Upper bin edge (eV/atom rel), default 0.75 "
                        "(margin over the flat-basin top ~0.67)")
    p.add_argument("--e-reject", type=float, default=None,
                   help="Relative energy (eV/atom) above which a trial is "
                        "rejected as GPR extrapolation (default 5*e_max)")
    p.add_argument("--rattle", type=float, default=1.5,
                   help="Uniform-in-volume rattle amplitude of the Fe atoms "
                        "(Angstrom), default 1.5. TEST MULTIPLE VALUES — the "
                        "flat/island weight is delta-sensitive.")
    p.add_argument("--relax-steps", type=int, default=100,
                   help="GPR BFGS relaxation steps per trial (GO run's cap), "
                        "default 100")
    p.add_argument("--perturb-symbols", default="Fe",
                   help="Symbols of atoms to rattle/relax, comma-separated, "
                        "default 'Fe'")
    p.add_argument("--flat-island-spread", type=float, default=1.0,
                   help="Fe z-spread threshold (Angstrom) for flat vs island "
                        "labelling, default 1.0")
    p.add_argument("--flatness-criterion", type=float, default=0.80,
                   help="Flatness threshold, default 0.80")
    p.add_argument("--check-interval", type=int, default=5000,
                   help="Flatness check interval (MC steps), default 5000")
    p.add_argument("--n-stages-standard", type=int, default=14,
                   help="Standard-scheme halvings before switching to 1/t, "
                        "default 14")
    p.add_argument("--mc-steps", type=int, default=50000,
                   help="Number of WL MC steps, default 50000")
    p.add_argument("--temperatures", default="100,200,300,500,1000",
                   help="Comma-separated temperatures (K), default "
                        "100,200,300,500,1000")
    p.add_argument("--output", default=os.path.join(_HERE, "lp_output"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed for the sampler RNG, default 42")
    p.add_argument("--use-ray", action="store_true",
                   help="Enable Ray in GPR training (default: single-process)")
    args = p.parse_args()

    # --- 1. Load the dataset ------------------------------------------------
    print("=" * 70)
    print(f"Loading dataset from {args.dataset}")
    structures, energies, db_paths = load_all_seeds(args.dataset)
    print(f"  Total: {len(structures)} structures, {len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()} "
          f"({len(structures[0])} atoms)")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 2. Train the GPR surrogate -----------------------------------------
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures, use_ray=args.use_ray)
    validate_gpr(gpr, structures, energies)

    # --- 3. Run Landau-Plus --------------------------------------------------
    print("\nRunning Landau-Plus basin-hopping Wang-Landau sampling...")
    sampler = LandauPlusSampler(
        gpr=gpr,
        db_structures=structures,
        db_energies=energies,
        n_bins=args.n_bins,
        e_min=args.e_min,
        e_max=args.e_max,
        e_reject=args.e_reject,
        rattle=args.rattle,
        relax_steps=args.relax_steps,
        perturb_symbols=args.perturb_symbols,
        flat_island_spread_aa=args.flat_island_spread,
        flatness_criterion=args.flatness_criterion,
        check_interval=args.check_interval,
        n_stages_standard=args.n_stages_standard,
        rng=np.random.default_rng(args.rng),
    )
    sampler.initialize()
    sampler.run(n_steps=args.mc_steps,
                progress_every=max(args.check_interval, 1))
    sampler.save(args.output)
    bin_centers_rel, ln_g = sampler.g_of_E()
    E_ref = sampler.E_ref
    n_atoms = sampler.n_atoms

    # --- 4. Thermodynamics ---------------------------------------------------
    temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
    therm_rows = g_of_E_to_thermodynamics(
        bin_centers_rel, ln_g, E_ref, n_atoms, temps)
    out = Path(args.output)
    np.savetxt(out / "thermodynamics.csv",
               np.asarray(therm_rows, dtype=float), delimiter=',',
               header='T_K,beta_eV-1,logZ,Z,F_eV', comments='')
    print("\nThermodynamics (from normalised g(E)):")
    print("  T(K)   beta(eV^-1)   logZ      Z          F(eV)")
    for (T, beta, logZ, Z, F) in therm_rows:
        print(f"  {T:6.1f}  {beta:11.6f}  {logZ:9.4f}  {Z:9.4e}  {F:9.4f}")

    cv = heat_capacity_from_thermo(therm_rows)
    if cv:
        np.savetxt(out / "heat_capacity.csv",
                   np.asarray(cv, dtype=float), delimiter=',',
                   header='T_K,C_V_eV_per_K', comments='')
        print("\nHeat capacity C_V (needs >=3 temperatures):")
        for (T, c) in cv:
            print(f"  T = {T:6.1f} K:  C_V = {c:9.4f} eV/K")

    _plot_g_of_E(bin_centers_rel, ln_g, out)

    print(f"\nDone. Results written to {out}")


def _plot_g_of_E(bin_centers_rel, ln_g, output_dir):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(bin_centers_rel, ln_g, "o-", ms=3)
    ax.set_xlabel(r"$(E - E_{\\mathrm{min}})/N$  (eV/atom)")
    ax.set_ylabel(r"$\\ln g(E)$")
    ax.set_title("Landau-Plus inherent-structure density of states $g(E)$")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "g_of_E.png", dpi=150)
    plt.close(fig)
    print(f"  Wrote g_of_E.png to {output_dir}")


if __name__ == "__main__":
    main()