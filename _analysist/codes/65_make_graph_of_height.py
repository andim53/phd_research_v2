
z_height_spans = [atoms.get_positions()[:, 2].max() - atoms.get_positions()[:, 2].min() for atoms in trajs]
plt.scatter(rel_energies_mev, z_height_spans, color=colors[0], s=20, edgecolors='black', linewidths=0.5)
