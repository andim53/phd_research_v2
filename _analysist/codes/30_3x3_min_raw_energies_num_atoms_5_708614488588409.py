import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib import patheffects
from ase.io import read
from scipy.stats import gaussian_kde

# --- Configuration ---
plot_only_delta_z = True  # Set to False to see the State Density (KDE) plot as well

# --- Data Preparation ---
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
energies = (np.array(raw_energies) - min(raw_energies))/num_atoms
z_data = np.array(z_height_spans)
z_data = z_data - min(z_data)

# --- Structural Limits ---
limits = {
    "Islands": 0.07,
    "Quasi-flat": 0.25,
    "Flat": 0.50
}

min_e, max_e = 0.0, 0.8

# --- Plotting Logic ---
if plot_only_delta_z:
    fig, ax2 = plt.subplots(figsize=(4, 3), dpi=120)
    axes = [ax2]
else:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 3), sharey=True, 
                                   gridspec_kw={'width_ratios': [1, 2.5]}, dpi=120)
    axes = [ax1, ax2]
    
    # KDE Calculation & Plotting
    energy_grid = np.linspace(min_e, max_e, 200)
    kde = gaussian_kde(energies)
    density = kde.evaluate(energy_grid)
    
    ax1.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
    ax1.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.2)
    ax1.set_xlabel('State Density', fontsize=12)
    ax1.set_ylabel(r'$E_i - E_{glob}$ (eV/atom)', fontsize=12)

# --- Delta Z Scatter (Common to both modes) ---
ax2.scatter(z_data, energies, s=10, facecolors='grey', edgecolors='black', 
            linewidth=0.5, alpha=0.4, zorder=2)

# Global Minimum Highlight
glob_idx = np.argmin(energies)
ax2.scatter(z_data[glob_idx], energies[glob_idx], s=70, facecolors='red', 
            edgecolors='white', linewidth=1.2, zorder=5, label='Ground State')

# --- Add Structural Limit Lines and Outlined Labels ---
for label, val in limits.items():
    for ax in axes:
        ax.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=10)
    
    t = ax2.text(4, val + 0.005, f'{label}', 
                fontsize=10, color='black', 
                verticalalignment='bottom', zorder=11)
    t.set_path_effects([patheffects.withStroke(linewidth=3, foreground='white')])

# Final Styling
ax2.set_xlabel(r'$\Delta Z$ ($\AA$)', fontsize=12)
if plot_only_delta_z:
    ax2.set_ylabel(r'$E_i - E_{glob}$ (eV/atom)', fontsize=12)

ax2.set_ylim(min_e, max_e)
ax2.legend(frameon=False, loc='upper right', fontsize=10)

for ax in axes:
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

plt.tight_layout()
if not plot_only_delta_z:
    plt.subplots_adjust(wspace=0.08)
    
plt.show()