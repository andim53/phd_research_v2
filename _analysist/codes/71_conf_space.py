import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patheffects as patheffects
from scipy.stats import gaussian_kde

def plot_structure_landscape(
    X_eigen, 
    energies,                    # Can be an array, list of arrays, or dict of arrays
    z_data=None, 
    show_colorbar=True, 
    cmap='viridis',
    z_limit=(None, None, 5),
    e_limit=(0.0, 0.8, 5),
    figsize=(6, 3),
    limits={"Islands": 0.07, "Quasi-flat": 0.25, "Flat": 0.50},
    show_limits=True, 
    fontsize=10, 
    wspace=0.05, 
    cbar_pad=0.02, 
    density_left=True,
    plot_density_only=False,  
    custom_legends=None,         # Explicit text labels list if energies is a list
    density_cmap='Blues',        # Colormap gradient name (e.g., 'Blues', 'Purples', 'magma')
    black_seed_zero=False,       # NEW PARAMETER: Force index 0 to be black, remainder to be gradient
    fill_density=False,          # Toggle to fill under the curve or not
    density_alpha=0.12,          # Control fill opacity
    dens_line_weight=0.5,
    save_path='./'
):
    
    min_e, max_e = e_limit[0], e_limit[1]
    eticks = np.round(np.linspace(min_e, max_e, e_limit[2]), 1)

    # --- Structure & Normalize Input Energies ---
    energy_datasets = {}
    if isinstance(energies, dict):
        energy_datasets = energies
    elif isinstance(energies, (list, tuple)) and len(energies) > 0 and isinstance(energies[0], (list, np.ndarray)):
        for i, dataset in enumerate(energies):
            label = custom_legends[i] if (custom_legends and i < len(custom_legends)) else f"Dataset {i+1}"
            energy_datasets[label] = np.asarray(dataset)
    else:
        # Fallback for single data array
        label = custom_legends[0] if custom_legends else "State Density"
        energy_datasets[label] = np.asarray(energies)

    # --- Setup Gradient Color Palette ---
    num_curves = len(energy_datasets)
    try:
        color_gradient = plt.colormaps.get_cmap(density_cmap)
    except AttributeError:
        # Fallback for older Matplotlib versions
        color_gradient = plt.cm.get_cmap(density_cmap)
        
    sampled_colors = []
    if num_curves > 1:
        if black_seed_zero:
            # First element is black
            sampled_colors.append('black')
            # The remaining curves divide up the gradient space evenly
            remaining_count = num_curves - 1
            if remaining_count > 1:
                color_indices = np.linspace(0.85, 0.35, remaining_count)
                for x in color_indices:
                    sampled_colors.append(color_gradient(x))
            else:
                sampled_colors.append(color_gradient(0.60))
        else:
            # Traditional dark to lighter gradient mapping sequence
            color_indices = np.linspace(0.95, 0.35, num_curves)
            sampled_colors = [color_gradient(x) for x in color_indices]
    else:
        sampled_colors = ['black' if black_seed_zero else color_gradient(0.85)]

    # --- Setup Subplots Axis Framework ---
    if plot_density_only:
        width_mod = 0.55 if num_curves > 1 else 0.4
        fig, ax_dens = plt.subplots(figsize=(figsize[0] * width_mod, figsize[1]))
        ax_scat = None
    else:
        ratios = [1, 2.5] if density_left else [2.5, 1]
        fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=figsize, sharey=True, 
                                         gridspec_kw={'width_ratios': ratios})
        fig.subplots_adjust(wspace=wspace)
        ax_scat = ax_r if density_left else ax_l
        ax_dens = ax_l if density_left else ax_r

    # --- Scatter Plot Representation ---
    if not plot_density_only:
        if z_data is not None:
            vmin = z_limit[0] if z_limit[0] is not None else np.min(z_data)
            vmax = z_limit[1] if z_limit[1] is not None else np.max(z_data)
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            color_src = z_data
        else:
            norm = None
            color_src = 'white'

        scat_energies = next(iter(energy_datasets.values())) if num_curves > 1 else list(energy_datasets.values())[0]
        
        if len(X_eigen) == len(scat_energies):
            sc = ax_scat.scatter(X_eigen, scat_energies, c=color_src, s=25, 
                                 cmap=cmap if z_data is not None else None,
                                 norm=norm, edgecolors='black', linewidth=0.5, 
                                 alpha=0.5, zorder=2)
            
            if show_colorbar and z_data is not None:
                cbar = plt.colorbar(sc, ax=ax_scat, pad=cbar_pad)
                cbar.set_label(r'$\Delta z$ (Å)', fontsize=fontsize)
                tick_locs = np.linspace(vmin, vmax, z_limit[2])
                cbar.set_ticks(tick_locs)
                cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
        else:
            print("Warning: X_eigen layout dims don't match base layout. Skipping scatter population.")

    # --- Evaluate & Generate Multiple Gaussian KDE Curves with Gradient Colors ---
    energy_grid = np.linspace(min_e, max_e, 200)
    
    for idx, (name, data_array) in enumerate(energy_datasets.items()):
        if len(data_array) > 1:
            kde = gaussian_kde(data_array)
            density = kde.evaluate(energy_grid)
            
            curve_color = sampled_colors[idx]
            
            # Plot profiles
            ax_dens.plot(density, energy_grid, color=curve_color, lw=dens_line_weight, zorder=4, label=name)
            
            if fill_density:
                ax_dens.fill_betweenx(energy_grid, 0, density, color=curve_color, alpha=density_alpha, zorder=3)

    ax_dens.set_xlabel('State Density (config./eV)', fontsize=fontsize)
    
    # Places the legend vertically outside to the far right side of the entire layout
    if num_curves > 1:
        fig.legend(
            frameon=False, 
            fontsize=fontsize-2, 
            loc='center left', 
            bbox_to_anchor=(1.02, 0.5)
        )

    if not plot_density_only and ax_scat is not None:
        ax_scat.set_xlabel(r'$\psi_{1d}(a.u.)$', fontsize=fontsize)
        ax_scat.xaxis.set_minor_locator(AutoMinorLocator())

    if plot_density_only or density_left:
        ax_dens.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)', fontsize=fontsize)

    # --- Horizontal Boundaries Phase Limits Logic ---
    if show_limits:
        axes_to_mark = [ax_dens] if plot_density_only else [ax_l, ax_r]
        for label, val in limits.items():
            for ax in axes_to_mark:
                if ax is not None:
                    ax.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.5, zorder=1)
            
            display_text = f'{label}: {val:.2f} eV'
            t = ax_dens.text(0.05, val + 0.005, display_text, 
                             fontsize=8, color='black', verticalalignment='bottom', zorder=11)
            t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    # Boundary Fixes
    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(eticks)
    ax_dens.yaxis.set_minor_locator(AutoMinorLocator())

    plt.tight_layout()
    plt.savefig(f'{save_path}/conf_space.png', dpi=300, bbox_inches='tight')
    return fig
    
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patheffects as patheffects
from scipy.stats import gaussian_kde

