"""
Extracted from main_test.ipynb (cell 13).
Section: Thermal Volume Expansion
"""

import matplotlib.pyplot as plt
import numpy as np

def calculate_platinum_expansion_percent(current_temp_k, initial_temp_k=0):
    """
    Calculates the percentage increment from the original volume.
    Example: 1.0 means a 1% increase over the original baseline.
    """
    alpha = 8.8e-6  # Linear coefficient
    beta = 3 * alpha  # Volumetric coefficient
    
    temp_increase = current_temp_k - initial_temp_k
    
    # Growth percent relative to original: delta_V / V_0 * 100
    percent_increase = (beta * temp_increase) * 100
    return percent_increase

# 1. Generate loop data
temperatures = np.arange(0, 401, 10)
percentages = [calculate_platinum_expansion_percent(t) for t in temperatures]

# Print loop updates to console
for t, p in zip(temperatures, percentages):
    if t % 50 == 0:
        print(f"Temp: {t}K | Volume increased by: {p:.3f}% from original")

# 2. Plot the results
plt.figure(figsize=(8, 5))
plt.plot(temperatures, percentages, color='red', linewidth=2, label='Platinum Growth (%)')

# Chart formatting
plt.title('Platinum Volume Percent Increase (0K to 400K)', fontsize=14)
plt.xlabel('Temperature (K)', fontsize=12)
plt.ylabel('Volume Increase from Original (%)', fontsize=12)

# Format y-axis ticks explicitly as percentages (e.g., 0.20%, 0.40%)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}%'))

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()
