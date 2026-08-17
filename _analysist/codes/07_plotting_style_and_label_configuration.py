import matplotlib.pyplot as plt

# === Color Palette Definitions ===
colors = [
    '#FF0000',  # Pure Bold Red
    '#00FF00',  # Pure Bold Green
]

# === Matplotlib Global Configuration (rcParams) ===
custom_rc_params = {
    # Typography
    'font.size': 12,
    'font.family': 'serif',

    # Axes and Borders
    'axes.linewidth': 1.5,
    'axes.edgecolor': 'black',
    'axes.spines.top': True,
    'axes.spines.right': True,

    # Major Ticks (Outer edge "boxed" look)
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'xtick.top': True,
    'ytick.right': True,

    # Minor Ticks
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.minor.size': 2,
    'ytick.minor.size': 2,
    'xtick.minor.width': 1.0,
    'ytick.minor.width': 1.0,

    # Miscellaneous (Grid and Legend)
    'axes.grid': False,
    'legend.frameon': True,
}

# Apply the custom style settings
plt.rcParams.update(custom_rc_params)

# === Plot Labels and LaTeX Formatting ===
# Alternative: e_label = r'$E_{rel}$ (eV/atom)'
e_label = r'$E_{i}-E_{glob}$ (eV/atom)'