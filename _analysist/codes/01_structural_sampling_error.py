import os
import numpy as np
from ase.build import surface, bulk
from ase.io import write

from agox.environments import Environment
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.samplers import KMeansSampler

# Custom stack building modules
from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.build_heteroStruct import build_heteroStruct

# === System Parameters ===
vacuum = 20
a_mgo = 4.212
a_fe = 2.870190
dist_z_fe2o = 0.5 
supercell = (5, 5, 1)
sample_size = 20

# === Path Configuration ===
db_path = f'1_result/1_1ML_feOnMgo/1_db/db_0.db'

# === Lattice Matching and Base Slabs ===
bulk_mgo = bulk('MgO', 'rocksalt', a=a_mgo, cubic=True)
slab_fe_base = surface('Fe', (0, 0, 1), layers=1, vacuum=vacuum)

# === Substrate and Deposition Stacks ===
slab_mgofe = build_mgo_stack(slab_fe_base, num_layers=1, vacuum=vacuum)
slab_mgo = slab_mgofe[[atom.symbol != 'Fe' for atom in slab_mgofe]].repeat(supercell)
slab_fe = build_fe_stack(slab_fe_base, num_layers=1, vacuum=vacuum).repeat(supercell)

slab_substrate = slab_mgo.copy()
slab_deposition = slab_fe.copy()

# === AGOX Environment Geometry Setup ===
slab_substrate.pbc = [True, True, False]
confinement_corner = np.array([0, 0, slab_substrate.positions[:, 2].max() + dist_z_fe2o])

z_pos = slab_deposition.get_positions()[:, 2]
h_dep = max(z_pos.max() - z_pos.min(), 2.1)
confinement_cell = slab_deposition.cell.copy()
confinement_cell[2, 2] = h_dep * 4

environment = Environment(
    template=slab_substrate,
    symbols=slab_deposition.get_chemical_formula(),
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, False]
)

# === Database Loading and Sampling ===
if os.path.exists(db_path):
    db = Database(filename=db_path)
    all_structures = db.restore_to_trajectory() 
    print(f"Total structures in DB: {len(all_structures)}")

    # Initialize clustering descriptors and samplers
    descriptor = Fingerprint(environment=environment)
    sampler = KMeansSampler(
        descriptor=descriptor, 
        sample_size=20, 
        max_energy=500 
    )

    # Process and filter structural sample data
    try:
        filtered_structures = sampler.filters.filter(all_structures)
        print(f"Structures after energy filtering: {len(filtered_structures)}")
        
        if len(filtered_structures) == 0:
            print("ALERT: Energy filter is still too strict! Increase max_energy.")
        else:
            sampler.setup(filtered_structures)
            sample = sampler.get_sample(5)
            print(f"SUCCESS: Sampler retrieved {len(sample)} members.")
            write('check_sampler.xsf', sample[0])
    except Exception as e:
        print(f"Error: {e}")