def plot_structure_landscape(
    X_eigen, 
    energies,                    # Can be an array, list of arrays, or dict of arrays
    z_data=None, 
    show_colorbar=True, 
    cmap='viridis',
    z_limit=(None, None, 5),
    e_limit=(0.0, 0.8, 5),
    figsize=(6, 3),
    limits={"Islands": 0.07, "Quasi-flat": 0.25, "Flat": 0.50},
    show_limits=True, 
    fontsize=10, 
    wspace=0.05, 
    cbar_pad=0.02, 
    density_left=True,
    plot_density_only=False,  
    custom_legends=None,         # Explicit text labels list if energies is a list
    density_cmap='Blues',        # Colormap gradient name (e.g., 'Blues', 'Purples', 'magma')
    black_seed_zero=False,       # Force index 0 to be black, remainder to be gradient
    seed_zero_top_zorder=False,  # NEW PARAMETER: Force seed 0 to have the highest zorder layer visibility
    fill_density=False,          # Toggle to fill under the curve or not
    density_alpha=0.12,          # Control fill opacity
    dens_line_weight=1.5,
    save_path='./'
):
    
    min_e, max_e = e_limit[0], e_limit[1]
    eticks = np.round(np.linspace(min_e, max_e, e_limit[2]), 1)

    # --- Structure & Normalize Input Energies ---
    energy_datasets = {}
    if isinstance(energies, dict):
        energy_datasets = energies
    elif isinstance(energies, (list, tuple)) and len(energies) > 0 and isinstance(energies[0], (list, np.ndarray)):
        for i, dataset in enumerate(energies):
            label = custom_legends[i] if (custom_legends and i < len(custom_legends)) else f"Dataset {i+1}"
            energy_datasets[label] = np.asarray(dataset)
    else:
        # Fallback for single data array
        label = custom_legends[0] if custom_legends else "State Density"
        energy_datasets[label] = np.asarray(energies)

    # --- Setup Gradient Color Palette ---
    num_curves = len(energy_datasets)
    try:
        color_gradient = plt.colormaps.get_cmap(density_cmap)
    except AttributeError:
        # Fallback for older Matplotlib versions
        color_gradient = plt.cm.get_cmap(density_cmap)
        
    sampled_colors = []
    if num_curves > 1:
        if black_seed_zero:
            # First element is black
            sampled_colors.append('black')
            # The remaining curves divide up the gradient space evenly
            remaining_count = num_curves - 1
            if remaining_count > 1:
                color_indices = np.linspace(0.85, 0.35, remaining_count)
                for x in color_indices:
                    sampled_colors.append(color_gradient(x))
            else:
                sampled_colors.append(color_gradient(0.60))
        else:
            # Traditional dark to lighter gradient mapping sequence
            color_indices = np.linspace(0.95, 0.35, num_curves)
            sampled_colors = [color_gradient(x) for x in color_indices]
    else:
        sampled_colors = ['black' if black_seed_zero else color_gradient(0.85)]

    # --- Setup Subplots Axis Framework ---
    if plot_density_only:
        width_mod = 0.55 if num_curves > 1 else 0.4
        fig, ax_dens = plt.subplots(figsize=(figsize[0] * width_mod, figsize[1]))
        ax_scat = None
    else:
        ratios = [1, 2.5] if density_left else [2.5, 1]
        fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=figsize, sharey=True, 
                                         gridspec_kw={'width_ratios': ratios})
        fig.subplots_adjust(wspace=wspace)
        ax_scat = ax_r if density_left else ax_l
        ax_dens = ax_l if density_left else ax_r

    # --- Scatter Plot Representation ---
    if not plot_density_only:
        if z_data is not None:
            vmin = z_limit[0] if z_limit[0] is not None else np.min(z_data)
            vmax = z_limit[1] if z_limit[1] is not None else np.max(z_data)
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            color_src = z_data
        else:
            norm = None
            color_src = 'white'

        scat_energies = next(iter(energy_datasets.values())) if num_curves > 1 else list(energy_datasets.values())[0]
        
        if len(X_eigen) == len(scat_energies):
            sc = ax_scat.scatter(X_eigen, scat_energies, c=color_src, s=25, 
                                 cmap=cmap if z_data is not None else None,
                                 norm=norm, edgecolors='black', linewidth=0.5, 
                                 alpha=0.8, zorder=2)
            
            if show_colorbar and z_data is not None:
                cbar = plt.colorbar(sc, ax=ax_scat, pad=cbar_pad)
                cbar.set_label(r'$\Delta z$ (Å)', fontsize=fontsize)
                tick_locs = np.linspace(vmin, vmax, z_limit[2])
                cbar.set_ticks(tick_locs)
                cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
        else:
            print("Warning: X_eigen layout dims don't match base layout. Skipping scatter population.")

    # --- Evaluate & Generate Multiple Gaussian KDE Curves with Gradient Colors ---
    energy_grid = np.linspace(min_e, max_e, 200)
    
    for idx, (name, data_array) in enumerate(energy_datasets.items()):
        if len(data_array) > 1:
            kde = gaussian_kde(data_array)
            density = kde.evaluate(energy_grid)
            
            curve_color = sampled_colors[idx]
            
            # Dynamically select zorder based on the parameter choice
            if idx == 0 and seed_zero_top_zorder:
                current_line_zorder = 10
                current_fill_zorder = 9
            else:
                current_line_zorder = 4
                current_fill_zorder = 3
            
            # Plot profiles
            ax_dens.plot(density, energy_grid, color=curve_color, lw=dens_line_weight, zorder=current_line_zorder, label=name)
            
            if fill_density:
                ax_dens.fill_betweenx(energy_grid, 0, density, color=curve_color, alpha=density_alpha, zorder=current_fill_zorder)

    ax_dens.set_xlabel('State Density (config./eV)', fontsize=fontsize)
    
    # Places the legend vertically outside to the far right side of the entire layout
    if num_curves > 1:
        fig.legend(
            frameon=False, 
            fontsize=fontsize-2, 
            loc='center left', 
            bbox_to_anchor=(1.02, 0.5)
        )

    if not plot_density_only and ax_scat is not None:
        ax_scat.set_xlabel(r'$\psi_{1d}(a.u.)$', fontsize=fontsize)
        ax_scat.xaxis.set_minor_locator(AutoMinorLocator())

    if plot_density_only or density_left:
        ax_dens.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)', fontsize=fontsize)

    # --- Horizontal Boundaries Phase Limits Logic ---
    if show_limits:
        axes_to_mark = [ax_dens] if plot_density_only else [ax_l, ax_r]
        for label, val in limits.items():
            for ax in axes_to_mark:
                if ax is not None:
                    ax.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.5, zorder=1)
            
            display_text = f'{label}: {val:.2f} eV'
            t = ax_dens.text(0.05, val + 0.005, display_text, 
                             fontsize=8, color='black', verticalalignment='bottom', zorder=11)
            t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    # Boundary Fixes
    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(eticks)
    ax_dens.yaxis.set_minor_locator(AutoMinorLocator())

    plt.tight_layout()
    plt.savefig(f'{save_path}/conf_space.png', dpi=300, bbox_inches='tight')
    return fig
    
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator 
from matplotlib import patheffects
from scipy.stats import gaussian_kde
from ase.io import read
import matplotlib.colors as mcolors

