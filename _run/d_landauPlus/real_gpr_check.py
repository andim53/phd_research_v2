#!/usr/bin/env python3
"""Short real-GPR wiring check for d_landauPlus.

Loads the femgo data, trains the real GPR, validates GPR-vs-DFT on a few
structures, confirms the descriptor feature dim, then runs a tiny LandauPlus
walk (a few steps) to confirm the real surrogate feeds the relax path (forces +
energy) correctly. This is the M5 fingerprint-space check + the "real GPR
drives BFGS" check the fake smoke test could not cover.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python real_gpr_check.py [--mc-steps N]
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from landau_plus.gpr_training import load_all_seeds, build_gpr, validate_gpr
from landau_plus.wang_landau_sampler import LandauPlusSampler

DATA_DIR = os.path.join(_HERE, "data", "femgo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc-steps", type=int, default=15,
                    help="tiny walk length for the wiring check, default 15")
    args = ap.parse_args()

    t0 = time.time()
    structures, energies, db_paths = load_all_seeds(DATA_DIR)
    print(f"[check] loaded {len(structures)} structures in "
          f"{time.time()-t0:.1f}s")

    t0 = time.time()
    gpr = build_gpr(structures, use_ray=False)
    print(f"[check] GPR trained in {time.time()-t0:.1f}s")
    validate_gpr(gpr, structures, energies, n_show=3)

    # --- M5 explicit check: descriptor feature dim + a single relax step ----
    from agox.models.descriptors.fingerprint import Fingerprint
    desc = Fingerprint.from_atoms(structures[0])
    dim = desc.create_features(structures[0]).shape[1]
    print(f"[check] Fingerprint feature dim = {dim}")

    # --- tiny walk to confirm the real GPR drives rattle+relax+accept -------
    sampler = LandauPlusSampler(
        gpr=gpr, db_structures=structures, db_energies=energies,
        n_bins=50, e_min=0.0, e_max=0.75, rattle=1.5, relax_steps=20,
        perturb_symbols="Fe", flat_island_spread_aa=1.0,
        check_interval=1000, n_stages_standard=14,
        rng=np.random.default_rng(42),
    )
    sampler.initialize()
    t0 = time.time()
    sampler.run(n_steps=args.mc_steps, progress_every=max(args.mc_steps, 1))
    print(f"[check] {args.mc_steps}-step walk ran in {time.time()-t0:.1f}s; "
          f"ensemble size = {len(sampler.ensemble_structs)}")

    if len(sampler.ensemble_structs) < 2:
        print("[check] WARNING: walk accepted <2 structures (expected at tiny n)")
    print("[check] real-GPR wiring check COMPLETE")


if __name__ == "__main__":
    main()