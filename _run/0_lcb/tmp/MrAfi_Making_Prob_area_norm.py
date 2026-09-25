import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import patheffects # Required for the outline
from ase.io import read
from matplotlib.ticker import AutoMinorLocator
from scipy.stats import gaussian_kde
from scipy.integrate import trapezoid
import os

# === Directory Definitions ===
dir_simul = '1_result'            # Directory for resulted simulations
dir_out = '0_analy'               # Directory for the analysis

dir_xsf_traj = '0_xsf_traj'       # Stores entire trajectory
dir_xsf = '1_xsf'                 # Stores all structures
dir_im = '2_im'
dir_xsf_min_so_far = '3_min_so_far'

# === Directory Initialization ===
os.makedirs(f'{dir_out}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf_traj}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_im}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf_min_so_far}', exist_ok=True)

def calculate_boltzmann_probs(energies, kde_model, T):
    """
    Calculates normalized Pi = [rho(E) * exp(-dE/kbT)] / Z
    """
    kb = 8.6173e-5 # eV/K

    # Adding epsilon to avoid zero
    rho_i = kde_model.evaluate(energies) + 1e-15

    # 2. Calculate Boltzmann Weights (relative to min energy)
    relative_e = energies - np.min(energies)
    exponent = -relative_e / (kb * T)
    weights = np.exp(exponent)

    # 3. Calculate Partition Function Z 
    numerator = rho_i * weights
    Z = np.sum(numerator)

    # 4. Return Probabilities
    return numerator / Z

# --- Constants & Setup ---
kb = 8.6173e-5 # eV/K
temps = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 2000, 3000]
colors_plasma = cm.get_cmap('plasma')(np.linspace(0, 0.85, len(temps)))

# --- Target Temperature for Shading (Manual Variable) ---
target_temp = 300  # 曲線の下に色を塗りたい温度を手動で指定

# Base formation energy offset for global min (eV/atom)
E_global_form_base = 0.1288632

# Load and compute Formation Energies
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_0.traj", index=':')

raw_energies = [atoms.get_potential_energy() for atoms in structures]
num_atoms = len(structures[0])

# Formation Energy per atom
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms + E_global_form_base
kde = gaussian_kde(energies)

limits = {}

# --- Plotting ---
fig, ax = plt.subplots(figsize=(6, 3), dpi=120)

# 1. Plot Boltzmann Probabilities for each Temp (Area Normalization: Integral = 1)
for T, color in zip(temps, colors_plasma):
    probs = calculate_boltzmann_probs(energies, kde, T)
    
    # Normalize by area (integral) = 1 using trapezoidal rule
    sort_idx = np.argsort(energies)
    sorted_e = energies[sort_idx]
    sorted_p = probs[sort_idx]
    
    area = trapezoid(sorted_p, sorted_e)
    if area > 0:
        sorted_p = sorted_p / area
    
    note_label = f'{T} K'
    
    # Plot lines for all temperatures
    ax.plot(sorted_e, sorted_p, color=color, alpha=0.6, linewidth=1.2, label=note_label)
    
    # If T matches target_temp, fill the area under the curve
    if T == target_temp:
        ax.fill_between(sorted_e, 0, sorted_p, color=color, alpha=0.3)

# 2. Add Structural Limit Vertical Lines (Black) with Outlined Text
y_text_pos = 0.05 

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
ax.set_xlabel(r'Formation Energy (eV/atom)', fontsize=13)
ax.set_ylabel(r'Probability Density (Area = 1)', fontsize=13)

# Set axes limits based on Formation Energy range
ax.set_ylim(bottom=0, top=100)
ax.set_xlim(energies.min() - 0.005, energies.max() + 0.005)

ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())

# --- Legend Outside ---
ax.legend(frameon=False, 
          fontsize=10, 
          loc='upper left', 
          bbox_to_anchor=(1.02, 1.15))

plt.subplots_adjust(right=0.75) 
plt.savefig('boltzmann_probabilities_area_norm.png', dpi=300, bbox_inches='tight')

print("Plot saved to boltzmann_probabilities_area_norm.png")
plt.show()
