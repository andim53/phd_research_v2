import pandas as pd
import matplotlib.pyplot as plt

seed_map = {3: 'Island (Ground State)', 4: 'Flat'}
use_multi_color = True                 
main_color = 'black'                   
color_map = {'Island': '#1f77b4', 'Flat': '#d62728'} 
line_styles = {'Island': '-', 'Flat': '-'} 
energy_range = (-5.1, 5.1)                 

plot_type = 'overlay'                  # Options: 'subplot' or 'overlay'
fig_dims = (4, 4)                      
dpi_val = 300                          
x_label = '$E$ - $E_f$ (eV)'
y_label = 'Fe-3d PDOS (states/eV)'
plot_title = 'Fe-3d Comparison: Island vs Flat Growth'
legend_loc = 'lower right'             

data = {}
for seed, name in seed_map.items():
    try:
        df = pd.read_csv(f"{dir_simul}/37_dos/dos_seed_{seed}.csv")
        data[name] = df
    except (FileNotFoundError, NameError) as e:
        print(f"Skipping {name}: {e}")

if plot_type == 'subplot':
    fig, axes = plt.subplots(2, 1, figsize=(fig_dims[0], fig_dims[1] * 1.8), sharex=True, dpi=dpi_val)
    
    for i, name in enumerate(data.keys()):
        ax = axes[i]
        df = data[name]
        c = color_map.get(name, main_color) if use_multi_color else main_color
        
        # Total DOS + Filled Fe-3d
        ax.plot(df['energy'], df['total_dos_up'], color='black', lw=1, label='Total DOS')
        ax.fill_between(df['energy'], df['total_Fe_d_up'], color=c, alpha=0.4, label=f'{name}')
        
        # Spin Down Mirrored
        ax.plot(df['energy'], -df['total_dos_down'], color='black', lw=1)
        ax.fill_between(df['energy'], -df['total_Fe_d_down'], color=c, alpha=0.6)
        
        ax.axvline(x=0, color='gray', linestyle=':', lw=1, alpha=0.7)
        ax.axhline(y=0, color='black', lw=0.8)
        ax.set_xlim(energy_range)
        ax.set_ylabel('DOS (states/eV)')
        ax.set_title(f'Electronic Structure: {name}', fontweight='bold')
        ax.legend(frameon=False, loc=legend_loc)
    plt.xlabel(x_label)

elif plot_type == 'overlay':
    plt.figure(figsize=fig_dims, dpi=dpi_val)
    
    for name in data.keys():
        df = data[name]
        ls = line_styles.get(name, '-')
        c = color_map.get(name, main_color) if use_multi_color else main_color
        
        # Plotting manifold
        plt.plot(df['energy'], df['total_Fe_d_up'], 
                 color=c, ls=ls, lw=2, label=f'{name}')
        
        # Spin down mirrored
        plt.plot(df['energy'], -df['total_Fe_d_down'], 
                 color=c, ls=ls, lw=2, alpha=0.7)
    
    plt.axvline(x=0, color='black', linestyle=':', alpha=0.5)
    plt.axhline(y=0, color='black', lw=0.8)
    plt.xlim(energy_range)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # plt.title(plot_title)
    plt.legend(frameon=False, loc=legend_loc)

# --- SAVE & DISPLAY ---
plt.tight_layout()
output_name = f"dos_comparison_{plot_type}.png"
plt.savefig(output_name, bbox_inches='tight')
plt.show()

print(f"Plotting complete. File saved: {output_name}")