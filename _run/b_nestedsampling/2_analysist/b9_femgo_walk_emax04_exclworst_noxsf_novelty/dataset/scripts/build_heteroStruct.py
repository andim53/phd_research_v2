from ase.io import read, write
import numpy as np
from ase import Atoms

def build_heteroStruct(slab_substrate, slab_deposition, dist_inter=2.3, vacuum=10, output_path=None):
    """
    Builds a heterostructure by stacking a deposition slab on top of a substrate slab.

    The deposition slab is positioned at a specified distance from the top of the
    substrate slab. The entire structure is then centered along the z-axis with
    a given vacuum spacing.

    Parameters:
        slab_substrate (Atoms): The ASE Atoms object representing the substrate.
        slab_deposition (Atoms): The ASE Atoms object representing the deposition layer.
        dist_inter (float): The desired interfacial distance (in Å) between the
                            maximum z-position of the substrate and the minimum
                            z-position of the deposition slab.
        vacuum (float): The vacuum spacing (in Å) to apply around the final
                        heterostructure along the z-axis.
        output_path (str, optional): If provided, the final heterostructure will be
                                     written to this file path in XSF format.

    Returns:
        Atoms: An ASE Atoms object representing the combined heterostructure.
    """
    # Center the substrate along the z-axis and determine its maximum z-coordinate
    slab_substrate.center(vacuum=vacuum, axis=2)
    slab_substrate_pos_max = slab_substrate.positions[:, 2].max()

    # Determine the minimum z-coordinate of the deposition slab
    slab_deposition_pos_min = slab_deposition.positions[:, 2].min()

    # Calculate the translation distance needed to achieve the desired interfacial distance
    dz = slab_substrate_pos_max - slab_deposition_pos_min + dist_inter

    # Translate the deposition slab along the z-axis
    slab_deposition.translate((0, 0, dz))

    # Combine the translated deposition slab with the substrate to form the heterostructure
    slab_heteroStruct = slab_deposition + slab_substrate

    # Write the heterostructure to a file if an output path is specified
    if output_path is not None:
        write(output_path, slab_heteroStruct)

    return slab_heteroStruct

# slab_heteroStruct = build_heteroStruct(slab_substrate, slab_deposition, output_path='heteroStruct.xsf')