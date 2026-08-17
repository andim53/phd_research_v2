import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib import patheffects
from scipy.stats import gaussian_kde
from ase.io import read

# --- Configuration ---
traj_ids = [19, 22, 23, 24]  
colors = ['#1f77c5', '#1f77b4', '#ff7f0e', '#2ca02c']  
# dir_out and dir_xsf_traj should be defined in your environment

fig, ax = plt.subplots(figsize=(5, 4), dpi=120)

# To store data for global limit calculation
all_z_data = []

for i, t_id in enumerate(traj_ids):
    # --- Data Extraction ---
    try:
        structures = read(f"{dir_out}/{dir_xsf_traj}/traj_{t_id}.traj", index=':')
    except Exception as e:
        print(f"Could not read traj_{t_id}: {e}")
        continue

    raw_energies, z_height_spans = [], []
    for atoms in structures:
        try:
            raw_energies.append(atoms.get_potential_energy())
            z_pos = atoms.get_positions()[:, 2]
            z_height_spans.append(z_pos.max() - z_pos.min())
        except: continue

    num_atoms = len(structures[0])
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
    z_data = np.array(z_height_spans)
    z_data = z_data - min(z_data)

    # --- KDE Calculation ---
    # Create a smooth grid for plotting
    z_grid = np.linspace(z_data.min() - 0.2, z_data.max() + 0.2, 300)
    kde = gaussian_kde(z_data)
    density = kde.evaluate(z_grid)

    # --- Plotting the KDE ---
    ax.plot(z_grid, density, color=colors[i], lw=1.8, label=f'Traj {t_id}', zorder=4)
    ax.fill_between(z_grid, 0, density, color=colors[i], alpha=0.15, zorder=3)

    # --- Ground State Marker ---
    glob_idx = np.argmin(energies)
    gs_z = z_data[glob_idx]
    
    # Vertical line for GS
    ax.axvline(gs_z, color=colors[i], linestyle='--', lw=1.2, alpha=0.7, zorder=5)
    
    # Outlined Ground State Label
    # y_pos is staggered slightly for each trajectory
    y_pos = ax.get_ylim()[1] if i == 0 else plt.gca().get_ylim()[1] 
    # Update y_pos logic to use current max height
    t = ax.text(gs_z, 0.02, f'GS {t_id}', color=colors[i], fontsize=9, 
                rotation=90, ha='right', va='bottom', zorder=10)
    t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

# --- Final Styling ---
ax.set_xlabel(r'Relative $\Delta Z$ ($\AA$)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)

# Ensure Y-axis starts at 0
ax.set_ylim(0, None)

ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())

ax.legend(frameon=False, loc='upper right', fontsize=10)

plt.tight_layout()
plt.show()