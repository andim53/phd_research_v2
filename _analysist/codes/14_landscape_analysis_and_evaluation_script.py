import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
from matplotlib import patheffects
from matplotlib.ticker import AutoMinorLocator
from scipy.stats import gaussian_kde

from agox.models.descriptors.fingerprint import Fingerprint

# from scripts.plot_structure_landscape import plot_structure_landscape

# === Script Tuning Parameters ===
use_z_data = False
show_limits = False
animate_scatter = False
# custom_peak_labels = ['Island', 'Flat']
# custom_peak_labels = ['Flat', 'Disordered']
custom_peak_labels = None
z_atom_type = 'Fe'

# === Data Ingestion and Trajectory Extraction ===
# structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')
# structures = read(f"{dir_out}/{dir_xsf_traj}/traj_39.traj", index=':')
structures = read(f"{dir_out}/{dir_xsf_traj}/traj_65.traj", index=':')

raw_energies = []
valid_structures = []
z_height_spans = []

for atoms in structures:
    try:
        e = atoms.get_potential_energy()
        raw_energies.append(e)
        valid_structures.append(atoms)

        if use_z_data:
            z_pos = atoms.get_positions()[:, 2]
            z_height_spans.append(z_pos.max() - z_pos.min())
    except Exception:
        continue

# === Properties Scaling and Normalization ===
num_atoms = len(valid_structures[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms

if use_z_data:
    z_data = np.array(z_height_spans)
    z_data = z_data - min(z_data)  # Relative delta_z value
    show_cbar = True
    cbar_padding = 0.05
    colormap = 'PuBu'
else:
    z_data = None
    show_cbar = False
    cbar_padding = 0.02
    colormap = 'PuBu'

# === Dimensionality Reduction (PCA via Fingerprints) ===
fp_instance = Fingerprint.from_atoms(valid_structures[0])
data = np.array([fp_instance.create_features(s).flatten() for s in valid_structures])

X_centered = data - np.mean(data, axis=0)
cov_matrix = np.cov(X_centered, rowvar=False)
evals, evecs = np.linalg.eigh(cov_matrix)
idx = np.argsort(evals)[::-1]
X_eigen = X_centered @ evecs[:, idx[0]]

# === Figure Generation and Landscape Visualization ===
fig = plot_structure_landscape(
    # Core Data Inputs
    X_eigen,
    energies,
    z_data=z_data,

    # File and Save Settings
    save_path=f"{dir_out}/{dir_im}",
    animate_scatter=animate_scatter,

    # Plot Layout and Sizing
    # figsize=(6, 3),
    figsize=(5, 3),
    wspace=0.1,
    fontsize=10,

    # Energy and Density View Constraints
    # e_limit=(0.0-0.1, max(energies) + 0.1, 5),
    e_limit=(0.0-0.1, 2.0 + 0.1, 5),
    fill_density=True,
    dens_line_weight=0.9,
    show_limits=show_limits,
    custom_peak_labels=custom_peak_labels,

    # Colorbar and Colormap Styling
    cmap=colormap,
    show_colorbar=show_cbar,
    cbar_pad=cbar_padding,
    z_limit=(5.85, 0, 5),
    black_seed_zero=True,

    # Evaluation Flags
    plot_z_vs_e=False,
)
plt.show()