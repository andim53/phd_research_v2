import os
import numpy as np
import matplotlib.pyplot as plt
from ase.io import write, read
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint

def plot_energy_progression(db_paths, labels, dir_out, dir_im):
    """
    Plots the best-so-far relative energy progression for selected databases.

    Parameters:
        db_paths (list): List of tuples (dir_path, label, file_idx, base_key) for databases.
        labels (list): List of labels for the plots.
        dir_out (str): Output directory for analysis results.
        dir_im (str): Directory to save image files.
    """
    # === Plotting Style Setup ===
    plt.rcParams.update({
        'font.size': 10,
        'font.family': 'sans-serif',
        'axes.linewidth': 1.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.edgecolor': 'black',
        'xtick.major.size': 6,
        'ytick.major.size': 6,
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'xtick.color': 'black',
        'ytick.color': 'black',
        'axes.grid': False,
        'legend.frameon': False
    })

    # Define line styles and markers for differentiation without color
    line_styles = [':', '--', '-', '-.']
    # Define markers for scatter plot
    scatter_markers = ['o', 's', '^', 'd']

    # === Plot Setup ===
    fig, ax = plt.subplots(figsize=(6, 3), dpi=300)

    for i, (dir_path, file_idx) in enumerate(db_paths[:4]):
        # if file_idx in [1,3]:
        #     continue

        db_path = f"{dir_path}/1_db/db_0.db"

        database = Database(filename=db_path)
        trajs = database.restore_to_trajectory()
        print(f"Loaded DB: {db_path}")

        all_e = []
        for atoms_frame in trajs:
            e = atoms_frame.get_potential_energy()
            all_e.append(e)

        rel_energies = calculate_normalized_relative_energies(all_e)
        best_energies, best_indices = compute_best_so_far_idx(rel_energies)

        # Filter best_indices to remove consecutive indices with small increments
        filtered_best_indices = [best_indices[0]]
        for j in range(1, len(best_indices)):
            if best_indices[j] > filtered_best_indices[-1] + 2: # Keep if index is more than 2 greater than the last kept index
                filtered_best_indices.append(best_indices[j])

        # best_energies = compute_best_so_far(all_e)

        # Use line style and marker based on index
        ax.plot(range(len(best_energies)), best_energies,
                linewidth=1.5,
                linestyle=line_styles[i % len(line_styles)],
                markevery=max(1, len(best_energies) // 10), # Add markers at intervals
                color='black', # Use black color
                label=labels[file_idx % len(labels)])

        # Add scatter plot for filtered best indices
        filtered_best_energies = [best_energies[idx] for idx in filtered_best_indices]
        ax.scatter(filtered_best_indices, filtered_best_energies,
                   color=plt.rcParams['axes.edgecolor'], # Use the same color as axes
                   marker=scatter_markers[i % len(scatter_markers)],
                   s=5,  # Size of the scatter markers
                   zorder=2) # Ensure scatter points are above the line

    # === Final Plot Formatting ===
    ax.set_xlabel("Structure")
    # ax.set_ylabel("Relative Energy (eV)")
    ax.set_ylabel(r'$P$ (%)')
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.legend(fontsize=7, loc='upper right')
    plt.tight_layout()

    # === Save and Show Plot ===
    plt.savefig(f"{dir_out}/{dir_im}/relative_energy_progression.png",
                dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.show()

# Call the function with appropriate arguments
# plot_energy_progression(db_paths, labels, dir_out, dir_im)