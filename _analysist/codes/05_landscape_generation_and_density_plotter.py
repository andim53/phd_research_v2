import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde
from matplotlib.patches import ConnectionPatch

# === Tuning Parameters ===
kde_smoothing = 0.4
graph_distance = 0.5  # Adjusts spacing between the two subplots

# === Potential Energy Surface Generation ===
np.random.seed(42)
x = np.linspace(0, 50, 1000)

# Build a parabolic well envelope with overlapping micro-oscillations
y_container = 0.015 * (x - 25)**2
y_oscillations = -1.5 * np.cos(x * 0.8) + 0.8 * np.sin(x * 2.1)
y_base = y_container + y_oscillations

# Add fine-grained noise to simulate micro-barriers
noise = 0.15 * np.sin(x * 10) + 0.05 * np.random.normal(size=len(x))
y_raw = y_base + noise

# Shift absolute minimum to zero and apply scaling compression
y_shifted = y_raw - y_raw.min()
compression_factor = 0.8  
y = y_shifted * compression_factor

# === Peak Detection and Trough Extraction ===
minima_indices, _ = find_peaks(-y, distance=25, prominence=0.1)
minima_energies = y[minima_indices]
minima_x = x[minima_indices]

# === Density of States Estimation ===
kde = gaussian_kde(minima_energies, bw_method=kde_smoothing)
y_eval = np.linspace(y.min(), y.max(), 500)
dos_density = kde(y_eval)

# === Side-by-Side Visualization ===
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3), dpi=300, gridspec_kw={'width_ratios': [2.5, 1]})

# --- Left Plot: Rugged Potential Energy Surface ---
ax1.scatter(x, y, color='darkgray', edgecolor='gray', s=20, alpha=0.5, zorder=2)
ax1.scatter(
    minima_x, minima_energies, 
    facecolors='white', 
    edgecolors='black', 
    linewidths=1.2, 
    s=60, 
    zorder=4
)

# Format left plot axes
ax1.set_xlabel(' ', fontsize=9)
ax1.set_ylabel(' ', fontsize=9)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_xticklabels([])
ax1.set_yticklabels([])
ax1.set_xticks([])
ax1.set_yticks([])
ax1.set_xlim(x.min() - 0.5, x.max())
ax1.set_ylim(y.min() - 0.5, y.max())

# --- Right Plot: Density of States ---
ax2.plot(dos_density, y_eval, color='black', linewidth=1.5, label='KDE (DOS)', zorder=3)
ax2.fill_betweenx(y_eval, 0, dos_density, color='gray', alpha=0.2, zorder=2)

# Format right plot axes
ax2.set_ylim(ax1.get_ylim())
ax2.set_xlabel(' ', fontsize=9)
ax2.set_ylabel(' ', fontsize=9)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_xticklabels([])
ax2.set_yticklabels([])
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xlim(dos_density.min(), dos_density.max())
ax2.set_ylim(y_eval.min() - 0.5, y_eval.max())

# --- Cross-Axes Alignment Lines ---
for mx, my in zip(minima_x, minima_energies):
    kde_val = kde(my)[0]
    con = ConnectionPatch(
        xyA=(mx, my), coordsA=ax1.transData,
        xyB=(kde_val, my), coordsB=ax2.transData,
        axesA=ax1, axesB=ax2,
        color='gray', linestyle='--', linewidth=1.0, alpha=0.7, zorder=1
    )
    fig.add_artist(con)

# Layout adjustments and file export
plt.tight_layout()
plt.subplots_adjust(wspace=graph_distance)
plt.savefig('rugged_pes_and_dos.png', dpi=300, bbox_inches='tight')
plt.show()