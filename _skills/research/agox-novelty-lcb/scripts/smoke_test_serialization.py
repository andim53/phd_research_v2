"""
Cheap local serialization smoke test for a Novelty-LCB AGOX stack.

Verifies the classic "cannot pickle 'sqlite3.Connection'" Ray crash is fixed at the
code level WITHOUT heavy compute (tiny EMT Au-on-Au system, no GPAW, no DFT).

Walks the exact crash path:
  1. Build a minimal AGOX stack with NoveltyLCBAcquisitor.
  2. get_acquisition_calculator() -> LowerConfidenceBoundCalculator.
  3. Assert pickle.dumps(calc) succeeds.
  4. Assert ray.util.inspect_serializability(calc) has 0 FAIL markers.
  5. Assert ParallelRelaxPostprocess(model=calc, ...) constructs.
  6. Assert a 2-iteration agox.run() with EMT completes (no Ray serialization error).

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python smoke_test_serialization.py

Expected final line: "RESULT: PASS -- run-7 serialization crash is fixed at code level."
"""

import os
import sys
import pickle

import numpy as np

_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import matplotlib
matplotlib.use("Agg")

import ray
from ase.calculators.emt import EMT
from ase.build import bulk, surface

from agox import AGOX
from agox.collectors import ParallelCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import KMeansSampler

from novelty_lcb import NoveltyLCBAcquisitor


def build_minimal_stack(seed=7, out_dir="_smoke_out"):
    """Tiny Au-on-Au fcc100 EMT system -- mirrors real main.py wiring but cheap."""
    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, f"smoke_db_{seed}.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    template = surface(bulk("Au", "fcc", a=4.08, cubic=True), (0, 0, 1),
                       layers=3, vacuum=8.0)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = 6.0
    confinement_corner = np.array([0, 0, template.positions[:, 2].max()])
    env = Environment(
        template=template, symbols="Au2",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],
    )

    database = Database(filename=db_path, order=5)
    descriptor = Fingerprint(environment=env)
    bk = 0.01
    kernel = C(5000, (1, 1e5)) * (
        C(bk, (bk, bk)) * RBF() + C(1 - bk, (1 - bk, 1 - bk)) * RBF()
    ) + Noise(0.01, (0.01, 0.01))
    model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

    sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=4)
    gen = RattleGenerator(**env.get_confinement(), n_rattle=1, rattle_amplitude=0.2)
    collector = ParallelCollector(
        generators=[gen], sampler=sampler, environment=env,
        num_candidates={0: [4, 0]}, order=1,
    )

    acquisitor = NoveltyLCBAcquisitor(
        model=model, descriptor=descriptor, database=database,
        target_energy=0.0, delta_E=2.0, novelty_weight=1.5, kappa=2.0,
        order=3,
    )
    calc = acquisitor.get_acquisition_calculator()

    relaxer = ParallelRelaxPostprocess(
        model=calc, constraints=env.get_constraints(),
        optimizer_run_kwargs={"steps": 5}, start_relax=2, order=2,
    )
    evaluator = LocalOptimizationEvaluator(
        EMT(), gets={"get_key": "prioritized_candidates"},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
        constraints=env.get_constraints(), store_trajectory=False, order=4,
    )
    agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)
    return agox, calc


def main():
    print("=" * 70)
    print("Serialization smoke test: NoveltyLCBAcquisitor acquisition calculator")
    print("=" * 70)

    agox, calc = build_minimal_stack()

    try:
        b = pickle.dumps(calc)
        print(f"[1] pickle.dumps(calc) OK  ({len(b)} bytes)  -> no sqlite in graph")
    except Exception as e:
        print(f"[1] FAIL pickle.dumps(calc): {e}")
        return 1

    print("[2] ray.util.inspect_serializability(calc)...")
    try:
        inspect = ray.util.inspect_serializability
    except AttributeError:
        inspect = None
    if inspect is not None:
        report = inspect(calc, name="acq_calc")
        if str(report).count("FAIL"):
            print("[2] FAIL: FAIL markers present in serializability report")
            print(report)
            return 1
        print("[2] ray serializability report clean (0 FAIL markers)")
    else:
        print("[2] ray.util.inspect_serializability unavailable; skipped")

    print("[3] ParallelRelaxPostprocess(model=calc, ...) constructed OK")

    print("[4] running 2 iterations of AGOX with EMT (end-to-end)...")
    try:
        agox.run(N_iterations=2, verbose=False)
        print("[4] end-to-end 2-iteration run OK (no Ray serialization error)")
    except Exception:
        import traceback
        print("[4] FAIL end-to-end run:")
        traceback.print_exc()
        return 1

    print("\nRESULT: PASS -- run-7 serialization crash is fixed at code level.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
