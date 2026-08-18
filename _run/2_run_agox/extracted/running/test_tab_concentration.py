"""
Extracted from main_test.ipynb (cell 37).
Section: Ta-B concentration test
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


import numpy as np
from ase.build import bulk

# Custom-made import from your environment
from scripts.add_B_concentration import add_B_concentration

# --- Configuration to test ---
a_ta = 3.331167              # Lattice parameter
supercell = (3, 3, 3)        # Change this to test larger/smaller structures
cB = 0.08                    # Boron concentration (e.g., 0.05 = 5%)
scale_cell = 1.00            # Cell scaling factor

print(f"Testing Concentration: {cB * 100}% | Supercell: {supercell}")
print("-" * 50)

# 1. Generate the pristine Tantalum bulk supercell
ta_bulk = bulk("Ta", "bcc", a=a_ta, cubic=True) * supercell
ta_bulk.set_cell(ta_bulk.cell * scale_cell, scale_atoms=True)

# 2. Add Boron using your custom script
tab_bulk, n_b, n_ta = add_B_concentration(
    ta_bulk, cB=cB, make_structure=True
)

# 3. Output the results
print(f"Number of Boron atoms (n_b):     {n_b}")
print(f"Number of Tantalum atoms (n_ta): {n_ta}")
print(f"Total atoms in cell:             {len(tab_bulk)}")
print(f"Actual calculated ratio:         {n_b / (n_b + n_ta) * 100:.2f}%")
