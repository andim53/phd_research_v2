#!/usr/bin/env python3
"""Nested Sampler — log-space nested sampling with GPR likelihood."""

from __future__ import annotations

__version__ = "1.2.0"

import os
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from ase import Atoms


def _logsumexp(a: np.ndarray) -> float:
    """Numerically stable log(sum(exp(a)))."""
    a = np.asarray(a, dtype=float)
    m = a.max()
    if not np.isfinite(m):
        return m
    return m + np.log(np.sum(np.exp(a - m)))


class NestedSampler:
    """
    Nested sampling with GPR likelihood, working in log-space for numerical
    stability.

    Two modes, selected by ``temperature_free``:

    **Fixed-temperature mode (default, ``temperature_free=False``).**
    The likelihood is L(x) = exp(-beta * (E(x) - E_ref)) where E_ref is the
    minimum training energy and beta = 1/(k_B * T). Evidence is accumulated at
    that single temperature. This is the historical behaviour of this code.

    **Temperature-free mode (``temperature_free=True``, consistent with the
    papers: Partay 2021 / Yang 2024 and the wiki's ``nested-sampling`` page).**
    The likelihood is beta-free: log L = -(E - E_ref), i.e. sampling is a single
    top-down pass over configuration space constrained only by a decreasing
    energy limit (the "worst" live point is simply the highest-energy one). The
    sampler records, for every discarded sample, its energy ``E_i`` and its
    prior-volume weight ``w_i = Gamma(E_{i-1}) - Gamma(E_i) = delta_X``. The
    partition function at ANY temperature is then evaluated in post-processing:

        Z(beta) = sum_i w_i * exp(-beta * E_i)   (+ final live-point term)

    so one sample set yields Z(T), free energy F = -k_B T ln Z, and the posterior
    at every temperature of interest — matching the papers' temperature-free
    sampling with beta applied only in post-processing.
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
        temperature_free: bool = False,
    ):
        self.gpr = gpr
        self.db_structures = db_structures
        self.db_energies = db_energies
        self.n_live = n_live
        self.temperature_free = temperature_free
        if temperature_free:
            # beta is deliberately NOT set: sampling is temperature-independent.
            self.beta = None
            self.temperature = None
        else:
            self.beta = beta if beta is not None else 1.0 / (8.617333262e-5 * temperature)
            self.temperature = temperature
        self.perturb = perturb
        self.rng = rng or np.random.default_rng()
        self.perturb_symbols = perturb_symbols

        # Indices of the atoms to perturb (the deposition layer). A single list is
        # computed from the (uniform-composition) dataset and reused for every draw.
        # --perturb-symbols may list multiple symbols separated by commas, e.g. "Fe,B"
        # (whitespace-trimmed); all matching atoms are perturbed.
        perturb_list = [s.strip() for s in str(perturb_symbols).split(",") if s.strip()]
        symbols = np.array(db_structures[0].get_chemical_symbols())
        self.perturb_indices = np.where(np.isin(symbols, perturb_list))[0]
        if len(self.perturb_indices) == 0:
            raise ValueError(
                f"No atoms with any symbol {perturb_list} found in the dataset."
            )
        print(f"[NestedSampler] Perturbing {len(self.perturb_indices)} atoms of "
              f"symbol(s) {perturb_list} (amplitude {perturb:.4f} A); "
              f"all other atoms are left fixed.")

        # Energy reference: shift so minimum training energy is 0
        self.E_ref = db_energies.min()

        # Live points (stored as log-likelihoods for numerical stability)
        self.live_structures: List[Atoms] = []
        self.live_energies: np.ndarray = np.array([])
        self.live_log_L: np.ndarray = np.array([])

        # Evidence in log space (fixed-T mode only)
        self.log_Z = -np.inf
        self.Z_history: List[float] = []
        self.iteration = 0

        # Posterior (discarded samples, in removal order)
        self.posterior_samples: List[Atoms] = []
        self.posterior_log_weights: List[float] = []

        # Temperature-free bookkeeping: per-discarded-sample energy + prior weight
        self.sample_energies: List[float] = []
        self.sample_prior_weights: List[float] = []

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
        """log L for ranking the live set.

        - Fixed-T mode:  log L = -beta * (E - E_ref)
        - Temperature-free mode:  log L = -(E - E_ref)   (beta-free; energy-based)
        """
        E = self.gpr.predict_energy(atoms)
        if abs(E) > 1e4:
            return -np.inf
        if self.temperature_free:
            return -(E - self.E_ref)
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
              f"(E_boundary = {self.E_ref - self.log_L_boundary:.3f} eV)")

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
        """Draw from prior with log_L > log_L_boundary.

        In temperature-free mode this is the energy constraint E < E_boundary
        (equivalently log_L = -(E - E_ref) > log_L_boundary); in fixed-T mode it
        is the beta-weighted likelihood constraint. Either way, the prior volume
        shrinks toward low energy.
        """
        for _ in range(n_attempts):
            s = self.sample_from_prior()
            ll = self.log_likelihood(s)
            if ll > self.log_L_boundary and abs(self.gpr.predict_energy(s)) < 1e4:
                return s
        return None

    # -- Step --

    def step(self) -> bool:
        """One NS iteration. Remove the worst live point, shrink the prior volume."""
        worst_idx = np.argmin(self.live_log_L)
        log_L_min = self.live_log_L[worst_idx]
        E_worst = self.live_energies[worst_idx]

        i = self.iteration
        # Prior volume shrinkage
        X_prev = np.exp(-i / self.n_live)
        X_this = np.exp(-(i + 1) / self.n_live)
        delta_X = X_prev - X_this

        # Fixed-T mode: accumulate evidence  Z += L_min * delta_X  (log space)
        if not self.temperature_free:
            term = np.exp(log_L_min) * delta_X
            if self.log_Z == -np.inf:
                self.log_Z = np.log(term) if term > 0 else -np.inf
            else:
                self.log_Z = np.logaddexp(
                    self.log_Z, np.log(term) if term > 0 else -np.inf)
            self.Z_history.append(np.exp(self.log_Z) if self.log_Z > -np.inf else 0.0)

        # Save posterior sample (discarded worst point)
        self.posterior_samples.append(self.live_structures[worst_idx])
        self.posterior_log_weights.append(
            log_L_min + np.log(delta_X) if delta_X > 0 else -np.inf
        )
        # Temperature-free bookkeeping: (E_i, w_i = delta_X) for post-processing
        if self.temperature_free:
            self.sample_energies.append(E_worst)
            self.sample_prior_weights.append(delta_X)

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
        mode = "temperature-free" if self.temperature_free else \
               f"T = {self.temperature} K, beta = {self.beta:.4f} eV^-1"
        print(f"\nNested sampling: {n_iterations} iters, {self.n_live} live, {mode}")
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
                if self.temperature_free:
                    # progress metric = remaining prior volume X_i
                    X_now = np.exp(-(it + 1) / self.n_live)
                    print(f"  Iter {it+1:5d}/{n_iterations}  "
                          f"X = {X_now:.6e}  "
                          f"E: [{E_min:.3f}, {E_max:.3f}] eV  "
                          f"unphys: {n_unphys}")
                else:
                    Z_now = np.exp(self.log_Z) if self.log_Z > -700 else 0.0
                    print(f"  Iter {it+1:5d}/{n_iterations}  "
                          f"Z = {Z_now:.6e}  "
                          f"log_L_min = {log_L_min:.4f}  "
                          f"E: [{E_min:.3f}, {E_max:.3f}] eV  "
                          f"unphys: {n_unphys}")

        if not self.temperature_free:
            # Final evidence correction (fixed-T mode)
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
                log_total = max_log_w + np.log(sum(
                    np.exp(lw - max_log_w) for lw in self.posterior_log_weights
                    if lw > -700))
                self.posterior_log_weights = [
                    lw - log_total for lw in self.posterior_log_weights]
        else:
            X_final = np.exp(-n_iterations / self.n_live)
            print(f"\nFinal prior volume: X = {X_final:.6e}")
            print("Temperature-free sampling complete. Evaluate Z(beta)/posterior "
                  "at any temperature via evaluate()/posterior_at().")

        # Summary (physical posterior energies)
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

        return X_final

    # -- Temperature-free post-processing --

    def evaluate(self, beta: float) -> Tuple[float, float]:
        """Temperature-free evidence Z(beta) = sum_i w_i exp(-beta E_i).

        Returns
        -------
        Z : float
            Z(beta) (exponentiated; 0.0 if it underflows).
        logZ : float
            log Z(beta) (robust number).

        Only meaningful when ``temperature_free=True``; the fixed-T mode should
        use the accumulated ``self.log_Z`` instead.
        """
        if not self.temperature_free:
            raise ValueError(
                "evaluate() is only for temperature-free mode (temperature_free=True).")
        if len(self.sample_prior_weights) == 0:
            return 0.0, -np.inf
        w = np.array(self.sample_prior_weights, dtype=float)
        E = np.array(self.sample_energies, dtype=float)
        logw = np.log(np.maximum(w, 1e-300))
        logL = -beta * (E - self.E_ref)
        logZ = _logsumexp(logw + logL)
        # final live-point term: X_final * <exp(-beta(E-E_ref))>_live
        mask = np.abs(self.live_energies) < 1e4
        E_live = self.live_energies[mask]
        if len(E_live) > 0:
            X_final = np.exp(-self.iteration / self.n_live)
            logL_live = -beta * (E_live - self.E_ref)
            log_mean = _logsumexp(logL_live) - np.log(len(E_live))
            logZ = np.logaddexp(logZ, np.log(X_final) + log_mean)
        Z = np.exp(logZ) if logZ > -700 else 0.0
        return Z, logZ

    def posterior_at(self, beta: float) -> Tuple[List[Atoms], np.ndarray]:
        """Temperature-free posterior at inverse temperature beta.

        Returns
        -------
        structures : list of ase.Atoms
            Discarded posterior samples (removal order) plus the final live set.
        weights : np.ndarray
            Normalised posterior weights (sum to 1) at this beta.

        weight_i = w_i * exp(-beta E_i) / Z(beta)  (discarded samples)
        plus the final live set share X_final/N_live * exp(-beta E_i) / Z(beta).
        """
        if not self.temperature_free:
            raise ValueError(
                "posterior_at() is only for temperature-free mode (temperature_free=True).")
        Z, logZ = self.evaluate(beta)
        if not np.isfinite(logZ) or logZ < -700:
            return list(self.posterior_samples), np.zeros(len(self.posterior_samples))

        w = np.array(self.sample_prior_weights, dtype=float)
        E = np.array(self.sample_energies, dtype=float)
        logw = np.log(np.maximum(w, 1e-300))
        logL = -beta * (E - self.E_ref)
        weights_disc = np.exp(logw + logL - logZ)

        structures = list(self.posterior_samples)
        weights = list(weights_disc)

        # final live set
        mask = np.abs(self.live_energies) < 1e4
        X_final = np.exp(-self.iteration / self.n_live)
        if len(self.live_structures) > 0:
            for idx in np.where(mask)[0]:
                E_live = self.live_energies[idx]
                w_live = X_final / self.n_live * np.exp(-beta * (E_live - self.E_ref)) / Z
                structures.append(self.live_structures[idx])
                weights.append(w_live)

        weights = np.array(weights, dtype=float)
        # renormalise (numerical guard)
        tot = weights.sum()
        if tot > 0:
            weights = weights / tot
        return structures, weights

    # -- Save --

    def save(self, output_dir: str):
        """Save results."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        if self.temperature_free:
            # samples.csv (iteration, energy_eV, prior_weight) -> re-runnable
            # post-processing; final_live_energies.csv
            rows = np.column_stack([
                np.arange(len(self.sample_energies)),
                np.array(self.sample_energies),
                np.array(self.sample_prior_weights),
            ])
            np.savetxt(out / "samples.csv", rows, delimiter=',',
                       header='iteration,energy_eV,prior_weight', comments='')
            np.savetxt(out / "final_live_energies.csv",
                       self.live_energies.reshape(-1, 1),
                       delimiter=',', header='energy_eV', comments='')
            print(f"  Wrote samples.csv ({len(self.sample_energies)} discarded "
                  f"samples) + final_live_energies.csv to {out}")
            print("  (temperature-free mode: run post-processing to write "
                  "thermodynamics.csv + per-T posterior structures)")
        else:
            np.savetxt(out / "evidence_history.csv",
                       np.column_stack([np.arange(len(self.Z_history)), self.Z_history]),
                       delimiter=',', header='iteration,evidence_Z', comments='')
            np.savetxt(out / "log_evidence.csv",
                       np.column_stack([[i, self.log_Z] for i in range(len(self.Z_history))]),
                       delimiter=',', header='iteration,log_Z', comments='')

            # Posterior samples (physical only), all of them + summary CSV
            phys_pairs = [
                (w, s) for w, s in zip(self.posterior_log_weights, self.posterior_samples)
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
                np.savetxt(out / "posterior_summary.csv",
                           np.asarray(summary_rows, dtype=float), delimiter=',',
                           header='rank,energy_eV,weight,log_weight', comments='')
                print(f"  Saved {len(phys_pairs)} posterior structures to {xsf_dir}")

            np.savetxt(out / "final_live_energies.csv",
                       self.live_energies.reshape(-1, 1),
                       delimiter=',', header='energy_eV', comments='')

        print(f"Results saved to {out}")
