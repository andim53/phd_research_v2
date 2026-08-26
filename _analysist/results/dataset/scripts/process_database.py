from ase.io import write
import os
import numpy as np
import pandas as pd
from agox.databases import Database
from .plot_structure import plot_structure
# from .percentage_energy_change import percentage_energy_change
from .plot_1d_scatter import plot_1d_scatter
from .plot_distance_distributions import plot_distance_distributions

def process_database(db_path, file_idx, num_of_min, dir_out, dir_xsf_traj, dir_xsf):
    """
    Processes a database file, extracts trajectories and energies, and saves minimum energy structures.

    Parameters:
        db_path (str): Path to the database file.
        file_idx (int): Index associated with the file.
        num_of_min (int): Number of minimum energy structures to save.
        dir_out (str): Output directory for analysis results.
        dir_xsf_traj (str): Directory to save full trajectories in XSF and TRAJ format.
        dir_xsf (str): Directory to save individual selected structures in XSF format.
    """
    __version__ = "0.0.2"

    database = Database(filename=db_path)
    database.restore_to_memory()
    trajs = database.restore_to_trajectory()

    print(f"Loaded {file_idx} from Database")

    os.makedirs(f"{dir_out}/{dir_xsf}/{file_idx}", exist_ok=True)


    path_fig = f'{dir_out}/7_fig'
    os.makedirs(f'{path_fig}', exist_ok=True)

    path_fig_atom = f'{path_fig}/0_fig_atom'
    os.makedirs(f'{path_fig}', exist_ok=True)
    os.makedirs(f'{path_fig_atom}/{file_idx}', exist_ok=True)

    write(f"{dir_out}/{dir_xsf_traj}/traj_{file_idx}.xsf", trajs)
    write(f"{dir_out}/{dir_xsf_traj}/traj_{file_idx}.traj", trajs)

    all_e = []
    for atoms_frame in trajs:
        e = atoms_frame.get_potential_energy()
        all_e.append(e)

    sorted_e = np.argsort(all_e)
    min_e = all_e[sorted_e[0]]
    e_new = [e - min_e for e in all_e]
    x_label = r"$E$ Relative (eV)"

    struct_min = trajs[sorted_e[0]].copy()
    if 'initial_magmoms' in struct_min.arrays:
        del struct_min.arrays['initial_magmoms']
    if 'magmoms' in struct_min.arrays:
        del struct_min.arrays['magmoms']
    write(f"{dir_out}/{dir_xsf}/{file_idx}/struct_min_{sorted_e[0]}.xsf", struct_min)


    with open(f'{dir_out}/e_note.md', 'a') as file:
        scheme = db_path.split("/")[-3] # Adjusted to get the parent directory name
        file.write(f'\n=== Scheme: {scheme} | Index: {file_idx} | Total Structures: {len(trajs)} ===\n')
        file.write(f'idx\tEtotal (eV)\tE_relative (eV)\n')
        file.write(f'{db_path}\n')

        list_new = sorted_e[:num_of_min]
        list_new = [list_new[i] for i in range(len(list_new)) if list_new[i] != list_new[i-1] - 1]
        
        e_new_plot = [e_new[i] for i in list_new]
        plot_1d_scatter(
              e_new_plot, 
              xlabel=x_label, 
              xlim_low = 0,
              xlim_high = 1,
              xticks = np.arange(0,1.1,0.25),
              save_path=f'{path_fig_atom}/axis_{file_idx}.png',
              save_data_path=f'{path_fig_atom}/data_{file_idx}.csv')

        print(f'{sorted_e[:num_of_min]=}')
        print(f'{list_new=}')
        for j, i in enumerate(list_new):
            file.write(f'{i}\t{all_e[i]:.6f}\t{e_new[i]:.6f}\n')

            # Remove magmom before saving each selected structure
            atoms_i = trajs[i].copy()
            if 'initial_magmoms' in atoms_i.arrays:
                del atoms_i.arrays['initial_magmoms']
            if 'magmoms' in atoms_i.arrays:
                del atoms_i.arrays['magmoms']
            write(f'{dir_out}/{dir_xsf}/{file_idx}/struct_{i}_{j}.xsf', atoms_i)

            cell_offset = np.array([0.5, 0.5, 0.0])
            plot_structure(
                        atoms_i,
                        plane='xy+',
                        save_path=f"{path_fig_atom}/{file_idx}/figure_xy_{i}_{j}.png",
                        figsize = (5,5),
                        repeat=5,
                        cell_offset = cell_offset,
                        plot_show = False,
                )
            
            plot_structure(
                        atoms_i,
                        plane='yz+',
                        save_path=f"{path_fig_atom}/{file_idx}/figure_yz_{i}_{j}.png",
                        figsize = (5,5),
                        repeat=5,
                        cell_offset = cell_offset,
                        plot_show = False,
                )

            plot_structure(
                        atoms_i,
                        plane='xz+',
                        save_path=f"{path_fig_atom}/{file_idx}/figure_xz_{i}_{j}.png",
                        figsize = (5,5),
                        repeat=5,
                        cell_offset = cell_offset,
                        plot_show = False,
                )
            
            

# dir_out = "."

# # Create the note file before the loop
# with open(f'{dir_out}/e_note.md', 'w') as f:
#     f.close()

# num_of_min = 10

# # Process each database path
# for dir_path, file_idx in db_paths:
#     db_path = f"{dir_path}/1_db/db_0.db"
#     process_database(db_path, file_idx, num_of_min, dir_out, dir_xsf_traj, dir_xsf)