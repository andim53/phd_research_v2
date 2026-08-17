import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib import patheffects  # Required for the white outline
from ase.io import read
from scipy.stats import gaussian_kde

# --- Data Preparation ---
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_20.traj", index=':')
raw_energies, z_height_spans = [], []

for atoms in structures:
    try:
        raw_energies.append(atoms.get_potential_energy())
        z_pos = atoms.get_positions()[:, 2]
        z_height_spans.append(z_pos.max() - z_pos.min())
    except Exception:
        continue

num_atoms = len(structures[0])
energies = (np.array(raw_energies) - min(raw_energies))/num_atoms
print(f"{min(raw_energies)/num_atoms=}")
z_data = np.array(z_height_spans)
z_data = z_data - min(z_data)

# --- Structural Limits (Horizontal on this graph) ---
limits = {
    "Islands": 0.07,
    "Quasi-flat": 0.25,
    "Flat": 0.50
}

# --- KDE Calculation ---
min_e, max_e = 0.0, 0.8
energy_grid = np.linspace(min_e, max_e, 200)
kde = gaussian_kde(energies)
density = kde.evaluate(energy_grid)

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 3), sharey=True, 
                               gridspec_kw={'width_ratios': [1, 2.5]}, dpi=120)

# Subplot 1: State Density (Standard Weights)
ax1.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
ax1.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.2)
ax1.set_xlabel('State Density', fontsize=12)
ax1.set_ylabel(r'$E_i - E_{glob}$ (eV/atom)', fontsize=12)

# Subplot 2: Delta Z Scatter
ax2.scatter(z_data, energies, s=10, facecolors='grey', edgecolors='black', 
            linewidth=0.5, alpha=0.4, zorder=2)

# Global Minimum Highlight
glob_idx = np.argmin(energies)
ax2.scatter(z_data[glob_idx], energies[glob_idx], s=70, facecolors='red', 
            edgecolors='white', linewidth=1.2, zorder=5, label='Ground State')

# list_of_indices = np.argsort(energies)[-1]
# ax2.scatter(z_data[list_of_indices], energies[list_of_indices], s=70, facecolors='blue', 
#             edgecolors='white', linewidth=1.2, zorder=5, label='Other')

# --- Add Structural Limit Lines and Outlined Labels ---
for label, val in limits.items():
    # Horizontal lines across both plots
    ax1.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=10)
    ax2.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=10)
    
    # Create the horizontal text label (No bold fontweight)
    t = ax2.text(0.1, val + 0.005, f'{label}: {val:.2f} eV/atom', 
                fontsize=10, color='black', 
                verticalalignment='bottom', zorder=11)
    
    # Apply the white outline effect for readability
    t.set_path_effects([
        patheffects.withStroke(linewidth=3, foreground='white')
    ])

# Final Styling
ax2.set_xlabel(r'Relative $\Delta Z$ ($\AA$)', fontsize=12)
ax2.set_ylim(min_e, max_e)

# Standard tick styling (No bold)
for ax in [ax1, ax2]:
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

ax2.legend(frameon=False, loc='upper right', fontsize=10)

plt.tight_layout()
plt.subplots_adjust(wspace=0.08)
plt.show()