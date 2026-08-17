import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms
from ase.filters import FrechetCellFilter
from ase.optimize import BFGS

from agox import AGOX
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.collectors import ParallelCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RandomGenerator, RattleGenerator
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import KMeansSampler

# Manually set seed and database-index
seed = 41
database_index = 0

class CellRelaxationBFGS:
    def __init__(self, atoms, **kwargs):
        # 6-component mask: [xx, yy, zz, yz, zx, xy]
        mask = kwargs.pop("mask", [True, True, True, True, True, True])

        # Wrap atoms in ASE FrechetCellFilter
        self.filter = FrechetCellFilter(atoms, mask=mask)
        # Instantiate BFGS using the filtered atoms
        self.optimizer = BFGS(self.filter, **kwargs)

    def attach(self, function, interval=1, *args, **kwargs):
        self.optimizer.attach(function, interval, *args, **kwargs)

    def run(self, **kwargs):
        self.optimizer.run(**kwargs)

    def get_number_of_steps(self):
        return self.optimizer.get_number_of_steps()

##############################################################################
# Calculator
##############################################################################

from agox.helpers import SubprocessGPAW

calc = SubprocessGPAW(
    ncores=1,
    mode={"name": "pw", "ecut": 200},
    xc="PBE",
    kpts=(1, 1, 1),
)

##############################################################################
# System & general settings:
##############################################################################

# Make an empty template with a cubic cell of size 6x6x6 with periodic boundary conditions
# in all directions
template = Atoms("", cell=np.eye(3) * 6, pbc=True)

# Confinement cell matches the template cell in all dimensions and is placed at
# the origin of the template cell.
confinement_cell = template.cell.copy()
confinement_corner = np.array([0, 0, 0])

environment = Environment(
    template=template,
    symbols="Au6Ni6",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, True],  # Confinement is periodic in all directions.
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=5)

##############################################################################
# Search Settings:
##############################################################################

# Setup a ML model.
descriptor = Fingerprint(environment=environment)
beta = 0.01
k0 = C(beta, (beta, beta)) * RBF()
k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

# Sampler to choose candidates to modify using the generators.
sample_size = 10
sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)

# Generators to produce candidates structures
rattle_generator = RattleGenerator(**environment.get_confinement())
random_generator = RandomGenerator(**environment.get_confinement(), contiguous=False)

# Dict specificies how many candidates are created with and the dict-keys are iterations.
generators = [random_generator, rattle_generator]
num_candidates = {0: [10, 0], 5: [3, 7]}

# Collector creates a number of structures in each iteration.
collector = ParallelCollector(
    generators=generators,
    sampler=sampler,
    environment=environment,
    num_candidates=num_candidates,
    order=1,
)

# Acquisitor to choose a candidate to evaluate in the real potential.
acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=2, order=3)

# Number of steps is very low - should be set higher for a real search!
relaxer = ParallelRelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    constraints=environment.get_constraints(),
    optimizer_run_kwargs={"steps": 5},
    start_relax=8,
    order=2,
)


# Evaluator to evaluate the candidates in the real potential.
evaluator = LocalOptimizationEvaluator(
    calc,
    optimizer=CellRelaxationBFGS,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={
        "logfile": "opt.log",  # Logging local optimizer progress to opt.log
        "mask": [True, True, True, True, True, True],
    },
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5},
    constraints=environment.get_constraints(),
    store_trajectory=True,
    order=4,
)

##############################################################################
# Let get the show running!
##############################################################################

# The oder of things here does not matter. But it can be simpler to understand
# what the expected behaviour is if they are put in order.
agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)

agox.run(N_iterations=10)