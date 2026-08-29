from ase.build import rotate
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_1d_scatter(data_1d, 
                    xlabel="Value", 
                    xlim_low = 0,
                    xlim_high = 2,
                    xticks = np.arange(0,2.1,0.5),
                    show_labels = True,
                    save_path=None,
                    save_data_path=None):
    """
    Plots a 1D scatter plot using vertical lines.

    Args:
        data_1d (ndarray): A 1D numpy array of data points.
        xlabel (str): Label for the x-axis.
    """

    plt.rcParams.update({
    'font.size': 12,  # Slightly smaller font for professionalism
    'font.family': 'sans-serif',
    'axes.linewidth': 1.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': True,
    'axes.spines.bottom': True,
    'axes.edgecolor': 'black',
    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'xtick.color': 'black',
    'ytick.color': 'black',
    'axes.grid': False,
    'legend.frameon': False
    })

    __version__ = "0.0.1"

    # Create a 1D scatter plot
    fig, ax = plt.subplots(figsize=(4, 2)) # Adjust figsize to be wider than tall

    # Plotting points along a single line (y=0) using vertical lines
    ax.vlines(data_1d, ymin=-0.2, ymax=0.2, color='black', alpha=0.7) # Use vlines for vertical lines

    if show_labels:
        for i, val in enumerate(data_1d):
            ax.text(val, 0.25, f"{i}", ha='center', va='bottom', fontsize=12, rotation=-90)

    # Set limits and remove y-axis
    ax.set_ylim([-0.5, 0.5])
    ax.yaxis.set_visible(False) # Hide the y-axis
    ax.set_xlabel(xlabel, rotation=180)
    # ax.set_title("1D Scatter Plot") # Removed title

    # Make the plot more professional by adjusting spines and ticks
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False) # Hide left spine as y-axis is hidden
    ax.tick_params(axis='x', width=1.5, length=5, rotation=-90) # Adjust tick appearance

    ax.set_xlim(xlim_low, xlim_high)
    ax.set_xticks(xticks)
    if save_path:
        plt.savefig(save_path, bbox_inches='tight') 
    
    if save_data_path:
        data_to_save = pd.DataFrame({'Index': range(len(data_1d)), 'Value': data_1d})
        data_to_save['Label'] = data_to_save.apply(lambda row: f"{int(row['Index'])}: {row['Value']:.2f}", axis=1)
        data_to_save.to_csv(save_data_path, index=False)

    plt.close()
    # plt.show()

# Example usage (optional):
# data_1d = np.random.rand(50)
# plot_1d_scatter(data_1d)