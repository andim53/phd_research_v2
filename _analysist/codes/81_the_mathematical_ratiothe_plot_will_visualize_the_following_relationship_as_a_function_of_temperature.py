import numpy as np
import matplotlib.pyplot as plt
from agox.databases import Database
import matplotlib.ticker as ticker

# 1. Load Data
dir_path = db_paths[0][0]
db_path = f"{dir_path}/1_db/db_0.db"
db = Database(filename=db_path)
db.restore_to_memory()
traj = db.restore_to_trajectory()

# 2. Extract Energies (assumed to be in eV from AGOX)
energies = []
for atoms in traj:
    try:
        energies.append(atoms.get_potential_energy()/len(atoms))
    except Exception:
        continue 

energies = np.array(energies)

# 3. Process Energies (Relative to Ground State)
min_idx = np.argmin(energies)
min_energy = energies[min_idx]
relative_energies = energies - min_energy

# 4. Constants & Calculation
# Converting eV to Joules for the standard k_B value
ev_to_j = 1.60218e-19
k_B = 1.380649e-23  
# T = 298.15
T = 447.875
T = 1047.875
# T1 = 298.15
# T2 = 447.875

def calculate_probabilities(E_ev, temp):
    # Convert eV to Joules inside the exponential
    boltzmann_factors = np.exp(-(E_ev * ev_to_j) / (k_B * temp))
    Z = np.sum(boltzmann_factors)
    probabilities = boltzmann_factors / Z
    return probabilities, Z

probs, partition_Z = calculate_probabilities(relative_energies, T)
# probs_t1, partition_Z_t1 = calculate_probabilities(relative_energies, T1)
# probs_t2, partition_Z_t2 = calculate_probabilities(relative_energies, T2)

# 5. Sorting for a smooth Line Graph
# This ensures the line represents the probability distribution from lowest to highest energy
sort_idx = np.argsort(relative_energies)
sorted_relative_energies = relative_energies[sort_idx]
sorted_probs = probs[sort_idx]

# 6. Plotting
import matplotlib.pyplot as plt

# Using a clean style base
plt.style.use('seaborn-v0_8-white') 

fig, ax = plt.subplots(figsize=(6, 5)) # Square-ish ratios look better in papers
ax.plot(sorted_relative_energies, sorted_probs, 
        color='black', 
        marker='o', 
        markersize=4, 
        markerfacecolor='white', 
        markeredgewidth=1,
        linewidth=1, 
        label=f'T = {T} K',
        zorder=1)

ax.scatter(sorted_relative_energies[8], sorted_probs[8], 
           edgecolors='red', 
           facecolors='white', 
           marker='o', 
           s=16,  # s is marker size in points^2; 4^2 = 16
           linewidth=5, 
           label=f'T = {T} K',
           zorder=2)
ax.scatter(sorted_relative_energies[10], sorted_probs[10], 
           edgecolors='red', 
           facecolors='white', 
           marker='o', 
           s=16,  # s is marker size in points^2; 4^2 = 16
           linewidth=5, 
           label=f'T = {T} K',
           zorder=2)

# Minimalist Axis Styling
ax.set_xlabel('Relative Energy (eV/atom)', fontsize=11)
ax.set_ylabel(r'Probability $p_i$', fontsize=11)
# ax.set_yscale('log')

ax.tick_params(axis='both', which='major', direction='in', length=6, width=1, top=True, right=True)
# Minor ticks: Shorter, thinner, pointing IN
ax.tick_params(axis='both', which='minor', direction='in', length=3, width=0.8, top=True, right=True)

# Remove top and right spines (standard minimalist look)
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Refined Grid (Only horizontal for readability, or very subtle)
ax.grid(axis='y', which='both', linestyle=':', alpha=0.3)
# ax.grid(True, which="major", axis="y", ls="-", alpha=0.2, color='gray')

# Title and Layout
ax.set_title(f'Boltzmann Distribution ($T$ = {T} K)', loc='left', fontsize=12, fontweight='bold')
plt.tight_layout()

# Save with high DPI for publications
# plt.savefig('boltzmann_plot.pdf', dpi=300, bbox_inches='tight')
plt.show()