import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, AutoMinorLocator 
from agox.models.descriptors.fingerprint import Fingerprint
from scipy.stats import gaussian_kde
from agox.databases import Database
from ase.io import read

structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')

raw_energies, valid_structures = [], []
for atoms in structures:
    try:
        raw_energies.append(atoms.get_potential_energy())
        valid_structures.append(atoms)
    except: continue 

num_atoms = len(valid_structures[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
# energies = (np.array(raw_energies) - min(raw_energies))

fp_instance = Fingerprint.from_atoms(valid_structures[0])
data = np.array([fp_instance.create_features(s).flatten() for s in valid_structures])

X_centered = data - np.mean(data, axis=0)
cov_matrix = np.cov(X_centered, rowvar=False)
evals, evecs = np.linalg.eigh(cov_matrix)
idx = np.argsort(evals)[::-1]
X_eigen = X_centered @ evecs[:, idx[0]]


min_x, max_x = -4, 4
min_e, max_e = 0.0, 0.8
# Target Style Parameters from Memory
# min_x, max_x = min(X_eigen), max(X_eigen)
# min_e, max_e = min(energies), max(energies)
xticks = np.round(np.linspace(min_x, max_x, 5), 0)
eticks = np.round(np.linspace(min_e, max_e, 5), 1)

energy_grid = np.linspace(min_e, max_e, 100)

plt.rcParams.update(rcParams)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3), sharey=True, 
                               gridspec_kw={'width_ratios': [2, 1]})

# Scatter Plot of raw data on ax1
ax1.scatter(X_eigen, energies, s=15, facecolors='white', edgecolors='black', 
            linewidth=1.0, alpha=0.5, zorder=2)

# Raw State Density on ax2 (Calculated from actual energy distribution)
kde = gaussian_kde(energies)
density = kde.evaluate(energy_grid)
ax2.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
ax2.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.2)

# Ticks and Labels
ax1.set_xlabel(r'$\psi_{1d}$ (Valle-Oganov)')
ax1.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)')
# ax1.set_xlim(min_x, max_x)
ax1.set_ylim(min_e, max_e)
# ax1.set_xticks(xticks)
ax1.set_yticks(eticks)
ax1.tick_params(labelsize=12)
# ax1.xaxis.set_minor_locator(FixedLocator((xticks[:-1] + xticks[1:]) / 2))
# ax1.yaxis.set_minor_locator(FixedLocator((eticks[:-1] + eticks[1:]) / 2))
ax1.xaxis.set_minor_locator(AutoMinorLocator())
ax1.yaxis.set_minor_locator(AutoMinorLocator())

ax2.set_xlabel('State Density')
ax2.tick_params(labelsize=12)

plt.tight_layout()
plt.show()


########

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, AutoMinorLocator 
from agox.models.descriptors.fingerprint import Fingerprint
from scipy.stats import gaussian_kde
from agox.databases import Database
from ase.io import read

from matplotlib import patheffects  # Required for the white outline


structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')

raw_energies, valid_structures = [], []
for atoms in structures:
    try:
        raw_energies.append(atoms.get_potential_energy())
        valid_structures.append(atoms)
    except: continue 

limits = {
    "Islands": 0.07,
    "Quasi-flat": 0.25,
    "Flat": 0.50
}

num_atoms = len(valid_structures[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
# energies = (np.array(raw_energies) - min(raw_energies))

fp_instance = Fingerprint.from_atoms(valid_structures[0])
data = np.array([fp_instance.create_features(s).flatten() for s in valid_structures])

X_centered = data - np.mean(data, axis=0)
cov_matrix = np.cov(X_centered, rowvar=False)
evals, evecs = np.linalg.eigh(cov_matrix)
idx = np.argsort(evals)[::-1]
X_eigen = X_centered @ evecs[:, idx[0]]


min_x, max_x = -4, 4
min_e, max_e = 0.0, 0.8
# Target Style Parameters from Memory
# min_x, max_x = min(X_eigen), max(X_eigen)
# min_e, max_e = min(energies), max(energies)
xticks = np.round(np.linspace(min_x, max_x, 5), 0)
eticks = np.round(np.linspace(min_e, max_e, 5), 1)

energy_grid = np.linspace(min_e, max_e, 100)

plt.rcParams.update(rcParams)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3), sharey=True, 
                               gridspec_kw={'width_ratios': [2, 1]})

# Scatter Plot of raw data on ax1
ax1.scatter(X_eigen, energies, s=15, facecolors='white', edgecolors='black', 
            linewidth=1.0, alpha=0.5, zorder=2)

# Raw State Density on ax2 (Calculated from actual energy distribution)
kde = gaussian_kde(energies)
density = kde.evaluate(energy_grid)
ax2.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
ax2.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.2)

# Ticks and Labels
ax1.set_xlabel(r'$\psi_{1d}$')
ax1.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)')
# ax1.set_xlim(min_x, max_x)
ax1.set_ylim(min_e, max_e)
# ax1.set_xticks(xticks)
ax1.set_yticks(eticks)
ax1.tick_params(labelsize=12)
# ax1.xaxis.set_minor_locator(FixedLocator((xticks[:-1] + xticks[1:]) / 2))
# ax1.yaxis.set_minor_locator(FixedLocator((eticks[:-1] + eticks[1:]) / 2))
ax1.xaxis.set_minor_locator(AutoMinorLocator())
ax1.yaxis.set_minor_locator(AutoMinorLocator())

for label, val in limits.items():
    # Horizontal lines across both plots
    ax1.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=10)
    ax2.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=10)
    
    # Create the horizontal text label (No bold fontweight)
    t = ax2.text(0, val + 0.005, f'{val:.2f} eV/atom', 
                fontsize=10, color='black', 
                verticalalignment='bottom', zorder=11)
    
    # Apply the white outline effect for readability
    t.set_path_effects([
        patheffects.withStroke(linewidth=3, foreground='white')
    ])

ax2.set_xlabel('State Density')
ax2.tick_params(labelsize=12)

plt.tight_layout()
plt.show()