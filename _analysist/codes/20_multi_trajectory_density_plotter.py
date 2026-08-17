import os
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

# === Path and File Setup ===
dir_path = f"{dir_out}/{dir_xsf_traj}"
traj_files = [
    "traj_27.traj", 
    "traj_28.traj", 
    "traj_29.traj", 
    "traj_30.traj", 
    "traj_31.traj",
]
# legend_labels = ["0% MgO latt.", "25% MgO latt.", "50% MgO latt.", "75% MgO latt."]
legend_labels = [
    '2.0 ML',  # 27_fe_con0 (Baseline)
    '1.75 ML',  # 28_fe_con5 (-5 atoms)
    '1.5 ML',  # 29_fe_con10 (-10 atoms)
    '1.25 ML',  # 30_fe_con15 (-15 atoms)
    '1.0 ML',  # 31_fe_con20 (-20 atoms)
]

# === Dictionary Energy Creation Framework ===
energy_landscape_dict = {}
num_atoms = None

for i, filename in enumerate(traj_files):
    try:
        full_path = os.path.join(dir_path, filename)
        structures = read(full_path, index=':')
        
        raw_energies = []
        for atoms in structures:
            try:
                raw_energies.append(atoms.get_potential_energy())
                if num_atoms is None:
                    num_atoms = len(atoms)
            except Exception:
                continue
                
        if not raw_energies:
            continue
            
        # Normalize and store entries matching the target labels
        energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
        dict_key = legend_labels[i] if i < len(legend_labels) else filename.replace('.traj', '')
        energy_landscape_dict[dict_key] = energies

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# === Calculate Global Min and Max for Energy Limits ===
if energy_landscape_dict:
    all_energies = np.concatenate(list(energy_landscape_dict.values()))
    min_e = np.min(all_energies)
    max_e = np.max(all_energies)
    # Formats to (min, max, num_ticks/steps) or adjust step count as needed
    e_limit_val = (min_e, max_e, 5) 
else:
    e_limit_val = (None, None, None)

# === Landscape Visualization Generation ===
fig = plot_structure_landscape(
    # Core Data Inputs
    X_eigen=None,
    energies=energy_landscape_dict,

    # Plot Layout and Sizing
    figsize=(4, 3),
    plot_density_only=True,

    # Energy View Constraints
    e_limit=(min_e, max_e, 5), #(0.0, 0.8, 5),
    dens_line_weight=1.0,
    fill_density=True,
    density_alpha=0.1,
    show_limits=False,

    # Styling Flags
    density_cmap='viridis'
)

plt.savefig("state_dent_comp.png", dpi=300, bbox_inches="tight")
plt.show()