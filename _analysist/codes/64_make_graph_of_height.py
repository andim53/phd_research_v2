import matplotlib.pyplot as plt
from pathlib import Path

from agox.databases import Database

from scripts.calculate_relative_energy import calculate_relative_energy
from scripts.calculate_best_so_far import calculate_best_so_far

db_path = db_paths[0][0]
# Database loading
db_path = Path(db_path) / "1_db" / "db_0.db"
database = Database(filename=str(db_path))
trajs = database.restore_to_trajectory()

# Data Calculation
_, _, _, rel_energies = calculate_relative_energy(trajs)
best_energies, best_indices = calculate_best_so_far(rel_energies)

z_height_spans = [atoms.get_positions()[:, 2].max() - atoms.get_positions()[:, 2].min() for atoms in trajs]