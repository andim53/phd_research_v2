import os
from pathlib import Path
import numpy as np

# ASE Imports
from ase import Atoms
from ase.build import bulk
from ase.io import write

# AGOX Core & Utilities
from agox import AGOX
from agox.environments import Environment
from agox.databases import Database
from agox.helpers import SubprocessGPAW

# AGOX Pipeline Components
from agox.generators import RattleGenerator
from agox.samplers import KMeansSampler, FixedSampler
from agox.collectors import ParallelCollector
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.postprocessors import ParallelRelaxPostprocess
from agox.evaluators import LocalOptimizationEvaluator

# AGOX Machine Learning Components
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

# Custom Scripts
from scripts.amorph_struct_randomize import AmorphStructRandomize
from scripts.amorph_permutation import AmorphPermutationGenerator
from scripts.generate_interstitial_alloy import generate_interstitial_alloy

# === CONFIGURATION PARAMETERS ===

# Simulation Environment
N_SEEDS = 100
N_ITERATIONS = 100
N_CORES = 24 #16

# Host Material & Crystal Structure Settings
HOST_ELEMENT = "Pt"
CRYSTAL_STRUCTURE = "fcc"
LATTICE_CONSTANT = 3.975534 # optmized
SUPERCELL_DIM = (4, 4, 4)
SCALE_CELL = 1.05  # Cell volume scaling factor

# Interstitial Element & Alloy Settings
INTERSTITIAL_ELEMENT = "P"
CONCENTRATION_PERCENT = 20.0  # Desired interstitial concentration (e.g., 5.0 for 5%)

# Generator & Perturbation Parameters
MAX_SWAPS = 20
PERMUT_ATTEMPTS = 20
CHECK_OVERLAP = False
RAND_ATTEMPTS = 500
CHECK_COVALENT = False
RATTLE_AMPLITUDE = 1.5
RATTLE_STRENGTH = 1.5  # For permutation generator

# AGOX Machine Learning & Sampling Settings
NUM_CANDIDATES = {0: [10, 0, 0], 10: [5, 5, 0], 25: [0, 5, 5]}
SAMPLE_SIZE = 10
BETA = 0.01

