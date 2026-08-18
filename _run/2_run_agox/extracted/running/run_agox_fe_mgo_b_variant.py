"""
Extracted from main_test.ipynb (cell 36).
Section: Trash: B-doped Fe/MgO variant
"""
import sys
import os
# Make the repo-local `scripts/` package importable regardless of cwd:
# walk up from this file until we find the directory containing `scripts/`.
_HERE = os.path.dirname(os.path.abspath(__file__))
_d = _HERE
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, 'scripts')):
        if _d not in sys.path:
            sys.path.insert(0, _d)
        break
    _d = os.path.dirname(_d)


import os
import re
import numpy as np
from ase import Atoms
from ase.build import bulk, surface
from ase.constraints import FixAtoms
from ase.io import read, write

from agox import AGOX
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.collectors import ParallelCollector, StandardCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.helpers import SubprocessGPAW
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess, RelaxPostprocess
from agox.samplers import FixedSampler, KMeansSampler

# Custom project scripts for stacking, structural modification, and plotting
from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows
from scripts.build_fe_stack import build_fe_stack
from scripts.build_heteroStruct import build_heteroStruct
from scripts.build_mgo_stack import build_mgo_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.plot_structure import plot_structure
from scripts.remove_random_atoms_by_species import remove_random_atoms_by_species


# =====================================================================
# 1. Global Simulation & Lattice Parameter Tuning
# =====================================================================
vacuum = 20
a_mgo = 4.212
a_fe = 2.870190                     # Fe optimized LCAO lattice constant (Å)
a_mgo_matched = a_mgo / np.sqrt(2)  # Coherent interfacial matching scaling factor
strain = (a_mgo_matched - a_fe) / a_fe * 100

dist_z_fe2o = 0.5                   # Experimental initial Fe-O vertical separation (Å)
ncores = 24                         # Parallel CPU core count allocation
supercell = (5, 5, 1)               # Lateral simulation slab repetition dimensions
kpts = (1, 1, 1)                    # Gamma-point Brillouin zone sampling

# =====================================================================
# 2. AGOX Active Learning Parameters
# =====================================================================
kappa = 2                           # Exploration/Exploitation balance parameter (LCB Acquisition)
N_iterations = 100                  # Maximum active learning iterations per run
sample_size = 20                    # Representative clustering pool size

mgo_layer_number = 1                # Total thickness of bottom MgO support (monolayers)
fe_layer_number = 1                 # Total thickness of top Fe film (monolayers)
confinement_cell_height_multiplyer = 4  # Scale height of non-periodic search domain

# Interpolate structural strain: 0.0 = Pure Fe, 1.0 = Fully coherent with MgO
interpolation_factor = 0
a_custom = a_fe + interpolation_factor * (a_mgo_matched - a_fe)

# Multi-stage candidate generator allocation mapping iteration steps
num_candidates = {
    0: [20, 0],   # Gen 1 (structural randomize) active, Gen 2 (rattle) inactive
    10: [10, 10],  # Mixed generation mode
    25: [0, 20]   # Solely apply rattle searches to near-equilibrium hulls
}

# =====================================================================
# 3. Alloy & Adsorbate Composition Modification
# =====================================================================
removed_num = 0       # Number of Fe atoms randomly pruned to simulate coverage/defects
symbol_add = 'B'      # Dopant/adsorbate atomic species
z_height_add = 0      # Vertical coordinate height offset relative to the base layer
num_atoms_add = 2     # Number of dopant/adsorbate atoms to insert into hollow sites

