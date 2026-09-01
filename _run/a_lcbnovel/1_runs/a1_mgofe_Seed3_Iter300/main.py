"""
AGOX Workflow: Novelty-LCB search of Fe deposition on MgO(001).

Faithful repair of _run/7_lcbnovel_mgofe/main.py for project a_lcbnovel.

- Constructs a matched Fe/MgO hetero-interface (Fe slab deposited on an MgO
  (001) substrate, MgO substrate atoms FIXED, only Fe atoms mobile).
- Wires the canonical AGOX stack: ParallelCollector -> ParallelRelaxPostprocess
  (on the acquisition calculator) -> NoveltyLCBAcquisitor -> LocalOptimizationEvaluator
  (GPAW via SubprocessGPAW) -> Database.
- Uses the FIXED novelty_lcb package (module-level free functions + functools.partial
  in get_acquisition_calculator) so the acquisition calculator pickles cleanly
  across the Ray pool (run-7 crash: "cannot pickle 'sqlite3.Connection'").

Run one seed or a range. Designed for HPC PJM array launch (one seed per job)
so the search can be scaled out across many independent runs.

Usage:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py --seed 3 \
        --n-iterations 100 --kappa 3.0 --novelty-weight 2.0 --out-root ./output
    # or a range:
    ... --seed-start 3 --seed-end 105
"""



__version__ = "1.2.0"

import argparse
import os

import numpy as np
from ase import Atoms  # noqa: F401  (imported for interface parity with run 7)
from ase.build import surface, bulk
from agox.environments import Environment
from agox.generators import RattleGenerator
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.samplers import KMeansSampler
from agox.collectors import ParallelCollector
from agox.postprocessors import ParallelRelaxPostprocess
from agox.helpers import SubprocessGPAW
from agox.evaluators import LocalOptimizationEvaluator
from agox import AGOX

from novelty_lcb import NoveltyLCBAcquisitor

from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.hetero_struct_randomize import HeteroStructRandomize
from scripts.build_heteroStruct import build_heteroStruct
from scripts.add_adsorbate_to_hollows import add_adsorbate_to_hollows
from scripts.global_permutation_generator import GlobalPermutationGenerator


# ==== Physical parameters (match run 7) ====
VACUUM = 20                 # vacuum spacing (Angstrom)
A_MGO = 4.212               # MgO bulk lattice constant (Angstrom)
A_FE = 2.870190             # Fe optimized lcao lattice constant (Angstrom)
DIST_Z_FE2O = 0.5           # interface spacing (Angstrom)
SUPERCELL = (5, 5, 1)
KPTS = (1, 1, 1)
N_ITERATIONS = 100

MGO_LAYER_NUMBER = 1        # substrate slab layers
FE_LAYER_NUMBER = 1         # deposition slab layers
CONFINEMENT_CELL_HEIGHT_MULTIPLYER = 4

# ==== Generators ====
NUM_CANDIDATES = {0: [20, 0], 10: [10, 10], 25: [0, 20]}
SAMPLE_SIZE = 20
RATTLE_AMPLITUDE = 2.3
HETERO_RATTLE_AMPLITUDE = 1.5

# ==== Boron doping (from 66_MgOFe_20B) ====
# When NUM_ATOMS_ADD > 0, B atoms are added into the Fe deposition layer via
# add_adsorbate_to_hollows (B placed in hollows between 4 Fe atoms) and a
# GlobalPermutationGenerator (Fe<->B swaps) is added as a 3rd generator.
# Default 0 = no B (root and existing runs keep the pure Fe/MgO behavior).
NUM_ATOMS_ADD = 0             # number of B dopant atoms in the Fe deposition layer
SYMBOL_ADD = "B"              # dopant species
Z_HEIGHT_ADD = 0              # adsorption height offset from the surface plane
# 3-generator candidate schedule used when B is enabled (Randomize/Rattle/Permute)
NUM_CANDIDATES_B = {0: [20, 0, 0], 10: [10, 5, 5], 25: [0, 10, 10]}

# ==== Model ====
BK = 0.01

