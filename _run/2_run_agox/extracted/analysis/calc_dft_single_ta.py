"""
Extracted from main_test.ipynb (cell 15).
Section: Calc DFT (single Ta SCF)
"""

from ase.build import bulk
from gpaw import GPAW, FermiDirac

# 1. Define the lattice constant and create the bulk structure
a_ta = 3.303  # Standard bcc Tantalum lattice constant in Å
ta_bulk = bulk("Ta", "bcc", a=a_ta, cubic=True)

# 2. Define the k-point grid
kpts = (4, 4, 4)

# 3. Initialize GPAW with your parameters
calc = GPAW(
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    kpts=kpts,
    symmetry="off",
    nbands="nao",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    # convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    occupations=FermiDirac(width=0.05),
    # maxiter=100,
    txt="ta_bulk.txt"
)

# 4. Attach calculator and run calculation
ta_bulk.calc = calc
total_energy = ta_bulk.get_potential_energy()

# 5. Save the potential energy to a text file
output_filename = "potential_energy.txt"
with open(output_filename, "w") as f:
    f.write(f"Total Potential Energy: {total_energy:.6f} eV\n")

print(f"Calculation complete. Potential energy saved to '{output_filename}'.")