def plot_structure_landscape(
    X_eigen, 
    energies, 
    z_data=None, 
    show_colorbar=True, 
    cmap='viridis',
    z_limit=(None,None,5),
    e_limit=(0.0, 0.8, 5),
    figsize = (6, 3),
    limits = {"Islands": 0.07, "Quasi-flat": 0.25, "Flat": 0.50},
    wspace=0.05, # gap between ax1, and ax2
    cbar_pad=0.02, # gap of ax1 and colorbar
    density_left=True
):
    
    min_e, max_e = e_limit[0], e_limit[1]
    eticks = np.round(np.linspace(min_e, max_e, e_limit[2]), 1)

    ratios = [1, 2.5] if density_left else [2.5, 1]

    fig, (ax_l, ax_r)= plt.subplots(1, 2, figsize=figsize, sharey=True, 
                                   gridspec_kw={'width_ratios': ratios})

    fig.subplots_adjust(wspace=wspace)

    ax_scat = ax_r if density_left else ax_l
    ax_dens = ax_l if density_left else ax_r

    if z_data is not None:
        vmin = z_limit[0] if z_limit[0] is not None else np.min(z_data)
        vmax = z_limit[1] if z_limit[1] is not None else np.max(z_data)
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        color_src = z_data
    else:
        norm = None
        color_src = 'white'

    sc = ax_scat.scatter(X_eigen, energies, c=color_src, s=25, 
                         cmap=cmap if z_data is not None else None,
                         norm=norm, edgecolors='black', linewidth=0.5, 
                         alpha=0.8, zorder=2)

    if show_colorbar and z_data is not None:
        cbar = plt.colorbar(sc, ax=ax_scat, pad=cbar_pad)
        cbar.set_label(r'$\Delta z$ (Å)', fontsize=10)
        tick_locs = np.linspace(vmin, vmax, z_limit[2])
        cbar.set_ticks(tick_locs)
        cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
    elif show_colorbar and z_data is None:
        print("Warning: show_colorbar is True but no z_data was provided.")
    
    energy_grid = np.linspace(min_e, max_e, 100)
    kde = gaussian_kde(energies)
    density = kde.evaluate(energy_grid)
    ax_dens.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
    ax_dens.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.1)

    ax_scat.set_xlabel(r'$\psi_{1d}(a.u.)$')
    ax_scat.xaxis.set_minor_locator(AutoMinorLocator())
    ax_dens.set_xlabel('State Density (config./eV)')

    ax_l.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)')
    ax_l.set_ylim(min_e, max_e)
    ax_l.set_yticks(eticks)
    ax_l.yaxis.set_minor_locator(AutoMinorLocator())

    for label, val in limits.items():
        ax_l.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.8, zorder=1)
        ax_r.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.8, zorder=1)
        
        display_text = f'{label}: {val:.2f} eV'

        t = ax_dens.text(0.05, val + 0.005, display_text, 
                         fontsize=10, color='black', verticalalignment='bottom', zorder=11)
        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    plt.tight_layout()
    return fig

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator 
from matplotlib import patheffects
from scipy.stats import gaussian_kde
from ase.io import read