# =====================================================================
# 4. Multi-Seed Loop & Infrastructure Initialization
# =====================================================================
for seed in range(103):
    print(f"\n==================================================")
    print(f"Executing Global Optimization Sequence | Seed: {seed}")
    print(f"==================================================")
    
    # Path infrastructure mapping directory outputs
    path_result = f"seed_{seed}/0_result"
    path_xsf = f"{path_result}/0_xsf"
    path_fig = f"{path_result}/1_fig"
    db_dir = f"seed_{seed}/1_db"
    latt_log = f'{path_result}/latt_log.md'

    for d in [path_xsf, path_fig, db_dir]:
        os.makedirs(d, exist_ok=True)
        
    with open(latt_log, 'w') as f:
        f.write(f"{a_fe=}\n{a_mgo=}\n{a_mgo_matched=}\n{strain=:.2f}%\n")
        
    # --- Base Substrate Layer Definition ---
    bulk_mgo = bulk('MgO', 'rocksalt', a=a_mgo, cubic=True)
    slab_mgo = surface(bulk_mgo, (0, 0, 1), layers=1, vacuum=vacuum)

    # Compute step profile height distances within MgO layers
    z_positions = slab_mgo.get_positions()[:, 2]
    unique_z = np.unique(np.round(z_positions, 5))
    
    if len(unique_z) >= 2:
        unique_z.sort()
        dist_mgo = unique_z[1] - unique_z[0]
    else:
        dist_mgo = 2.106  # Empirical fallback default spacing
    
    # --- Thin Film and Heterostructure Assembly ---
    fe_bulk = bulk('Fe', 'bcc', a=a_custom, cubic=True)
    slab_fe_base = surface(fe_bulk, (0, 0, 1), layers=1, vacuum=vacuum)
    
    # Stack configurations
    slab_mgofe = build_mgo_stack(
        slab_fe_base, num_layers=mgo_layer_number, dist_mgo=dist_mgo, 
        vacuum=vacuum, output_path=f"{path_xsf}/slab_mgofe.xsf", rotate_system=False
    )
    slab_mgo = slab_mgofe[[atom.symbol != 'Fe' for atom in slab_mgofe]].repeat(supercell)
    slab_fe = build_fe_stack(
        slab_fe_base, num_layers=fe_layer_number, vacuum=vacuum, 
        output_path=f"{path_xsf}/slab_fe.xsf"
    ).repeat(supercell)
    
    slab_deposition = slab_fe.copy() 
    slab_substrate = slab_mgo.copy()
    
    # Apply chemical concentration modifications (atom removal)
    slab_deposition = remove_random_atoms_by_species(slab_deposition, 'Fe', removed_num)

    # Place and insert dopant species (e.g. Boron) into structural hollows
    slab_deposition = add_adsorbate_to_hollows(
        slab_deposition, symbol=symbol_add, height=z_height_add, 
        num_atoms=num_atoms_add, seed=seed
    )

    # Build the target interface and verify structure configurations
    test_hetero, _, _, _, _ = build_heteroStruct(
        slab_substrate, slab_deposition, output_path=f'{path_xsf}/heteroStruct.xsf'
    )

    # =====================================================================
    # 5. AGOX Search Environment Setup
    # =====================================================================
    slab_substrate.pbc = [True, True, False]
    confinement_corner = np.array([0, 0, slab_substrate.positions[:, 2].max() + dist_z_fe2o])
    
    # Build search box confinement constraints for structural modification
    z_pos = slab_deposition.get_positions()[:, 2]
    h_dep = max(z_pos.max() - z_pos.min(), 2.1)
    confinement_cell = slab_deposition.cell.copy()
    confinement_cell[2, 2] = h_dep * confinement_cell_height_multiplyer

    environment = Environment(
        template=slab_substrate,
        symbols=slab_deposition.get_chemical_formula(),
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False]
    )
    
    # =====================================================================
    # 6. Candidate Generators Setup
    # =====================================================================
    n_rattle = len(slab_deposition)
    generators = [
        # Generator 0: Large-scale structural randomization
        HeteroStructRandomize(
            **environment.get_confinement(),
            slab_deposition=slab_deposition,
            hetero_slab_dist=dist_z_fe2o,
            rattle_amplitude=1.5,
            n_rattle=n_rattle,
            generate_pristine=False,
            write_struct=True,
        ),
        # Generator 1: Small-scale structural perturbation
        RattleGenerator(
            **environment.get_confinement(),
            n_rattle=int(n_rattle * 0.5),
            rattle_amplitude=2.3
        ),
    ]
    
    # Write initial validation/test structures to disk
    hetero_candidate = generators[0](sampler=None, environment=environment)[0]
    write(f'{path_xsf}/hetero_candidate.xsf', hetero_candidate)
    
    sampler_fixed = FixedSampler(hetero_candidate)
    rattle_candidate = generators[1](sampler_fixed, environment)[0]
    write(f'{path_xsf}/rattle_candidate.xsf', rattle_candidate)
    
    # =====================================================================
    # 7. Machine Learning & Model Pipeline (GPR + Fingerprint)
    # =====================================================================
    database = Database(filename=f"{db_dir}/db_{seed}.db", order=5)
    descriptor = Fingerprint(environment=environment)
    
    # Compound Gaussian Process Regression kernel definition
    beta = 0.01
    kernel = C(5000, (1, 1e5)) * (
        C(beta, (beta, beta)) * RBF() + C(1 - beta, (1 - beta, 1 - beta)) * RBF()
    ) + Noise(0.01, (0.01, 0.01))
    
    model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())
    
    # Sampler and Collector operations (parallelized configuration tracking)
    sampler_kmeans = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)
    collector = ParallelCollector(
        generators=generators,
        sampler=sampler_kmeans,
        environment=environment,
        num_candidates=num_candidates,
        order=1
    )
    
    # =====================================================================
    # 8. Optimization & Quantum Mechanical Evaluators (GPAW)
    # =====================================================================
    acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=kappa, order=3)
    
    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        constraints=environment.get_constraints(),
        optimizer_run_kwargs={"steps": 100},
        start_relax=10,
        order=2
    )
    
    # DFT Calculator backend settings
    calc = SubprocessGPAW(
        ncores=ncores,
        mode={"name": "lcao"},
        basis="dzp",
        xc="PBE",
        mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
        convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
        txt=f"output_seed_{seed}.txt",
        kpts=kpts,
        symmetry='off',
        nbands='nao',
        maxiter=100,
        occupations={"name": "fermi-dirac", "width": 0.05},
        hund=True,
        spinpol=True
    )
    
    evaluator = LocalOptimizationEvaluator(
        calc,
        gets={"get_key": "prioritized_candidates"},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
        constraints=environment.get_constraints(),
        store_trajectory=False,
        order=4
    )
    
    # =====================================================================
    # 9. AGOX Active Learning Execution
    # =====================================================================
    agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
    # agox.run(N_iterations=N_iterations)  # Uncomment to execute optimization loop
