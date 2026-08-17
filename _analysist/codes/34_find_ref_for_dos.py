from ase.io import read, write, Trajectory
import numpy as np

custom_struct = read('hetero.xsf')
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')

num_atoms = len(structures[0])
raw_energies = [atoms.get_potential_energy() for atoms in structures]
rel_energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms

min_energy_idx = np.argmin(rel_energies)

target_indices = [919, 789, 1075, int(min_energy_idx)]
new_traj_list = []

for idx in target_indices:
    try:
        new_traj_list.append(structures[idx])
    except IndexError:
        print(f"Warning: Index {idx} out of range for the loaded trajectory.")

new_traj_list.append(custom_struct)
output_traj_path = "selected_structures_dos.traj"
write(output_traj_path, new_traj_list)