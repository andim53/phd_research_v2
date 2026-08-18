"""
Extracted from main_test.ipynb (cell 9).
Section: Cell Scale Sweep
"""
import sys
import os
# Make the repo-local `scripts/` package importable regardless of cwd:
# walk up from this file until we find the directory containing `scripts/`.
_HERE = os.path.dirname(os.path.abspath(__file__))
_d = _HERE
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, 'scripts')):
        if _d not in sys.path:
            sys.path.insert(0, _d)
        break
    _d = os.path.dirname(_d)


import os
import json
from pathlib import Path
import numpy as np

# ASE Imports
from ase import Atoms
from ase.build import bulk
from ase.io import write

# AGOX Core & Utilities
from agox.environments import Environment
from agox.generators import RattleGenerator
from agox.samplers import FixedSampler

# Custom Scripts
# from scripts.amorph_struct_randomize import AmorphStructRandomize
# from scripts.amorph_permutation import AmorphPermutationGenerator
from scripts.generate_interstitial_alloy import generate_interstitial_alloy

# === CONFIGURATION PARAMETERS ===

# Host Material & Crystal Structure Settings
HOST_ELEMENT = "Pt"
CRYSTAL_STRUCTURE = "fcc"
LATTICE_CONSTANT = 3.30
SUPERCELL_DIM = (3, 3, 3)

# Interstitial Element & Alloy Settings
INTERSTITIAL_ELEMENT = "P"
CONCENTRATION_PERCENT = 20.0  # Desired interstitial concentration (%)

# Cell Volume Scaling Sweep Parameters
SCALE_START = 1.00
SCALE_STEP = 0.01
N_SCALE_LOOP = 1000
N_STRUCTURE_CHECK = 5

# Generator & Perturbation Parameters
MAX_SWAPS = 20
RAND_ATTEMPTS = 1
PERMUT_ATTEMPTS = 10
RATTLE_AMPLITUDE = 1.5
RATTLE_STRENGTH = 1.5  # For permutation generator

# Overlap & Validation Constraints
CHECK_OVERLAP = True
CHECK_COVALENT = False
MIN_DISTANCE_SCALE = 0.85
MAX_DISTANCE_SCALE = 1.15

# Output Settings
OUTPUT_JSON_PATH = "valid_cell_scale.json"

# === INITIALIZE SWEEP VARIABLES ===

valid_scales = []
best_results = []
save_json = {f"{INTERSTITIAL_ELEMENT}_concentration: {CONCENTRATION_PERCENT}%": []}

# === CELL SCALE SWEEP LOOP ===

for scale_idx in range(N_SCALE_LOOP):
    scale_cell = SCALE_START + scale_idx * SCALE_STEP

    # Establish Directory Structures
    path_result = Path(f"0_result/scale_{scale_cell:.4f}")
    path_xsf = path_result / "0_xsf"
    
    path_result.mkdir(parents=True, exist_ok=True)
    path_xsf.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"Testing Scale Cell: {scale_cell:.4f}")
    print("=" * 80)

    # === Structure Generation ===
    host_bulk = bulk(HOST_ELEMENT, CRYSTAL_STRUCTURE, a=LATTICE_CONSTANT, cubic=True)
    host_bulk.set_cell(host_bulk.cell * scale_cell, scale_atoms=True)

    # Calculate number of interstitials to insert dynamically
    amount_a = len(host_bulk * SUPERCELL_DIM)
    concentration_decimal = CONCENTRATION_PERCENT / 100.0
    amount_b = (concentration_decimal * amount_a) / (1.0 - concentration_decimal)
    num_to_add = int(round(amount_b))
    
    print(f"-> Host atoms: {amount_a}, Target: {CONCENTRATION_PERCENT}%, Calculated interstitials to add: {num_to_add}")

    alloy_structure = generate_interstitial_alloy(
        host_unit=host_bulk,
        interstitial_element=INTERSTITIAL_ELEMENT,
        supercell_dim=SUPERCELL_DIM,
        lattice_type=CRYSTAL_STRUCTURE,
        num_to_add=num_to_add,
    )

    write("alloy_structure.xsf", alloy_structure)
    write("host_bulk.xsf", host_bulk * SUPERCELL_DIM)

    # === Define AGOX Environment ===
    template = Atoms("", cell=alloy_structure.cell.copy(), pbc=True)
    environment = Environment(
        template=template,
        symbols=alloy_structure.get_chemical_formula(),
        confinement_cell=template.cell.copy(),
        confinement_corner=np.array([0, 0, 0]),
        box_constraint_pbc=[True, True, True],
    )

    # === Initialize Generators ===
    n_rattle = len(alloy_structure)
    generators = [
        AmorphStructRandomize(
            **environment.get_confinement(),
            amorph=alloy_structure,
            write_struct=True,
            write_temp_struct=False,
            rattle_amplitude=RATTLE_AMPLITUDE,
            attempts=RAND_ATTEMPTS,
            n_rattle=n_rattle,
            generate_pristine=False,
            print_result=False,
            check_covalent=CHECK_COVALENT,
        ),
        RattleGenerator(
            **environment.get_confinement(),
            n_rattle=int(n_rattle),
            rattle_amplitude=RATTLE_AMPLITUDE,
        ),
        AmorphPermutationGenerator(
            **environment.get_confinement(),
            max_number_of_swaps=MAX_SWAPS,
            rattle_strength=RATTLE_STRENGTH,
            use_xy_only=False,
            ignore_species=None,
            write_candidates_to_disk=False,
            replace=True,
            attempts=PERMUT_ATTEMPTS,
            check_overlap=CHECK_OVERLAP,
            min_distance_scale=MIN_DISTANCE_SCALE,
            max_distance_scale=MAX_DISTANCE_SCALE,
            print_result=False,
            write_struct=False,
        ),
    ]

    # === Candidate Trial Generation ===
    success_count = 0
    fail_count = 0

    for i in range(N_STRUCTURE_CHECK):
        try:
            # Generate and save amorphous trial
            amorph_candidate = generators[0](sampler=None, environment=environment)[0]
            write(path_xsf / f"amorph_candidate_{i}.xsf", amorph_candidate)
            print(f"amorph {i}")

            sampler_test = FixedSampler(amorph_candidate)

            # Generate and save permutation trial
            permut_candidate = generators[2](sampler_test, environment)[0]
            write(path_xsf / f"permut_candidate_{i}.xsf", permut_candidate)
            print(f"permut {i}")

            success_count += 1

        except Exception as e:
            print(f"Generation failed at trial {i}: {e}")
            fail_count += 1

    # === Process & Record Sweep Iteration Results ===
    best_results.append({
        "scale_cell": scale_cell,
        "success": success_count,
        "fail": fail_count,
    })

    print(f"Result for scale_cell={scale_cell:.4f}: success={success_count}, fail={fail_count}")

    # Stop early if we find a scale configuration that successfully passes all trials
    if fail_count == 0:
        valid_scales.append({
            "scale_cell": scale_cell,
            "success": success_count
        })
        print(f"\n[VALID SCALE FOUND] Stop Sweeping at: {scale_cell:.4f}")
        break

    save_json[f"{INTERSTITIAL_ELEMENT}_concentration: {CONCENTRATION_PERCENT}%"].append({
        "valid_scales": valid_scales
    })

# === WRITE DATA TO JSON ===

with open(OUTPUT_JSON_PATH, "w") as f:
    json.dump(save_json, f, indent=4)

print("=" * 80)
print("Sweep Completed Successfully.")
print(f"Saved Results to: {OUTPUT_JSON_PATH}")
