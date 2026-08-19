#!/usr/bin/env python3
"""
Benchmark 2: Tighter energy window to showcase novelty LCB advantage.

With a narrow energy window, the novelty LCB must find structurally
diverse candidates within a restricted energy range, while the regular
LCB simply minimizes E - kappa*sigma globally.

Key hypothesis: With a tight window, regular LCB will tend to find
fewer distinct minima (focusing on the lowest-E basin), while novelty
LCB will discover more distinct structures within the window.
"""
import sys
sys.path.insert(0, "/home/think/Desktop/research")

import os
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

from novelty_lcb_acquisitor import NoveltyLCBAcquisitor
from agox.acquisitors import LowerConfidenceBoundAcquisitor

# ── Parameters ───────────────────────────────────────────────────────────────
N_ATOMS = 10
SYMBOLS = "Au10"
N_ITERATIONS = 80
N_RUNS = 5
TEMPERATURE = 0.2
RATTLE_AMPLITUDE = 2.0
RATTLE_N = 5
KAPPA = 2.0
NOVELTY_WEIGHT = 1.5
# Tight window: only accept candidates in [5.0, 6.5] eV
TARGET_ENERGY = 5.75
DELTA_E = 0.75
DUP_THRESHOLD = 1.0  # fingerprint distance for "distinct" clustering
RANDOM_SEEDS = [42, 123, 456, 789, 1024]
OUTDIR = "/home/think/Desktop/research/benchmark_results"

os.makedirs(OUTDIR, exist_ok=True)


def make_template():
    return Atoms("", cell=np.eye(3) * 16.0, pbc=False)


def run_single(seed, label, acq_type):
    np.random.seed(seed)
    db_file = f"{OUTDIR}/{label}_db.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    template = make_template()
    env = Environment(
        template=template, symbols=SYMBOLS,
        confinement_cell=np.eye(3) * 14,
        confinement_corner=np.array([4, 4, 4]),
        print_report=False,
    )
    calc = EMT()

    db = Database(filename=db_file, order=5)
    desc = Fingerprint(rc1=6, rc2=4, binwidth=0.2, Nbins=30,
                        environment=env, use_angular=True)
    model = GPR(descriptor=desc, kernel=RBF(), prior=Repulsive(),
                database=db, order=0,
                iteration_start_training=5, update_period=3)
    sampler = MetropolisSampler(temperature=TEMPERATURE, order=3)
    generator = RattleGenerator(
        **env.get_confinement(), environment=env, sampler=sampler,
        n_rattle=RATTLE_N, rattle_amplitude=RATTLE_AMPLITUDE, order=1,
    )
    evaluator = LocalOptimizationEvaluator(
        calc, gets={"get_key": "candidates"}, store_trajectory=False,
        optimizer_run_kwargs={"fmax": 0.05, "steps": 100}, order=2,
        constraints=env.get_constraints(),
    )

    if acq_type == "novelty_lcb":
        acq = NoveltyLCBAcquisitor(
            model=model, descriptor=desc, database=db,
            target_energy=TARGET_ENERGY, delta_E=DELTA_E,
            novelty_weight=NOVELTY_WEIGHT, order=4,
        )
    else:
        acq = LowerConfidenceBoundAcquisitor(model=model, kappa=KAPPA, order=4)

    agox = AGOX(generator, db, sampler, evaluator, acq, seed=seed)
    agox.run(N_iterations=N_ITERATIONS, verbose=False, hide_log=True)

    # Analyze
    db2 = Database(filename=db_file, initialize=False)
    db2.restore_to_memory()
    all_c = db2.get_all_candidates()

    features, energies = [], []
    for c in all_c:
        try:
            e = c.get_potential_energy()
            if not np.isfinite(e): continue
            f = desc.get_features(c).ravel()
            features.append(f); energies.append(e)
        except: pass

    if not features:
        return {"seed": seed, "label": label, "acq": acq_type,
                "n_evals": 0, "n_distinct": 0, "best_E": np.nan,
                "e_range": 0.0, "all_energies": []}

    features = np.array(features); energies = np.array(energies)

    # Cluster
    order = np.argsort(energies); remaining = list(order); selected = []
    while remaining:
        idx = remaining.pop(0); selected.append(idx)
        remaining = [j for j in remaining
                     if np.linalg.norm(features[j] - features[idx]) > DUP_THRESHOLD]

    return {
        "seed": seed, "label": label, "acq": acq_type,
        "n_evals": len(energies), "n_distinct": len(selected),
        "best_E": float(energies.min()),
        "e_range": float(energies.max() - energies.min()),
        "distinct_energies": [float(energies[i]) for i in selected],
        "all_energies": [float(e) for e in energies],
    }


