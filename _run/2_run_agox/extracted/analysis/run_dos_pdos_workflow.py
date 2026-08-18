"""
Extracted from main_test.ipynb (cell 22).
Section: Dos: DOS+PDOS workflow
"""

from gpaw import GPAW, FermiDirac
from ase.io import read
import numpy as np
import pandas as pd
import os

def run_workflow(atoms, seed, kpts=(12, 12, 1), npts=2000, width=0.15):
    calc = GPAW(
        mode={"name": "lcao"},
        basis="dzp",
        xc="PBE",
        mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
        convergence={"energy": 1e-4, "density": 1e-3},
        txt=f"output_seed_{seed}.txt",
        kpts=kpts,
        symmetry='off',
        nbands='nao',
        maxiter=500,
        occupations={"name": "fermi-dirac", "width": 0.05},
        hund=True,
        spinpol=True
    )

    atoms.calc = calc
    atoms.get_potential_energy()
    
    e_fermi = calc.get_fermi_level()
    emin, emax = -15, 10
    energies_grid = np.linspace(emin, emax, npts)
    
    results = {'energy': energies_grid} 
    
    doscalc = calc.dos()
    spins = range(calc.get_number_of_spins())
    
    total_dos_all_spins = np.zeros(npts)
    for s in spins:
        dos_s = doscalc.raw_dos(energies_grid + e_fermi, spin=s, width=width)
        label = "up" if s == 0 else "down"
        results[f'total_dos_{label}'] = dos_s
        total_dos_all_spins += dos_s
    results['total_dos_sum'] = total_dos_all_spins

    # PDOS for Fe (dz2) and O (pz)
    # Note: In GPAW LCAO PDOS:
    # l=1: p-orbitals (m=0 is pz, m=1 is px, m=2 is py usually, check GPAW basis docs)
    # l=2: d-orbitals (m=2 is dz2)
    symbols = atoms.get_chemical_symbols()
    for i, symbol in enumerate(symbols):
        if symbol == 'Fe':
            for s in spins:
                pdos_val = doscalc.raw_pdos(energies_grid + e_fermi, a=i, l=2, m=2, spin=s, width=width)
                label = "up" if s == 0 else "down"
                results[f'Fe{i}_dz2_{label}'] = pdos_val
                
        elif symbol == 'O':
            for s in spins:
                # m=0 for pz in many spherical harmonic conventions; check specific GPAW version if needed
                pdos_val = doscalc.raw_pdos(energies_grid + e_fermi, a=i, l=1, m=0, spin=s, width=width)
                label = "up" if s == 0 else "down"
                results[f'O{i}_pz_{label}'] = pdos_val

    df = pd.DataFrame(results)
    csv_name = f"dos_seed_{seed}.csv"
    df.to_csv(csv_name, index=False)
    print(f"Analysis for seed {seed} saved to {csv_name}. GPW file discarded.")

from ase.io import write
try:
    structs = read("selected_structures_dos.traj", index=':')
    for i, s in enumerate(structs):
        if i < 3:
            continue
        print(f"{i} ",s)
        write(f"{i}.xsf", s)
        run_workflow(s, seed=i)
except Exception as e:
    print(f"Note: Ensure 'selected_structures_dos_test.traj' exists. Error: {e}")
