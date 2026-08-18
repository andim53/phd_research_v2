#!/usr/bin/env python3
"""
Stage 0 (standalone): Researcher plotting style — applied once at import time.

Not a runnable pipeline stage; imported by the other stage scripts (or called
explicitly) to guarantee every figure matches the codes/07 convention.

Usage (import):
  from run_stage0_style import apply_style
  apply_style()

Or as a standalone sanity check:
  /home/miniconda3/envs/agox_v2/bin/python run_stage0_style.py
"""
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Color palette — same two colours used in codes/07
# ---------------------------------------------------------------------------
COLORS = ['#FF0000', '#00FF00']

# ---------------------------------------------------------------------------
# Matplotlib global rcParams — mirrors codes/07_plotting_style_and_label_
# configuration.py and the inline rcParams block in run_analysis_indices.py
# ---------------------------------------------------------------------------

CUSTOM_RC_PARAMS = {
    # Font & Text Styling
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif', 'Times New Roman', 'Computer Modern'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    
    # Axes & Box Frame
    # 'axes.frameon': True,
    'axes.linewidth': 1.0,
    'axes.edgecolor': 'black',
    'axes.facecolor': 'white',
    
    # Ticks Placement & Direction
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    
    # Grid Settings (Disabled as per reference image)
    'axes.grid': False,
    
    # Figure Layout
    'figure.autolayout': True,
    'figure.dpi': 300,
}

# CUSTOM_RC_PARAMS = {
#     # Typography
#     'font.size': 12,
#     'font.family': 'serif',
#     # Axes and borders
#     'axes.linewidth': 1.5,
#     'axes.edgecolor': 'black',
#     'axes.spines.top': True,
#     'axes.spines.right': True,
#     # Major ticks (outer "boxed" look)
#     'xtick.direction': 'out',
#     'ytick.direction': 'out',
#     'xtick.major.size': 5,
#     'ytick.major.size': 5,
#     'xtick.major.width': 1.5,
#     'ytick.major.width': 1.5,
#     'xtick.top': True,
#     'ytick.right': True,
#     # Minor ticks
#     'xtick.minor.visible': True,
#     'ytick.minor.visible': True,
#     'xtick.minor.size': 2,
#     'ytick.minor.size': 2,
#     'xtick.minor.width': 1.0,
#     'ytick.minor.width': 1.0,
#     # Miscellaneous
#     'axes.grid': False,
#     'legend.frameon': True,
# }

# Energy axis label used by every figure in the pipeline
E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'


def apply_style() -> None:
    """Apply the researcher plotting style globally (rcParams)."""
    plt.rcParams.update(CUSTOM_RC_PARAMS)


def test_sanity() -> None:
    """Quick self-check: draw and save a tiny figure to prove the style works."""
    import os
    apply_style()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot([0, 1], [0, 1], label='test', lw=1.5)
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel('arbitrary')
    ax.legend(frameon=True)
    out = os.path.join(os.path.dirname(__file__), '_style_sanity.png')
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Style sanity check — figure saved to {out}")


if __name__ == '__main__':
    test_sanity()