def main():
    print("=" * 70)
    print("BENCHMARK 2: Tight Energy Window")
    print("=" * 70)
    print("Window: [%.2f, %.2f] eV" % (TARGET_ENERGY - DELTA_E, TARGET_ENERGY + DELTA_E))
    print("Distinctness threshold: %.1f" % DUP_THRESHOLD)
    print("Iterations: %d, Runs: %d" % (N_ITERATIONS, N_RUNS))
    print("=" * 70)

    results = {"regular_lcb": [], "novelty_lcb": []}

    for i, seed in enumerate(RANDOM_SEEDS):
        print("\nRun %d/%d (seed=%d)" % (i+1, N_RUNS, seed))

        label_r = "tight_run%02d_regular" % (i+1)
        print("  Regular LCB...")
        r = run_single(seed, label_r, "regular_lcb")
        results["regular_lcb"].append(r)
        print("    evals=%d, distinct=%d, best_E=%.3f" %
              (r["n_evals"], r["n_distinct"], r["best_E"]))

        label_n = "tight_run%02d_novelty" % (i+1)
        print("  Novelty LCB...")
        n = run_single(seed, label_n, "novelty_lcb")
        results["novelty_lcb"].append(n)
        print("    evals=%d, distinct=%d, best_E=%.3f" %
              (n["n_evals"], n["n_distinct"], n["best_E"]))

    # Aggregate
    print("\n" + "=" * 70)
    print("AGGREGATE RESULTS (tight window)")
    print("=" * 70)
    for acq_type in ["regular_lcb", "novelty_lcb"]:
        runs = results[acq_type]
        nd = [r["n_distinct"] for r in runs]
        ne = [r["n_evals"] for r in runs]
        be = [r["best_E"] for r in runs]
        print("\n%s:" % acq_type)
        print("  Distinct minima: mean=%.1f, std=%.1f, min=%d, max=%d" %
              (np.mean(nd), np.std(nd), min(nd), max(nd)))
        print("  Evaluations:     mean=%.1f, std=%.1f" %
              (np.mean(ne), np.std(ne)))
        print("  Best energy:     mean=%.3f +/- %.3f eV" %
              (np.mean(be), np.std(be)))
        for r in runs:
            print("    seed=%-5d: distinct=%-3d evals=%-3d best_E=%.3f" %
                  (r["seed"], r["n_distinct"], r["n_evals"], r["best_E"]))

    # Comparison
    rd = [r["n_distinct"] for r in results["regular_lcb"]]
    nd = [r["n_distinct"] for r in results["novelty_lcb"]]
    diff = np.array(nd) - np.array(rd)
    print("\nDifference (novelty - regular) in distinct minima:")
    print("  Per-run: %s" % diff)
    print("  Mean:   %+.1f +/- %.1f" % (np.mean(diff), np.std(diff)))
    print("  Novelty finds more: %d/%d runs" % (np.sum(diff > 0), N_RUNS))
    print("  Tie:                %d/%d runs" % (np.sum(diff == 0), N_RUNS))
    print("  Regular finds more: %d/%d runs" % (np.sum(diff < 0), N_RUNS))

    # Save JSON
    import json
    with open("%s/benchmark2_results.json" % OUTDIR, "w") as f:
        json.dump({"parameters": {
            "N_ATOMS": N_ATOMS, "SYMBOLS": SYMBOLS,
            "N_ITERATIONS": N_ITERATIONS, "N_RUNS": N_RUNS,
            "KAPPA": KAPPA, "NOVELTY_WEIGHT": NOVELTY_WEIGHT,
            "TARGET_ENERGY": TARGET_ENERGY, "DELTA_E": DELTA_E,
            "DUP_THRESHOLD": DUP_THRESHOLD,
        }, "results": results}, f, indent=2, default=str)
    print("\nResults saved to %s/benchmark2_results.json" % OUTDIR)


if __name__ == "__main__":
    main()