structures = read(f"{dir_out}/{dir_xsf_traj}/traj_19.traj", index=':')

raw_energies = []
valid_structures = []
z_height_spans = []

for atoms in structures:
    try:
        e = atoms.get_potential_energy()
        z_pos = atoms.get_positions()[:, 2]
        
        raw_energies.append(e)
        z_height_spans.append(z_pos.max() - z_pos.min())
        valid_structures.append(atoms)
    except Exception: 
        continue 

num_atoms = len(valid_structures[0])
energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
z_data = np.array(z_height_spans)
z_data = z_data - min(z_data)  # Relative delta_z

from agox.models.descriptors.fingerprint import Fingerprint
fp_instance = Fingerprint.from_atoms(valid_structures[0])
data = np.array([fp_instance.create_features(s).flatten() for s in valid_structures])

X_centered = data - np.mean(data, axis=0)
cov_matrix = np.cov(X_centered, rowvar=False)
evals, evecs = np.linalg.eigh(cov_matrix)
idx = np.argsort(evals)[::-1]
X_eigen = X_centered @ evecs[:, idx[0]]

# Option 1: With Colorbar
fig1 = plot_structure_landscape(
    X_eigen, 
    energies, 
    z_data=z_data, 
    show_colorbar=True, 
    wspace=0.01,
    cmap='PuBu',
)