# ==== Novelty-LCB energy window (AUTO global-minimum mode) ====
# The window is anchored to the LIVE global minimum found in the database and
# searches a fixed amount ABOVE it: candidates with predicted E > E_min + X are
# excluded; E < E_min is allowed so a new, lower global minimum can be found.
# This removes the need to run a regular-LCB search first to calibrate the window.
#   window = (-inf, E_min + X]   (X = NOVELTY_ENERGY_ABOVE_MIN)
# With NOVELTY_ENERGY_PER_ATOM=True (default), X is in eV/atom: the window is
# (E_min/N) + X per atom, i.e. 1-2 eV/atom is a sensible, size-independent choice.
# With per_atom=False, X is in total eV (e.g. 5-10 eV for this 75-atom system).
# Set energy_above_min to None to fall back to the centered target_energy±delta_E mode.
NOVELTY_ENERGY_ABOVE_MIN = 1.0   # eV/atom (per-atom mode default) -- window height above the live global min
# Per-atom mode: when True, NOVELTY_ENERGY_ABOVE_MIN is interpreted in eV/atom
# (both predicted E and E_min divided by the atom count N). Makes choosing the
# window size easier (e.g. 0.5-2 eV/atom). Requires a fixed composition / atom count.
NOVELTY_ENERGY_PER_ATOM = True   # interpret NOVELTY_ENERGY_ABOVE_MIN as eV per atom
NOVELTY_WEIGHT = 1.5             # lambda in a(x) = sigma + lambda*Novelty
KAPPA = 2.0                      # LCB kappa (surrogate relaxation surface)

# ==== GPAW / SubprocessGPAW ====
NCORES = 64
GPAW_KWARGS = dict(
    ncores=NCORES,
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    kpts=KPTS,
    symmetry="off",
    nbands="nao",
    maxiter=100,
    occupations={"name": "fermi-dirac", "width": 0.05},
    hund=True,
    spinpol=True,
)


def build_slabs():
    """Lattice-match and build the MgO substrate and Fe deposition slabs."""
    a_mgo_matched = A_MGO / np.sqrt(2)
    strain = (a_mgo_matched - A_FE) / A_FE * 100

    bulk_mgo = bulk("MgO", "rocksalt", a=A_MGO, cubic=True)
    slab_fe_base = surface("Fe", (0, 0, 1), layers=1, vacuum=VACUUM)

    # MgO substrate (matching build_mgo_stack recipe)
    slab_mgofe = build_mgo_stack(
        slab_fe_base, num_layers=MGO_LAYER_NUMBER, vacuum=VACUUM
    )
    slab_substrate = slab_mgofe[[a.symbol != "Fe" for a in slab_mgofe]].repeat(SUPERCELL)

    # Fe deposition
    slab_deposition = build_fe_stack(
        slab_fe_base, num_layers=FE_LAYER_NUMBER, vacuum=VACUUM
    ).repeat(SUPERCELL)

    return slab_substrate, slab_deposition, strain


def build_environment(slab_substrate, slab_deposition):
    """Set periodicity + confinement for the mobile (Fe) layer."""
    slab_substrate.pbc = [True, True, False]
    confinement_corner = np.array(
        [0, 0, slab_substrate.positions[:, 2].max() + DIST_Z_FE2O]
    )
    z_pos = slab_deposition.get_positions()[:, 2]
    h_dep = max(z_pos.max() - z_pos.min(), 2.1)
    confinement_cell = slab_deposition.cell.copy()
    confinement_cell[2, 2] = h_dep * CONFINEMENT_CELL_HEIGHT_MULTIPLYER

    return Environment(
        template=slab_substrate,
        symbols=slab_deposition.get_chemical_formula(),
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],
    )


