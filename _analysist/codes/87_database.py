def process_database(
    dir_path: str,
    file_idx: int,
    dir_out: str,
    dir_xsf_traj: str,
    dir_xsf: str,
    plot_best_so_far: bool = True,
    plot_by_seed: bool = True,
    figsize=(6, 3.5),
    show_legend: bool = False,  # Added as parameter
) -> None:
    """
    Extracts trajectory data. Seeds are renamed to start at 0 sequentially 
    for cleaner labeling.
    """
    root = Path(dir_path)
    # Sort seeds naturally by name
    seed_dirs = sorted(root.glob("seed_*"), key=lambda x: int(x.name.split('_')[-1]) if x.name.split('_')[-1].isdigit() else x.name)
    
    seed_data: Dict[str, List] = {}

    if not seed_dirs:
        db_path = root / "1_db" / "db_0.db"
        if db_path.exists():
            db = Database(filename=str(db_path))
            db.restore_to_memory()
            seed_data["Seed 0"] = db.restore_to_trajectory()
    else:
        for i, p in enumerate(seed_dirs):
            seed_num = p.name.split('_')[-1]
            db_path = p / "1_db" / f"db_{seed_num}.db"
            if db_path.exists():
                db = Database(filename=str(db_path))
                db.restore_to_memory()
                seed_data[f"Seed {i}"] = db.restore_to_trajectory()

    all_traj = []
    sorted_seed_names = sorted(seed_data.keys(), key=lambda x: int(x.split()[-1]))
    for s_name in sorted_seed_names:
        all_traj.extend(seed_data[s_name])

    if not all_traj:
        return

    out_base = Path(dir_out)
    traj_dir = out_base / dir_xsf_traj
    xsf_dir = out_base / dir_xsf / str(file_idx)
    traj_dir.mkdir(parents=True, exist_ok=True)
    xsf_dir.mkdir(parents=True, exist_ok=True)

    write(traj_dir / f"traj_{file_idx}.xsf", all_traj)
    write(traj_dir / f"traj_{file_idx}.traj", all_traj)
    energies, _, rel_e, rel_e_atom = calculate_relative_energy(all_traj)

    df = pd.DataFrame({
        "index": range(len(all_traj)),
        "energy": energies,
        "relative_energy": rel_e,
        "relative_energy_per_atom": rel_e_atom
    })
    df.to_csv(out_base / f"data_{file_idx}.csv", index=False)

    for i, frame in enumerate(all_traj):
        frame_i = frame.copy()
        for key in ["initial_magmoms", "magmoms"]:
            frame_i.arrays.pop(key, None)
        write(xsf_dir / f"struct_{i}.xsf", frame_i)

    # --- Best-So-Far Plotting ---
    if plot_best_so_far:
        fig, ax = plt.subplots(figsize=figsize)
        max_y = 0
        max_x = 0

        if plot_by_seed:
            cmap = plt.get_cmap('tab10')
            for i, s_name in enumerate(sorted_seed_names):
                s_traj = seed_data[s_name]
                _, _, _, s_rel_e_atom = calculate_relative_energy(s_traj)
                s_best_so_far = np.minimum.accumulate(s_rel_e_atom)
                
                if i == 0:
                    current_color = 'black'
                    linewidth = 2.0  
                    zorder = 50      
                else:
                    current_color = cmap((i-1) % 10) 
                    linewidth = 1.5
                    zorder = 1

                ax.plot(range(len(s_best_so_far)), s_best_so_far, 
                        label=s_name, lw=linewidth, color=current_color, zorder=zorder)
                
                max_y = max(max_y, np.max(s_rel_e_atom))
                max_x = max(max_x, len(s_best_so_far))
        else:
            best_so_far = np.minimum.accumulate(rel_e_atom)
            ax.plot(range(len(best_so_far)), best_so_far, color='black', lw=2, label='Combined')
            max_y = np.max(rel_e_atom)
            max_x = len(best_so_far)

        # Formatting
        ax.set_xlabel('Evaluated Candidates')
        ax.set_ylabel(r'$E_{i}-E_{glob}$ (eV/atom)')
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y * 1.1)
        
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.tick_params(axis='both', which='both', top=False, right=False)

        # Updated Legend Logic
        if show_legend:
            ax.legend(
                loc='upper left', 
                fontsize=9, 
                ncol=1, 
                frameon=True,
                bbox_to_anchor=(1.02, 1),
                borderaxespad=0.,
            )
            
        plt.tight_layout()
        
        plot_path = out_base / "progression_plots"
        plot_path.mkdir(exist_ok=True)
        plt.savefig(plot_path / f"progression_seed_split_{file_idx}.png", dpi=300)
        plt.show()
        plt.close(fig)