import numpy as np
import matplotlib.pyplot as plt

# Define a smoother range of temperatures for a clean curve
temp_range = np.linspace(200, 1000, 200) 

ratio_values = []
for t in temp_range:
    # Using your function with the plot_ratio=True flag
    _, _, ratio = calculate_weighted_probability(relative_energies, t, plot_ratio=True)
    ratio_values.append(ratio)

# --- Plot Construction ---
plt.figure(figsize=(6, 4), dpi=100)

# Main ratio curve
plt.plot(temp_range, ratio_values, color='teal', linewidth=2.5, label='Relative Probability Ratio')

# Reference values: specific points from your original list
for t_spec in [298.15, 646.425]:
    _, _, r_spec = calculate_weighted_probability(relative_energies, t_spec, plot_ratio=True)
    plt.scatter(t_spec, r_spec, color='darkorange', zorder=5)
    plt.annotate(f'{r_spec:.2f} @ {t_spec}K', (t_spec, r_spec), 
                 textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

# Formatting for Research
plt.yscale('log') # Probability ratios are best viewed on log scales
plt.xlabel('Temperature (K)', fontsize=12, fontweight='bold')
plt.ylabel(r'$P(E_{flat}) / P(E_{glob})$', fontsize=14, fontweight='bold')
# plt.title('Relative State Occupancy vs. Temperature', fontsize=14, pad=15)

# Adding a horizontal line at 1.0 (where states are equally likely)
plt.axhline(1, color='black', linewidth=0.8, linestyle='--', alpha=0.6, label='Equiprobability')

plt.grid(True, which="both", linestyle=':', alpha=0.4)
plt.legend(frameon=True, loc='lower right')
plt.tight_layout()

plt.show()