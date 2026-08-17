from scripts.plot_energy_progression import plot_energy_progression
import numpy as np

max_x = 120
max_y = 1.1

xticks = np.linspace(0, max_x, 7)
xticks = np.round(xticks).astype(int)

yticks = np.linspace(0, max_y, 5)
yticks = np.round(yticks, 2)

x_lim=(0, max_x)
y_lim=(0, max_y)


plot_energy_progression(
    db_paths,
    labels,
    dir_out,
    dir_im,

    figsize=(6, 3),

    y_label=e_label,
    x_label=r'Evaluated Candidate',
    line_styles=['-'],

    rcParams=rcParams,
    colors=colors,

    linewidth=2.0,

    x_lim=x_lim,
    y_lim=y_lim,

    xticks = xticks,
    yticks = yticks,

    # index_skip=3,
    # add_scatter=True,
    #scale_up = 1,
)