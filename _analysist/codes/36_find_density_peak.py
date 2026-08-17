from scipy.signal import find_peaks

peaks, properties = find_peaks(density)

peak_densities = density[peaks]
peak_energies = energy_grid[peaks]

sorted_indices = np.argsort(peak_densities)[::-1]
top_3_indices = sorted_indices[:3]

print("--- Top 3 Energy Peaks (Highest State Density) ---")
for i, idx in enumerate(top_3_indices):
    e_val = peak_energies[idx]
    d_val = peak_densities[idx]
    print(f"Rank {i+1}: Energy = {e_val:.4f} eV/atom (Density = {d_val:.2f})")
    
    ax1.hlines(e_val, 0, d_val, colors='red', linestyles='--', alpha=0.5)