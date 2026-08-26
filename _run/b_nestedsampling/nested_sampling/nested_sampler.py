#!/usr/bin/env python3
"""Nested Sampler — log-space nested sampling with GPR likelihood."""

from __future__ import annotations

__version__ = "1.0.0"

import os
from pathlib import Path
from typing import List, Optional

import numpy as np

from ase import Atoms


class NestedSampler:
    """
    Nested sampling with GPR likelihood, working in log-space for numerical
    stability.

    The likelihood is L(x) = exp(-beta * (E(x) - E_ref)) where E_ref is the
    minimum training energy (so L is O(1) at the best structures).

    Evidence is accumulated as log(Z).
    """

    def __init__(
        self,
        gpr,
        db_structures: List[Atoms],
        db_energies: np.ndarray,
        n_live: int = 50,
        beta: float = None,
        temperature: float = 300.0,
        perturb: float = 0.01,
        rng: np.random.Generator = None,
        perturb_symbols: str = "Fe",
    ):
        self.gpr = gpr
        self.db_structures = db_structures
        self.db_energies = db_energies
        self.n_live = n_live
        self.beta = beta if beta is not None else 1.0 / (8.617333262e-5 * temperature)
        self.temperature = temperature
        self.perturb = perturb
        self.rng = rng or np.random.default_rng()
        self.perturb_symbols = perturb_symbols

        # Indices of the atoms to perturb (the deposition layer). A single list is
        # computed from the (uniform-composition) dataset and reused for every draw.
        symbols = np.array(db_structures[0].get_chemical_symbols())
        self.perturb_indices = np.where(np.isin(symbols, [perturb_symbols]))[0]
        if len(self.perturb_indices) == 0:
            raise ValueError(
                f"No atoms with symbol '{perturb_symbols}' found in the dataset."
            )
        print(f"[NestedSampler] Perturbing {len(self.perturb_indices)} atoms of "
              f"symbol '{perturb_symbols}' (amplitude {perturb:.4f} A); "
              f"all other atoms are left fixed.")

        # Energy reference: shift so minimum training energy is 0
        self.E_ref = db_energies.min()

        # Live points (stored as log-likelihoods for numerical stability)
        self.live_structures: List[Atoms] = []
        self.live_energies: np.ndarray = np.array([])
        self.live_log_L: np.ndarray = np.array([])

        # Evidence in log space
        self.log_Z = -np.inf
        self.Z_history: List[float] = []
        self.iteration = 0

        # Posterior
        self.posterior_samples: List[Atoms] = []
        self.posterior_log_weights: List[float] = []

        self.log_L_boundary = -np.inf

    # -- Prior sampling --

    def sample_from_prior(self) -> Atoms:
        """Draw from empirical DB distribution + optional perturbation.

        Perturbation is applied ONLY to the deposition-species atoms (the
        ``perturb_indices``), e.g. Fe; the substrate and every other atom are left
        in their database positions (fixed).
        """
        idx = self.rng.integers(0, len(self.db_structures))
        base = self.db_structures[idx].copy()
        if self.perturb > 0:
            noise = self.rng.normal(0, self.perturb,
                                    (len(self.perturb_indices), 3))
            base.positions[self.perturb_indices] += noise
        return base

    # -- Log-likelihood --

    def log_likelihood(self, atoms: Atoms) -> float:
        """log L = -beta * (E - E_ref)."""
        E = self.gpr.predict_energy(atoms)
        if abs(E) > 1e4:
            return -np.inf
        return -self.beta * (E - self.E_ref)

    def likelihood(self, atoms: Atoms) -> float:
        """L = exp(log_L), with underflow protection."""
        ll = self.log_likelihood(atoms)
        if ll < -700:   # exp(-700) ~ 10^-304, below float64 minimum
            return 0.0
        return np.exp(ll)

    # -- Initialisation --

    def initialize(self):
        """Draw initial live points."""
        print(f"Drawing {self.n_live} initial live points...")
        for i in range(self.n_live):
            s = self.sample_from_prior()
            E = self.gpr.predict_energy(s)
            ll = self.log_likelihood(s)

            self.live_structures.append(s)
            self.live_energies = np.append(self.live_energies, E)
            self.live_log_L = np.append(self.live_log_L, ll)

            if (i + 1) % 10 == 0:
                valid_E = self.live_energies[np.abs(self.live_energies) < 1e4]
                if len(valid_E) > 0:
                    print(f"  [{i+1}/{self.n_live}] E: "
                          f"{valid_E.min():.3f} to {valid_E.max():.3f} eV")
                else:
                    print(f"  [{i+1}/{self.n_live}] WARNING: unphysical energies")

        self._filter_unphysical()
        self.log_L_boundary = self.live_log_L.min()
        print(f"Initial log_L_boundary = {self.log_L_boundary:.4f}  "
              f"(E_boundary = {self.E_ref - self.log_L_boundary/self.beta:.3f} eV)")

    def _filter_unphysical(self, max_E: float = 1e4):
        """Replace live points with |E| > max_E."""
        mask = np.abs(self.live_energies) < max_E
        n_bad = (~mask).sum()
        if n_bad == 0:
            return
        print(f"  Replacing {n_bad} unphysical live points...")
        for i in range(len(self.live_structures)):
            if not mask[i]:
                for _ in range(100):
                    s = self.sample_from_prior()
                    E = self.gpr.predict_energy(s)
                    if abs(E) < max_E:
                        self.live_structures[i] = s
                        self.live_energies[i] = E
                        self.live_log_L[i] = self.log_likelihood(s)
                        break

    # -- Constrained sampling --

    def sample_constrained(self, n_attempts: int = 500) -> Optional[Atoms]:
        """Draw from prior with log_L > log_L_boundary."""
        for _ in range(n_attempts):
            s = self.sample_from_prior()
            ll = self.log_likelihood(s)
            if ll > self.log_L_boundary and abs(self.gpr.predict_energy(s)) < 1e4:
                return s
        return None

    # -- Step --

    def step(self) -> bool:
        """One NS iteration. Accumulate log_evidence via log-sum-exp."""
        worst_idx = np.argmin(self.live_log_L)
        log_L_min = self.live_log_L[worst_idx]

        i = self.iteration
        # Prior volume shrinkage
        X_prev = np.exp(-i / self.n_live)
        X_this = np.exp(-(i + 1) / self.n_live)
        delta_X = X_prev - X_this

        # Accumulate evidence: Z += L_min * delta_X
        # In log space: log(Z_new) = log(Z_old + exp(log_L_min) * delta_X)
        term = np.exp(log_L_min) * delta_X
        if self.log_Z == -np.inf:
            self.log_Z = np.log(term) if term > 0 else -np.inf
        else:
            self.log_Z = np.logaddexp(self.log_Z, np.log(term) if term > 0 else -np.inf)

        self.Z_history.append(np.exp(self.log_Z) if self.log_Z > -np.inf else 0.0)

        # Save posterior sample
        self.posterior_samples.append(self.live_structures[worst_idx])
        self.posterior_log_weights.append(
            log_L_min + np.log(delta_X) if delta_X > 0 else -np.inf
        )

        # Replace worst point
        new_struct = self.sample_constrained()
        if new_struct is None:
            new_struct = self.sample_from_prior()

        self.live_structures[worst_idx] = new_struct
        self.live_energies[worst_idx] = self.gpr.predict_energy(new_struct)
        self.live_log_L[worst_idx] = self.log_likelihood(new_struct)

        self.log_L_boundary = self.live_log_L.min()
        self.iteration += 1
        return True

    # -- Run --

    def run(self, n_iterations: int, progress_every: int = 20):
        """Run nested sampling."""
        print(f"\nNested sampling: {n_iterations} iters, {self.n_live} live, "
              f"T = {self.temperature} K, beta = {self.beta:.4f} eV^-1")
        print(f"E_ref (training min) = {self.E_ref:.4f} eV")
        print("=" * 60)

        for it in range(n_iterations):
            self.step()
            if (it + 1) % progress_every == 0:
                log_L_min = self.live_log_L.min()
                valid_E = self.live_energies[np.abs(self.live_energies) < 1e4]
                n_unphys = (np.abs(self.live_energies) >= 1e4).sum()
                E_min = valid_E.min() if len(valid_E) > 0 else float('nan')
                E_max = valid_E.max() if len(valid_E) > 0 else float('nan')
                Z_now = np.exp(self.log_Z) if self.log_Z > -700 else 0.0
                print(f"  Iter {it+1:5d}/{n_iterations}  "
                      f"Z = {Z_now:.6e}  "
                      f"log_L_min = {log_L_min:.4f}  "
                      f"E: [{E_min:.3f}, {E_max:.3f}] eV  "
                      f"unphys: {n_unphys}")

        # Final evidence correction
        X_final = np.exp(-n_iterations / self.n_live)
        log_L_avg = np.mean(self.live_log_L)
        term_final = np.exp(log_L_avg) * X_final
        if term_final > 0:
            self.log_Z = np.logaddexp(self.log_Z, np.log(term_final))

        Z_final = np.exp(self.log_Z) if self.log_Z > -700 else 0.0
        print(f"\nFinal evidence: Z = {Z_final:.6e}  (log Z = {self.log_Z:.4f})")
        print(f"Final prior volume: X = {X_final:.6e}")

        # Normalise posterior weights (in log space, then exponentiate)
        max_log_w = max(self.posterior_log_weights) if self.posterior_log_weights else 0
        if max_log_w > -np.inf:
            log_total = max_log_w + np.log(sum(np.exp(lw - max_log_w)
                                                for lw in self.posterior_log_weights
                                                if lw > -700))
            self.posterior_log_weights = [lw - log_total for lw in self.posterior_log_weights]

        # Summary
        phys_E = []
        for s in self.posterior_samples:
            E = self.gpr.predict_energy(s)
            if abs(E) < 1e4:
                phys_E.append(E)
        if phys_E:
            phys_E = np.array(phys_E)
            print(f"\nPosterior: {len(phys_E)} physical / {len(self.posterior_samples)} total")
            print(f"  E_mean = {phys_E.mean():.4f} eV")
            print(f"  E_std  = {phys_E.std():.4f} eV")
            print(f"  E_min  = {phys_E.min():.4f} eV")
            print(f"  E_max  = {phys_E.max():.4f} eV")

        return Z_final

    # -- Save --

    def save(self, output_dir: str):
        """Save results."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        np.savetxt(out / "evidence_history.csv",
                   np.column_stack([np.arange(len(self.Z_history)), self.Z_history]),
                   delimiter=',', header='iteration,evidence_Z', comments='')
        np.savetxt(out / "log_evidence.csv",
                   np.column_stack([[i, self.log_Z] for i in range(len(self.Z_history))]),
                   delimiter=',', header='iteration,log_Z', comments='')

        # Posterior samples (physical only), all of them + summary CSV so the
        # analysis can be re-run standalone without re-training the GPR.
        phys_pairs = [(w, s) for w, s in zip(self.posterior_log_weights, self.posterior_samples)
                      if abs(self.gpr.predict_energy(s)) < 1e4]
        if phys_pairs:
            phys_pairs.sort(key=lambda x: x[0], reverse=True)
            xsf_dir = out / "posterior_structures"
            xsf_dir.mkdir(exist_ok=True)
            summary_rows = []
            from ase.io import write
            for i, (lw, s) in enumerate(phys_pairs):
                w = np.exp(lw) if lw > -700 else 0.0
                E = self.gpr.predict_energy(s)
                write(xsf_dir / f"posterior_{i:03d}_w{w:.4e}_E{E:.3f}.xsf", s)
                summary_rows.append((i, E, w, lw))
            np.savetxt(out / "posterior_summary.csv", np.asarray(summary_rows, dtype=float),
                       delimiter=',',
                       header='rank,energy_eV,weight,log_weight', comments='')
            print(f"  Saved {len(phys_pairs)} posterior structures to {xsf_dir}")

        np.savetxt(out / "final_live_energies.csv",
                   self.live_energies.reshape(-1, 1),
                   delimiter=',', header='energy_eV', comments='')

        print(f"Results saved to {out}")
