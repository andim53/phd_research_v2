import glob
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

from scripts.plot_structure_landscape import plot_structure_landscape

# === Path Configuration ===
seeds_dir = os.path.join(dir_out, dir_xsf_traj, '19')
traj_files = glob.glob(os.path.join(seeds_dir, '*.traj'))

# === Step 1: Group Raw Energies by Unique Seed ID ===
seed_groups = defaultdict(list)
num_atoms = None

for file_path in traj_files:
    file_name = os.path.basename(file_path)
    match = re.search(r'seed_(\d+)', file_name)
    
    if not match:
        print(f"Skipping file with unrecognized name pattern: {file_name}")
        continue
        
    seed_num = int(match.group(1))

    try:
        structures = read(file_path, index=':')
    except Exception as e:
        print(f"Failed to read file {file_name}: {e}")
        continue

    # Extract stable trajectory potential energies into the matching seed bucket
    for atoms in structures:
        try:
            e = atoms.get_potential_energy()
            if num_atoms is None:
                num_atoms = len(atoms)  # Capture atom count from the first valid structure
            seed_groups[seed_num].append(e)
        except Exception: 
            continue 

# === Step 2: Cumulative Energy Normalization & Aggregation ===
energy_landscape_dict = {}
cumulative_raw_energies = []
processed_seeds = []

# Process keys sequentially (e.g., 0, 1, 2...)
sorted_unique_seeds = sorted(seed_groups.keys())

for seed_num in sorted_unique_seeds:
    seed_energies = seed_groups[seed_num]
    if not seed_energies:
        continue
        
    processed_seeds.append(str(seed_num))
    cumulative_raw_energies.extend(seed_energies)

    # Shift energy against the global relative minimum of the accumulated pool
    cumulative_arr = np.array(cumulative_raw_energies)
    normalized_energies = (cumulative_arr - np.min(cumulative_arr)) / num_atoms

    # Format interval string range labels (e.g., "seed 0", "seed 0-1", "seed 0-2")
    start_seed = processed_seeds[0]
    current_seed = processed_seeds[-1]
    dict_key = f"seed {start_seed}" if len(processed_seeds) == 1 else f"seed {start_seed}-{current_seed}"

    energy_landscape_dict[dict_key] = normalized_energies

# === Logging Terminal Summary ===
# print("\nExtraction finished! Cumulative map keys:")
# for key, entries in energy_landscape_dict.items():
#     print(f"-> Key: '{key}' (Contains {len(entries)} total entries)")

# === Plot Generation and Export ===
fig = plot_structure_landscape(
    # Core Data Inputs
    X_eigen=None, 
    energies=energy_landscape_dict, 

    # Plot Layout and Sizing
    figsize=(5, 3),
    plot_density_only=True,

    # Energy View Constraints
    e_limit=(0.0, 1.0, 6),
    dens_line_weight=0.9,
    show_limits=False,

    # Styling Flags
    black_seed_zero=True,
    seed_zero_top_zorder=True
)

plt.savefig('state_denst.png', dpi=300, bbox_inches='tight')
plt.show()