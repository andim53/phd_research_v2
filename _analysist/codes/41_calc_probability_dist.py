import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LogLocator, LogFormatterExponent
from matplotlib import patheffects # Required for the outline
from ase.io import read
from scipy.stats import gaussian_kde

# --- Constants & Setup ---
kb = 8.6173e-5 # eV/K
temps = [300, 400, 500, 600, 700, 800, 900, 1000, 1100, 2000, 3000, 5000, 6000, 10000]
colors_plasma = cm.get_cmap('plasma')(np.linspace(0, 0.85, len(temps)))

# Load and normalize energies
# structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')
# structures = read(f"{dir_out}/{dir_xsf_traj}/traj_47.traj", index=':')
# structures = read(f"{dir_out}/{dir_xsf_traj}/traj_39.traj", index=':')
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_66.traj", index=':')

raw_energies = [atoms.get_potential_energy() for atoms in structures]
num_atoms = len(structures[0])

# Defining U = E_i - E_glob (normalized per atom)
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
kde = gaussian_kde(energies)

# --- Define Structural Limits ---
# limits = {
#     "Islands": 0.074,
#     "Flat": 0.255
# }

# limits = {
#     "Disordered": 1.447,
#     "Flat": 0.093
# }

limits = {}

# --- Plotting ---
fig, ax = plt.subplots(figsize=(6, 3), dpi=120)

# 1. Plot Boltzmann Probabilities for each Temp
for T, color in zip(temps, colors_plasma):
    probs = calculate_boltzmann_probs(energies, kde, T)
    
    peak_idx = np.argmax(probs)
    peak_energy = energies[peak_idx]
    
    note_label = f'{T} K'
    ax.scatter(energies, probs, color=color, s=15, alpha=0.5, 
               edgecolors='none', label=note_label)

# 2. Add Structural Limit Vertical Lines (Black) with Outlined Text
y_text_pos = 2e-8 

for label, val in limits.items():
    ax.axvline(x=val, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=10)
    
    # Create the text object
    t = ax.text(val + 0.008, y_text_pos, f'{label}', 
                rotation=90, verticalalignment='bottom', fontsize=10, 
                color='black', zorder=11)
    
    # Apply the white outline (path effect)
    t.set_path_effects([
        patheffects.withStroke(linewidth=3, foreground='white')
    ])

# --- Final Styling ---
ax.set_xlabel(r'$E - E_{glob}$ (eV/atom)', fontsize=13)
ax.set_ylabel(r'$P$ (a.u.)', fontsize=13)
ax.set_yscale('log')

ax.set_xlim(0.0, 0.7) # ax.set_xlim(0.0-0.1, 1.8) # ax.set_xlim(0.0, 0.5)
ax.set_ylim(1e-8, 1e-1)
ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=10))

ax.xaxis.set_minor_locator(AutoMinorLocator())

# --- Legend Outside ---
ax.legend(frameon=False, 
          fontsize=10, 
          loc='upper left', 
          bbox_to_anchor=(1.02, 1.15))

plt.subplots_adjust(right=0.75) 
plt.savefig('boltzmann_probabilities.png', dpi=300, bbox_inches='tight')
plt.show()