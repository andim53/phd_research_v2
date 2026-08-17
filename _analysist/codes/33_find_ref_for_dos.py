import pandas as pd
import numpy as np
from ase.io import read

structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')
raw_energies, z_height_spans = [], []

for atoms in structures:
    try:
        raw_energies.append(atoms.get_potential_energy())
        z_pos = atoms.get_positions()[:, 2]
        z_height_spans.append(z_pos.max() - z_pos.min())
    except Exception:
        continue
    
num_atoms = len(structures[0])
rel_energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
rel_z = np.array(z_height_spans) - min(z_height_spans)

df = pd.DataFrame({
    'traj_index': np.arange(len(rel_energies)),
    'energy_per_atom': rel_energies,
    'z_height_rel': rel_z
})

num_bins = 10
df['energy_range'] = pd.cut(df['energy_per_atom'], bins=num_bins)

best_structures = df.sort_values('z_height_rel').groupby('energy_range', observed=True).first().reset_index()

output_file = "lowest_height_per_energy.csv"
best_structures.to_csv(output_file, index=False)

print("done")