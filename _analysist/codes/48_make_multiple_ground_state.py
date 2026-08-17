from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

# Optional import for plotting structures
# from scripts.plot_structure import plot_structure

# ==========================================
# 1. Configuration & Parameters
# ==========================================
# Set directory paths (adjust strings if necessary)
dir_out = Path(dir_out)
dir_xsf_traj = Path(dir_xsf_traj)

# trajs = [
#     "traj_27.traj",
#     "traj_28.traj",
#     "traj_29.traj",
#     "traj_30.traj",
#     "traj_31.traj",
#     "traj_19.traj"
# ]

# labels = ["1.2 ML", "1.4 ML", "1.6 ML", "1.8 ML", "2.0 ML", "2.2 ML"]

trajs = [
    "traj_22.traj", 
    "traj_23.traj", 
    "traj_24.traj", 
    "traj_25.traj", 
    "traj_26.traj"
]

# legend_labels = ["0% MgO latt.", "25% MgO latt.", "50% MgO latt.", "75% MgO latt."]
labels = [
    '2.0 ML Fe/MgO',  # 27_fe_con0 (Baseline)
    '1.8 ML Fe/MgO',  # 28_fe_con5 (-5 atoms)
    '1.6 ML Fe/MgO',  # 29_fe_con10 (-10 atoms)
    '1.4 ML Fe/MgO',  # 30_fe_con15 (-15 atoms)
    '1.2 ML Fe/MgO',  # 31_fe_con20 (-20 atoms)
    '1.0 ML Fe/MgO',  # 31_fe_con20 (-20 atoms)
]
coverages = [float(lbl.split()[0]) for lbl in labels]

# Energy cutoff above ground state (in eV/atom)
ENERGY_THRESHOLD_PER_ATOM = 0.001  

output_img_dir = dir_out / "2_im"
output_img_dir.mkdir(parents=True, exist_ok=True)

# Helper function to compute thickness
def get_fe_thickness(atoms):
    symbols = np.array(atoms.get_chemical_symbols())
    positions = atoms.get_positions()
    fe_indices = np.where(symbols == 'Fe')[0]
    
    if len(fe_indices) > 0:
        z_fe = positions[fe_indices, 2]
        return z_fe.max() - z_fe.min()
    return 0.0

# ==========================================
# 2. Trajectory Processing
# ==========================================
scatter_x = []         # Coverages for structures in energy window
scatter_y = []         # Thicknesses for structures in energy window
ground_state_x = []    # Coverages for lowest energy structures
ground_state_y = []    # Thicknesses for lowest energy structures

for traj, coverage in zip(trajs, coverages):
    traj_path = dir_out / dir_xsf_traj / traj
    structures = read(traj_path, index=':')
    
    # Calculate energies and energy per atom
    energies = np.array([s.get_potential_energy() for s in structures])
    num_atoms = np.array([len(s) for s in structures])
    energies_per_atom = energies / num_atoms

    # Determine ground state energy (per atom)
    min_energy_per_atom = np.min(energies_per_atom)
    min_idx = np.argmin(energies_per_atom)

    # Filter structures within the energy window [E_min, E_min + 0.02 eV/atom]
    energy_diffs = energies_per_atom - min_energy_per_atom
    valid_indices = np.where(energy_diffs <= ENERGY_THRESHOLD_PER_ATOM)[0]

    # Collect data for valid structures
    for idx in valid_indices:
        struct = structures[idx]
        thickness = get_fe_thickness(struct)
        scatter_x.append(coverage)
        scatter_y.append(thickness)

    # Collect data specifically for the ground state
    ground_thickness = get_fe_thickness(structures[min_idx])
    ground_state_x.append(coverage)
    ground_state_y.append(ground_thickness)

    print(f"Traj: {traj} ({coverage} ML)")
    print(f"  Ground state energy: {min_energy_per_atom:.4f} eV/atom")
    print(f"  Structures within +{ENERGY_THRESHOLD_PER_ATOM} eV/atom: {len(valid_indices)}/{len(structures)}")

# ==========================================
# 3. Scatter Plot Generation
# ==========================================
plt.figure(figsize=(8, 6))

# Plot all low-energy candidate structures as translucent scatter points
plt.scatter(
    scatter_x,
    scatter_y,
    color='tab:blue',
    alpha=0.6,
    s=40,
    edgecolors='none',
    label=rf'Structures ($\leq$ +{ENERGY_THRESHOLD_PER_ATOM} eV/atom)'
)

# Overlay ground state points and trendline
sorted_ground = sorted(zip(ground_state_x, ground_state_y))
x_gs, y_gs = zip(*sorted_ground)

plt.plot(
    x_gs,
    y_gs,
    linestyle='--',
    color='tab:red',
    linewidth=1.5,
    alpha=0.7,
    label='Ground State Trend'
)

plt.scatter(
    x_gs,
    y_gs,
    color='tab:red',
    s=70,
    marker='o',
    zorder=3,
    label='Ground State'
)

# Axis & aesthetic formatting
plt.xlabel("Fe Coverage (ML)", fontsize=14)
plt.ylabel(r"Fe Layer Thickness ($\AA$)", fontsize=14)
plt.title(rf"Fe Layer Thickness vs. Coverage ($\Delta E \leq {ENERGY_THRESHOLD_PER_ATOM}$ eV/atom)", fontsize=14)
plt.xticks(np.arange(1.2, 2.3, 0.2))
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend(fontsize=11)

plt.tight_layout()
plt.savefig(output_img_dir / "fe_thickness_scatter_low_energy.png", dpi=300)
plt.show()