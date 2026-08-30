#!/usr/bin/env python3
"""
Nested Sampling over the combined multi-seed Fe/MgO AGOX dataset.

Loads EVERY structure from every seed database in dataset/seed_*/1_db/db_*.db,
trains a single GPR surrogate on the combined 1297 structures, then runs the
NestedSampler from the `nested_sampling` package on the combined dataset.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]

    /home/think/miniconda3/envs/agox_v2/bin/python main.py \
    --temperature-free --temperatures 100,200,300,500,1000 \
    --n-live 100 --n-iters 1000 --perturb 0.01 --output ./ns_output_tfree --rng 42

This script relies on:
  - the `nested_sampling` package in this directory (imported as a package)
  - the AGOX / ASE stack installed in the agox_v2 conda env
"""

from __future__ import annotations

__version__ = "1.7.0"

import os
import sys
import glob
import argparse
from pathlib import Path

import numpy as np

# --- Make `nested_sampling` importable from this directory -------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# AGOX imports
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

# Nested sampling package
from nested_sampling.nested_sampler import NestedSampler
from nested_sampling.utils import K_B
from nested_sampling.state_density import analyze_state_density, analyze_saved_output


# =============================================================================
# Parameters
# =============================================================================
DATASET_DIR = os.path.join(_HERE, "dataset")
DB_PATTERN = "seed_*/1_db/db_*.db"        # every seed in the dataset


# =============================================================================
# Helpers
# =============================================================================
def load_all_seeds(dataset_dir: str, pattern: str):
    """Load and concatenate all structures/energies from every seed DB.

    Returns
    -------
    structures : list of ase.Atoms
        All structures from all seeds (1297 total).
    energies : np.ndarray
        Potential energy of each structure (eV).
    db_paths : list of str
        Database files that were loaded.
    """
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, pattern)))
    if not db_paths:
        raise FileNotFoundError(
            f"No databases matched {os.path.join(dataset_dir, pattern)}"
        )

    structures = []
    energies = []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        traj = db.restore_to_trajectory()
        structures.extend(traj)
        energies.extend(a.get_potential_energy() for a in traj)
        print(f"  {os.path.relpath(p)}: {len(traj)} structures")

    energies = np.asarray(energies, dtype=float)
    return structures, energies, db_paths


def build_gpr(traj):
    """Build the GPR surrogate (AGOX recipe from dataset/main.py)."""
    descriptor = Fingerprint.from_atoms(traj[0])
    print(f"  Descriptor feature dim: {descriptor.create_features(traj[0]).shape[1]}")

    bk = 0.01
    kernel = (
        C(5000, (1, 1e5)) *
        (C(bk, (bk, bk)) * RBF() +
         C(1 - bk, (1 - bk, 1 - bk)) * RBF())
        + Noise(0.01, (0.01, 0.01))
    )

    gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(),
              use_ray=True)
    print(f"  Training on {len(traj)} structures...")
    gpr.train(traj)
    print("  GPR training done.")
    return gpr


