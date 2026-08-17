import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

dir_path = db_paths[0][0]
db_path = f"{dir_path}/1_db/db_0.db"
db = Database(filename=db_path)
db.restore_to_memory()
traj = db.restore_to_trajectory()

energies = np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj if hasattr(atoms, 'get_potential_energy')])

min_energy = np.min(energies)
relative_energies = energies - min_energy

# Constants
k_B = 1.380649e-23  # J/K
ev_to_j = 1.60218e-19

temperatures = [298.15, 348.60, 447.875, 547.15, 646.425]
# temperatures = np.linspace(298.15, 1046.425, 100)

def calculate_weighted_probability(relative_energies, temp, num_points=1000, plot_ratio=False):
    # 1. Fit the Energy Density (KDE)
    # This represents the density of states (how often an energy level appears)
    kde = gaussian_kde(relative_energies)
    
    # Create an energy grid for evaluation
    energy_grid = np.linspace(np.min(relative_energies), np.max(relative_energies), num_points)
    energy_density = kde(energy_grid)

    if plot_ratio:
        j = 0.04715
        k = 0
        idx_j = np.abs(energy_grid - j).argmin()
        idx_k = np.abs(energy_grid - k).argmin()

        Ej = energy_grid[idx_j]
        Ek = energy_grid[idx_k]

        g_Ej = energy_density[idx_j]
        g_Ek = energy_density[idx_k]

        energy_diff = Ej - Ek
        boltzmann_ratio = np.exp(-(energy_diff * ev_to_j) / (k_B * temp))
        ratio = (g_Ej / g_Ek) * boltzmann_ratio
        return energy_grid, energy_density, ratio

    
    # 2. Calculate Boltzmann Factors for the grid
    # We use the grid points to ensure the density and factors align
    boltzmann_factors = np.exp(-(energy_grid * ev_to_j) / (k_B * temp))
    
    # 3. Combine: Probability = Density of States * Boltzmann Occupancy
    # Unnormalized combined probability
    combined_prob_unnorm = energy_density * boltzmann_factors
    
    # 4. Normalize so the integral/sum equals 1
    # total_probability = np.trapz(combined_prob_unnorm, energy_grid)
    # final_probability_density = combined_prob_unnorm / total_probability

    final_probability_density = combined_prob_unnorm / np.sum(combined_prob_unnorm)
    energy_density = energy_density / np.sum(energy_density)

    avg_energy = np.sum(energy_grid * final_probability_density)

    
    # if plot_ratio:
    #     idx_ref = 0 
    #     E_k = energy_grid[idx_ref]
    #     g_Ek = energy_density[idx_ref]
        
        # ratio_all = []
        # for T in temp:
        #     # Calculate P(Ej) / P(Ek)
        #     # Ratio = (g_j / g_k) * exp(-(Ej - Ek) / kT)
        #     energy_diff = grid - E_k
        #     boltzmann_ratio = np.exp(-(energy_diff * ev_to_j) / (k_B * T))
        #     ratio = (energy_density / g_Ek) * boltzmann_ratio
        #     ratio_all.append(ratio)
            
    return energy_grid, final_probability_density, energy_density, avg_energy


plt.figure(figsize=(6, 4))

# ratio_all = []
# for i, temp in enumerate(temperatures):
#     # Use ratios
#     grid, prob_dist, ratio = calculate_weighted_probability(relative_energies, temp, plot_ratio=True)
#     ratio_all.append(ratio)

# plt.plot(temperatures,ratio_all)
# plt.show()

# We only need to plot the Raw Density once as a background
grid, _, raw_density_norm, _ = calculate_weighted_probability(relative_energies, temperatures[0])
plt.fill_between(grid, raw_density_norm, alpha=0.5, color='black', label='State Density (KDE)')

# Use a colormap to distinguish temperatures
colors = plt.cm.plasma(np.linspace(0, 0.8, len(temperatures)))

ratio_all = []
for i, temp in enumerate(temperatures):
    grid, prob_dist, _, avg_E = calculate_weighted_probability(relative_energies, temp)
    
    # Plot probability curve
    line, = plt.plot(grid, prob_dist, label=f'{temp} K', color=colors[i], linewidth=2)

    # Plot vertical line for <E> with same color
    # plt.axvline(avg_E, color=colors[i], linestyle='--', alpha=0.7, linewidth=1.5)
    
    # Annotate the average energy for clarity
    # plt.text(avg_E, np.max(prob_dist)*1.02, f'{avg_E:.3f}', 
    #          color=colors[i], horizontalalignment='center', fontsize=9)



plt.xlabel(r'$E_{rel}$ (eV/atom)', fontsize=12)
plt.ylabel('$P$ (a.u.)', fontsize=12)
# plt.title('Evolution of Energy Probability and Ensemble Average with Temperature', fontsize=14)
plt.legend(title="Temp.")
# plt.grid(True, alpha=0.2, linestyle='--')
# plt.ylim(0, 0.08) # Ensure y-axis starts at 0
# plt.xlim(0, 0.30) # Ensure y-axis starts at 0
plt.tight_layout()
plt.show()