from ase.io import read
# from scripts.plot_structure import plot_structure
import numpy as np

# cell_offset = np.array([0, 8.7, 0])  # 22
# cell_offset = np.array([8.7, 8.7, 0]) # 23
# cell_offset = np.array([5, 5, 0]) # 24

# cell_offset = np.array([10, 10, 0])  
# structs = read(f"{dir_out}/{dir_xsf}/20/struct_1577.xsf")
# structs = read(f"{dir_out}/{dir_xsf}/18/struct_259.xsf")
# structs = read(f"{dir_out}/{dir_xsf}/19/struct_1109.xsf")
# atom_center = structs.get_positions().mean(axis=0)
# structs.rotate(90, 'z', center=atom_center)

# structs = read(f"{dir_out}/{dir_xsf}/19/struct_919.xsf")
# structs = read(f"{dir_out}/{dir_xsf}/19/struct_1124.xsf")
# structs = read(f"{dir_out}/{dir_xsf}/19/struct_1255.xsf")
# atom_center = structs.get_positions().mean(axis=0)
# structs.rotate(90, 'z', center=atom_center) #90

"""
734        | 0.447726        | 0.150352 
1040       | 0.500796        | 0.128013 
1237       | 0.549279        | 0.160606  

528        | 0.203660        | 1.223577 
748        | 0.247753        | 0.363083  
947        | 0.304457        | 0.445915 

1109| 0.0
56         | 0.098679        | 3.001485  
1268       | 0.181848        | 5.850280 
"""


# structs = read(f"{dir_out}/{dir_xsf}/18/struct_259.xsf")
# structs = read(f"{dir_out}/{dir_xsf}/20/struct_1577.xsf")
# constraint_symbols = ['Mg', 'O'] 
# height_darken_symbols = ['Fe']
# show_colorbar = True
# max_cbar = 5.0

# structs = read(f"1_result/32_dos/selected_structures_dos.traj", index=0)
# show_colorbar = False
# constraint_symbols = ['Mg', 'O'] 


# structs = read(f"{dir_out}/{dir_xsf}/19/struct_431.xsf") # struct_476
structs = read(f"{dir_out}/{dir_xsf}/22/struct_265.xsf")
constraint_symbols =  ['Mg', 'O'] 
height_darken_symbols =  ['Fe'] # ['Mg', 'O']
atom_center = structs.get_positions().mean(axis=0)
structs.rotate(90, 'z', center=atom_center) #90
show_colorbar = True
max_cbar = 5.0
cell_offset = np.array([3, 3, 0]) # 24


plot_structure(
    structs, 
    # axis_off = True,
    # plane='xz+',
    plane='xy+',
    # figsize=(3, 3),
    # figsize=(4, 4),
    figsize=(7, 7),

    cell_offset = cell_offset,
    repeat=3,
    constraint_symbols= constraint_symbols, 
    # height_darken_symbols=height_darken_symbols,  
    
    add_cell = True,
    radius_factor = 0.9,
    # linewidths = 2.5,
    linewidths = 2.0,
    cbar_label=r'$\Delta z$ ($\AA$)',
    show_colorbar = show_colorbar,
    fontsize = 21,
    max_cbar = max_cbar, #0.75,
    darken_factor=0.7,   # 0.0 = original color, 1.0 = goes toward black
    num_ticks=3          # Custom number of axis values
)