# =============================================================================
# Main
# =============================================================================
def main():
    p = argparse.ArgumentParser(
        description="Nested sampling on the combined multi-seed Fe/MgO dataset"
    )
    p.add_argument("--temp", type=float, default=300.0,
                   help="Temperature (K), default 300 (fixed-T mode only)")
    p.add_argument("--temperature-free", action="store_true",
                   help="Temperature-free nested sampling: beta is kept OUT of the "
                        "likelihood (energy-constrained top-down pass, consistent "
                        "with Partay 2021 / Yang 2024). Post-processes Z(beta)/"
                        "free-energy/posterior at each --temperatures value.")
    p.add_argument("--temperatures", default="100,200,300,500,1000",
                   help="Comma-separated temperatures (K) at which to evaluate "
                        "Z, free energy F=-k_B T ln Z and the posterior in "
                        "temperature-free mode (default 100,200,300,500,1000)")
    p.add_argument("--n-live", type=int, default=50,
                   help="Number of live points, default 50")
    p.add_argument("--n-iters", type=int, default=300,
                   help="Nested sampling iterations, default 300")
    p.add_argument("--perturb", type=float, default=0.01,
                   help="Perturbation amplitude (A), default 0.01")
    p.add_argument("--perturb-symbols", default="Fe",
                   help="Symbol(s) of atoms to perturb (deposition layer), "
                        "comma-separated for multiple, e.g. 'Fe,B' or 'Fe, B'; "
                        "default 'Fe'. All matching atoms move; all others stay fixed")
    p.add_argument("--e-max-per-atom", type=float, default=None,
                   help="Exclude structures whose RELATIVE energy above the dataset "
                        "minimum exceeds this threshold (eV/atom), i.e. keep "
                        "(E/atom - min E/atom) <= value. Applies to the dataset used "
                        "for nested sampling, the GPR training data, AND the initial "
                        "sampler structures (filtered once after loading). Use to "
                        "drop high-energy outlier structures that break the GPR fit, "
                        "e.g. --e-max-per-atom 0.67. Default: None (keep all).")
    p.add_argument("--e-window-lo", type=float, default=None,
                   help="Lower bound of the windowed initial-live seeding (eV/atom "
                        "above the global minimum). When both --e-window-lo and "
                        "--e-window-hi are set, ONE initial live point (the 'worst') "
                        "is found by bounded-attempt search with rel energy in "
                        "[lo, hi]; the remaining live points are uniform draws capped "
                        "at hi. rel uses the GPR-predicted energy. Default: None "
                        "(windowed seeding disabled).")
    p.add_argument("--e-window-hi", type=float, default=None,
                   help="Upper bound of the windowed initial-live seeding (eV/atom "
                        "above the global minimum); also the cap on the remaining "
                        "initial live draws. See --e-window-lo. Default: None.")
    p.add_argument("--e-window-max-attempts", type=int, default=1000,
                   help="Max attempts to find a structure in the windowed seeding "
                        "band [lo, hi]; a RuntimeError is raised if not found within "
                        "this many draws. Default: 1000.")
    p.add_argument("--walk", action="store_true",
                   help="Enable the dual-scale constrained MC walk (Fortran-style "
                        "clone-and-walk) in sample_constrained. Clones a random "
                        "surviving live point and evolves it with Gaussian steps, "
                        "falling back to rejection draws if the walk fails.")
    p.add_argument("--walk-steps", type=int, default=40,
                   help="Number of trial steps in the constrained walk (the Fortran "
                        "'mixing_steps'). Default: 40.")
    p.add_argument("--walk-small", type=float, default=0.05,
                   help="Small displacement scale (Angstrom) for the constrained walk. "
                        "Default: 0.05.")
    p.add_argument("--walk-large", type=float, default=0.40,
                   help="Large displacement scale (Angstrom) for the constrained walk "
                        "(barrier crossing). Default: 0.40.")
    p.add_argument("--walk-mode", type=str, default="both",
                   choices=["both", "small", "large"],
                   help="Which displacement scale(s) to use in the walk: 'both' (50/50 "
                        "small/large, Fortran default), 'small' (only small steps), "
                        "'large' (only large steps). Default: both.")
    p.add_argument("--walk-exclude-worst", action="store_true",
                   help="When the walk is enabled, clone ONLY from live points "
                        "EXCLUDING the worst one (Fortran-style: don't clone the "
                        "walker being replaced). Default False = clone uniformly "
                        "over all live points.")
    p.add_argument("--novelty-threshold", type=float, default=None,
                   help="Minimum Euclidean distance (in AGOX Fingerprint feature "
                        "space) between any two INITIAL live points. When >0, the "
                        "initial live set is de-duplicated: each initial live point "
                        "must be >= this far from all already-kept ones. Applied "
                        "ONLY at initialization (windowed anchor + fills + default "
                        "draws); GPR training and the run use the full DB. "
                        "Default: None (disabled).")
    p.add_argument("--novelty-max-attempts", type=int, default=500,
                   help="Max prior draws to find a novel initial live point before "
                        "accepting the last draw anyway. Default: 500.")
    p.add_argument("--output", default=os.path.join(_HERE, "ns_output_allseeds"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42,
                   help="Random seed for the sampler RNG")
    p.add_argument("--analysis-dir", default=None,
                   help="Directory for the state-density/landscape analysis "
                        "outputs (default: <--output>/analysis)")
    p.add_argument("--no-analysis", action="store_true",
                   help="Skip the state-density / landscape analysis that runs "
                        "automatically after sampling")
    p.add_argument("--no-posterior-xsf", action="store_true",
                   help="Do NOT write the posterior structure .xsf files (fixed-T "
                        "posterior_structures/ and temperature-free posterior_T{KKK}/). "
                        "The posterior_summary.csv (rank, energy, weight) is still "
                        "written. Default: False (xsf files are saved as before). "
                        "Note: disabling xsf means saved-run re-analysis via "
                        "--analyze-only will not find the structures.")
    p.add_argument("--analyze-only", default=None, metavar="RUN_OUTPUT_DIR",
                   help="Re-run the state-density / landscape analysis on an "
                        "already-finished run's output directory (must contain "
                        "posterior_structures/ and posterior_summary.csv). "
                        "Skips data loading, GPR training and sampling. "
                        "Requires --output for the analysis destination.")
    args = p.parse_args()

    # --- 0. Standalone re-analysis of a saved run ----------------------------
    if args.analyze_only:
        analysis_dir = args.analysis_dir or os.path.join(args.output, "analysis")
        print("=" * 70)
        print("Standalone analysis of a saved nested-sampling run")
        print(f"  run output   : {args.analyze_only}")
        print(f"  analysis dir : {analysis_dir}")
        print("=" * 70)
        # training set (structures + DFT energies) for comparison
        structures, energies, _ = load_all_seeds(DATASET_DIR, DB_PATTERN)
        if args.e_max_per_atom is not None:
            n_atoms = len(structures[0])
            e_per_atom = np.asarray(energies, dtype=float) / n_atoms
            keep = (e_per_atom - e_per_atom.min()) <= args.e_max_per_atom
            structures = [s for s, k in zip(structures, keep) if k]
            energies = np.asarray(energies, dtype=float)[keep]
            print(f"  --e-max-per-atom {args.e_max_per_atom}: {len(structures)} "
                  f"structures remain (relative filter)")
        print(f"  Training set: {len(structures)} structures")
        analyze_saved_output(
            run_output_dir=args.analyze_only,
            training_structures=structures,
            training_energies=energies,
            output_dir=analysis_dir,
            normalize_density=False,
            e_max=None,
        )
        print("\nDone (standalone analysis).")
        return

    # --- 1. Load the combined multi-seed dataset -----------------------------
    print("=" * 70)
    print("Loading combined dataset from all seeds")
    print(f"  Pattern: {DB_PATTERN}")
    structures, energies, db_paths = load_all_seeds(DATASET_DIR, DB_PATTERN)
    print(f"  Total: {len(structures)} structures, "
          f"{len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()}")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 1b. Optional high-energy outlier exclusion (relative to dataset min) ---
    if args.e_max_per_atom is not None:
        n_atoms = len(structures[0])
        e_per_atom = np.asarray(energies, dtype=float) / n_atoms
        rel_e = e_per_atom - e_per_atom.min()   # relative to dataset min
        keep = rel_e <= args.e_max_per_atom
        n_drop = int((~keep).sum())
        structures = [s for s, k in zip(structures, keep) if k]
        energies = np.asarray(energies, dtype=float)[keep]
        print(f"  --e-max-per-atom {args.e_max_per_atom} (relative to dataset min "
              f"E/atom = {e_per_atom.min():.4f} eV/atom): dropped {n_drop} "
              f"high-energy structures (E/atom - min > {args.e_max_per_atom}); "
              f"{len(structures)} remain")
        if len(structures) == 0:
            raise SystemExit(f"No structures remain after --e-max-per-atom "
                             f"{args.e_max_per_atom} exclusion.")

    # --- 2. Train GPR on the combined dataset --------------------------------
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures)

    # Sanity check the surrogate on a few training points
    print("\nValidation (first 5):")
    print("  idx  DFT_E(eV)    GPR_E(eV)    delta(eV)")
    for i in range(min(5, len(structures))):
        Ed = energies[i]
        Eg = gpr.predict_energy(structures[i])
        print(f"  {i:3d}  {Ed:10.4f}  {Eg:10.4f}  {Eg-Ed:10.4f}")

    # --- 3. Run nested sampling ----------------------------------------------
    if args.temperature_free:
        print(f"\nTemperature-free mode: beta kept OUT of the likelihood "
              f"(energy-constrained top-down pass).")
        print(f"Post-processing temperatures: {args.temperatures} K")
        sampler = NestedSampler(
            gpr=gpr,
            db_structures=structures,
            db_energies=energies,
            n_live=args.n_live,
            perturb=args.perturb,
            perturb_symbols=args.perturb_symbols,
            rng=np.random.default_rng(args.rng),
            temperature_free=True,
            e_window_lo=args.e_window_lo,
            e_window_hi=args.e_window_hi,
            e_window_max_attempts=args.e_window_max_attempts,
            walk=args.walk,
            walk_steps=args.walk_steps,
            walk_small=args.walk_small,
            walk_large=args.walk_large,
            walk_mode=args.walk_mode,
            walk_exclude_worst=args.walk_exclude_worst,
            novelty_threshold=args.novelty_threshold,
            novelty_max_attempts=args.novelty_max_attempts,
        )
    else:
        beta = 1.0 / (K_B * args.temp)
        print(f"\nbeta = {beta:.6f} eV^-1  (T = {args.temp} K)")
        print(f"perturb = {args.perturb} A")
        sampler = NestedSampler(
            gpr=gpr,
            db_structures=structures,
            db_energies=energies,
            n_live=args.n_live,
            beta=beta,
            temperature=args.temp,
            perturb=args.perturb,
            perturb_symbols=args.perturb_symbols,
            rng=np.random.default_rng(args.rng),
            e_window_lo=args.e_window_lo,
            e_window_hi=args.e_window_hi,
            e_window_max_attempts=args.e_window_max_attempts,
            walk=args.walk,
            walk_steps=args.walk_steps,
            walk_small=args.walk_small,
            walk_large=args.walk_large,
            walk_mode=args.walk_mode,
            walk_exclude_worst=args.walk_exclude_worst,
            novelty_threshold=args.novelty_threshold,
            novelty_max_attempts=args.novelty_max_attempts,
        )

    sampler.initialize()
    sampler.run(n_iterations=args.n_iters, progress_every=20)
    sampler.save(args.output, save_xsf=not args.no_posterior_xsf)

    # --- 3b. Temperature-free post-processing --------------------------------
    if args.temperature_free:
        output_dir = Path(args.output)
        temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
        therm_rows = []
        for T in temps:
            beta = 1.0 / (K_B * T)
            Z, logZ = sampler.evaluate(beta)
            F = -K_B * T * logZ          # free energy F = -k_B T ln Z  (eV)
            structs, weights = sampler.posterior_at(beta)
            # per-T posterior structures + summary
            tdir = output_dir / f"posterior_T{int(T)}"
            tdir.mkdir(exist_ok=True)   # always created (holds posterior_summary.csv)
            order = np.argsort(-weights)
            summary_rows = []
            for rank, idx in enumerate(order):
                s = structs[idx]
                E = gpr.predict_energy(s)
                w = weights[idx]
                if not args.no_posterior_xsf:
                    from ase.io import write as ase_write
                    ase_write(tdir / f"posterior_{rank:03d}_w{w:.4e}_E{E:.3f}.xsf", s)
                summary_rows.append((rank, E, w))
            np.savetxt(tdir / "posterior_summary.csv",
                       np.asarray(summary_rows, dtype=float), delimiter=',',
                       header='rank,energy_eV,weight', comments='')
            print(f"  T = {T:.1f} K:  Z = {Z:.6e}  (log Z = {logZ:.4f})  "
                  f"F = {F:.4f} eV  -> {len(structs)} posterior samples"
                  + ("" if not args.no_posterior_xsf
                     else " (xsf writing disabled by --no-posterior-xsf)"))
            therm_rows.append((T, beta, logZ, Z, F))
        np.savetxt(output_dir / "thermodynamics.csv",
                   np.asarray(therm_rows, dtype=float), delimiter=',',
                   header='T_K,beta_eV-1,logZ,Z,F_eV', comments='')
        print(f"  Wrote thermodynamics.csv (T, beta, logZ, Z, F=-k_B T ln Z) to {output_dir}")

    # --- 4. State-density / landscape analysis -------------------------------
    if not args.no_analysis:
        analysis_dir = args.analysis_dir or os.path.join(args.output, "analysis")
        print("\nRunning state-density / landscape analysis of results...")
        analyze_state_density(
            posterior_structures=sampler.posterior_samples,
            training_structures=structures,
            gpr=gpr,
            output_dir=analysis_dir,
            normalize_density=False,
            e_max=None,
        )
    else:
        print("\nSkipping state-density analysis (--no-analysis).")

    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