def build_stack(environment, slab_deposition, db_path, seed, kappa=KAPPA,
                novelty_weight=NOVELTY_WEIGHT):
    """Construct the full, wired AGOX stack for one seed."""
    # Generators
    n_rattle = len(slab_deposition)
    generators = [
        HeteroStructRandomize(
            **environment.get_confinement(),
            slab_deposition=slab_deposition,
            hetero_slab_dist=DIST_Z_FE2O,
            rattle_amplitude=HETERO_RATTLE_AMPLITUDE,
            n_rattle=n_rattle,
            generate_pristine=False,
            write_struct=True,
        ),
        RattleGenerator(
            **environment.get_confinement(),
            n_rattle=int(n_rattle * 0.5),
            rattle_amplitude=RATTLE_AMPLITUDE,
        ),
    ]
    # When B doping is enabled, add the Fe<->B permutation generator (66_MgOFe_20B).
    if NUM_ATOMS_ADD > 0:
        generators.append(
            GlobalPermutationGenerator(
                **environment.get_confinement(),
                max_number_of_swaps=NUM_ATOMS_ADD,
                rattle_strength=0.5,
            )
        )
        num_candidates = NUM_CANDIDATES_B
    else:
        num_candidates = NUM_CANDIDATES

    # Database + descriptor + model
    database = Database(filename=db_path, order=5)
    descriptor = Fingerprint(environment=environment)
    kernel = C(5000, (1, 1e5)) * (
        C(BK, (BK, BK)) * RBF() + C(1 - BK, (1 - BK, 1 - BK)) * RBF()
    ) + Noise(0.01, (0.01, 0.01))
    model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

    # Sampler + collector
    sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=SAMPLE_SIZE)
    collector = ParallelCollector(
        generators=generators, sampler=sampler, environment=environment,
        num_candidates=num_candidates, order=1,
    )

    # Acquisitor -- Novelty-LCB (FIXED package: serialization-safe calculator)
    # Auto global-minimum mode: target is the live DB minimum; searches
    # NOVELTY_ENERGY_ABOVE_MIN (eV or eV/atom if NOVELTY_ENERGY_PER_ATOM) above it.
    # No manual calibration needed.
    acquisitor = NoveltyLCBAcquisitor(
        model=model,
        descriptor=descriptor,
        database=database,
        energy_above_min=NOVELTY_ENERGY_ABOVE_MIN,
        per_atom=NOVELTY_ENERGY_PER_ATOM,
        novelty_weight=novelty_weight,
        kappa=kappa,
        order=3,
    )

    # Relaxer -- runs on the acquisition calculator (LCB surface), NOT GPAW.
    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        constraints=environment.get_constraints(),
        optimizer_run_kwargs={"steps": 100},
        start_relax=10,
        order=2,
    )

    # Evaluator -- the real GPAW calculator.
    calc = SubprocessGPAW(**GPAW_KWARGS, txt=f"output_seed_{seed}.txt")
    evaluator = LocalOptimizationEvaluator(
        calc,
        gets={"get_key": "prioritized_candidates"},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
        constraints=environment.get_constraints(),
        store_trajectory=False,
        order=4,
    )

    agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
    return agox, environment


def main():
    ap = argparse.ArgumentParser(description="Novelty-LCB Fe/MgO AGOX search")
    ap.add_argument("--seed", type=int, default=None,
                    help="Single seed. Overrides --seed-start/--seed-end.")
    ap.add_argument("--seed-start", type=int, default=3)
    ap.add_argument("--seed-end", type=int, default=104,
                    help="Inclusive upper bound of seed range.")
    ap.add_argument("--n-iterations", type=int, default=N_ITERATIONS)
    ap.add_argument("--kappa", type=float, default=KAPPA,
                    help="LCB kappa for the surrogate relaxation surface (default KAPPA=2.0).")
    ap.add_argument("--novelty-weight", type=float, default=NOVELTY_WEIGHT,
                    help="Novelty weight lambda in a(x)=sigma+lambda*Novelty (default NOVELTY_WEIGHT=1.5).")
    ap.add_argument("--out-root", type=str, default="./output",
                    help="Root dir; per-seed subdirs out_root/seed_<N>/{0_result,1_db}.")
    args = ap.parse_args()

    if args.seed is not None:
        seeds = [args.seed]
    else:
        seeds = list(range(args.seed_start, args.seed_end + 1))

    os.makedirs(args.out_root, exist_ok=True)

    # Build slabs once (identical for every seed).
    slab_substrate, slab_deposition, strain = build_slabs()
    print(f"Lattice match: a_MgO_matched={A_MGO/np.sqrt(2):.4f}  "
          f"strain vs Fe = {strain:.2f}%")

    for seed in seeds:
        print(f"\n--- Starting AGOX Run with Seed: {seed} ---")
        path_result = f"{args.out_root}/seed_{seed}/0_result"
        path_xsf = f"{path_result}/0_xsf"
        db_dir = f"{args.out_root}/seed_{seed}/1_db"
        for d in [path_xsf, db_dir]:
            os.makedirs(d, exist_ok=True)

        # Per-seed deposition copy; if B doping is enabled, add B into the Fe layer.
        dep = slab_deposition.copy()
        if NUM_ATOMS_ADD > 0:
            dep = add_adsorbate_to_hollows(
                dep, symbol=SYMBOL_ADD, height=Z_HEIGHT_ADD,
                num_atoms=NUM_ATOMS_ADD, seed=seed,
            )
            print(f"  Doped deposition layer with {NUM_ATOMS_ADD} {SYMBOL_ADD} "
                  f"atoms -> formula {dep.get_chemical_formula()}")

        env = build_environment(slab_substrate.copy(), dep)
        agox, _ = build_stack(env, dep, f"{db_dir}/db_{seed}.db", seed,
                              kappa=args.kappa, novelty_weight=args.novelty_weight)
        agox.run(N_iterations=args.n_iterations)


if __name__ == "__main__":
    main()
