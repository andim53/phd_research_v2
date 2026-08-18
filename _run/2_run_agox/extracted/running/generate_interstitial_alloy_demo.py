"""
Extracted from main_test.ipynb (cell 7).
Section: Interstitial Alloy Generation Script
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


# from scripts.generate_interstitial_alloy import generate_interstitial_alloy
# Define your host unit cell here (e.g., Pt, Pd, Ir, etc.)
# Note: Must be a conventional cubic FCC cell for correct octahedral mapping
my_host_unit = bulk("Pt", crystalstructure="fcc", cubic=True)
# my_host_unit = bulk("Ta", crystalstructure="bcc", cubic=True)

supercell=(1, 1, 1)

# Generate alloy using the external host unit cell
alloy_structure = generate_interstitial_alloy(
    host_unit=my_host_unit,
    interstitial_element="B",
    supercell_dim=supercell,
    lattice_type = "bcc",
    num_to_add=6
)

from ase.io import write
write("alloy_structure.xsf",alloy_structure)
write("my_host_unit.xsf",my_host_unit*supercell)
