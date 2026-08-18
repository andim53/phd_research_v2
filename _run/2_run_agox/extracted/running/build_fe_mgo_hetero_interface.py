"""
Extracted from main_test.ipynb (cell 2).
Section: Heterostructure Interface Builder
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
import re
import numpy as np
from ase import Atoms
from ase.build import bulk, surface
from ase.constraints import FixAtoms
from ase.io import read, write

# Custom project scripts for stacking, structural modification, and plotting
from scripts.build_fe_stack import build_fe_stack
from scripts.build_heteroStruct import build_heteroStruct
from scripts.build_mgo_stack import build_mgo_stack
from scripts.remove_random_atoms_by_species import remove_random_atoms_by_species
from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows

# === Core Materials & Crystal Structure Configuration
# Substrate settings
substrate_species = 'MgO'
substrate_crystal_structure = 'rocksalt'
a_substrate = 4.212

# Deposition layer settings
deposition_species = 'Fe'
deposition_crystal_structure = 'bcc'
a_deposition = 2.870190        # Optimized LCAO lattice constant (Å)

# Interfacial geometry & matching parameters
vacuum = 20
dist_z_interface = 0.5         # Experimental initial vertical layer separation (Å)
supercell = (5, 5, 1)          # Lateral simulation slab repetition dimensions

substrate_layer_number = 1     # Total thickness of bottom substrate support (monolayers)
deposition_layer_number = 1    # Total thickness of top deposition film (monolayers)

# Strain interpolation: 0.0 = Pure deposition lattice, 1.0 = Fully coherent with substrate
interpolation_factor = 0
a_substrate_matched = a_substrate / np.sqrt(2)  # Coherent interfacial matching scaling factor
strain = (a_substrate_matched - a_deposition) / a_deposition * 100
a_custom = a_deposition + interpolation_factor * (a_substrate_matched - a_deposition)

# === Composition & Adsorbate Modification
removed_num = 0       # Number of deposition atoms randomly pruned for defects
symbol_add = 'B'      # Adsorbate atomic species to insert into hollow sites
z_height_add = 0      # Vertical coordinate height offset relative to the base layer
num_atoms_add = 25     # Target number of adsorbate atoms to insert

# Run & infrastructure setup
seed = 0
path_result = "0_result"
path_xsf = f"{path_result}/xsf"
os.makedirs(path_xsf, exist_ok=True)

# === Structure Building Execution Pipeline
# --- Base Substrate Layer Definition ---
bulk_substrate = bulk(substrate_species, substrate_crystal_structure, a=a_substrate, cubic=True)
slab_substrate_initial = surface(bulk_substrate, (0, 0, 1), layers=1, vacuum=vacuum)

z_positions = slab_substrate_initial.get_positions()[:, 2]
unique_z = np.unique(np.round(z_positions, 5))

if len(unique_z) >= 2:
    unique_z.sort()
    dist_substrate = unique_z[1] - unique_z[0]
else:
    dist_substrate = 2.106

# --- Thin Film and Heterostructure Assembly ---
bulk_deposition = bulk(deposition_species, deposition_crystal_structure, a=a_custom, cubic=True)
slab_deposition_initial = surface(bulk_deposition, (0, 0, 1), layers=1, vacuum=vacuum)

slab_combined_stack = build_mgo_stack(
    slab_deposition_initial, num_layers=substrate_layer_number, dist_mgo=dist_substrate, 
    vacuum=vacuum, output_path=f"{path_xsf}/slab_combined_stack.xsf", rotate_system=False
)
slab_substrate_base = slab_combined_stack[[atom.symbol != deposition_species for atom in slab_combined_stack]].repeat(supercell)
slab_deposition_base = build_fe_stack(
    slab_deposition_initial, num_layers=deposition_layer_number, vacuum=vacuum, 
    output_path=f"{path_xsf}/slab_deposition.xsf"
).repeat(supercell)

slab_deposition = slab_deposition_base.copy() 
slab_substrate = slab_substrate_base.copy()

# Apply modifications (pruning and hollow-site filling)
slab_deposition = remove_random_atoms_by_species(slab_deposition, deposition_species, removed_num)
slab_deposition = add_adsorbate_to_hollows(
    slab_deposition, symbol=symbol_add, height=z_height_add, 
    num_atoms=num_atoms_add, seed=seed
)

# Output generation files
test_hetero, _, _, _, _ = build_heteroStruct(
    slab_substrate, slab_deposition, output_path=f'{path_xsf}/heteroStruct_final.xsf'
)
write(f'{path_xsf}/deposition_layer_only.xsf', slab_deposition)
write(f'{path_xsf}/test_hetero.xsf', test_hetero)

print(f"Structure generation complete. Output saved to: {path_xsf}/")
