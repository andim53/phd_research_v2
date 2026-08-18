"""
Extracted from main_test.ipynb (cell 27).
Section: Dos: plot DOS from CSV
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_dos_from_csv(csv_file, seed=0):
    # 1. Load the data
    df = pd.read_csv(csv_file)
    
    # 2. Extract column names dynamically based on the seed
    # (Matches the naming convention from our previous DOS script)
    energy_col = f'energy_{seed}'
    total_up = f'spin_up_{seed}'
    total_down = f'spin_down_{seed}'
    
    # Look for any dz2 columns (there might be multiple if you have multiple Fe atoms)
    dz2_cols_up = [c for c in df.columns if f'dz2_atom' in c and f'up_{seed}' in c]
    dz2_cols_down = [c for c in df.columns if f'dz2_atom' in c and f'down_{seed}' in c]

    # 3. Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot Total DOS
    # We multiply 'down' values by -1 to create the mirrored effect
    plt.plot(df[energy_col], df[total_up], color='black', lw=1.5, label='Total DOS (Up)')
    plt.plot(df[energy_col], -df[total_down], color='black', lw=1.5, label='Total DOS (Down)')
    plt.fill_between(df[energy_col], df[total_up], color='gray', alpha=0.2)
    plt.fill_between(df[energy_col], -df[total_down], color='gray', alpha=0.2)

    # Plot PDOS (dz2)
    # If multiple atoms were saved, we sum them or plot them individually.
    # Here we sum them for a 'total dz2' contribution.
    if dz2_cols_up:
        sum_dz2_up = df[dz2_cols_up].sum(axis=1)
        sum_dz2_down = df[dz2_cols_down].sum(axis=1)
        
        plt.plot(df[energy_col], sum_dz2_up, color='crimson', lw=2, label=r'$d_{z^2}$ (Up)')
        plt.plot(df[energy_col], -sum_dz2_down, color='crimson', lw=2, label=r'$d_{z^2}$ (Down)')
        plt.fill_between(df[energy_col], sum_dz2_up, color='crimson', alpha=0.3)
        plt.fill_between(df[energy_col], -sum_dz2_down, color='crimson', alpha=0.3)

    # 4. Formatting
    plt.axvline(0, color='blue', linestyle='--', alpha=0.5, label='Fermi Level')
    plt.axhline(0, color='black', lw=0.8)
    
    plt.xlabel('Energy - $E_F$ (eV)', fontsize=12)
    plt.ylabel('Density of States (states/eV)', fontsize=12)
    plt.title(f'Spin-Polarized DOS and $d_{{z^2}}$ PDOS (Seed {seed})', fontsize=14)
    
    # Adjust y-axis to be symmetric
    y_limit = plt.gca().get_ylim()
    max_val = max(abs(y_limit[0]), abs(y_limit[1]))
    plt.ylim(-max_val, max_val)
    
    plt.legend(loc='upper right', frameon=False)
    plt.grid(axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    # Save and Show
    plt.savefig(f'dos_plot_seed_{seed}.png', dpi=300)
    plt.show()

# Run the plotting function
plot_dos_from_csv('dos_analysis.csv', seed=1)
