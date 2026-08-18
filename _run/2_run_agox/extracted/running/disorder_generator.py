"""
Extracted from main_test.ipynb (cell 32).
Section: bragg: DisorderGenerator (custom)
"""

import numpy as np
from ase import Atoms
from ase.io import write
from ase.data import covalent_radii

from pathlib import Path
from datetime import datetime

import random

from agox.generators.ABC_generator import GeneratorBaseClass


class DisorderGenerator(GeneratorBaseClass):

    name = "DisorderGenerator"
    def __init__(
        self,
        contiguous=False,
        attempts=100,
        may_nucleate_at_several_places=None,
        replace=True,
        write_struct=True,
        output_dir="generated_structures",
        min_distance_scale=0.8,        
        print_result = False,

        reference_atoms = None, 
        S = 0.9, 
        r_param=0.5, #FePt 0.5, Fe3Pt 0.625
        seed=1

        
        # a=3.161058820599375,
        # cell=None,
        # frac_positions=None,

        # elements=(
        #     ["Fe"] * 6 +
        #     ["Co"] * 6 +
        #     ["Ni"] * 6 +
        #     ["Cu"] * 4 +
        #     ["Pt"] * 10
        # ),

        # json_path=None,
        **kwargs
    ):
        super().__init__(replace=replace, **kwargs)
        self.contiguous = contiguous
        self.attempts = attempts
        self.write_struct = write_struct
        self.output_dir = Path(output_dir)
        self.run_dir = self._create_new_run_dir() if write_struct else None
        self.min_distance_scale = min_distance_scale
        self.print_result = print_result
        if may_nucleate_at_several_places is not None:
            DeprecationWarning(
                "'may_nucleate_at_several_places' is deprecated and will be removed. "
                "Use 'contiguous' instead."
            )
            self.contiguous = not may_nucleate_at_several_places

        self.seed = seed
        self.reference_atoms = reference_atoms
        self.S = S
        self.r_param=r_param

    def check_too_close(self, atoms, scale=None):
        """
        Check whether any atom pair is too close.

        Uses covalent radii and periodic boundary conditions.

        Parameters
        ----------
        atoms : ASE Atoms
            Structure to check.

        scale : float
            Multiplication factor for covalent radii sum.
            If None, uses self.min_distance_scale.

        Returns
        -------
        bool
            True if atoms are too close.
        """

        if scale is None:
            scale = self.min_distance_scale

        numbers = atoms.get_atomic_numbers()

        # Distance matrix using minimum image convention
        dmat = atoms.get_all_distances(mic=True)

        # Ignore self-distances
        np.fill_diagonal(dmat, np.inf)

        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):

                cutoff = scale * (
                    covalent_radii[numbers[i]] +
                    covalent_radii[numbers[j]]
                )

                if dmat[i, j] < cutoff:
                    return True

        return False
