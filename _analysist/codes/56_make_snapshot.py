import os
import numpy as np
from ase.io import read
from ase.constraints import FixAtoms
from scripts.plot_structure import plot_structure

# --- 1. Selection Logic & Data Preparation ---
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
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
z_data = np.array(z_height_spans)
z_data = z_data - min(z_data)

energy_threshold = 0.25
low_energy_indices = np.where(energies < energy_threshold)[0]
n_show = 4  

if len(low_energy_indices) >= n_show:
    subset_z = z_data[low_energy_indices]
    sorted_subset_indices = np.argsort(subset_z)
    
    # Define the three distinct groups
    low_z_indices = low_energy_indices[sorted_subset_indices[:n_show]]
    high_z_indices = low_energy_indices[sorted_subset_indices[-n_show:]]
    
    mid_point = len(sorted_subset_indices) // 2
    half_n = n_show // 2
    mid_z_indices = low_energy_indices[sorted_subset_indices[mid_point - half_n : mid_point - half_n + n_show]]

    # This is the variable used by the plotting loop below
    categories = {
        "flat": low_z_indices,
        "mid": mid_z_indices,
        "tall": high_z_indices
    }
else:
    print(f"Error: Not enough structures below {energy_threshold}.")
    categories = {}

# --- 2. Automated Plotting Loop ---
output_img_dir = f"./{dir_out}/structure_images"
if not os.path.exists(output_img_dir) and categories:
    os.makedirs(output_img_dir)

for cat_prefix, idx_list in categories.items():
    for i, idx in enumerate(idx_list):
        file_path = f"{dir_out}/{dir_xsf}/19/struct_{idx}.xsf"
        
        if not os.path.exists(file_path):
            print(f"Skipping: {file_path} not found.")
            continue
            
        structs = read(file_path)
        
        # Substrate setup
        substrate_symbols = ['Mg', 'O']
        substrate_indices = [atom.index for atom in structs if atom.symbol in substrate_symbols]
        structs.set_constraint(FixAtoms(indices=substrate_indices))

        # View settings
        cell_offset = np.array([5, 5, 0])  
        save_path = f"{output_img_dir}/{cat_prefix}_{i}_idx{idx}.png"

        print(f"Generating image: {save_path}")
        plot_structure(
            structs,
            plane='yz+', # Side view to capture Delta Z evolution
            save_path=save_path,
            figsize=(5, 5),
            repeat=7,
            plot_show=False, 
            linewidths_cell=4.0,
            cell_offset=cell_offset,
            darken_factor=0.3,
            n_darken_layers=2,
        )

print("\nProcessing complete.")