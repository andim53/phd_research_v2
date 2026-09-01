# @title
from agox.utils.plot.colors import Colors
from agox.utils.plot import plot_atoms, plot_cell
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read
from ase.constraints import FixAtoms
from typing import Optional # Import Optional
from numpy.typing import NDArray # Import NDArray

def plot_structure(atoms,
                   plane='yz+',
                   plot_constraint=True,
                   figsize=(10, 10),
                   darken_symbol=None,
                   environment = None,
                   save_path=None,
                   radius_factor=0.8,
                   repeat=1,
                   cell_offset: Optional[NDArray] = np.array([0.0, 0.0, 0.0]),
                   set_axis_off = True,
                   add_cell = True,
                   linewidths_cell = 1.5,
                   linewidths_environment = 1,
                   plot_show = True,
                   color_factor=0.4
                   ): # Added save_path parameter
    """
    Plots the atomic structure with custom colors and constraints.

    Parameters:
        atoms (Atoms): ASE Atoms object to plot.
        plane (str): The viewing plane ('xy+', 'yz+', 'xz+').
        plot_constraint (bool): Whether to plot constraints.
        figsize (tuple): Figure size for the plot.
        colors_set (dict): 
        environment (Environment): AGoX Environment object for plotting confinement.
        save_path (str): If provided, the plot will be saved to this file path.
    """

    __version__ = "0.0.1"

    
    atom_colors = Colors(atoms)

    o_indices = [atom.index for atom in atoms if atom.symbol == 'O']
    atom_colors.set_color('red', indices=o_indices)
    atom_colors.lighten(indices=o_indices, factor=0.2)

    mg_indices = [atom.index for atom in atoms if atom.symbol == 'Mg']
    atom_colors.set_color('orange', indices=mg_indices)

    fe_indices = [atom.index for atom in atoms if atom.symbol == 'Fe']
    atom_colors.set_color('green', indices=fe_indices)
    
    if darken_symbol:
        for symbol in darken_symbol:
            indices = [atom.index for atom in atoms if atom.symbol == symbol]

            # Darken lower layers for each symbol (optional)
            symbol_atoms = [atom for atom in atoms if atom.symbol == symbol]
            if symbol_atoms:
                atom_colors.darken(indices=indices, factor=color_factor)


    # Create a matplotlib figure and axes
    fig, ax = plt.subplots(figsize=figsize)

    # Plot the atoms and cell
    plot_atoms(ax,
               atoms,
               colors=atom_colors,
               plane=plane,
               radius_factor=radius_factor,
               plot_constraint=plot_constraint,
               patch_kwargs = dict(linewidth=1.0),
               repeat=repeat,
               )


    if add_cell:
        plot_cell(ax,
                  atoms.cell,
                  plane=plane,
                  collection_kwargs=dict(linewidths = linewidths_cell, linestyles='--', dashes=(0,(5,10)))) # Use 'dashes' attribute

        plot_cell(ax,
                  atoms.cell,
                  plane=plane,
                  offset=cell_offset,
                  collection_kwargs = dict(linewidths=0))
        plot_cell(ax,
                  atoms.cell,
                  plane=plane,
                  offset=-1 * cell_offset,
                  collection_kwargs = dict(linewidths=0))

    if environment:
        plot_cell(ax,
                  environment.get_confinement_cell(),
                  plane=plane,
                  offset=environment.get_confinement_corner(),
                  collection_kwargs=dict(linewidths = linewidths_environment, edgecolors="red", linestyles="dashed"),
                  )

    if set_axis_off:
        ax.set_axis_off()
    # ax.set_title(f"Structure View ({plane.upper()})")

    # Display the plot
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    if plot_show:
        plt.show()

    plt.close()

# Example usage:
# Load your atoms object (replace with your actual atoms object)
# atoms = read('your_structure_file.xsf')

# environment = Environment(...
# )

# Apply constraints if needed (replace with your actual constraints)
# fe_indices = [atom.index for atom in atoms if atom.symbol == 'Fe']
# constraint = FixAtoms(indices=fe_indices)
# atoms.set_constraint(constraint)

# Example with custom colors:
# darken_symbol = ['O','Mg','Fe']

# Example offset:
# cell_offset = np.array([2.0, 2.0, 0.0])

# plot_structure(atoms,
#                plane='yz+',
#                darken_symbol=darken_symbol,
#                environment=environment,
#                save_path="figure1.png",
#                figsize = (5,5),
#                repeat=5,
#                color_factor = 0.1,
#                cell_offset = cell_offset)

# plot_structure(atoms,
#                plane='xy+',
#                darken_symbol=darken_symbol,
#                environment=environment,
#                save_path="figure1.png",
#                figsize = (3,3),
#                repeat=5,
#                color_factor = 0.1,
#                cell_offset = cell_offset)