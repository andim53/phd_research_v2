import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from ase.io import read 
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.analysis.diffraction.xrd import XRDCalculator
from scipy.stats import norm

# ==============================================================================
# CONFIGURATION PARAMETERS
# ==============================================================================
# Define the specific representative energy points you want to pick out
target_energies = [0.0, 0.01, 0.05]
tolerance = 0.002  # Maximum allowed delta distance to capture a target match

dir_out = '0_analy'               # Directory for the analysis
dir_xsf_traj = '0_xsf_traj'       # Stores entire trajectory
trajectory_file = f"{dir_out}/{dir_xsf_traj}/traj_61.traj"

# Peak Broadening Parameters for the continuous profile representation
two_theta_grid = np.linspace(30, 50, 1000)
fwhm = 0.40  # Slightly broadened peak width for clarity
sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))

# Initialize Pymatgen XRD calculator (Standard Cu K-alpha radiation)
xrd_calc = XRDCalculator(wavelength="CuKa")
adaptor = AseAtomsAdaptor()

# ==============================================================================
# 1. DATA INGESTION & ENERGY EVALUATION
# ==============================================================================
print(f"Reading structures from: {trajectory_file}")
all_structures = read(trajectory_file, index=":")

energies_per_atom = []
for atoms in all_structures:
    num_atoms = len(atoms)
    try:
        total_energy = atoms.get_potential_energy()
    except RuntimeError:
        total_energy = atoms.info.get('energy', None)
        if total_energy is None:
            raise RuntimeError("Atoms object has no potential energy calculated or stored.")
    energies_per_atom.append(total_energy / num_atoms)

energies_per_atom = np.array(energies_per_atom)
min_energy_per_atom = np.min(energies_per_atom)
relative_energies_per_atom = energies_per_atom - min_energy_per_atom

# ==============================================================================
# 2. TARGETED ONE-STRUCTURE SELECTION
# ==============================================================================
datasets = []

for target in target_energies:
    # Find the structure that sits closest to the exact target energy
    abs_diffs = np.abs(relative_energies_per_atom - target)
    best_match_idx = np.argmin(abs_diffs)
    
    if abs_diffs[best_match_idx] <= tolerance:
        dE_atom = relative_energies_per_atom[best_match_idx]
        matched_atoms = all_structures[best_match_idx]
        
        syms = matched_atoms.get_chemical_symbols()
        ta_count = syms.count('Ta')
        b_count = syms.count('B')
        
        label = f"Target {target} eV/atom (Struct {best_match_idx}: [Ta{ta_count}B{b_count}] @ {dE_atom:.4f} eV/atom)"
        datasets.append({"atoms": matched_atoms, "label": label, "dE_atom": dE_atom})
    else:
        print(f"Warning: No structure found within tolerance window for target energy {target} eV/atom")

# Sort them so they layer naturally in the plot window (lowest energy at the back)
datasets = sorted(datasets, key=lambda x: x["dE_atom"])

# ==============================================================================
# 3. RUN PYMATGEN XRD & GENERATE DISCRETE HIGH-CONTRAST PLOT
# ==============================================================================
fig, ax = plt.subplots(figsize=(10.5, 5.5))

# --- MAXIMUM CONTRAST HEX COLORS ---
# Hardcoded to match targets sequentially: Black (0.0), Teal (0.01), Crimson Red (0.05)
high_contrast_colors = ["#000000", "#00a896", "#e63946"] 

for rank, data in enumerate(datasets):
    atoms = data["atoms"]
    
    # Convert to Pymatgen Structure object
    pmg_structure = adaptor.get_structure(atoms)
    
    # scaled=False turns off normalization to 100
    pattern = xrd_calc.get_pattern(pmg_structure, scaled=False, two_theta_range=(30, 50))
    
    # Generate continuous 2-theta profile using the calculated intensities
    simulated_intensity = np.zeros_like(two_theta_grid)
    for peak_angle, intensity in zip(pattern.x, pattern.y):
        simulated_intensity += intensity * norm.pdf(two_theta_grid, peak_angle, sigma)
    
    # Assign distinct visual weights and colors to each trace
    line_color = high_contrast_colors[rank % len(high_contrast_colors)]
    line_width = 2.2 if line_color == "#000000" else 1.8
    
    ax.plot(
        two_theta_grid, 
        simulated_intensity, 
        color=line_color, 
        lw=line_width, 
        label=data["label"],
        alpha=0.95
    )

# ==============================================================================
# 4. GRAPH LAYOUT & LEGEND MANAGEMENT
# ==============================================================================
ax.set_xlabel(r"$2\theta$ (degree)", fontsize=11)
ax.set_ylabel("Absolute Structural Intensity (a.u.)", fontsize=11)
ax.set_title("Pymatgen Crystal XRD: High-Contrast Energy Profile Comparison", fontsize=12, pad=15)
ax.set_xlim(30, 50)

# Clean legend for direct, effortless curve identification
ax.legend(loc="upper right", frameon=True, fontsize=9.5, facecolor="white", edgecolor="none")

output_img = "pymatgen_high_contrast_discrete_xrd.png"
plt.tight_layout()
plt.savefig(output_img, dpi=300)
print(f"\nSuccess! Plotted {len(datasets)} highly distinguishable target structures. Saved to '{output_img}'")
plt.show()