import numpy as np
import matplotlib.pyplot as plt

# Reproducibility
np.random.seed(42)

# Control parameter
complexity = 3 

# 1. Define the parameterized PES function
def complex_potential_surface(x, complexity_factor=0.5):
    y = 0.45 
    primary_valleys = [
        (2.0, 0.45, 0.7), (4.8, 0.35, 0.6), 
        (7.5, 0.40, 0.8), (10.5, 0.28, 0.5)
    ]
    local_valleys = [
        (1.2, 0.1, 0.2), (2.8, 0.08, 0.15), (4.0, 0.15, 0.25), 
        (5.5, 0.12, 0.2), (6.5, 0.2, 0.3), (8.5, 0.18, 0.25),
        (9.5, 0.1, 0.2), (11.2, 0.05, 0.1)
    ]
    for pos, depth, width in primary_valleys:
        y -= depth * np.exp(-((x - pos)**2) / (2 * width**2))
    for pos, depth, width in local_valleys:
        y -= (depth * complexity_factor) * np.exp(-((x - pos)**2) / (2 * width**2))
    y += (0.015 * complexity_factor) * np.sin(2 * np.pi * x * 1.5)
    return y

# 2. Sampling
x_range = np.linspace(0.2, 12, 1500)
x_minima = [1.2, 2.0, 2.8, 4.0, 4.8, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.2]
x_extra = [np.random.normal(xm, 0.12, 100) for xm in x_minima]
X_eigen = np.sort(np.concatenate([x_range] + x_extra))

# 3. Apply Energies and Normalize
raw_energies = complex_potential_surface(X_eigen, complexity) + np.random.exponential(0.006, len(X_eigen))
offset = np.min(raw_energies)
energies = raw_energies - offset

# 4. Generate Smooth Line Data
x_line = np.linspace(0.5, 11.5, 1000)
y_line = complex_potential_surface(x_line, complexity) - offset

# 5. Create the plot
fig, ax = plt.subplots(figsize=(5, 3), dpi=120)

# Clean scatter
ax.scatter(X_eigen, energies, s=10, facecolors='white', edgecolors='black', 
            linewidth=0.5, alpha=0.3, zorder=2)

# Line Graph
ax.plot(x_line, y_line, color='black', linewidth=1.5, alpha=0.8, zorder=1)

# --- REMOVE AXIS ENTIRELY ---
ax.axis('off')

# Ensure consistent framing
ax.set_ylim(-0.05, 1.0) 
ax.set_xlim(0.5, 11.5)

plt.tight_layout()
plt.show()