# Option 2: Without Colorbar
# fig2 = plot_structure_landscape(X_eigen, energies, z_data=None, show_colorbar=False)

plt.show()

import os
import glob
import re
import numpy as np
from ase.io import read

seeds_dir = os.path.join(dir_out, dir_xsf_traj, "seeds")
traj_files = glob.glob(os.path.join(seeds_dir, "*.traj"))
energy_landscape_dict = {}

for file_path in traj_files:
    file_name = os.path.basename(file_path)
    
    match = re.search(r'seed_(\d+)', file_name)
    if match:
        dict_key = f"seed {match.group(1)}"
    else:
        # Fallback to the file name without extension if format varies
        dict_key = os.path.splitext(file_name)[0]

    try:
        # Read all frames from the trajectory file
        structures = read(file_path, index=':')
    except Exception as e:
        print(f"Failed to read file {file_name}: {e}")
        continue

    raw_energies = []

    for atoms in structures:
        try:
            e = atoms.get_potential_energy()
            
            raw_energies.append(e)
        except Exception: 
            continue 

    num_atoms = len(valid_structures[0])
    raw_energies_arr = np.array(raw_energies)
    
    normalized_energies = (raw_energies_arr - np.min(raw_energies_arr)) / num_atoms
    
    energy_landscape_dict[dict_key] = normalized_energies



plot_structure_landscape(
    X_eigen=None, 
    energies=energy_landscape_dict, 
    plot_density_only=True,
    e_limit=(0.0, 1.0, 6),
    show_limits=False
)
    
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patheffects as patheffects
from scipy.stats import gaussian_kde

