"""
AGOX Workflow Script for Fe/MgO interface System
- Constructs matched Fe/MgO interface
- Configures AGOX optimization loop with GPAW
"""

import os
import numpy as np
from ase import Atoms
from ase.build import surface, bulk
from ase.io import read, write
from agox.environments import Environment
from agox.generators import RattleGenerator
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.samplers import KMeansSampler
from agox.collectors import ParallelCollector, StandardCollector
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.postprocessors import ParallelRelaxPostprocess, RelaxPostprocess
from agox.helpers import SubprocessGPAW
from agox.evaluators import LocalOptimizationEvaluator
from agox import AGOX
from agox.samplers import FixedSampler
from ase.constraints import FixAtoms
from ase import Atoms

# from icecream import ic

from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.plot_structure import plot_structure
from scripts.build_heteroStruct import build_heteroStruct

# ==== Parameters ====
vacuum = 20               # Vacuum spacing in Å
a_mgo = 4.212             # MgO bulk lattice constant (Å)
a_fe = 2.870190           # Fe optimized lcao lattice constant (Å)
path_result = "0_result"
path_xsf = f"{path_result}/0_xsf"
path_fig = f"{path_result}/1_fig"
latt_log = f'{path_result}/latt_log.md'
dist_z_fe2o = 0.5 #2.3         # Interface spacing (Å), experimental
ncores = 24 # 16 cores for genkai
supercell = (3, 3, 1)
kpts = (4, 4, 1)
kappa=2
N_iterations = 50
seed = 5

# ==== Slab Number of Layer
mgo_layer_number = 1
fe_layer_number = 1

# ==== Generators Parameters
num_candidates={0:[20,0], 10:[10,10], 25:[0,20]}
#num_candidates={0:[20]}
sample_size = 20

# === Directory Setup ===
os.makedirs(path_result, exist_ok=True)
os.makedirs(path_xsf, exist_ok=True)
os.makedirs(path_fig, exist_ok=True)

# === Lattice Matching ===
a_mgo_matched = a_mgo / np.sqrt(2)
strain = (a_mgo_matched - a_fe) / a_fe * 100

with open(latt_log, 'w') as f:
    f.write(f"{a_fe=}\n{a_mgo=}\n{a_mgo_matched=}\n{strain=:.2f}%\n")

# === MgO Slab (bulk) ===
bulk_mgo = bulk('MgO', 'rocksalt', a=a_mgo, cubic=True)
slab_mgo = surface(bulk_mgo, (0, 0, 1), layers=1, vacuum=vacuum)

# Measure layer spacing
dist_z_mgo = slab_mgo[5].position[2] - slab_mgo[0].position[2]
with open(latt_log, 'a') as f:
    f.write(f"{dist_z_mgo=}\n")
write(f"{path_xsf}/slab_mgo_regular.xsf", slab_mgo)

# === Fe Slab ===
# Create a Fe(001) surface with 1 atomic layer and a given vacuum thickness
slab_fe = surface('Fe', (0, 0, 1), layers=1, vacuum=vacuum)
write(f"{path_xsf}/slab_fe.xsf", slab_fe)

# Build the Fe/MgO stack by placing the Fe slab on top of the MgO slab
# 'num_layers=1' specifies how many MgO layers to include below the Fe
# The result is saved to the specified .xsf file
slab_mgofe = build_mgo_stack(
    slab_fe,
    num_layers=mgo_layer_number,
    vacuum = vacuum,
    output_path=f"{path_xsf}/slab_mgofe.xsf")

# === Remove All Fe Atoms ===
slab_mgo = slab_mgofe[[atom.symbol != 'Fe' for atom in slab_mgofe]]
write(f"{path_xsf}/slab_mgo.xsf", slab_mgo)

slab_fe = build_fe_stack(
    slab_fe,
    num_layers=fe_layer_number,
    vacuum = vacuum,
    output_path=f"{path_xsf}/slab_fe.xsf")

# === Supercell Generation ===
slab_mgofe_33 = slab_mgofe.repeat(supercell)
# write(f"{path_xsf}/slab_mgofe_33.xsf", slab_mgofe_33)

# Repeat the MgO slab 3 times along x and y (to enlarge the surface), keep 1 layer along z
slab_mgo = slab_mgo.repeat(supercell)
# write(f"{path_xsf}/slab_mgo_33.xsf", slab_mgo)

# Repeat the Fe slab 3 times along x and y (to match the MgO slab size), keep 1 layer along z
slab_fe = slab_fe.repeat(supercell)
# write(f"{path_xsf}/slab_fe_33.xsf", slab_fe)

# === Substrate and Deposition ===
slab_substrate = slab_mgo.copy() 
slab_deposition = slab_fe.copy()
confinement_cell_height_multiplyer = 4

slab_heteroStruct = build_heteroStruct(slab_substrate, slab_deposition, output_path=f'{path_xsf}/heteroStruct.xsf')
# z_coords = [atom.position[2] for atom in slab_heteroStruct]
# unique_heights = np.unique(np.round(z_coords, decimals=2))
# substrate_layer = unique_heights[:1]
# deposition_layer = unique_heights[1:]

# filter_substrate = [atom for atom in slab_heteroStruct if round(atom.position[2], 2) in substrate_layer]
# filter_deposition = [atom for atom in slab_heteroStruct if round(atom.position[2], 2) in deposition_layer]

