"""
Fe-Co/MgO — one monolayer of FeCo on MgO(001), boron-free.

New run (`data/cofe_v2/fecomgo`).  The Fe-Co host was archived out of the paper in CLAIMS v9
because it could not serve as a controlled counterpart of the Fe host; this directory rebuilds it
on the Fe host's strain convention so that it can, as the "separate study" described in
`_archive/cofe/README.md` -> "Reviving the host".

Provenance
  Copied from `data/_archive/fecomgo/main.py`, which produced the archived MT-4/MT-5 values.
  Everything is unchanged except the two items below, so the new run differs from the archived one
  only where intended.

CHANGED vs the archived script
  1. `interpolation_factor` 1 -> 0, so the cell is built on the film lattice.  The archived run sat
     on a_MgO/sqrt(2) = 2.97833 A (substrate at bulk, film stretched 4.9 %); that strain-convention
     mismatch, not the physics, is why the host was dropped.
     >>> NOTE: `a_feco` and the Fe-B + permutation run (`data/febmgo_v2/main.py`) are BOTH 2.870190 A,
     >>> and 2.870190 is also what the in-scope Fe host uses (`data/febmgo/main.py`), so all four
     >>> models (femgo, febmgo, fecomgo, fecobmgo) now sit on one cell: 5x5 = 14.351 A in-plane.
  2. `a_feco` 2.839177 -> 2.870190 A, so the Co host shares the Fe host's cell instead of sitting
     1.09 % away from it.  Without this the two hosts would differ in lattice parameter as well as
     in composition/boron.
  3. `latt_log.md` now records the cell that is actually built (`a_custom`) and the strain applied
     to it, instead of the strain of a_MgO/sqrt(2), which no longer describes this run.

UNCHANGED, deliberately (so any Co-vs-Fe difference is the host, not the method)
  - three generators, including the PermutationGenerator, with the schedule
      num_candidates = {0: [20, 0, 0], 10: [10, 5, 5], 25: [0, 10, 10]}
  - GPAW LCAO / dzp / PBE, mixer weight 50, convergence energy 1e-3, occupations width 0.10
  - ncores = 24, kappa = 2, N_iterations = 100, n_co = 7, supercell (5, 5, 1), kpts (1, 1, 1)
  - seed loop over range(103)
  - converged-search rule: a seed counts only if it reaches the full 100-iteration budget
    (`scripts/run_selection.py`, FULL_ITERATIONS = 100)
"""

import os
import numpy as np

from agox import AGOX
from agox.environments import Environment
from agox.generators import RattleGenerator, PermutationGenerator
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
from agox.samplers import FixedSampler

from ase import Atoms
from ase.constraints import FixAtoms
from ase.build import surface, bulk
from ase.io import read, write

from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.plot_structure import plot_structure
from scripts.build_heteroStruct import build_heteroStruct
from scripts.remove_random_atoms_by_species import remove_random_atoms_by_species

from scripts.feco_randamize_generater import feco_randamize_generater
# from icecream import ic

vacuum = 20
a_mgo = 4.212
a_feco = 2.870190   # aligned with the Fe host (data/febmgo/main.py); see NOTE above
n_co = 7

a_mgo_matched = a_mgo / np.sqrt(2)
strain_mgomatch = (a_mgo_matched - a_feco) / a_feco * 100

"""
Control Strain
0.0 = film lattice
1.0 = film stretched to fit MgO

CHANGED (was 1): 0 puts the cell on the film, as in the Fe host, so boron and the strain
convention do not vary together.  Simul: 0, 0.25, 0.5, 0.75, 1
"""

interpolation_factor = 0
a_custom = a_feco + interpolation_factor * (a_mgo_matched - a_feco)
cell_strain = (a_custom - a_feco) / a_feco * 100   # the strain this run actually applies

dist_z_fe2o = 0.5 # experimental: 2.3 A
ncores = 64 #24; 16 cosres for genkai
supercell = (5 , 5, 1)
kpts = (1, 1, 1)