def plot_structure_landscape(
    X_eigen, 
    energies,                    # Can be an array, list of arrays, or dict of arrays
    z_data=None, 
    show_colorbar=True, 
    cmap='viridis',
    z_limit=(None, None, 5),
    e_limit=(0.0, 0.8, 5),
    figsize=(6, 3),
    limits={"Islands": 0.07, "Quasi-flat": 0.25, "Flat": 0.50},
    show_limits=True, 
    fontsize=10, 
    wspace=0.05, 
    cbar_pad=0.02, 
    density_left=True,
    plot_density_only=False,  
    custom_legends=None,         # Explicit text labels list if energies is a list
    density_colors=None,         # List or dict of color mappings for DOS curves
    save_path='./'
):
    
    min_e, max_e = e_limit[0], e_limit[1]
    eticks = np.round(np.linspace(min_e, max_e, e_limit[2]), 1)

    # --- Structure & Normalize Input Energies ---
    energy_datasets = {}
    if isinstance(energies, dict):
        energy_datasets = energies
    elif isinstance(energies, (list, tuple)) and len(energies) > 0 and isinstance(energies[0], (list, np.ndarray)):
        for i, dataset in enumerate(energies):
            label = custom_legends[i] if (custom_legends and i < len(custom_legends)) else f"Dataset {i+1}"
            energy_datasets[label] = np.asarray(dataset)
    else:
        # Fallback for single data array
        label = custom_legends[0] if custom_legends else "State Density"
        energy_datasets[label] = np.asarray(energies)

    # Setup colors mapping for density profiles
    if density_colors is None:
        default_palette = ['black', '#1f77b4', '#d62728', '#2ca02c', '#9467bd']
        density_colors = {name: default_palette[i % len(default_palette)] for i, name in enumerate(energy_datasets.keys())}
    elif isinstance(density_colors, (list, tuple)):
        density_colors = {name: density_colors[i % len(density_colors)] for i, name in enumerate(energy_datasets.keys())}

    # --- Setup Subplots Axis Framework ---
    if plot_density_only:
        # Increase width dynamically if multiple datasets exist to fit the legend safely
        width_mod = 0.55 if len(energy_datasets) > 1 else 0.4
        fig, ax_dens = plt.subplots(figsize=(figsize[0] * width_mod, figsize[1]))
        ax_scat = None
    else:
        ratios = [1, 2.5] if density_left else [2.5, 1]
        fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=figsize, sharey=True, 
                                         gridspec_kw={'width_ratios': ratios})
        fig.subplots_adjust(wspace=wspace)
        ax_scat = ax_r if density_left else ax_l
        ax_dens = ax_l if density_left else ax_r

    # --- Scatter Plot Representation (Only valid if tracking a unified/primary sample set) ---
    if not plot_density_only:
        if z_data is not None:
            vmin = z_limit[0] if z_limit[0] is not None else np.min(z_data)
            vmax = z_limit[1] if z_limit[1] is not None else np.max(z_data)
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            color_src = z_data
        else:
            norm = None
            color_src = 'white'

        # Flatten/combine or pick primary dataset slice for underlying cluster landscape scattering
        scat_energies = next(iter(energy_datasets.values())) if len(energy_datasets) > 1 else list(energy_datasets.values())[0]
        
        # Ensure match sizing for scatter 
        if len(X_eigen) == len(scat_energies):
            sc = ax_scat.scatter(X_eigen, scat_energies, c=color_src, s=25, 
                                 cmap=cmap if z_data is not None else None,
                                 norm=norm, edgecolors='black', linewidth=0.5, 
                                 alpha=0.8, zorder=2)
            
            if show_colorbar and z_data is not None:
                cbar = plt.colorbar(sc, ax=ax_scat, pad=cbar_pad)
                cbar.set_label(r'$\Delta z$ (Å)', fontsize=fontsize)
                tick_locs = np.linspace(vmin, vmax, z_limit[2])
                cbar.set_ticks(tick_locs)
                cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
        else:
            print("Warning: X_eigen layout dims don't match base layout. Skipping scatter population.")

    # --- Evaluate & Generate Multiple Gaussian KDE Curves ---
    energy_grid = np.linspace(min_e, max_e, 200)
    
    for name, data_array in energy_datasets.items():
        if len(data_array) > 1: # Gaussian KDE requires variation
            kde = gaussian_kde(data_array)
            density = kde.evaluate(energy_grid)
            
            curve_color = density_colors.get(name, 'black')
            
            # Plot profiles
            ax_dens.plot(density, energy_grid, color=curve_color, lw=1.5, zorder=4, label=name)
            ax_dens.fill_betweenx(energy_grid, 0, density, color=curve_color, alpha=0.12, zorder=3)

    ax_dens.set_xlabel('State Density (config./eV)', fontsize=fontsize)
    
    # Add clear custom legend to density panel if plotting multiple sets
    if len(energy_datasets) > 1:
        ax_dens.legend(frameon=False, fontsize=fontsize-2, loc='best')

    if not plot_density_only and ax_scat is not None:
        ax_scat.set_xlabel(r'$\psi_{1d}(a.u.)$', fontsize=fontsize)
        ax_scat.xaxis.set_minor_locator(AutoMinorLocator())

    if plot_density_only or density_left:
        ax_dens.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)', fontsize=fontsize)

    # --- Horizontal Boundaries Phase Limits Logic ---
    if show_limits:
        axes_to_mark = [ax_dens] if plot_density_only else [ax_l, ax_r]
        for label, val in limits.items():
            for ax in axes_to_mark:
                if ax is not None:
                    ax.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.5, zorder=1)
            
            display_text = f'{label}: {val:.2f} eV'
            t = ax_dens.text(0.05, val + 0.005, display_text, 
                             fontsize=8, color='black', verticalalignment='bottom', zorder=11)
            t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    # Boundary Fixes
    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(eticks)
    ax_dens.yaxis.set_minor_locator(AutoMinorLocator())

    plt.tight_layout()
    plt.savefig(f'{save_path}/conf_space.png', dpi=300, bbox_inches='tight')
    return fig
    
