from scripts.plot_energy_distribution import plot_energy_distribution

max_x = 2
max_y = 2.0

xticks = np.linspace(0, max_x, 2)
xticks = np.round(xticks).astype(int)

yticks = np.linspace(0, max_y, 10)
yticks = np.round(yticks, 2)

x_lim=(0, max_x)
y_lim=(0, max_y)

plot_energy_distribution(
        db_paths,
        labels,
        dir_out,
        dir_im,
        figsize=(3, 5),
        y_label=e_label,
        x_label=None,
        colors=colors,

        # xticks = xticks,
        yticks = yticks,

        # x_lim=x_lim,
        y_lim=y_lim,
        
        plot_type="box",  # "box" or "density"
        font_family='serif',
        rcParams=rcParams,
        widths = 0.6
)