kappa=2
N_iterations = 100

mgo_layer_number = 1
fe_layer_number = 1
confinement_cell_height_multiplyer = 4 # multiply env cell height

"""
Concenstration controls. 
Removing atoms.cond
5x5 1 monolayer is 25 atoms (Fe layer). Remove 25 remove one monolayer.
"""
removed_num = 0 

num_candidates={0:[20,0,0], 10:[10,5,5], 25:[0,10,10]}
sample_size = 20

"""
Co decoration of the 1 ML film.  `feco_randamize_generater` defaults to seed=0, so the Fe/Co
pattern is FIXED and identical in every seed — the replicate-to-replicate variation comes from the
search and from the B placement, not from the Co arrangement.  That is what makes the FeCo and
FeCoB models comparable.  Pass seed=co_decoration_seed as `seed=seed` to vary it per replicate.
"""
co_decoration_seed = 0

success_count = 0
fail_count = 0

for seed in range(103):
	print(F"Start seed: {seed}")
	
	path_result = f"seed_{seed}/0_result"
	path_xsf = f"{path_result}/0_xsf"
	path_fig = f"{path_result}/1_fig"
	db_dir = f"seed_{seed}/1_db"
	latt_log = f'{path_result}/latt_log.md'
	
	for d in [path_xsf, path_fig, db_dir]:
		os.makedirs(d, exist_ok=True)
		
	with open(latt_log, 'w') as f:
		f.write(f"{a_feco=}\n{a_mgo=}\n{a_mgo_matched=}\n{strain_mgomatch=:.2f}%\n")
		f.write(f"{interpolation_factor=}\n{a_custom=}\n{cell_strain=:.2f}%\n")
		
	bulk_mgo = bulk('MgO', 'rocksalt', a=a_mgo, cubic=True)
	slab_mgo = surface(bulk_mgo, (0,0,1), layers=1, vacuum=vacuum)
	
	"""
	Calculating distance between MgO layer (Top Mg and bottom O).
	"""
	z_positions = slab_mgo.get_positions()[:, 2]
	unique_z = np.unique(np.round(z_positions, 5))
	
	if len(unique_z) >= 2:
		unique_z.sort()
		dist_mgo = unique_z[1] - unique_z[0]
	
	"""
	Building MgO/FeCo(001). Started by making the FeCo base (constraint lattice), then put O and Mg on top of it. 

	Make MgO(001). We can remove the FeCo base.
	Make FeCo(001). We multiple the FeCo base.

	"""
	
	#fe_bulk = bulk('Fe', 'bcc', a=a_custom, cubic=True)
	feco = Atoms('FeCo',scaled_positions=[[0.5, 0.5, 0.5], [0, 0, 0]],cell=[a_custom, a_custom, a_custom],pbc=True)
	slab_feco_base = surface(feco, (0, 0, 1), layers=1, vacuum=vacuum)


	slab_mgofe = build_mgo_stack(slab_feco_base, num_layers=mgo_layer_number, dist_mgo=dist_mgo, vacuum=vacuum, output_path=f"{path_xsf}/slab_mgofe.xsf")
	slab_mgo = slab_mgofe[[atom.symbol not in ['Fe', 'Co'] for atom in slab_mgofe]].repeat(supercell)
	#slab_feco = build_fe_stack(slab_feco_base, num_layers=fe_layer_number, vacuum=vacuum, output_path=f"{path_xsf}/slab_fe.xsf").repeat(supercell)
	slab_feco = feco_randamize_generater(
	    slab_feco_base,
	    n_co,
	    supercell=(5,5,1),
	    seed=co_decoration_seed
	)

	slab_deposition = slab_feco.copy()
	slab_substrate = slab_mgo.copy()
	
	# Consentrations controls
	slab_deposition = remove_random_atoms_by_species(slab_deposition, 'Fe', removed_num)
	
	slab_heteroStruct, slab_substrate, slab_deposition, substrate_layer_heights, deposition_layer_heights = build_heteroStruct(slab_substrate, slab_deposition, output_path=f'{path_xsf}/heteroStruct.xsf')
	write('slab_heterostructure.xsf',slab_heteroStruct)

	slab_substrate.pbc = [True, True, False]
	confinement_corner = np.array([0, 0, slab_substrate.positions[:, 2].max() + dist_z_fe2o])
	
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
	
	n_rattle = len(slab_deposition)
	generators = [
		HeteroStructRandomize(
			**environment.get_confinement(),
			slab_deposition=slab_deposition,
			hetero_slab_dist=dist_z_fe2o,
			rattle_amplitude=1.5,
			n_rattle=n_rattle,
			generate_pristine=False,
			write_struct=True,
		),
		RattleGenerator(
			**environment.get_confinement(),
			n_rattle=int(n_rattle * 0.5),
			rattle_amplitude=2.3
		),
		PermutationGenerator(
            **environment.get_confinement(),
            max_number_of_swaps=n_rattle,
            rattle_strength=0.3,
            use_xy_only=False,
            ignore_H=False,
            write_candidates_to_disk=False,
            replace=True,
        )
	]
	
	# hetero_candidate = generators[0](sampler=None, environment=environment)[0]
	# write(f'{path_xsf}/hetero_candidate.xsf', hetero_candidate)
	
	# sampler = FixedSampler(hetero_candidate)
	# rattle_candidate = generators[1](sampler, environment)[0]
	# write(f'{path_xsf}/rattle_candidate.xsf', rattle_candidate)
	
	# test generate structure
	try:
		Hetero_candidate = generators[0](
			sampler=None,
			environment=environment
		)[0]
		write(f"{path_xsf}/Hetero_candidate_{seed}.xsf", Hetero_candidate)
		print(f"bragg {seed}")

		sampler_test = FixedSampler(Hetero_candidate)

		rattle_candidate = generators[1](
			sampler_test,
			environment
		)[0]
		write(f"{path_xsf}/rattle_candidate_{seed}.xsf", rattle_candidate)
		print(f"rattle {seed}")

		permut_candidate = generators[2](
			sampler_test,
			environment
		)[0]
		write(f"{path_xsf}/permut_candidate_{seed}.xsf", permut_candidate)
		print(f"permut {seed}")

		success_count += 1

	except Exception as e:
		fail_count += 1
		print(f"Generator test failed at seed {seed}: {e}")

	database = Database(filename=f"{db_dir}/db_{seed}.db", order=5)
	descriptor = Fingerprint(environment=environment)
	
	beta = 0.01
	kernel = C(5000, (1, 1e5)) * (C(beta, (beta, beta)) * RBF() + C(1-beta, (1-beta, 1-beta)) * RBF()) + Noise(0.01, (0.01, 0.01))
	model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())
	
	sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)
	collector = ParallelCollector(
		generators=generators,
		sampler=sampler,
		environment=environment,
		num_candidates=num_candidates,
		order=1
	)
	
	acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=kappa, order=3)
	
	relaxer = ParallelRelaxPostprocess(
		model=acquisitor.get_acquisition_calculator(),
		constraints=environment.get_constraints(),
		optimizer_run_kwargs={"steps": 100},
		start_relax=10,
		order=2
	)
	
	calc = SubprocessGPAW(
		ncores=ncores,
		mode={"name": "lcao"},
		basis="dzp",
		xc="PBE",
		mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 50},
		convergence={"energy": 1e-3, "density": 1e-3, "eigenstates": 1e-3},
		txt=f"output_seed_{seed}.txt",
		kpts=kpts,
		symmetry='off',
		nbands='nao',
		maxiter=100,
		occupations={"name": "fermi-dirac", "width": 0.10},
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
	
	agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
	agox.run(N_iterations=N_iterations)
