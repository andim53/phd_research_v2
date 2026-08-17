from pathlib import Path
from ase.io import read
from scripts.write_best_so_far_xsf import write_best_so_far_xsf

# Define target workspace and subdirectory parameters
dir_out = Path(dir_out)
file_idx = "19"

# Construct paths for source trajectory and output directory
traj_file_path = dir_out / dir_xsf_traj / file_idx / f"{file_idx}_seed_0.traj"
output_dir_path = dir_out / dir_xsf_min_so_far / file_idx

# Ensure output directory exists
output_dir_path.mkdir(parents=True, exist_ok=True)

# Load all atomic structures from the ASE trajectory
trajs = read(traj_file_path, index=":")

# Extract potential energy for each trajectory frame
all_e = [atoms.get_potential_energy() for atoms in trajs]

# Export the best-so-far XSF trajectory and optimal structures
write_best_so_far_xsf(
    trajs=trajs,
    energies=all_e,
    output_dir=output_dir_path,
)