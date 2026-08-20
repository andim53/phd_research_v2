#!/usr/bin/env python3
"""
AGOX structure-search run script for Ni8 / Au(4,4,2) fcc100 surface.
Runs BOTH acquisition strategies side by side:

  1. Standard LowerConfidenceBoundAcquisitor (kappa=2)
  2. Novelty-LCB acquisitor (novelty_lcb package)

Both use the identical system setup, generators, sampler, and evaluator.
The only difference is the acquisitor — everything else is shared.

Novelty-LCB acquisition (to MAXIMIZE):
    a(x) = sigma(x) + lambda * Novelty(x)
    Novelty(x) = min_{i in DB} ||fingerprint(x) - fingerprint(x_i)||_2
    subject to:  E_target - delta_E <= mu(x) <= E_target + delta_E

Run:
    /home/miniconda3/envs/agox_v2/bin/python run.py
"""

import matplotlib

matplotlib.use("Agg")

import os
import sys
import numpy as np

# ── AGOX ─────────────────────────────────────────────────────────────────────
from ase.build import fcc100
from ase.calculators.emt import EMT

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

# Local copy of novelty_lcb (in working dir)
from novelty_lcb import NoveltyLCBAcquisitor

##############################################################################
# System parameters (shared by both runs)
##############################################################################

SEED = 41
SYMBOLS = "Ni8"
TEMPLATE_SIZE = (4, 4, 2)
VACUUM = 5.0
CONFINEMENT_Z = 4.0
SAMPLE_SIZE = 10
KAPPA = 2.0                    # for standard LCB
NOVELTY_TARGET_ENERGY = 0.0    # eV — TODO: calibrate for this system
NOVELTY_DELTA_E = 0.5          # eV — half-width of energy window
NOVELTY_WEIGHT = 1.0           # lambda
N_ITERATIONS = 10
NUM_CANDIDATES = {0: [10, 0], 5: [3, 7]}
RELAX_STEPS = 5
START_RELAX = 8
OPT_FMAX = 0.05
OPT_STEPS = 1

##############################################################################
# Build the shared parts of the AGOX stack
# (everything except the acquisitor — that's the variable)
##############################################################################

def build_system():
    """Return (environment, descriptor, model, sampler, generators,
    collector, relaxer_kwargs, evaluator_kwargs, calc)."""
    # Template surface
    template = fcc100("Au", size=TEMPLATE_SIZE, vacuum=VACUUM)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    # Confinement
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = CONFINEMENT_Z
    z0 = template.positions[:, 2].max()
    confinement_corner = np.array([0, 0, z0])

    environment = Environment(
        template=template,
        symbols=SYMBOLS,
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],
    )

    # Calculator
    calc = EMT()

    # Descriptor + model
    descriptor = Fingerprint(environment=environment)
    beta = 0.01
    k0 = C(beta, (beta, beta)) * RBF()
    k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
    kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))
    model = GPR(descriptor=descriptor, kernel=kernel,
                database=None, prior=Repulsive())  # database set later per-run

    # Sampler
    sampler = KMeansSampler(descriptor=descriptor, database=None,
                            sample_size=SAMPLE_SIZE)  # database set later

    # Generators
    rattle_generator = RattleGenerator(**environment.get_confinement())
    random_generator = RandomGenerator(**environment.get_confinement(),
                                       contiguous=False)
    generators = [random_generator, rattle_generator]

    # Collector
    collector = ParallelCollector(
        generators=generators,
        sampler=sampler,
        environment=environment,
        num_candidates=NUM_CANDIDATES,
        order=1,
    )

    # Relaxer kwargs (order=2, model set later)
    relaxer_kwargs = dict(
        constraints=environment.get_constraints(),
        optimizer_run_kwargs={"steps": RELAX_STEPS},
        start_relax=START_RELAX,
        order=2,
    )

    # Evaluator kwargs (order=4, calc + constraints fixed)
    evaluator_kwargs = dict(
        calc=calc,
        gets={"get_key": "prioritized_candidates"},
        optimizer_kwargs={"logfile": None},
        optimizer_run_kwargs={"fmax": OPT_FMAX, "steps": OPT_STEPS},
        constraints=environment.get_constraints(),
        store_trajectory=True,
        order=4,
    )

    return (environment, descriptor, model, sampler, generators, collector,
            relaxer_kwargs, evaluator_kwargs, calc)


