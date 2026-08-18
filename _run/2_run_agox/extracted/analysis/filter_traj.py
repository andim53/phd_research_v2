"""
Extracted from main_test.ipynb (cell 20).
Section: traj filter
"""

from ase.io import read, write

images = read('selected_structures_dos.traj', index=':')

# print(images[4])
indices_to_keep = [0, 4]
filtered_images = [atoms[indices_to_keep] for atoms in images]

write('ref_island.traj', filtered_images)