def plot_structure_landscape(
    X_eigen, 
    energies, 
    z_data=None, 
    show_colorbar=True, 
    cmap='viridis',
    z_limit=(None,None,5),
    e_limit=(0.0, 0.8, 5),
    figsize = (6, 3),
    limits = {"Islands": 0.07, "Quasi-flat": 0.25, "Flat": 0.50},
    show_limits = True, 
    fontsize = 10, 
    wspace=0.05, 
    cbar_pad=0.02, 
    density_left=True,
    plot_density_only=False,  
    save_path='./'
):
    
    min_e, max_e = e_limit[0], e_limit[1]
    eticks = np.round(np.linspace(min_e, max_e, e_limit[2]), 1)

    if plot_density_only:
        fig, ax_dens = plt.subplots(figsize=(figsize[0]*0.4, figsize[1]))
        ax_scat = None
    else:
        ratios = [1, 2.5] if density_left else [2.5, 1]
        fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=figsize, sharey=True, 
                                          gridspec_kw={'width_ratios': ratios})
        fig.subplots_adjust(wspace=wspace)
        ax_scat = ax_r if density_left else ax_l
        ax_dens = ax_l if density_left else ax_r

    if not plot_density_only:
        if z_data is not None:
            vmin = z_limit[0] if z_limit[0] is not None else np.min(z_data)
            vmax = z_limit[1] if z_limit[1] is not None else np.max(z_data)
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            color_src = z_data
        else:
            norm = None
            color_src = 'white'

        sc = ax_scat.scatter(X_eigen, energies, c=color_src, s=25, 
                             cmap=cmap if z_data is not None else None,
                             norm=norm, edgecolors='black', linewidth=0.5, 
                             alpha=0.8, zorder=2)
    
        if show_colorbar and z_data is not None:
            cbar = plt.colorbar(sc, ax=ax_scat, pad=cbar_pad)
            cbar.set_label(r'$\Delta z$ (Å)', fontsize=fontsize) # Applied fontsize
            tick_locs = np.linspace(vmin, vmax, z_limit[2])
            cbar.set_ticks(tick_locs)
            cbar.set_ticklabels([f"{t:.2f}" for t in tick_locs])
        elif show_colorbar and z_data is None:
            print("Warning: show_colorbar is True but no z_data was provided.")
    
    energy_grid = np.linspace(min_e, max_e, 100)
    kde = gaussian_kde(energies)
    density = kde.evaluate(energy_grid)
    ax_dens.plot(density, energy_grid, color='black', lw=1.5, zorder=4)
    ax_dens.fill_betweenx(energy_grid, 0, density, color='gray', alpha=0.1)
    
    # Applied fontsize to Density x-label
    ax_dens.set_xlabel('State Density (config./eV)', fontsize=fontsize)

    if not plot_density_only:
        # Applied fontsize to Scatter x-label
        ax_scat.set_xlabel(r'$\psi_{1d}(a.u.)$', fontsize=fontsize)
        ax_scat.xaxis.set_minor_locator(AutoMinorLocator())

    if plot_density_only or density_left:
        # Applied fontsize to y-label
        ax_dens.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)', fontsize=fontsize)

    # --- Horizontal Limits Logic ---
    if show_limits:
        axes_to_mark = [ax_dens] if plot_density_only else [ax_l, ax_r]
        for label, val in limits.items():
            for ax in axes_to_mark:
                ax.axhline(y=val, color='black', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
            
            display_text = f'{label}: {val:.2f} eV'
            t = ax_dens.text(0.05, val + 0.005, display_text, 
                             fontsize=9, color='black', verticalalignment='bottom', zorder=11)
            t.set_path_effects([patheffects.withStroke(linewidth=2, foreground='white')])

    # Set consistent y-limits for the energy axis
    ax_dens.set_ylim(min_e, max_e)
    ax_dens.set_yticks(eticks)
    ax_dens.yaxis.set_minor_locator(AutoMinorLocator())

    plt.tight_layout()
    plt.savefig(f'{save_path}/conf_space.png', dpi=300, bbox_inches='tight')
    return fig