from pathlib import Path
import numpy as np
from ase.io import read
# from scripts.plot_structure import plot_structure

# ==========================================
# 1. Configuration & Input Setup
# ==========================================
# dir_out = Path("output")
# dir_xsf = Path("xsf")

# Target structure path
# struct_path = dir_out / dir_xsf / "22" / "struct_265.xsf"
# structs = read(struct_path)
# structs = read(f"{dir_out}/{dir_xsf}/22/struct_265.xsf")
structs = read(f"{dir_out}/{dir_xsf}/23/struct_355.xsf")

# Transformation parameters
rotation_angle = 0 #90  # degrees
rotation_axis = 'z'
cell_offset = np.array([3, 3, 0])

# Visualization styling
constraint_symbols = ['Mg', 'O']
height_darken_symbols = ['Fe']
show_colorbar = True
max_cbar = 5.0

# ==========================================
# 2. Structure Transformation
# ==========================================
atom_center = structs.get_positions().mean(axis=0)
structs.rotate(rotation_angle, rotation_axis, center=atom_center)

# ==========================================
# 3. Plotting
# ==========================================
plot_structure(
    structs,
    plane= 'yz+', #'xy+',
    figsize=(4, 4),
    cell_offset=cell_offset,
    repeat=3,
    constraint_symbols=constraint_symbols,
    add_cell=True,
    radius_factor=0.9,
    linewidths=2.0,
    cbar_label=r'$\Delta z$ ($\AA$)',
    show_colorbar=show_colorbar,
    fontsize=21,
    max_cbar=max_cbar,
    darken_factor=0.7,
    num_ticks=3
)

# ==========================================
# Legacy Configuration Presets (Reference)
# ==========================================
"""
Alternative cell offsets:
- np.array([0, 8.7, 0])   # Run 22
- np.array([8.7, 8.7, 0]) # Run 23
- np.array([5, 5, 0])     # Run 24
- np.array([10, 10, 0])

Alternative structure paths:
- dir_out / dir_xsf / "20" / "struct_1577.xsf"
- dir_out / dir_xsf / "18" / "struct_259.xsf"
- dir_out / dir_xsf / "19" / "struct_1109.xsf"
- dir_out / dir_xsf / "19" / "struct_919.xsf"
- dir_out / dir_xsf / "19" / "struct_1124.xsf"
- dir_out / dir_xsf / "19" / "struct_1255.xsf"
- dir_out / dir_xsf / "19" / "struct_431.xsf"
- "1_result/32_dos/selected_structures_dos.traj" (index=0)

Reference coordinate/value pairs:
734   | 0.447726 | 0.150352
1040  | 0.500796 | 0.128013
1237  | 0.549279 | 0.160606

528   | 0.203660 | 1.223577
748   | 0.247753 | 0.363083
947   | 0.304457 | 0.445915

1109  | 0.0
56    | 0.098679 | 3.001485
1268  | 0.181848 | 5.850280
"""