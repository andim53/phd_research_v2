import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

dir_path = db_paths[0][0]
db_path = f"{dir_path}/1_db/db_0.db"
db = Database(filename=db_path)
db.restore_to_memory()
traj = db.restore_to_trajectory()
num_points=1000

# Constants for Binding Energy
# E_slab = -195.463476  # eV
E_slab = -92.946489 # eV
mu_fe = -8.553673     # eV/atom
n_fe = 9              # Number of Fe atoms


# Calculate Binding Energy for each frame: E_b = E_total - (E_slab + n*mu)
binding_energies = np.array([
    # atoms.get_potential_energy() - (E_slab + n_fe * mu_fe) 
    # for atoms in traj if hasattr(atoms, 'get_potential_energy')
    atoms.get_potential_energy()
    for atoms in traj if hasattr(atoms, 'get_potential_energy')
])


# Use relative binding energy for KDE
min_eb = np.min(binding_energies)
relative_eb = binding_energies - min_eb

kde = gaussian_kde(relative_eb)
eb_grid = np.linspace(np.min(relative_eb), np.max(relative_eb), num_points)
eb_density = kde(eb_grid)
eb_density = eb_density/min(eb_density)

########################################

# Statistical Mechanics Loop
kB = 8.617333262e-5
temperatures = [298.15, 348.60, 447.875, 547.15, 646.425]
results = []

for T in temperatures:
    beta = 1.0 / (kB * T)
    
    # 1. Intensive Gibbs Level (per atom)
    G_levels = eb_grid - kB * T * np.log(eb_density + 1e-20)
    delta_G_intensive = G_levels - np.min(G_levels)
    
    # 2. Boltzmann weighting using EXTENSIVE energy (total cluster)
    # This is the critical fix:
    boltzmann_factors = np.exp(-beta * (delta_G_intensive * n_fe))
    
    # 3. Partition Function and Probability
    Z = np.sum(boltzmann_factors)
    P_Eb = boltzmann_factors / Z
    
    # 4. Total Ensemble Gibbs Free Energy
    G_total = -kB * T * np.log(Z) + (np.min(G_levels) * n_fe)
    
    results.append({
        'T': T, 
        'G_total': G_total, 
        'P': P_Eb, 
        'G_levels': G_levels
    })

# 3. Plotting with Mandatory Researcher Style
fig, ax = plt.subplots(figsize=(7, 6))

# Tick Parameters as requested
min_x, max_x = -4, 4
min_y, max_y = -2, 4
min_e, max_e = 0.0, 0.8

xticks = np.round(np.linspace(min_x, max_x, 5), 0)
yticks = np.round(np.linspace(min_y, max_y, 5), 1)
eticks = np.round(np.linspace(min_e, max_e, 10), 1)

# xticks_minor = (xticks[:-1] + xticks[1:]) / 2
# yticks_minor = (yticks[:-1] + yticks[1:]) / 2

# ax.set_xlabel('Principal Component 1') # Keeping labels per your style instructions
# ax.set_ylabel('Principal Component 2')
# ax.set_xlim(min_x, max_x)
# ax.set_ylim(min_y, max_y)
# ax.set_xticks(xticks)
# ax.set_yticks(yticks)
# ax.tick_params(labelsize=12)
# ax.xaxis.set_minor_locator(FixedLocator(xticks_minor))
# ax.yaxis.set_minor_locator(FixedLocator(yticks_minor))

# Note: Mapping eb_grid to the required visual range [-4, 4] for PC1 compliance
# Here we plot the Probability P(Eb) across the normalized grid
for res in results:
    # Scale eb_grid for visualization if necessary, or plot directly
    ax.plot(eb_grid, res['P'], label=f"{res['T']} K", lw=1.5)

ax.legend(frameon=False, loc='upper right')
plt.tight_layout()
plt.savefig('binding_probability_vs_temperature.png', dpi=300)
plt.show()