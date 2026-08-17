import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from agox.databases import Database

# 1. Load Data
dir_path = db_paths[0][0]
db_path = f"{dir_path}/1_db/db_0.db"
db = Database(filename=db_path)
db.restore_to_memory()
traj = db.restore_to_trajectory()

# 2. Extract Energies per atom
energies = np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj if hasattr(atoms, 'get_potential_energy')])

# 3. Process Energies (Relative to Ground State)
min_energy = np.min(energies)
relative_energies = energies - min_energy
sort_idx = np.argsort(relative_energies)
sorted_relative_energies = relative_energies[sort_idx]

# 4. Constants & Temperatures
ev_to_j = 1.60218e-19
k_B = 1.380649e-23  

temperatures = [298.15, 348.60, 447.875, 547.15, 646.425]
colors = ['black', 'blue', 'green', 'orange', 'purple']

def calculate_probabilities(E_ev, temp):
    boltzmann_factors = np.exp(-(E_ev * ev_to_j) / (k_B * temp))
    Z = np.sum(boltzmann_factors)
    return boltzmann_factors / Z

# 5. Plotting Setup
plt.style.use('seaborn-v0_8-white') 
fig, ax = plt.subplots(figsize=(6.5, 5.5))

# Loop through temperatures
for i, T in enumerate(temperatures):
    # Calculate
    probs = calculate_probabilities(relative_energies, T)
    sorted_probs = probs[sort_idx]
    
    # CALCULATE GRADIENT (m)
    # We fit log10(p) = m * E + c
    log_p = np.log10(sorted_probs)
    m, c = np.polyfit(sorted_relative_energies, log_p, 1)
    
    # Line + Scatter Plot - Label now includes gradient m
    line_label = f'$T$ = {T:.1f} K, $m$ = {m:.2f}'
    ax.plot(sorted_relative_energies, sorted_probs, 
            color=colors[i], 
            marker='o', markersize=3, markerfacecolor='white',
            markeredgewidth=0.5, linewidth=1, 
            label=line_label, zorder=1)

    # Highlight specific indices
    highlight_idx = [8, 10, 16]
    ax.scatter(sorted_relative_energies[highlight_idx[0]], sorted_probs[highlight_idx[0]], 
               edgecolors='black', facecolors='none', marker='o', s=40, linewidth=1.5, zorder=3)
    ax.scatter(sorted_relative_energies[highlight_idx[1]], sorted_probs[highlight_idx[1]], 
               edgecolors='red', facecolors='none', marker='o', s=40, linewidth=1.5, zorder=3)
    ax.scatter(sorted_relative_energies[highlight_idx[2]], sorted_probs[highlight_idx[2]], 
               edgecolors='blue', facecolors='none', marker='o', s=40, linewidth=1.5, zorder=3)

# 6. Minimalist Research Styling
# ax.set_yscale('log')
ax.set_xlabel('Relative Energy (eV/atom)', fontsize=11)
ax.set_ylabel(r'Probability $p_i$', fontsize=11)

# Tickers
ax.yaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=10))
ax.yaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=10))
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))

ax.tick_params(axis='both', which='major', direction='in', length=6, width=1, top=True, right=True)
ax.tick_params(axis='both', which='minor', direction='in', length=3, width=0.8, top=True, right=True)

# Grid and Legend
ax.grid(axis='y', which='major', linestyle=':', alpha=0.4)
ax.legend(frameon=True, fontsize=8, loc='upper right', title="Temperature & Gradient")

ax.set_xlim(0.0, 0.1)
ax.set_ylim(0.001, 0.15)

# Mathematical Note Annotation
ax.text(0.05, 0.002, r'$\log_{10}(p_i) = -\frac{1}{k_B T \ln(10)} E_i + C$', 
        fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# Title
ax.set_title('Boltzmann Distribution: Slope Analysis', loc='left', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.show()