"""
AGOX Workflow: Amorphous Ta–B Bulk Optimization
-----------------------------------------------
1. Builds a periodic Ta supercell with dilute B concentration.
2. Initializes an AGOX environment with periodic confinement.
3. Uses GPR with a Fingerprint descriptor as a surrogate model.
4. Generates candidates via Amorphous randomization, Permutation, and Rattle.
5. Performs Bayesian optimization (UCB) with GPAW (LCAO) as the true evaluator.
"""

import os
import numpy as np
import ray
from ase import Atoms
from ase.build import bulk
from ase.io import write

# AGOX Core Imports
from agox import AGOX
from agox.environments import Environment
from agox.generators import RattleGenerator, PermutationGenerator
from agox.samplers import KMeansSampler, FixedSampler
from agox.collectors import StandardCollector
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.postprocessors import RelaxPostprocess
from agox.evaluators import LocalOptimizationEvaluator
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.helpers import SubprocessGPAW

# Custom/Project-specific Imports
from scripts.amorph_struct_randomize import AmorphStructRandomize
from scripts.add_B_concentration import add_B_concentration
from gpaw import FermiDirac

# =============================================================================
# 1. GLOBAL PARAMETERS & DIRECTORIES
# =============================================================================
a_ta = 3.30             # Ta bcc lattice constant (Å)
scale_cell = 1.05       # Slight expansion (+5%) for amorphous headroom
supercell_size = (3, 3, 3)
kpts_grid = (3, 3, 3)
cB = 0.04               # Target Boron concentration
N_iterations = 100      # Total AGOX optimization steps
ncores = 1              # MPI cores per GPAW task

# Setup output directory structure
path_result = "0_simul"
paths = [path_result, f"{path_result}/0_xsf", f"{path_result}/1_fig", f"{path_result}/1_db"]
for p in paths:
    os.makedirs(p, exist_ok=True)

# =============================================================================
# 2. STRUCTURE BUILDING & ENVIRONMENT
# =============================================================================
# Build the base Ta supercell
ta_bulk = bulk("Ta", "bcc", a=a_ta, cubic=True) * supercell_size
ta_bulk.set_cell(ta_bulk.cell * scale_cell, scale_atoms=True)

# Define template (empty cell for AGOX)
template = Atoms("", cell=ta_bulk.cell.copy(), pbc=True)

# Inject Boron atoms based on concentration
tab_bulk, n_b, n_ta = add_B_concentration(ta_bulk, cB=cB, make_structure=True)

# Set up the search space environment
environment = Environment(
    template=template,
    symbols=tab_bulk.get_chemical_formula(),
    confinement_cell=template.cell.copy(),
    confinement_corner=np.array([0, 0, 0]),
    box_constraint_pbc=[True, True, True],
)

# =============================================================================
# 3. SEARCH STRATEGY (GENERATORS & SAMPLERS)
# =============================================================================
n_atoms = len(ta_bulk)

generators = [
    # Primary: Complete randomization into amorphous state
    AmorphStructRandomize(
        **environment.get_confinement(),
        amorph=tab_bulk,
        rattle_amplitude=1.5,
        n_rattle=n_atoms,
        generate_pristine=False,
    ),
    # Secondary: Swap Ta and B positions
    PermutationGenerator(
        **environment.get_confinement(),
        max_number_of_swaps=1,
        rattle_strength=1.0,
    ),
    # Tertiary: Small local displacements
    RattleGenerator(
        **environment.get_confinement(),
        n_rattle=int(0.7 * n_atoms),
        rattle_amplitude=2.3,
    ),
]

# Database for storing calculated structures
database = Database(filename=f"{path_result}/1_db/db_0.db", order=5)

# =============================================================================
# 4. SURROGATE MODEL (GPR)
# =============================================================================
descriptor = Fingerprint(environment=environment)

# Kernel setup: Composite RBF with noise and scaling
beta = 0.01
k_base = (C(beta, (beta, beta)) * RBF()) + (C(1 - beta, (1 - beta, 1 - beta)) * RBF())
kernel = C(5000, (1, 1e5)) * k_base + Noise(0.01, (0.01, 0.01))

model = GPR(
    descriptor=descriptor,
    kernel=kernel,
    database=database,
    prior=Repulsive(),  # Prior to prevent atoms from overlapping
    use_ray=False
)

# =============================================================================
# 5. AGOX COMPONENTS (COLLECTOR, RELAXER, EVALUATOR)
# =============================================================================
sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=10)

# Diversity-driven candidate collection
num_candidates = {0: [10, 0, 0], 10: [5, 5, 0], 25: [0, 5, 5]}
collector = StandardCollector(
    generators=generators,
    sampler=sampler,
    environment=environment,
    num_candidates=num_candidates,
    order=1,
)

# Bayesian Acquisition (LCB)
acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=2, order=3)

# Surrogate Relaxation: Relax candidates on the GPR surface before DFT evaluation
relaxer = RelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    optimizer_run_kwargs={"fmax": 0.05, "steps": 200},
    constraints=environment.get_constraints(),
    start_relax=10,
    order=2,
)

# DFT Evaluator: High-fidelity calculations with GPAW
calc = SubprocessGPAW(
    ncores=ncores,
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    h=0.22,
    kpts={'size': kpts_grid, 'gamma': True},
    occupations=FermiDirac(0.1),
    convergence={'energy': 1e-6, 'density': 1e-4},
    symmetry={'point_group': False},
    maxiter=100,
    txt="gpaw_eval.txt",
)

evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={"logfile": None},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
    constraints=environment.get_constraints(),
    order=4,
)

# =============================================================================
# 6. EXECUTION
# =============================================================================
agox = AGOX(
    collector,
    relaxer,
    acquisitor,
    evaluator,
    database,
    seed=1,
)

agox.run(N_iterations=N_iterations)