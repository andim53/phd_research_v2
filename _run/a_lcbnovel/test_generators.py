"""
Test each generator in main.py by generating candidate structures and writing
them as .xsf files into `_tmp/`.

Replicates the environment and wiring from main.py, but with B doping ENABLED
(B6Fe25 deposition layer) so that all three generators are exercised
(GlobalPermutationGenerator only activates when NUM_ATOMS_ADD > 0).

Generator order (as in main.py build_stack):
    [0] HeteroStructRandomize   (built from scratch, sampler=None)
    [1] RattleGenerator          (chained from the hetero candidate via FixedSampler)
    [2] GlobalPermutationGenerator (chained from the hetero candidate via FixedSampler)

Usage:
    /home/think/miniconda3/envs/agox_v2/bin/python test_generators.py
    # optional: N_SAMPLES / SEED / OUT_DIR via CLI flags
"""

__version__ = "1.0.0"

import argparse
import os

import numpy as np
from ase.io import write
from agox.generators import RattleGenerator
from agox.samplers import FixedSampler

from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows
from scripts.global_permutation_generator import GlobalPermutationGenerator

# Imported from main.py to reuse the exact same environment/config
from main import (
    VACUUM, A_MGO, A_FE, DIST_Z_FE2O, SUPERCELL,
    MGO_LAYER_NUMBER, FE_LAYER_NUMBER, CONFINEMENT_CELL_HEIGHT_MULTIPLYER,
    SAMPLE_SIZE, RATTLE_AMPLITUDE, HETERO_RATTLE_AMPLITUDE,
    NUM_ATOMS_ADD, SYMBOL_ADD, Z_HEIGHT_ADD, NUM_CANDIDATES_B,
    build_slabs, build_environment,
)


def build_generators(environment, slab_deposition, num_b):
    """Construct the three generators exactly as main.py's build_stack does (B-enabled)."""
    n_rattle = len(slab_deposition)
    generators = [
        HeteroStructRandomize(
            **environment.get_confinement(),
            slab_deposition=slab_deposition,
            hetero_slab_dist=DIST_Z_FE2O,
            rattle_amplitude=HETERO_RATTLE_AMPLITUDE,
            n_rattle=n_rattle,
            generate_pristine=False,
            write_struct=True,
        ),
        RattleGenerator(
            **environment.get_confinement(),
            n_rattle=int(n_rattle * 0.5),
            rattle_amplitude=RATTLE_AMPLITUDE,
        ),
        GlobalPermutationGenerator(
            **environment.get_confinement(),
            max_number_of_swaps=num_b,
            rattle_strength=0.5,
        ),
    ]
    return generators


def main():
    ap = argparse.ArgumentParser(description="Test each generator in main.py -> _tmp/*.xsf")
    ap.add_argument("--n-samples", type=int, default=10, help="candidates per generator")
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--out-dir", type=str, default="./_tmp")
    ap.add_argument("--num-b", type=int, default=NUM_ATOMS_ADD,
                    help="B dopant count (defaults to main.py NUM_ATOMS_ADD; pass >0 to enable B)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Build the substrate + deposition slabs (same as main.py)
    slab_substrate, slab_deposition, strain = build_slabs()
    print(f"Lattice match: strain vs Fe = {strain:.2f}%")

    # Apply B doping so all three generators (incl. permutation) are exercised
    num_b = args.num_b
    if num_b > 0:
        slab_deposition = add_adsorbate_to_hollows(
            slab_deposition, symbol=SYMBOL_ADD, height=Z_HEIGHT_ADD,
            num_atoms=num_b, seed=args.seed,
        )
        print(f"B-doped deposition layer -> {slab_deposition.get_chemical_formula()} "
              f"({len(slab_deposition)} atoms)")
    else:
        print("No B doping (num_b=0) -> permutation generator will be inert; "
              "pass --num-b > 0 to test it.")

    # Build the environment (same confinement as main.py)
    env = build_environment(slab_substrate.copy(), slab_deposition)
    generators = build_generators(env, slab_deposition, num_b)
    gen_names = ["hetero", "rattle", "permut"]

    for i in range(args.n_samples):
        # HeteroStructRandomize is built from scratch
        hetero_candidate = generators[0](sampler=None, environment=env)[0]
        write(f"{args.out_dir}/{gen_names[0]}_candidate_{i}.xsf", hetero_candidate)

        # Rattle + Permutation are chained from the hetero candidate via FixedSampler
        sampler = FixedSampler(hetero_candidate)
        write(f"{args.out_dir}/{gen_names[1]}_candidate_{i}.xsf",
              generators[1](sampler, env)[0])
        write(f"{args.out_dir}/{gen_names[2]}_candidate_{i}.xsf",
              generators[2](sampler, env)[0])

        print(f"sample {i}: wrote {gen_names[0]}/{gen_names[1]}/{gen_names[2]} candidates")

    print(f"\nDone. {args.n_samples} x 3 candidates written to {args.out_dir}/")


if __name__ == "__main__":
    main()
