"""
Extracted from main_test.ipynb (cell 16).
Section: Ta-B amorph setup
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
import numpy as np

from ase import Atoms
from ase.build import bulk
from ase.io import write

from agox.environments import Environment

from scripts.amorph_struct_randomize import AmorphStructRandomize
from scripts.amorph_permutation import AmorphPermutationGenerator
from scripts.add_B_concentration import add_B_concentration

scale_cell = 1.01 
a_ta = 3.30
supercell = (3, 3, 3)
cB = 0.05 

path_result = "single_run/0_result"
path_xsf = f"{path_result}/0_xsf"
os.makedirs(path_xsf, exist_ok=True)

ta_bulk = bulk("Ta", "bcc", a=a_ta, cubic=True) * supercell
ta_bulk.set_cell(ta_bulk.cell * scale_cell, scale_atoms=True)

tab_bulk, n_b, n_ta = add_B_concentration(
    ta_bulk, cB=cB, make_structure=True
)

print(f"{n_b=}")

template = Atoms("", cell=ta_bulk.cell.copy(), pbc=True)
environment = Environment(
    template=template,
    symbols=tab_bulk.get_chemical_formula(),
    confinement_cell=template.cell.copy(),
    confinement_corner=np.array([0, 0, 0]),
    box_constraint_pbc=[True, True, True],
)

write(f"tab_bulk_initial.xsf", tab_bulk)
