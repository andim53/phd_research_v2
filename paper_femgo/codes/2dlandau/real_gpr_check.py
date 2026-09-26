#!/usr/bin/env python3
"""Short real-GPR wiring check for 2dlandau.

Loads the femgo data, trains the real GPR, validates GPR-vs-DFT, confirms the
Fingerprint feature dim, then runs a TINY 2D Landau walk (a few steps) to
confirm the real surrogate drives the generate->relax->bin path (forces +
energy). This is the M3 extrapolation checkpoint + the "real GPR drives BFGS"
check the fake smoke test cannot cover.

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

from landau_2d.gpr_training import load_all_seeds, build_gpr, validate_gpr
from landau_2d.generator import DeltaZGenerator
from landau_2d.wang_landau_2d import WangLandau2DSampler

DATA_DIR = os.path.join(_HERE, "..", "data", "femgo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc-steps", type=int, default=8,
                    help="tiny walk length for the wiring check, default 8")
    ap.add_argument("--reference-steps", type=int, default=5)
    args = ap.parse_args()

    t0 = time.time()
    structures, energies, db_paths = load_all_seeds(DATA_DIR)
    print(f"[check] loaded {len(structures)} structures in "
          f"{time.time()-t0:.1f}s")

    t0 = time.time()
    gpr = build_gpr(structures, use_ray=False)
    print(f"[check] GPR trained in {time.time()-t0:.1f}s")
    validate_gpr(gpr, structures, energies, n_show=3)

    from agox.models.descriptors.fingerprint import Fingerprint
    desc = Fingerprint.from_atoms(structures[0])
    dim = desc.create_features(structures[0]).shape[1]
    print(f"[check] Fingerprint feature dim = {dim}")

    gen = DeltaZGenerator(structures[0], z_contact=None, contact_gap=2.08,
                          rng=np.random.default_rng(0))
    print(f"[check] z_contact = {gen.z_contact:.4f} A")

    # film-height range: flat ~ contact gap, top = natural island height
    dz_min = gen.z_contact - gen.substrate_top_z
    i_min = int(np.argmin(energies))
    dz_max = gen.fe_film_height(structures[i_min])
    print(f"[check] dZ range (film height): [{dz_min:.3f}, {dz_max:.3f}] A")

    # --- M3: GPR prediction spread on dZ-extreme generated structures -------
    print("[check] M3 extrapolation spot-check (dZ-extreme structures):")
    for dzt in [dz_min, dz_max]:
        es = [gpr.predict_energy(gen(dzt)) for _ in range(5)]
        es = np.asarray(es)
        print(f"  dZ_target={dzt:4.2f} A -> E mean {es.mean():.3f} "
              f"std {es.std():.3f} eV")

    sampler = WangLandau2DSampler(
        gpr=gpr, generator=gen, E_ref=energies.min(), n_atoms=len(structures[0]),
        n_e_bins=35, e_min=0.0, e_max=0.7,
        n_dz_bins=12, dz_min=dz_min, dz_max=dz_max,
        relax_steps=20, flat_island_spread_aa=1.0,
        check_interval=1000, n_stages_standard=14,
        reference_steps=args.reference_steps,
        rng=np.random.default_rng(42),
    )
    sampler.initialize()
    t0 = time.time()
    sampler.run(n_steps=args.mc_steps, progress_every=max(args.mc_steps, 1))
    print(f"[check] {args.mc_steps}-step walk ran in {time.time()-t0:.1f}s; "
          f"ensemble size = {len(sampler.ensemble_structs)}")
    if len(sampler.ensemble_structs) < 1:
        print("[check] WARNING: walk accepted 0 structures (expected at tiny n)")
    print("[check] real-GPR wiring check COMPLETE")


if __name__ == "__main__":
    main()
