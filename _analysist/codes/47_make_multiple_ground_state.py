from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from ase.constraints import FixAtoms
from ase.io import read
# from scripts.plot_structure import plot_structure

# ==========================================
# 1. Configuration & Input Setup
# ==========================================
dir_out = Path(dir_out)
dir_xsf_traj = Path(dir_xsf_traj)

# Files and dataset descriptors
trajs = [
    "traj_27.traj",
    "traj_28.traj",
    "traj_29.traj",
    "traj_30.traj",
    "traj_31.traj",
    "traj_19.traj"
]

# (Placeholder data for missing external structures in original snippet)
db_paths = [("db_path", i) for i in range(len(trajs))]
labels = ["1.2 ML", "1.4 ML", "1.6 ML", "1.8 ML", "2.0 ML", "2.2 ML"]
cell_offset = np.array([0, 0, 0])

# Directory setup
output_img_dir = dir_out / "2_im"
output_img_dir.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Trajectory Analysis & Structure Plotting
# ==========================================
thickness_list = []

for traj, (_, num) in zip(trajs, db_paths):
    output_img_dir_num = output_img_dir / str(num)
    output_img_dir_num.mkdir(parents=True, exist_ok=True)

    # Read trajectory and extract lowest energy structure
    traj_path = dir_out / dir_xsf_traj / traj
    structures = read(traj_path, index=':')
    energies = [s.get_potential_energy() for s in structures]
    best_idx = np.argmin(energies)
    best_structure = structures[best_idx]

    # Calculate Fe layer thickness
    symbols = np.array(best_structure.get_chemical_symbols())
    positions = best_structure.get_positions()
    fe_indices = np.where(symbols == 'Fe')[0]
    
    if len(fe_indices) > 0:
        z_fe = positions[fe_indices, 2]
        fe_thickness = z_fe.max() - z_fe.min()
    else:
        fe_thickness = 0.0

    # Save structure visualization
    plot_structure(
        best_structure,
        plane='xy+',
        save_path=str(output_img_dir_num / f"ground_{best_idx}.png"),
        figsize=(5, 5),
        cell_offset=cell_offset,
        repeat=3,
        constraint_symbols=['Mg', 'O'],
        height_darken_symbols=['Fe'],
        add_cell=True,
        radius_factor=0.9,
        linewidths=2.5,
        cbar_label=r'$\Delta z$ ($\AA$)',
        show_colorbar=True,
        fontsize=21,
        max_cbar=5.61,
        darken_factor=0.7,
        num_ticks=3,
        plot_show=False
    )

    print(f"Traj: {traj}")
    print(f"  Lowest Energy: {best_structure.get_potential_energy():.4f} eV")
    print(f"  Fe layer thickness (span): {fe_thickness:.3f} Å")

    thickness_list.append(fe_thickness)

# ==========================================
# 3. Data Sorting & Summary Plot
# ==========================================
coverage_list = [float(label.split()[0]) for label in labels]
sorted_data = sorted(zip(coverage_list, thickness_list))
x_plot, y_plot = zip(*sorted_data)

plt.figure(figsize=(7, 5))
plt.plot(
    x_plot,
    y_plot,
    marker='o',
    markersize=8,
    linestyle='-',
    linewidth=2,
    color='tab:red',
    label='Fe Thickness'
)

# Formatting
plt.xlabel("Fe Coverage (ML)", fontsize=14)
plt.ylabel(r"Fe Layer Thickness ($\AA$)", fontsize=14)
plt.title("Fe Layer Thickness vs. Coverage on MgO", fontsize=15)
plt.xticks(np.arange(1.2, 2.3, 0.2))
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

plt.tight_layout()
plt.savefig(output_img_dir / "fe_thickness_vs_coverage.png", dpi=300)
plt.show()