import matplotlib.pyplot as plt

plt.rcParams.update(rcParams)

# Data Conversion
rel_energies_mev = [e * 1000 for e in rel_energies]

# Plotting with Reversed Axes
plt.figure(figsize=(5, 3))
plt.scatter(rel_energies_mev, z_height_spans, color=colors[0], s=20, edgecolors='black', linewidths=0.5)

plt.xlabel(r"Relative Energy ($\text{meV}$)")
plt.ylabel(r"Height Span ($\text{\AA}$)")
plt.tight_layout()
plt.savefig('energy_vs_z_scatter.png', dpi=300)