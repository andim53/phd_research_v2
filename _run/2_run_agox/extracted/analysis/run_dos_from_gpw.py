"""
Extracted from main_test.ipynb (cell 26).
Section: Dos: DOS from .gpw
"""

import numpy as np
import pandas as pd
from gpaw import restart

def run_dos_from_file(seed, npts=2000, width=0.15):
    """
    Calculates DOS and PDOS using the modern GPAW DOS-calculator API.
    """
    # 1. Load atoms and calculator
    atoms, calc = restart(f"seed_{seed}.gpw", txt=None)
    e_fermi = calc.get_fermi_level()
    
    # Define energy grid (eV)
    # The API usually expects energies relative to the average potential, 
    # but we will shift it to be relative to E_f in the final output.
    emin, emax = -15, 10
    energies_grid = np.linspace(emin, emax, npts)
    
    # Initialize storage
    results = {f'energy_{seed}': energies_grid} 

    # 2. Get the DOS Calculator from the GPAW object
    # Note: Modern GPAW documentation suggests using calc.dos() 
    # which returns a DOSCalculator instance.
    doscalc = calc.dos()

    # 3. Total DOS
    # raw_dos takes energies in eV. We pass absolute energies (grid + fermi).
    spins = range(calc.get_number_of_spins())
    total_dos_acc = np.zeros(npts)
    
    for s in spins:
        dos_s = doscalc.raw_dos(energies_grid + e_fermi, spin=s, width=width)
        results[f'spin_{"up" if s==0 else "down"}_{seed}'] = dos_s
        total_dos_acc += dos_s
        
    results[f'total_dos_{seed}'] = total_dos_acc

    # 4. Atomic Orbital PDOS (dz2)
    # Parameters from documentation: l=2 (d-orbitals), m=2 (3z2-r2)
    symbols = atoms.get_chemical_symbols()
    for i, symbol in enumerate(symbols):
        if symbol in ['Fe', 'Ni', 'Co', 'Mo', 'Cr']:
            for s in spins:
                # raw_pdos handles the projection and smearing in one step
                pdos_dz2 = doscalc.raw_pdos(
                    energies_grid + e_fermi, 
                    a=i,      # Atom index
                    l=2,      # d-orbital
                    m=2,      # dz2 orbital
                    spin=s, 
                    width=width
                )
                
                label = "up" if s == 0 else "down"
                results[f'dz2_atom{i}_{symbol}_{label}_{seed}'] = pdos_dz2

    return results

results_seed_0 = run_dos_from_file(seed=1)
df = pd.DataFrame(results_seed_0)
df.to_csv("dos_analysis.csv", index=False)
