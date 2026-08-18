"""
Extracted from main_test.ipynb (cell 31).
Section: bragg: FePt/Fe3Pt anti-site order
"""

import random
import numpy as np

from ase.io import read, write
from ase.build import make_supercell

###############################################################################
# Function to calculate number of swaps for target S
###############################################################################

def number_of_swaps_for_S(total_atoms, S, r=0.5):
    """
    Long-range order parameter:
        S = (p - r) / (1 - r)
    
    Rearranged to solve for p (fraction of correctly occupied sites):
        p = S * (1 - r) + r

    wrong_sites = total_atoms * (1 - p)
    One anti-site swap creates TWO wrong sites.
    """

    # Calculate fraction of correct occupation 'p' using your formula
    p = S * (1.0 - r) + r

    # Calculate wrong sites based on p
    wrong_sites = int(round(total_atoms * (1.0 - p)))

    # Each swap fixes/breaks 2 sites (one Fe and one Pt)
    swaps = wrong_sites // 2

    return swaps

###############################################################################
# Apply anti-site defects
###############################################################################

def apply_order_parameter(reference_atoms, S, r_param=0.5, seed=1):

    random.seed(seed)

    atoms = reference_atoms.copy()

    symbols = atoms.get_chemical_symbols()

    total_atoms = len(atoms)

    swaps_needed = number_of_swaps_for_S(total_atoms, S, r=r_param)

    print("===================================")
    print(f"Target S = {S}")
    print(f"Required swaps = {swaps_needed}")

    ###########################################################################
    # Find atoms still occupying correct sites
    ###########################################################################

    fe_correct = []
    pt_correct = []

    for i in ideal_fe_sites:

        if symbols[i] == "Fe":
            fe_correct.append(i)

    for i in ideal_pt_sites:

        if symbols[i] == "Pt":
            pt_correct.append(i)

    swaps_needed = min(
        swaps_needed,
        len(fe_correct),
        len(pt_correct)
    )

    ###########################################################################
    # Randomly select atoms to swap
    ###########################################################################

    chosen_fe = random.sample(fe_correct, swaps_needed)
    chosen_pt = random.sample(pt_correct, swaps_needed)

    ###########################################################################
    # Introduce anti-site defects
    ###########################################################################

    for fe_i, pt_i in zip(chosen_fe, chosen_pt):

        symbols[fe_i] = "Pt"
        symbols[pt_i] = "Fe"

    atoms.set_chemical_symbols(symbols)

    ###########################################################################
    # Calculate actual S using the new formula
    ###########################################################################

    correct_sites = 0

    for i in ideal_fe_sites:

        if symbols[i] == "Fe":
            correct_sites += 1

    for i in ideal_pt_sites:

        if symbols[i] == "Pt":
            correct_sites += 1

    # p_actual is the actual fraction of correct sites
    p_actual = correct_sites / total_atoms

    # S = (p - r) / (1 - r)
    S_actual = (p_actual - r_param) / (1.0 - r_param)

    print(f"Actual S = {S_actual:.4f}")

    return atoms

###############################################################################
# 1. Read bulk FePt structure from CIF
###############################################################################

# Example:
# bulk_FePt.cif

atoms = read("Fe3Pt.cif") # FePt.cif

###############################################################################
# 2. Create supercell
###############################################################################

# Supercell size
P = np.diag([3, 3, 3])

supercell = make_supercell(atoms, P)

###############################################################################
# 3. Define ideal sublattices from the original ordered structure
###############################################################################

# In L10-FePt:
# one sublattice is Fe-rich
# the other is Pt-rich
#
# We determine the ideal sites directly from the CIF structure.

scaled = supercell.get_scaled_positions()
symbols = supercell.get_chemical_symbols()

###############################################################################
# 4. Identify Fe and Pt ideal sites
###############################################################################

ideal_fe_sites = []
ideal_pt_sites = []

for i, symbol in enumerate(symbols):

    if symbol == "Fe":
        ideal_fe_sites.append(i)

    elif symbol == "Pt":
        ideal_pt_sites.append(i)

###############################################################################
# 6. Generate structures for multiple S values
###############################################################################

S_values = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]

r_alloy = 0.625 # 0.625 Fe3Pt; 0.5 FePt

for S in S_values:

    structure = apply_order_parameter(supercell, S, r_param=r_alloy, seed=2)

    # filename = f"FePt_S_{S:.1f}.xsf"
    filename = f"Fe3Pt_S_{S:.1f}.xsf"

    write(filename, structure)

    print(f"Saved: {filename}")

###############################################################################
# 7. Optional visualization
###############################################################################

# from ase.visualize import view
# view(structure)
