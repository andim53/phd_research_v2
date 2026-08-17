"""
Quantification of the Fe/MgO(001) ensemble free energy.
Calculates configuration-specific Helmholtz Free Energies and the 
total ensemble free energy G_total at a given temperature.
"""

import os
import numpy as np
import pandas as pd
from ase.io import read
from ase.vibrations import Vibrations
from ase.thermochemistry import HarmonicThermo
from ase.units import kB
from gpaw import GPAW

def calculate_f_vib_from_traj(traj_file, temperature, gpaw_params, output_name="vibrational_data"):
    # 1. Initialization
    configs = read(traj_file, index=':')
    f_vib_list = []
    data_log = []
    
    # Pre-calculate beta for ensemble math
    beta = 1.0 / (kB * temperature)

    # 2. Iterate through ensemble configurations
    for i, atoms in enumerate(configs):
        # Set up GPAW calculator
        calc = GPAW(**gpaw_params)
        atoms.calc = calc
        
        # Calculate Potential Energy (H_0K)
        potential_energy = atoms.get_potential_energy()
        
        # Harmonic vibrational analysis
        name = f'vib_tmp_{i}'
        vib = Vibrations(atoms, name=name)
        vib.run()
        vib_energies = vib.get_energies()
        
        # Calculate Helmholtz Free Energy: F_i(T) = E_pot + F_vib(T)
        thermo = HarmonicThermo(vib_energies=vib_energies, 
                                potential_energy=potential_energy)
        
        f_i = thermo.get_helmholtz_free_energy(temperature=temperature)
        f_vib_list.append(f_i)

        # Log individual configuration data
        data_log.append({
            'Config_Index': i,
            'Temperature_K': temperature,
            'Potential_Energy_eV': potential_energy,
            'Helmholtz_Free_Energy_F_eV': f_i
        })
        
        # Cleanup temporary vibration files and directories
        vib.clean()
        if os.path.exists(name):
            import shutil
            shutil.rmtree(name)

    # 3. Ensemble Statistics (Partition Function math)
    f_vibs = np.array(f_vib_list)
    f_min = np.min(f_vibs)
    
    # Calculate G_total = -kBT * ln(sum(exp(-beta * (F_i - F_min)))) + F_min
    # Subtracting F_min prevents exponential overflow/underflow
    z_relative = np.sum(np.exp(-beta * (f_vibs - f_min)))
    g_total = f_min - (kB * temperature * np.log(z_relative))

    # 4. Save Results
    pd.DataFrame(data_log).to_csv(f"{output_name}_configs.csv", index=False)
    
    df_summary = pd.DataFrame([{
        'Temperature_K': temperature,
        'G_total_ensemble_eV': g_total,
        'F_min_eV': f_min,
        'Num_Configurations': len(f_vibs)
    }])
    df_summary.to_csv(f"{output_name}_summary.csv", index=False)
    
    return f_vibs, g_total

# --- Execution ---
# Ensure your path variables (dir_out, etc.) are defined prior to this block
path_traj = f"{dir_out}/{dir_xsf_traj}/traj_0.traj"

gpaw_params = {
    "mode": "lcao",
    "xc": "PBE",
    "basis": "dzp",
    "txt": "gpaw_vib.txt",
    "mixer": {"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    "convergence": {"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    "kpts": {"size": (4, 4, 1), "gamma": True},
    "nbands": "nao",
    "occupations": {"name": "fermi-dirac", "width": 0.01},
    "spinpol": True,
    "symmetry": "off",
}

f_values, g_sum = calculate_f_vib_from_traj(
    traj_file=path_traj, 
    temperature=1500, 
    gpaw_params=gpaw_params, 
    output_name="5x5_island_results"
)