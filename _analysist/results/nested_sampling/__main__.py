#!/usr/bin/env python3
"""CLI entry point for nested sampling."""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

# Ensure the project root is importable
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from nested_sampling.gpr_training import train_gpr
from nested_sampling.nested_sampler import NestedSampler
from nested_sampling.utils import K_B


def main():
    p = argparse.ArgumentParser(description="Nested sampling with AGOX GPR")
    p.add_argument("--db-dir", default="_analysist/1_result/"
                   "19_kappa2_iter100_trajNoSave_repSeedDat0_5x5",
                   help="AGOX result directory")
    p.add_argument("--seed", type=int, default=3, help="Seed number")
    p.add_argument("--temp", type=float, default=300.0, help="Temperature (K)")
    p.add_argument("--n-live", type=int, default=50, help="Live points")
    p.add_argument("--n-iters", type=int, default=200, help="Iterations")
    p.add_argument("--output", default="./ns_output", help="Output dir")
    p.add_argument("--db-file", default=None, help="Direct .db path")
    p.add_argument("--perturb", type=float, default=0.01,
                   help="Perturbation amplitude (A, 0.01 default, 0 = none)")
    args = p.parse_args()

    if args.db_file:
        db_path = args.db_file
    else:
        db_path = os.path.join(args.db_dir, f"seed_{args.seed}", "1_db", f"db_{args.seed}.db")

    if not os.path.exists(db_path):
        print(f"ERROR: DB not found: {db_path}")
        sys.exit(1)

    gpr, structures, energies = train_gpr(db_path)

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
        rng=np.random.default_rng(42),
    )

    sampler.initialize()
    sampler.run(n_iterations=args.n_iters, progress_every=20)
    sampler.save(args.output)
    print("\nDone.")


if __name__ == "__main__":
    main()
