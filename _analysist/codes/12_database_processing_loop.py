from scripts.process_database import process_database

# === Database Processing Execution ===
for dir_path, file_idx in db_paths:
    process_database(
        # Input and Output Paths
        dir_path=dir_path,
        file_idx=file_idx,
        dir_out=dir_out,
        dir_xsf_traj=dir_xsf_traj,
        dir_xsf=dir_xsf,
        individual_seeds_dir_name=file_idx,
        # dir_best_xsf = "3_min_so_far",

        # Processing and Save Flags
        save_individual_trajectories=True,
        plot_best_so_far=True,
        plot_by_seed=True,

        # Plot Settings and Limits
        figsize=(8, 5),
        custom_max_x=None,
        custom_max_y=None,
        start_iter=10 # 10,  # Starts at iteration ten
    )