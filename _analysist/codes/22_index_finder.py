from pathlib import Path
import numpy as np
from ase.io import read

# ==========================================
# Configuration & Setup
# ==========================================
TARGET_ENERGY = 0.134      # eV/atom target
TOLERANCE = 0.01          # Energy matching window
TOP_N = 5                # Number of structures to retrieve per category
ELEMENT = "Fe"           # Target element for Z-span calculations

DIR_OUT = Path(dir_out)
DIR_XSF_TRAJ = Path(dir_xsf_traj)

# TRAJ_FILE = Path(DIR_OUT) / DIR_XSF_TRAJ / "traj_19.traj"
# TRAJ_FILE = Path(DIR_OUT) / DIR_XSF_TRAJ / "traj_39.traj"
TRAJ_FILE = Path(DIR_OUT) / DIR_XSF_TRAJ / "traj_66.traj"


def analyze_trajectory(traj_path: Path):
    structures = read(traj_path, index=":")
    raw_energies, z_height_spans = [], []

    # 1. Feature Extraction
    for atoms in structures:
        try:
            fe_mask = atoms.symbols == ELEMENT
            if not np.any(fe_mask):
                continue

            z_fe = atoms.positions[fe_mask, 2]
            z_height_spans.append(z_fe.max() - z_fe.min())
            raw_energies.append(atoms.get_potential_energy())

        except Exception as err:
            print(f"Skipping frame due to error: {err}")
            continue

    if not raw_energies:
        print("No valid structures extracted.")
        return

    # 2. Normalization
    num_atoms = len(structures[0])
    energies = (np.array(raw_energies) - min(raw_energies)) / num_atoms
    z_data = np.array(z_height_spans) - min(z_height_spans)

    # 3. Energy Window Selection
    energy_mask = np.abs(energies - TARGET_ENERGY) <= TOLERANCE
    target_indices = np.where(energy_mask)[0]

    if len(target_indices) == 0:
        print("No structures fell within the target energy tolerance.")
        return

    subset_z = z_data[target_indices]

    # 4. Sorting & Categorization
    idx_flat = target_indices[np.argsort(subset_z)[:TOP_N]]
    idx_peak = target_indices[np.argsort(subset_z)[::-1][:TOP_N]]

    target_median_z = np.median(subset_z)
    median_diffs = np.abs(subset_z - target_median_z)
    idx_median = target_indices[np.argsort(median_diffs)[:TOP_N]]

    categories = [
        ("Flattest & Near Flattest", idx_flat),
        ("Median & Near Median", idx_median),
        ("Peak & Near Peak", idx_peak),
    ]

    # 5. Results Display
    for label, indices in categories:
        print(f"[{label}]")
        print(f"{'Index':<10} | {'Energy (eV/at)':<15} | {'Z-Span (Å)':<10}")
        print("-" * 42)
        for idx in indices:
            print(f"{idx:<10} | {energies[idx]:<15.6f} | {z_data[idx]:<10.6f}")
        print()


if __name__ == "__main__":
    analyze_trajectory(TRAJ_FILE)