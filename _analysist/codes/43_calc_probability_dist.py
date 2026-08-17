import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import AutoMinorLocator
from matplotlib import patheffects
from matplotlib.animation import FuncAnimation, PillowWriter
from ase.io import read
from scipy.stats import gaussian_kde

# --- Data Preparation ---
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')
raw_energies = [atoms.get_potential_energy() for atoms in structures]
num_atoms = len(structures[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
kde = gaussian_kde(energies)

temps = [300, 400, 500, 600, 700, 800, 900, 1000, 1100, 2000, 3000, 5000, 6000, 10000]
colors_plasma = cm.get_cmap('plasma')(np.linspace(0, 0.85, len(temps)))

limits = {"Islands": 0.075, "Flat": 0.256}

# --- Setup Figure for Animation ---
# Increased bottom margin via subplots_adjust later to prevent cutting
fig, ax = plt.subplots(figsize=(5, 4), dpi=120)

def init():
    ax.clear()
    ax.set_xlabel(r'Internal Energy $U = E_i - E_{glob}$ (eV/atom)', fontsize=12)
    ax.set_ylabel(r'Probability $P_i$', fontsize=12)
    ax.set_yscale('log')
    ax.set_xlim(0.0, 0.5)
    ax.set_ylim(1e-8, 1e-1)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    
    # Static Structural Lines
    # Moved text pos slightly up to ensure it's within the axis box
    for label, val in limits.items():
        ax.axvline(x=val, color='black', linestyle='--', linewidth=1, alpha=0.4)
        t = ax.text(val + 0.008, 1.5e-8, label, rotation=90, va='bottom', fontsize=10)
        t.set_path_effects([patheffects.withStroke(linewidth=3, foreground='white')])
    
    plt.tight_layout()
    return []

def update(frame):
    # We NO LONGER remove ax.collections to allow stacking
    
    # Remove ONLY the previous large temperature header text
    for text in ax.texts:
        if "HEADER_TEMP" in text.get_label():
            text.remove()

    T = temps[frame]
    color = colors_plasma[frame]
    
    # Calculate probabilities
    probs = calculate_boltzmann_probs(energies, kde, T)
    
    # Add new scatter (stacking on top of old ones)
    ax.scatter(energies, probs, color=color, s=15, alpha=0.6, 
               edgecolors='none', label=f'{T} K')
    
    # Floating Header Temperature Label (Current frame indicator)
    temp_text = ax.text(0.38, 0.5e-1, f'Current: {T} K', fontsize=14, color=color, 
                        fontweight='bold', ha='right', label="HEADER_TEMP")
    temp_text.set_path_effects([patheffects.withStroke(linewidth=3, foreground='white')])
    
    # Optional: Update legend to show progress
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1), frameon=False, fontsize=8)
    
    return []

# --- Create and Save Animation ---
# Note: repeat=True will keep the gif looping
ani = FuncAnimation(fig, update, frames=len(temps), init_func=init, blit=False)

# Adjust plot to make room for labels and legend
plt.subplots_adjust(bottom=0.15, right=0.8)

# Save as GIF
writer = PillowWriter(fps=3) 
save_path = f"{dir_out}/temp_stacking_evolution.gif"
ani.save(save_path, writer=writer)

plt.show()
print(f"Stacking animation saved to: {save_path}")