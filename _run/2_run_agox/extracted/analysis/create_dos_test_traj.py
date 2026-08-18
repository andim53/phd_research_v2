"""
Extracted from main_test.ipynb (cell 23).
Section: Dos: create test traj
"""

from ase import Atoms
from ase.build import bulk
from ase.io import Trajectory

# Reference BCC Iron lattice constant is ~2.87 Angstroms
lattice_constants = [2.75, 2.80]
traj = Trajectory('selected_structures_dos_test.traj', 'w')

for a in lattice_constants:
    # Create BCC Fe
    atoms = bulk('Fe', 'bcc', a=a)
    
    # Set a magnetic moment since you are using spinpol=True
    # Pure BCC Fe usually has a magnetic moment around 2.22 Bohr magnetons
    atoms.set_initial_magnetic_moments([2.2])
    
    traj.write(atoms)

print("Created selected_structures_dos_test.traj with 5 structures.")