# GPAW DFT Calculator Settings
KPTS = (1, 1, 1)
DFT_MODE = {"name": "lcao"}
DFT_BASIS = "dzp"
DFT_XC = "PBE"
DFT_SYMMETRY = "off"
DFT_NBANDS = "nao"
DFT_MIXER = {"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100}
DFT_CONVERGENCE = {"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3}
DFT_OCCUPATIONS = {"name": "fermi-dirac", "width": 0.05}
DFT_MAX_ITERATIONS = 100

# Run Stats Tracker
success_count = 0
fail_count = 0

# === SEED ITERATION LOOP ===

for seed in range(N_SEEDS):
    print(f"\n--- Starting Seed: {seed} ---")

    # Establish Directory Structures
    base_dir = Path(f"seed_{seed}")
    path_xsf = base_dir / "0_result" / "0_xsf"
    path_fig = base_dir / "0_result" / "1_fig"
    db_dir = base_dir / "1_db"

    for directory in [path_xsf, path_fig, db_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # === Structure Generation ===
    host_bulk = bulk(HOST_ELEMENT, CRYSTAL_STRUCTURE, a=LATTICE_CONSTANT, cubic=True)
    host_bulk.set_cell(host_bulk.cell * SCALE_CELL, scale_atoms=True)

    # Calculate number of interstitials to insert dynamically:
    # Formula: B = (C * A) / (1 - C)
    # where:
    #   A = Host atoms (amount_a)
    #   B = Interstitial atoms to add (amount_b)
    #   C = Target concentration in decimal form
    amount_a = len(host_bulk * SUPERCELL_DIM)
    concentration_decimal = CONCENTRATION_PERCENT / 100.0
    amount_b = (concentration_decimal * amount_a) / (1.0 - concentration_decimal)
    
    # We round to the nearest integer to use for our atomic additions
    num_to_add = int(round(amount_b))
    print(f"-> Host atoms: {amount_a}, Target: {CONCENTRATION_PERCENT}%, Calculated interstitials to add: {num_to_add}")

    alloy_structure = generate_interstitial_alloy(
        host_unit=host_bulk,
        interstitial_element=INTERSTITIAL_ELEMENT,
        supercell_dim=SUPERCELL_DIM,
        lattice_type=CRYSTAL_STRUCTURE,
        num_to_add=num_to_add,
    )

    write("alloy_structure.xsf", alloy_structure)
    write("host_bulk.xsf", host_bulk * SUPERCELL_DIM)

    # === Define AGOX Environment ===
    template = Atoms("", cell=alloy_structure.cell.copy(), pbc=True)
    environment = Environment(
        template=template,
        symbols=alloy_structure.get_chemical_formula(),
        confinement_cell=template.cell.copy(),
        confinement_corner=np.array([0, 0, 0]),
        box_constraint_pbc=[True, True, True],
    )

    # === Initialize Generators ===
    n_rattle = len(alloy_structure)
    generators = [
        AmorphStructRandomize(
            **environment.get_confinement(),
            amorph=alloy_structure,
            write_struct=True,
            write_temp_struct=False,
            rattle_amplitude=RATTLE_AMPLITUDE,
            attempts=RAND_ATTEMPTS,
            n_rattle=n_rattle,
            generate_pristine=False,
            print_result=True,
            check_covalent=CHECK_COVALENT,
        ),
        RattleGenerator(
            **environment.get_confinement(),
            n_rattle=int(n_rattle),
            rattle_amplitude=RATTLE_AMPLITUDE,
        ),
        AmorphPermutationGenerator(
            **environment.get_confinement(),
            max_number_of_swaps=MAX_SWAPS,
            rattle_strength=RATTLE_STRENGTH,
            use_xy_only=False,
            ignore_species=None,
            write_candidates_to_disk=False,
            replace=True,
            attempts=PERMUT_ATTEMPTS,
            check_overlap=CHECK_OVERLAP,
            min_distance_scale=0.85,
            max_distance_scale=1.15,
            print_result=False,
            write_struct=False,
        ),
    ]

    # === Generate & Save Dry-Run Candidate Structures ===
    try:
        # Generate Amorphous Candidate
        amorph_candidate = generators[0](sampler=None, environment=environment)[0]
        write(path_xsf / f"amorph_candidate_{seed}.xsf", amorph_candidate)
        print(f"-> Generated amorphous candidate {seed}")

        sampler_test = FixedSampler(amorph_candidate)

        # Generate Rattled Candidate
        rattle_candidate = generators[1](sampler_test, environment)[0]
        write(path_xsf / f"rattle_candidate_{seed}.xsf", rattle_candidate)
        print(f"-> Generated rattled candidate {seed}")

        # Generate Permuted Candidate
        permut_candidate = generators[2](sampler_test, environment)[0]
        write(path_xsf / f"permut_candidate_{seed}.xsf", permut_candidate)
        print(f"-> Generated permuted candidate {seed}")

        success_count += 1
    except Exception as e:
        print(f"-> Failed candidate generation for seed {seed}: {e}")
        fail_count += 1

    print(f"Seed generation status: Successes = {success_count}, Failures = {fail_count}")

    # === Database & Descriptor Setup ===
    database = Database(filename=db_dir / f"db_{seed}.db", order=5)
    descriptor = Fingerprint(environment=environment)

    # === Gaussian Process Regression Model ===
    k0 = C(BETA, (BETA, BETA)) * RBF()
    k1 = C(1 - BETA, (1 - BETA, 1 - BETA)) * RBF()
    kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))

    model = GPR(
        descriptor=descriptor,
        kernel=kernel,
        database=database,
        prior=Repulsive(),
    )

    # === AGOX Search Components ===
    sampler = KMeansSampler(
        descriptor=descriptor,
        database=database,
        sample_size=SAMPLE_SIZE,
    )

    collector = ParallelCollector(
        generators=generators,
        sampler=sampler,
        environment=environment,
        num_candidates=NUM_CANDIDATES,
        order=1,
    )

    acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=2, order=3)

    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        constraints=environment.get_constraints(),
        optimizer_run_kwargs={"steps": 100},
        start_relax=10,
        order=2,
    )

    # === GPAW Calculator & Evaluator Setup ===
    calc = SubprocessGPAW(
        ncores=N_CORES,
        mode=DFT_MODE,
        basis=DFT_BASIS,
        xc=DFT_XC,
        kpts=KPTS,
        symmetry=DFT_SYMMETRY,
        nbands=DFT_NBANDS,
        mixer=DFT_MIXER,
        convergence=DFT_CONVERGENCE,
        occupations=DFT_OCCUPATIONS,
        maxiter=DFT_MAX_ITERATIONS,
        txt="output.txt",
    )

    evaluator = LocalOptimizationEvaluator(
        calc,
        gets={"get_key": "prioritized_candidates"},
        optimizer_kwargs={"logfile": None},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
        constraints=environment.get_constraints(),
        order=4,
    )

    # === Run AGOX Optimizer ===
    agox = AGOX(
        collector,
        relaxer,
        acquisitor,
        evaluator,
        database,
        seed=seed,
    )

    # To execute search iterations, uncomment the line below:
    agox.run(N_iterations=N_ITERATIONS)