##############################################################################
# Build a complete AGOX stack for a given acquisitor type
##############################################################################

def build_stack(acq_type, db_path, seed):
    """
    acq_type: 'regular_lcb' | 'novelty_lcb'
    Returns (agox, database, environment) — fully wired and ready to run.
    """
    (environment, descriptor, model_template, sampler, generators,
     collector, relaxer_kwargs, evaluator_kwargs, calc) = build_system()

    # Database (order=5, shared convention)
    database = Database(filename=db_path, order=5)

    # Wire database into model + sampler (they were created without it)
    model = GPR(descriptor=descriptor, kernel=model_template.kernel,
                database=database, prior=Repulsive())
    sampler = KMeansSampler(descriptor=descriptor, database=database,
                            sample_size=SAMPLE_SIZE)

    # Acquisitor (the variable part)
    if acq_type == "regular_lcb":
        acquisitor = LowerConfidenceBoundAcquisitor(
            model=model, kappa=KAPPA, order=3)
    elif acq_type == "novelty_lcb":
        acquisitor = NoveltyLCBAcquisitor(
            model=model,
            descriptor=descriptor,
            database=database,
            target_energy=NOVELTY_TARGET_ENERGY,
            delta_E=NOVELTY_DELTA_E,
            novelty_weight=NOVELTY_WEIGHT,
            order=3,
        )
    else:
        raise ValueError(f"Unknown acq_type: {acq_type!r}")

    # Relaxer — needs acquisitor's acquisition calculator
    relaxer = ParallelRelaxPostprocess(
        model=acquisitor.get_acquisition_calculator(),
        **relaxer_kwargs)

    # Evaluator
    evaluator = LocalOptimizationEvaluator(**evaluator_kwargs)

    # Orchestrate
    agox = AGOX(collector, relaxer, acquisitor, evaluator, database,
                seed=seed)

    return agox, database, environment


##############################################################################
# Run both strategies
##############################################################################

def main():
    print("=" * 70)
    print("Ni8 / Au(4,4,2) fcc100 surface  —  AGOX comparison run")
    print("=" * 70)
    print(f"  seed              = {SEED}")
    print(f"  symbols           = {SYMBOLS}")
    print(f"  template          = fcc100('Au', size={TEMPLATE_SIZE}, vacuum={VACUUM})")
    print(f"  confinement_z     = {CONFINEMENT_Z} Å")
    print(f"  sample_size       = {SAMPLE_SIZE}")
    print(f"  kappa (LCB)       = {KAPPA}")
    print(f"  novelty_target_E  = {NOVELTY_TARGET_ENERGY} eV")
    print(f"  novelty_delta_E   = {NOVELTY_DELTA_E} eV")
    print(f"  novelty_weight    = {NOVELTY_WEIGHT}")
    print(f"  N_iterations      = {N_ITERATIONS}")
    print("=" * 70)
    print()

    for acq_type, label in [("regular_lcb", "Standard LCB"),
                             ("novelty_lcb", "Novelty-LCB")]:
        db_path = f"db_{label.lower().replace(' ', '_')}_{SEED}.db"

        # Keep the DB after the run for later analysis.
        # (Previously removed here; now preserved.)

        print(f"--- {label} ---")
        print(f"  database: {db_path}")
        agox, database, environment = build_stack(acq_type, db_path, SEED)

        # Quick info print
        print(f"  environment symbols: {environment.symbols}")
        print(f"  confinement corner: {environment.confinement_corner}")
        print(f"  acquisitor: {agox.acquisitor.name}")
        if hasattr(agox.acquisitor, 'target_energy'):
            print(f"    target_energy = {agox.acquisitor.target_energy} eV")
            print(f"    delta_E       = {agox.acquisitor.delta_E} eV")
            print(f"    novelty_weight= {agox.acquisitor.novelty_weight}")
        print()

        agox.run(N_iterations=N_ITERATIONS)
        print(f"  {label} finished.\n")

    print("=" * 70)
    print("Both runs complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
