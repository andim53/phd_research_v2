import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ase.io import read
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from agox.models.descriptors import Fingerprint

INPUT_TRAJ = f"{dir_out}/{dir_xsf_traj}/traj_19.traj"
CSV_OUTPUT = "clustering_results.csv" 

structures = read(INPUT_TRAJ, index=':')
num_atoms = len(structures[0])
energies = np.array([s.get_potential_energy() for s in structures])
rel_energies = (energies - np.min(energies)) / num_atoms

descriptor = Fingerprint.from_atoms(structures[0])
X_raw = np.array(descriptor.get_features(structures))
X = X_raw.sum(axis=1) if X_raw.ndim == 3 else X_raw

# X_scaled = StandardScaler().fit_transform(X)
X_scaled = X

n_categories = 1 + min(9, int(np.floor(len(energies) / 5)))
kmeans = KMeans(
    n_clusters=n_categories, 
    init='k-means++', 
    n_init=10, 
    random_state=42
)
labels = kmeans.fit_predict(X_scaled)

# Calculate "certainty" based on distance to center 
# (Closer to center = higher alpha)
distances = kmeans.transform(X_scaled) 
min_distances = np.min(distances, axis=1)
# Normalize distances for alpha (1.0 at center, 0.2 at furthest point)
alpha_values = 1.0 - 0.8 * (min_distances / np.max(min_distances))

pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_scaled)
variance_ratio = pca.explained_variance_ratio_

data_to_save = {
    'structure_index': np.arange(len(structures)),
    'category_id': labels,
    'potential_energy_ev': energies,
    'relative_energy_ev_atom': rel_energies,
    'pca_1': X_2d[:, 0],
    'pca_2': X_2d[:, 1],
    'dist_to_centroid': min_distances
}

df = pd.DataFrame(data_to_save)
df.to_csv(f"{dir_out}/{CSV_OUTPUT}", index=False)
print(f"Success: Clustering results saved to {CSV_OUTPUT}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

scatter1 = ax1.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='tab10', 
                       s=60, alpha=alpha_values, edgecolors='black', linewidth=0.3)
# ax1.set_title(f"K-Means++ Categories ({n_categories} clusters)")
ax1.set_xlabel(f'PCA 1 ({variance_ratio[0]*100:.1f}%)')
ax1.set_ylabel(f'PCA 2 ({variance_ratio[1]*100:.1f}%)')
fig.colorbar(scatter1, ax=ax1, label='Category ID')

sns.boxplot(x=labels, y=rel_energies, ax=ax2, palette='tab10', hue=labels, legend=False)
sns.stripplot(x=labels, y=rel_energies, ax=ax2, color='black', size=3, alpha=0.4)
# ax2.set_title('Thermodynamic Stability by Category')
ax2.set_xlabel('Category ID')
ax2.set_ylabel(r'$E_i - E_{glob}$ (eV/atom)')

plt.tight_layout()
plt.show()

print(f"{'Category':<10} | {'Count':<8} | {'Avg Rel Energy (eV/atom)':<25}")
print("-" * 50)
for i in range(n_categories):
    mask = (labels == i)
    count = np.sum(mask)
    if count > 0:
        avg_e = np.mean(rel_energies[mask])
        print(f"{i:<10} | {count:<8} | {avg_e:.6f}")