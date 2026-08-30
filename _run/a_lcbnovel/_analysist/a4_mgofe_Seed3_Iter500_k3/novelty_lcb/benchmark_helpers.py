#!/usr/bin/env python3
"""Helper: build a MinimalAGOX instance for benchmarks."""



from __future__ import annotations

__version__ = "1.0.0"

import os
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.calculators.emt import EMT

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.samplers import MetropolisSampler
from agox.models import GPR
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR.kernels import RBF
from agox.models.GPR.priors import Repulsive

from novelty_lcb.acquisitor import NoveltyLCBAcquisitor
from agox.acquisitors import LowerConfidenceBoundAcquisitor


# ── Default parameters ( Au10 / EMT ) ───────────────────────────────────────

DEFAULT = dict(
    symbols="Au10",
    n_iterations=80,
    temperature=0.2,
    rattle_amplitude=2.0,
    rattle_n=5,
    kappa=2.0,
    novelty_weight=1.5,
    target_energy=5.75,
    delta_E=0.75,
    dup_threshold=1.0,
    seed=42,
)


# ── Template ────────────────────────────────────────────────────────────────

def make_template(cell_size: float = 16.0) -> Atoms:
    """Empty ASE Atoms template with a large cell for free clusters."""
    return Atoms("", cell=np.eye(3) * cell_size, pbc=False)


# ── Environment ─────────────────────────────────────────────────────────────

def make_environment(template: Atoms) -> Environment:
    return Environment(
        template=template,
        symbols=DEFAULT["symbols"],
        confinement_cell=np.eye(3) * 14,
        confinement_corner=np.array([4, 4, 4]),
        print_report=False,
    )


# ── Build full AGOX stack ───────────────────────────────────────────────────

def build_agox(
    seed: int,
    out_dir: str,
    label: str,
    acq_type: str,          # "regular_lcb" | "novelty_lcb"
    params: dict | None = None,
) -> AGOX:
    """Construct a fully wired AGOX instance, ready to ``.run()``.

    Parameters
    ----------
    seed : int
        Random seed.
    out_dir : str
        Directory for the .db file.
    label : str
        File-label prefix (e.g. ``run01_novelty``).
    acq_type : str
        Which acquisitor to build.
    params : dict or None
        Override default parameters.  Recognised keys:
        symbols, n_iterations, temperature, rattle_amplitude,
        rattle_n, kappa, novelty_weight, target_energy, delta_E.
    """
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    p = {**DEFAULT, **(params or {})}

    template = make_template()
    env = make_environment(template)

    # Database
    db_path = os.path.join(out_dir, f"{label}_db.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    database = Database(filename=db_path, order=5)

    # Descriptor
    descriptor = Fingerprint(
        environment=env,
        rc1=6, rc2=4, binwidth=0.2, Nbins=30,
        use_angular=True,
    )

    # GPR model
    model = GPR(
        descriptor=descriptor,
        kernel=RBF(),
        prior=Repulsive(),
        database=database,
        order=0,
        iteration_start_training=5,
        update_period=3,
    )

    # Sampler
    sampler = MetropolisSampler(temperature=p["temperature"], order=3)

    # Generator
    generator = RattleGenerator(
        **env.get_confinement(),
        environment=env,
        sampler=sampler,
        n_rattle=p["rattle_n"],
        rattle_amplitude=p["rattle_amplitude"],
        order=1,
    )

    # Evaluator
    evaluator = LocalOptimizationEvaluator(
        EMT(),
        gets={"get_key": "candidates"},
        store_trajectory=False,
        optimizer_run_kwargs={"fmax": 0.05, "steps": 100},
        order=2,
        constraints=env.get_constraints(),
    )

    # Acquisitor
    if acq_type == "novelty_lcb":
        acq = NoveltyLCBAcquisitor(
            model=model,
            descriptor=descriptor,
            database=database,
            target_energy=p["target_energy"],
            delta_E=p["delta_E"],
            novelty_weight=p["novelty_weight"],
            order=4,
        )
    elif acq_type == "regular_lcb":
        acq = LowerConfidenceBoundAcquisitor(
            model=model,
            kappa=p["kappa"],
            order=4,
        )
    else:
        raise ValueError(f"Unknown acquisitor type: {acq_type!r}")

    agox = AGOX(generator, database, sampler, evaluator, acq, seed=seed)
    return agox
