import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from matplotlib.colors import LinearSegmentedColormap

from matplotlib.ticker import FixedLocator

# Plot configuration
figsize = (4, 4)
min_x, max_x = -4, 4
min_y, max_y = -2, 4
min_e, max_e = 0.0, 0.8

# Generate tick values
xticks = np.round(np.linspace(min_x, max_x, 5), 0)
yticks = np.round(np.linspace(min_y, max_y, 5), 1)
eticks = np.round(np.linspace(min_e, max_e, 10), 1)

xticks_minor = (xticks[:-1] + xticks[1:]) / 2
yticks_minor = (yticks[:-1] + yticks[1:]) / 2
eticks_minor = (eticks[:-1] + eticks[1:]) / 2

# Load database
dir_path = db_paths[0][0]
db_path = os.path.join(dir_path, "1_db", "db_0.db")
db = Database(filename=db_path)
db.restore_to_memory()
traj = db.restore_to_trajectory()

# Extract descriptors and energies
descriptor = Fingerprint.from_atoms(traj[0])
all_features, raw_energies = [], []

for atoms in traj:
    try:
        f = descriptor.create_features(atoms)
        all_features.append(f.flatten())
        raw_energies.append(atoms.get_potential_energy())
    except Exception:
        continue 

# Process data
X = np.array(all_features)
num_atoms = len(traj[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms

# Dimension reduction
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# Initialize plot
fig, ax = plt.subplots(figsize=figsize, dpi=150)

# Create custom colormap
cmap = LinearSegmentedColormap.from_list("custom", ["#0000FF", "#FF0000"])

# Plot scatter data
sc = ax.scatter(
    X_pca[:, 0], X_pca[:, 1], c=energies, 
    cmap=cmap, vmin=min_e, vmax=max_e, 
    s=20, alpha=0.9, edgecolors='black', linewidths=0.3
)

# Find indices for the global minimum and maximum energies
idx_min: int = np.argmin(energies)
idx_max: int = np.argmax(energies)

# Add additional scatter points for extrema in black
# Using 'X_pca' for coordinates and a distinct size/edge for visibility
ax.scatter(
    X_pca[[idx_min, idx_max], 0], 
    X_pca[[idx_min, idx_max], 1], 
    color='white',
    s=40,               # Slightly larger than the standard points
    marker='o',         # Circular marker
    edgecolors='black', # White edge to make black points pop
    linewidths=0.8,
    zorder=10           # Ensure these points are on top of the main scatter
)

# Set axis aesthetics
ax.set_xlabel('Principal Component 1')
ax.set_ylabel('Principal Component 2')
# ax.set_xlim(min_x, max_x)
# ax.set_ylim(min_y, max_y)
# ax.set_xticks(xticks)
# ax.set_yticks(yticks)
# ax.tick_params(labelsize=12)

# ax.xaxis.set_minor_locator(FixedLocator(xticks_minor))
# ax.yaxis.set_minor_locator(FixedLocator(yticks_minor))

# Configure colorbar
cbar = fig.colorbar(sc, ax=ax, shrink=1, pad=0.03)
cbar.set_label(e_label)
# cbar.set_ticks(eticks)
# cbar.ax.yaxis.set_minor_locator(FixedLocator(eticks_minor))

# Save figure
fig.tight_layout()
out_path = os.path.join(dir_out, dir_im, 'energy_landscape_pca.png')
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.show()