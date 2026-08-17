"""
AGOX Data Analysis: Energy Distributions and Thermal Statistics
---------------------------------------------------------------
1. plot_energy_distribution: Versatile box/KDE plotting for database comparison.
2. calculate_weighted_probability: Thermodynamic weighting of State Density.
3. Temperature Sweep: Visualization of probability shift with T.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from agox.databases import Database
from scripts.calculate_relative_energy import calculate_relative_energy

# --- Constants ---
K_B = 1.380649e-23     # J/K
EV_TO_J = 1.60218e-19  # Conversion factor

# =============================================================================
# 1. ENSEMBLE VISUALIZATION TOOLS
# =============================================================================

def plot_energy_distribution(
        db_paths, labels, dir_out, dir_im,
        figsize=(4, 6),
        y_label=r'$E_{rel}$ (eV/atom)',
        x_label='State Density',
        colors=None,
        plot_single=False,
        single_index=0,
        linewidth=2.2,
        plot_type="box",  # "box" or "density"
        x_lim=(None, None, None),
        y_lim=(None, None, None),
        show_legend=True
    ):
    """
    Plots energy distributions from multiple databases as Box Plots or KDEs.
    """
    # Standard Publication-Style Formatting
    params = {
        'font.size': 10,
        'font.family': 'sans-serif',
        'mathtext.fontset': 'cm',
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'axes.linewidth': linewidth,
        'xtick.major.width': linewidth,
        'ytick.major.width': linewidth,
    }
    plt.rcParams.update(params)
    plt.figure(figsize=figsize, dpi=300)

    indices = [single_index] if plot_single else range(len(db_paths))

    for idx in indices:
        # Load Database
        dir_path, _ = db_paths[idx]
        db_file = os.path.join(dir_path, "1_db", "db_0.db")
        db = Database(filename=db_file)
        trajs = db.restore_to_trajectory()
        
        # Calculate Relative Energies (eV/atom)
        _, _, _, rel_energies = calculate_relative_energy(trajs)
        rel_energies = np.array(rel_energies)
        color = colors[idx % len(colors)] if colors else "lightgray"

        if plot_type == "box":
            plt.boxplot(
                rel_energies, positions=[idx + 1], patch_artist=True,
                boxprops=dict(facecolor=color, linewidth=linewidth),
                medianprops=dict(color='black', linewidth=linewidth)
            )
        else:
            # KDE Density Plot
            ys = np.sort(rel_energies)
            kde = gaussian_kde(ys)
            density_y = np.linspace(ys.min(), ys.max(), 300)
            density_x = kde(density_y)
            plt.plot(density_x, density_y, color=color, linewidth=linewidth)
            plt.fill_betweenx(density_y, 0, density_x, color=color, alpha=0.1)

    # Axis Styling
    plt.ylabel(y_label)
    if plot_type == "density": plt.xlabel(x_label)
    else: plt.xticks([i + 1 for i in indices], [labels[i] for i in indices], rotation=45)

    # Set Limits
    if x_lim[0] is not None: plt.xlim(x_lim[0:2])
    if y_lim[0] is not None: plt.ylim(y_lim[0:2])

    plt.tight_layout()
    plt.show()

# =============================================================================
# 2. THERMODYNAMIC PROBABILITY CALCULATIONS
# =============================================================================

def calculate_weighted_probability(relative_energies, temp, num_points=1000):
    """
    Calculates Boltzmann-weighted probability density from a KDE of the energy.
    Probability = Density of States * Boltzmann Occupancy
    """
    # 1. Density of States (KDE)
    kde = gaussian_kde(relative_energies)
    energy_grid = np.linspace(np.min(relative_energies), np.max(relative_energies), num_points)
    energy_density = kde(energy_grid)
    
    # 2. Boltzmann Factors
    boltzmann_factors = np.exp(-(energy_grid * EV_TO_J) / (K_B * temp))
    
    # 3. Combine and Normalize
    combined_prob_unnorm = energy_density * boltzmann_factors
    final_prob = combined_prob_unnorm / np.sum(combined_prob_unnorm)
    raw_density_norm = energy_density / np.sum(energy_density)

    # 4. Ensemble Average <E>
    avg_energy = np.sum(energy_grid * final_prob)
    
    return energy_grid, final_prob, raw_density_norm, avg_energy

# =============================================================================
# 3. EXECUTION: TEMPERATURE SWEEP VISUALIZATION
# =============================================================================

# Example setup for a single database (Index 3)
target_db = db_paths[3][0]
db = Database(filename=f"{target_db}/1_db/db_0.db")
traj = db.restore_to_trajectory()

# Extract per-atom relative energies
energies = np.array([a.get_potential_energy()/len(a) for a in traj if hasattr(a, 'get_potential_energy')])
rel_energies = energies - np.min(energies)

# Parameters
temperatures = [298.15, 348.60, 447.875, 547.15, 646.425]
colors = plt.cm.plasma(np.linspace(0, 0.8, len(temperatures)))

plt.figure(figsize=(10, 6))

# Plot underlying State Density
grid, _, raw_density, _ = calculate_weighted_probability(rel_energies, temperatures[0])
plt.fill_between(grid, raw_density, alpha=0.15, color='gray', label='State Density (KDE)')

# Plot Thermalized Distributions
for i, T in enumerate(temperatures):
    grid, prob_dist, _, avg_E = calculate_weighted_probability(rel_energies, T)
    
    plt.plot(grid, prob_dist, label=f'{T} K', color=colors[i], linewidth=2)
    plt.axvline(avg_E, color=colors[i], linestyle='--', alpha=0.7)
    
    # Annotate <E>
    plt.text(avg_E, np.max(prob_dist)*1.02, f'{avg_E:.3f}', 
             color=colors[i], ha='center', fontsize=9)

plt.xlabel('Relative Energy (eV/atom)')
plt.ylabel('Probability ($P_i$)')
plt.legend(title="Temperature")
plt.grid(True, alpha=0.2, linestyle='--')
plt.ylim(0, None)
plt.tight_layout()
plt.show()