# slab_substrate = Atoms(filter_substrate)
# slab_substrate.set_cell(slab_heteroStruct.get_cell())
# slab_substrate.set_pbc(slab_heteroStruct.get_pbc())

# slab_deposition = Atoms(filter_deposition)
# slab_deposition.set_cell(slab_heteroStruct.get_cell())
# slab_deposition.set_pbc(slab_heteroStruct.get_pbc())

# Introducting Oxidation by moving one O to the Fe
# slab_deposition_positions = slab_deposition.positions
# z_deposition_min = np.min(slab_deposition_positions[:, 2])
# slab_deposition_positions[18][2] = z_deposition_min
# slab_deposition.set_positions(slab_deposition_positions)

write(f'{path_xsf}/slab_substrate.xsf', slab_substrate)
write(f'{path_xsf}/slab_deposition.xsf', slab_deposition)

# === AGoX Environment ===
slab_substrate.pbc = [True, True, False]
confinement_corner = np.array([0, 0, slab_substrate.positions[:, 2].max() + dist_z_fe2o])
# confinement_corner = np.array([0, 0, slab_substrate.positions[:, 2].max() + 0.5])

confinement_cell = slab_deposition.cell.copy()
# Calculate the height of the deposition layer
deposition_z_positions = slab_deposition.get_positions()[:, 2]
deposition_layer_height = deposition_z_positions.max() - deposition_z_positions.min()

if deposition_layer_height < 2.1: # standard value of two monolayer height
    deposition_layer_height = 2.1

deposition_layer_height = deposition_layer_height * confinement_cell_height_multiplyer
confinement_cell[2, 2] = deposition_layer_height # Set the z-component of the confinement cell to the MgO layer height
environment = Environment(
    template= slab_substrate,
    symbols=slab_deposition.get_chemical_formula(),
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, False]
)

# Plot Environment Figure
# environment.plot(f'{path_fig}/environment.png')

# === Structure Generators ===
n_rattle = len(slab_deposition)
generators = [
    HeteroStructRandomize(
        **environment.get_confinement(),
        slab_deposition=slab_deposition,
        hetero_slab_dist=dist_z_fe2o,
        write_struct=True,
        rattle_amplitude=1.5,
        n_rattle=n_rattle,
        # add_inter_layer_space=1.5,
        generate_pristine=False,
    ),
    RattleGenerator(
        **environment.get_confinement(),
        n_rattle=int(n_rattle * 0.5),
        rattle_amplitude=2.3),
]

# === Test Generators ===
hetero_candidate = generators[0](sampler=None, environment=environment)[0]
write(f'{path_xsf}/hetero_candidate.xsf', hetero_candidate)

sampler = FixedSampler(hetero_candidate)
rattle_candidate = generators[1](sampler, environment)[0]
write(f'{path_xsf}/rattle_candidate.xsf', rattle_candidate)

# === Plotting Test Generators
# cell_offset = np.array([10.0, 10.0, 0.0]) # Example offset
# custom_colors = {'O': 'red', 'Mg': 'orange', 'Fe': 'green'}
# for label, i in [ ('hetero', hetero_candidate), ('rattle', rattle_candidate)]:
#     # Apply constraints for visualization
#     unique_substrate_symbols = list(set(slab_substrate.get_chemical_symbols()))
#     substrate_indices = [atom.index for atom in i if (atom.symbol in unique_substrate_symbols) and (round(atom.position[2], 2) in substrate_layer)]
#     constraint = FixAtoms(indices=substrate_indices)
#     i.set_constraint(constraint)
#     plot_structure(
#             i,
#             plane='yz+',
#             save_path=f"{path_fig}/figure_{label}.png",
#             environment=environment,
#             figsize = (20,20),
#             repeat=5,
#             cell_offset = cell_offset,
#             linewidths_cell = 5,
#             linewidths_environment = 5,
#             plot_show = False,
#     )

# === Database Setup ===
db_dir = "1_db"
os.makedirs(db_dir, exist_ok=True)
database = Database(filename=f"{db_dir}/db_0.db", order=5)

# === GPR Model with Fingerprint ===
descriptor = Fingerprint(environment=environment)
beta = 0.01
k0 = C(beta, (beta, beta)) * RBF()
k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))

model = GPR(
    descriptor=descriptor,
    kernel=kernel,
    database=database,
    prior=Repulsive()
)

# === Sampler and Collectors ===
sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)

collector = ParallelCollector(
    generators=generators,
    sampler=sampler,
    environment=environment,
    num_candidates=num_candidates,
    order=1
)

# === Acquisition and Relaxation ===
acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=kappa, order=3)

relaxer = ParallelRelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    constraints=environment.get_constraints(),
    optimizer_run_kwargs={"steps": 100},
    start_relax=10,
    order=2
)

# === GPAW Calculator ===
calc = SubprocessGPAW(
    ncores = ncores,
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    #convergence={"energy": 1e-4},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    txt="output.txt",
    kpts=kpts,
    symmetry='off',
    nbands='nao',
    maxiter=100,
    occupations={"name": "fermi-dirac", "width": 0.05},
    hund=True,
    spinpol=True
)

# === Evaluation and AGoX Run ===
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={"logfile": None},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
    constraints=environment.get_constraints(),
    store_trajectory=False,
    order=4
)

# seed = 1
agox = AGOX(
    collector,
    relaxer,
    acquisitor,
    evaluator,
    database,
    seed=seed
)

# === Start Optimization ===
agox.run(N_iterations=N_iterations)

