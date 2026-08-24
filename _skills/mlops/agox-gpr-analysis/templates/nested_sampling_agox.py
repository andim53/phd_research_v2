#!/usr/bin/env python3
"""
Nested Sampling using AGOX GPR surrogate model (TEMPLATE)

Loads an AGOX database, trains a GPR model, and performs nested sampling
to compute Bayesian evidence Z = integral L(x) pi(x) dx.

Likelihood: L(x) = exp(-beta * (E_GPR(x) - E_ref))
Prior: empirical distribution from the AGOX database.

CRITICAL: use perturb=0 (or <=0.01A) to keep GPR predictions physical.
See agox-gpr-analysis skill for detailed pitfalls.

Usage:
    python nested_sampling_agox.py --seed 3 --temp 300 --n-live 50 --n-iters 200
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
from ase import Atoms
from ase.io import write

K_B = 8.617333262e-5  # eV/K


class NestedSampler:
    """Nested sampling with GPR likelihood in log-space."""

    def __init__(self, gpr, db_structures, db_energies,
                 n_live=50, beta=None, temperature=300.0,
                 perturb=0.0, rng=None):
        self.gpr = gpr
        self.db_structures = db_structures
        self.db_energies = db_energies
        self.n_live = n_live
        self.beta = beta if beta is not None else 1.0 / (K_B * temperature)
        self.perturb = perturb
        self.rng = rng or np.random.default_rng()
        self.E_ref = db_energies.min()

        self.live_structures: List[Atoms] = []
        self.live_energies: np.ndarray = np.array([])
        self.live_log_L: np.ndarray = np.array([])
        self.log_Z = -np.inf
        self.Z_history: List[float] = []
        self.iteration = 0
        self.posterior_samples: List[Atoms] = []
        self.posterior_log_weights: List[float] = []
        self.log_L_boundary = -np.inf

    def sample_from_prior(self) -> Atoms:
        idx = self.rng.integers(0, len(self.db_structures))
        base = self.db_structures[idx].copy()
        if self.perturb > 0:
            base.positions += self.rng.normal(0, self.perturb, base.positions.shape)
        return base

    def log_likelihood(self, atoms):
        E = self.gpr.predict_energy(atoms)
        if abs(E) > 1e4:
            return -np.inf
        return -self.beta * (E - self.E_ref)

    def initialize(self):
        for i in range(self.n_live):
            s = self.sample_from_prior()
            E = self.gpr.predict_energy(s)
            ll = self.log_likelihood(s)
            self.live_structures.append(s)
            self.live_energies = np.append(self.live_energies, E)
            self.live_log_L = np.append(self.live_log_L, ll)
        self.log_L_boundary = self.live_log_L.min()

    def sample_constrained(self, n_attempts=500) -> Optional[Atoms]:
        for _ in range(n_attempts):
            s = self.sample_from_prior()
            ll = self.log_likelihood(s)
            if ll > self.log_L_boundary and abs(self.gpr.predict_energy(s)) < 1e4:
                return s
        return None

    def step(self):
        worst_idx = np.argmin(self.live_log_L)
        log_L_min = self.live_log_L[worst_idx]
        i = self.iteration
        X_prev = np.exp(-i / self.n_live)
        X_this = np.exp(-(i + 1) / self.n_live)
        delta_X = X_prev - X_this
        term = np.exp(log_L_min) * delta_X
        self.log_Z = np.logaddexp(self.log_Z, np.log(term) if term > 0 else -np.inf)
        self.Z_history.append(np.exp(self.log_Z) if self.log_Z > -700 else 0.0)
        self.posterior_samples.append(self.live_structures[worst_idx])
        self.posterior_log_weights.append(log_L_min + np.log(delta_X) if delta_X > 0 else -np.inf)
        new_s = self.sample_constrained() or self.sample_from_prior()
        self.live_structures[worst_idx] = new_s
        self.live_energies[worst_idx] = self.gpr.predict_energy(new_s)
        self.live_log_L[worst_idx] = self.log_likelihood(new_s)
        self.log_L_boundary = self.live_log_L.min()
        self.iteration += 1

    def run(self, n_iterations, progress_every=20):
        for it in range(n_iterations):
            self.step()
            if (it + 1) % progress_every == 0:
                Z = np.exp(self.log_Z) if self.log_Z > -700 else 0.0
                print(f"  Iter {it+1}/{n_iterations}  Z={Z:.6e}  "
                      f"log_L_min={self.live_log_L.min():.4f}")
        X_final = np.exp(-n_iterations / self.n_live)
        log_L_avg = np.mean(self.live_log_L)
        term_f = np.exp(log_L_avg) * X_final
        if term_f > 0:
            self.log_Z = np.logaddexp(self.log_Z, np.log(term_f))
        print(f"\nFinal Z = {np.exp(self.log_Z):.6e}  (log Z = {self.log_Z:.4f})")
        return np.exp(self.log_Z)

    def save(self, output_dir):
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        np.savetxt(out / "evidence_history.csv",
                   np.column_stack([np.arange(len(self.Z_history)), self.Z_history]),
                   delimiter=',', header='iteration,evidence_Z', comments='')
        phys = [(w, s) for w, s in zip(self.posterior_log_weights, self.posterior_samples)
                if abs(self.gpr.predict_energy(s)) < 1e4]
        if phys:
            phys.sort(key=lambda x: x[0], reverse=True)
            xsf_dir = out / "posterior_structures"
            xsf_dir.mkdir(exist_ok=True)
            for i, (lw, s) in enumerate(phys[:20]):
                w = np.exp(lw) if lw > -700 else 0.0
                write(xsf_dir / f"posterior_{i:03d}_w{w:.4e}.xsf", s)


def train_gpr(db_path):
    db = Database(filename=db_path)
    db.restore_to_memory()
    traj = db.restore_to_trajectory()
    energies = np.array([a.get_potential_energy() for a in traj])
    fp = Fingerprint.from_atoms(traj[0])
    kernel = C(5000,(1,1e5)) * (C(0.01,(0.01,0.01))*RBF() + C(0.99,(0.99,0.99))*RBF()) + Noise(0.01,(0.01,0.01))
    gpr = GPR(descriptor=fp, kernel=kernel, database=db, prior=Repulsive())
    gpr.train(traj)
    return gpr, traj, energies


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db-dir", default="_analysist/1_result/19_kappa2_iter100_trajNoSave_repSeedDat0_5x5")
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--temp", type=float, default=300.0)
    p.add_argument("--n-live", type=int, default=50)
    p.add_argument("--n-iters", type=int, default=200)
    p.add_argument("--output", default="./ns_output")
    p.add_argument("--perturb", type=float, default=0.0)
    args = p.parse_args()
    db_path = os.path.join(args.db_dir, f"seed_{args.seed}", "1_db", f"db_{args.seed}.db")
    gpr, structures, energies = train_gpr(db_path)
    beta = 1.0 / (K_B * args.temp)
    sampler = NestedSampler(gpr, structures, energies, n_live=args.n_live,
                            beta=beta, perturb=args.perturb, rng=np.random.default_rng(42))
    sampler.initialize()
    sampler.run(args.n_iters)
    sampler.save(args.output)


if __name__ == "__main__":
    main()
