#!/usr/bin/env python3
"""WangLandauSampler — flat-histogram density-of-states sampling on a GPR
surrogate.

Python port of the algorithm in `_tmp/main_wanglandau_1d.f`. The Fortran toy
walks a 1D coordinate x over an asymmetric double well E(x)=A(x^2-1)^2+Bx and
tracks g(E) in energy bins via the Wang-Landau flatness scheme, then switches
to the 1/t algorithm (Belardinelli & Pereyra 2007). Here the "coordinate" is
the full atomic configuration of a structure from an AGOX database; moves rattle
the deposition-species atoms with small/large Gaussian steps; the energy is
evaluated by the GPR surrogate; and bins are over relative energy per atom
(E - E_ref)/N.
"""

from __future__ import annotations

__version__ = "1.3.0"

from typing import List, Optional

import numpy as np
from ase import Atoms


class WangLandauSampler:
    """Wang-Landau flat-histogram sampler over a GPR energy surrogate.

    Tracks the (log) density of states ``ln_g`` over energy bins spanning
    ``[e_min, e_max]`` (eV/atom, relative to the training minimum). Each
    accepted move visits its bin, accumulating ``ln_f`` into ``ln_g`` and a
    visitation count into the histogram ``H``. When ``H`` is flat enough the
    refinement factor ``ln_f`` is halved (standard scheme); after a fixed number
    of halvings the run switches to the 1/t algorithm to avoid error saturation.
    """

    def __init__(
        self,
        gpr,
        db_structures: List[Atoms],
        db_energies: np.ndarray,
        n_bins: int = 40,
        e_min: float = 0.0,
        e_max: float = 0.40,
        e_reject: Optional[float] = None,
        small_step: float = 0.05,
        large_step: float = 0.20,
        perturb_symbols: str = "Fe",
        flatness_criterion: float = 0.80,
        check_interval: int = 5000,
        n_stages_standard: int = 14,
        swap_prob: float = 0.0,
        max_swaps: int = 1,
        swap_rattle: float = 0.05,
        rng: np.random.Generator = None,
    ):
        self.gpr = gpr
        self.db_structures = db_structures
        self.db_energies = np.asarray(db_energies, dtype=float)
        self.E_ref = self.db_energies.min()
        self.n_atoms = len(db_structures[0])

        # Energy bins over relative energy per atom (eV/atom above min)
        self.n_bins = int(n_bins)
        self.e_min = float(e_min)
        self.e_max = float(e_max)
        self.bin_width = (self.e_max - self.e_min) / self.n_bins
        self.bin_centers_rel = self.e_min + self.bin_width * (
            np.arange(self.n_bins) + 0.5)

        # Walk scales (Angstrom) — small = local refinement, large = barrier crossing
        self.small_step = float(small_step)
        self.large_step = float(large_step)

        # Extrapolation-rejection threshold: a trial whose rel energy exceeds
        # ``e_reject`` is treated as an UNPHYSICAL GPR extrapolation and REJECTED
        # (revisits the current bin) instead of being capped into the top bin.
        # Default = 5 * e_max (a "clearly unphysical" margin far above the window),
        # so MODERATE over-window energies (e_max .. e_reject) are still capped
        # into the top bin (Fortran behaviour), but pathological extrapolations
        # (e.g. the c2 159.9996 eV/atom init) are rejected. Set an explicit
        # ``e_reject`` (eV/atom) to override; a value <= e_max disables the guard
        # (revert to capping everything >= e_max into the top bin).
        if e_reject is not None and float(e_reject) > self.e_max:
            self.e_reject = float(e_reject)
        else:
            self.e_reject = 5.0 * self.e_max
        print(f"[WangLandau] extrapolation guard: reject rel E > {self.e_reject:.4f} "
              f"eV/atom (moderate over-window up to e_max {self.e_max:.3f} is capped "
              f"into the top bin)")

        # Atoms to rattle (deposition species); all others stay fixed
        perturb_list = [s.strip() for s in str(perturb_symbols).split(",")
                        if s.strip()]
        symbols = np.array(db_structures[0].get_chemical_symbols())
        self.perturb_indices = np.where(np.isin(symbols, perturb_list))[0]
        if len(self.perturb_indices) == 0:
            raise ValueError(
                f"No atoms with symbol(s) {perturb_list} found in the dataset.")

        # Permutation (swap) move: exchange positions of two atoms of DIFFERENT
        # species within the mobile set, then rattle the two swapped atoms a
        # little (mirrors the reference GlobalPermutationGenerator). Disabled
        # unless >=2 distinct species are present in the mobile set.
        self.swap_prob = float(swap_prob)
        self.max_swaps = int(max_swaps)
        self.swap_rattle = float(swap_rattle)
        mobile_symbols = symbols[self.perturb_indices]
        self._swap_species = np.unique(mobile_symbols)
        self.swap_available = len(self._swap_species) >= 2
        if self.swap_prob > 0:
            if self.swap_available:
                print(f"[WangLandau] Swap move ENABLED: prob={self.swap_prob:.3f}, "
                      f"1..{self.max_swaps} swaps/move, swap_rattle="
                      f"{self.swap_rattle:.3f} A; swapping among "
                      f"{list(self._swap_species)}")
            else:
                print(f"[WangLandau] WARNING: swap_prob>0 but only "
                      f"{len(self._swap_species)} mobile species "
                      f"({list(self._swap_species)}) present; swap moves "
                      f"DISABLED (need >=2 species in the perturb set).")

        # Wang-Landau state
        self.flatness_criterion = float(flatness_criterion)
        self.check_interval = int(check_interval)
        self.n_stages_standard = int(n_stages_standard)
        self.rng = rng or np.random.default_rng()
        self.ln_g = np.zeros(self.n_bins)
        self.H = np.zeros(self.n_bins, dtype=int)
        self.ln_f = 1.0
        self.stage = 0
        self.switched_to_1_over_t = False
        self.step_at_switch = 0
        self.step = 0

        # Move counters
        self.n_swap_moves = 0
        self.n_rattle_moves = 0

        # Current walker
        self.x_current: Optional[Atoms] = None
        self.E_current = float("nan")
        self.bin_current = -1

        print(f"[WangLandau] bins={self.n_bins} over [{e_min}, {e_max}] "
              f"eV/atom rel (width {self.bin_width:.4f})")
        print(f"[WangLandau] walk scales small={small_step:.3f} A, "
              f"large={large_step:.3f} A; rattling "
              f"{len(self.perturb_indices)} atoms of {perturb_list}")

    # -- Energy helpers ------------------------------------------------------

    def rel_energy(self, atoms: Atoms) -> float:
        """Relative energy per atom above the training minimum (eV/atom)."""
        E = self.gpr.predict_energy(atoms)
        return (E - self.E_ref) / self.n_atoms

    def get_bin(self, rel: float) -> int:
        """0-indexed bin for a relative energy; -1 if below the range floor.

        Energies above ``e_max`` are capped into the top bin (Fortran behaviour).
        """
        if rel < self.e_min:
            return -1
        b = int((rel - self.e_min) / self.bin_width)
        return min(b, self.n_bins - 1)

    # -- Moves ---------------------------------------------------------------

    def _propose(self) -> Atoms:
        """Gaussian rattle of all perturb atoms (small or large, 50/50)."""
        scale = self.large_step if self.rng.random() < 0.5 else self.small_step
        trial = self.x_current.copy()
        noise = self.rng.normal(0.0, scale, (len(self.perturb_indices), 3))
        trial.positions[self.perturb_indices] += noise
        return trial

    def _propose_swap(self) -> Atoms:
        """Permutation move: exchange positions of two atoms of DIFFERENT
        species within the mobile set, then rattle the two swapped atoms a
        little.

        Mirrors the reference ``GlobalPermutationGenerator``: ``num_swaps`` is a
        random integer in [1, max_swaps]; each swap picks two distinct species
        from the mobile set, then a random atom of each, swaps their positions
        and rattles them by ``swap_rattle``.

        Returns
        -------
        trial : Atoms
            A copy of the current walker with the swap(s) applied. If swaps are
            unavailable (single mobile species) or fail, returns None so the
            caller can fall back to a rattle.
        """
        if not self.swap_available:
            return None
        trial = self.x_current.copy()
        mobile_syms = np.array(trial.get_chemical_symbols())
        num_swaps = self.rng.integers(1, self.max_swaps + 1)
        for _ in range(num_swaps):
            # pick two distinct species among the mobile set
            if len(self._swap_species) < 2:
                return None
            sp_i = self._swap_species[self.rng.integers(len(self._swap_species))]
            others = self._swap_species[self._swap_species != sp_i]
            sp_j = others[self.rng.integers(len(others))]
            # absolute indices of the two atoms to swap
            idx_i = self.perturb_indices[
                np.where(mobile_syms[self.perturb_indices] == sp_i)[0]]
            idx_j = self.perturb_indices[
                np.where(mobile_syms[self.perturb_indices] == sp_j)[0]]
            i = idx_i[self.rng.integers(len(idx_i))]
            j = idx_j[self.rng.integers(len(idx_j))]
            # exchange positions
            pos = trial.positions.copy()
            pos[i], pos[j] = pos[j].copy(), pos[i].copy()
            trial.positions = pos
            # rattle the two swapped atoms a little
            for a in (i, j):
                trial.positions[a] += self.rng.normal(
                    0.0, self.swap_rattle, 3)
        return trial

    def _propose_move(self) -> Atoms:
        """Choose swap vs rattle by swap_prob and produce the trial structure.

        Falls back to a rattle when a swap is unavailable or returns None.
        """
        use_swap = (self.swap_prob > 0 and self.swap_available
                    and self.rng.random() < self.swap_prob)
        if use_swap:
            trial = self._propose_swap()
            if trial is not None:
                self.n_swap_moves += 1
                return trial
        self.n_rattle_moves += 1
        return self._propose()

    def _energy_of(self, atoms: Atoms) -> float:
        E = self.gpr.predict_energy(atoms)
        if abs(E) > 1e4:
            return float("nan")
        return E

    # -- Wang-Landau bookkeeping --------------------------------------------

    def _visit(self, b: int):
        self.ln_g[b] += self.ln_f
        self.H[b] += 1

    def _check_flatness(self) -> bool:
        visited = self.H > 0
        if not visited.any():
            return False
        mean_H = self.H[visited].mean()
        min_H = self.H[visited].min()
        return min_H > self.flatness_criterion * mean_H

    def _maybe_refine(self):
        """Standard f->sqrt(f) scheme, then switch to the 1/t algorithm."""
        if not self.switched_to_1_over_t:
            if self.step % self.check_interval == 0:
                if self._check_flatness():
                    self.ln_f /= 2.0
                    self.H[:] = 0
                    self.stage += 1
                    print(f"  stage {self.stage}: ln_f = {self.ln_f:.6e} "
                          f"(flat at step {self.step})")
            if self.stage >= self.n_stages_standard:
                self.switched_to_1_over_t = True
                self.step_at_switch = self.step
                self.H[:] = 0
                print(f"  Switching to 1/t algorithm at step {self.step} "
                      f"(after {self.stage} standard halvings)")
        else:
            # 1/t algorithm: ln_f = 1/t' for elapsed steps since the switch
            self.ln_f = 1.0 / max(self.step - self.step_at_switch, 1)

    # -- Initialisation & run ------------------------------------------------

    def initialize(self, start_from_top: bool = False):
        """Pick the initial walker.

        Default (``start_from_top=False``): start from the global minimum
        (lowest-energy DB structure, rel E ≈ 0) and let the walk ascend — the
        robust choice. This avoids the previous behaviour where starting at the
        'flat' (highest) structure could land ABOVE the tracked window (rel E
        > e_max, capped into the top bin) and trap the walk there.

        With ``start_from_top=True``: pick the highest-rel-energy DB structure
        whose rel energy is STRICTLY INSIDE [e_min, e_max) — out-of-window
        energies (rel >= e_max or rel < e_min) are rejected so the walker never
        starts outside the tracked range.
        """
        if start_from_top:
            candidates = []
            for s in self.db_structures:
                rel = self.rel_energy(s)
                # strictly inside the tracked window [e_min, e_max)
                if self.e_min <= rel < self.e_max:
                    candidates.append((rel, s))
            if not candidates:
                raise RuntimeError(
                    "No DB structure falls strictly inside the bin window "
                    f"[{self.e_min}, {self.e_max}) eV/atom. Widen --e-max.")
            rel, s = max(candidates, key=lambda c: c[0])   # highest in-window
        else:
            idx = int(np.argmin(self.db_energies))
            s = self.db_structures[idx]
            rel = self.rel_energy(s)
            # guard: if even the minimum structure is out of window, still allow
            # (it is at/near rel 0 which is inside [e_min, e_max) for e_min=0)
        self.x_current = s.copy()
        self.E_current = self._energy_of(s)
        self.bin_current = self.get_bin(rel)
        print(f"[WangLandau] init: rel E = {rel:.4f} eV/atom "
              f"(bin {self.bin_current})")

    def run(self, n_steps: int, progress_every: int = 50000):
        """Run the Wang-Landau walk for ``n_steps`` MC steps."""
        print(f"\nWang-Landau: {n_steps} MC steps, {self.n_bins} bins, "
              f"ln_f_init=1.0")
        print("=" * 60)
        for _ in range(n_steps):
            self.step += 1
            trial = self._propose_move()
            E_trial = self._energy_of(trial)
            rel_trial = (E_trial - self.E_ref) / self.n_atoms \
                if np.isfinite(E_trial) else float("nan")
            # Extrapolation guard: a trial far above e_reject is an unphysical GPR
            # extrapolation — reject it (revisit the current bin) instead of
            # capping it into the top bin, where it would trap the walk.
            if np.isfinite(rel_trial) and rel_trial > self.e_reject:
                self._visit(self.bin_current)
                self._maybe_refine()
                continue
            bin_trial = self.get_bin(rel_trial) if np.isfinite(rel_trial) else -1
            if bin_trial < 0:
                # out-of-range trial (below floor or unphysical) -> reject
                self._visit(self.bin_current)
                self._maybe_refine()
                continue

            # Wang-Landau acceptance: log(r) < ln_g(cur) - ln_g(trial)
            r = self.rng.random()
            if np.log(r) < self.ln_g[self.bin_current] - self.ln_g[bin_trial]:
                self.x_current = trial
                self.E_current = E_trial
                self.bin_current = bin_trial

            self._visit(self.bin_current)
            self._maybe_refine()

            if self.step % progress_every == 0:
                visited = int((self.H > 0).sum())
                print(f"  step {self.step:9d}  stage {self.stage:2d}  "
                      f"ln_f {self.ln_f:.3e}  visited {visited}/{self.n_bins}")

        print(f"\nTotal MC steps = {self.step}, stages reached = {self.stage}")
        print(f"  moves: {self.n_rattle_moves} rattle, {self.n_swap_moves} swap")
        if self.switched_to_1_over_t:
            print("Used the 1/t algorithm for the final stage.")
        else:
            print("NOTE: standard f->sqrt(f) scheme; did not reach the 1/t "
                  "switch. Increase n_steps or lower n_stages_standard.")

    # -- Results -------------------------------------------------------------

    def g_of_E(self):
        """Return (bin_centers_rel, ln_g)."""
        return self.bin_centers_rel.copy(), self.ln_g.copy()

    def save(self, output_dir: str):
        """Write g(E) (log density of states) and the final histogram to CSV."""
        import os
        from pathlib import Path
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        rows = np.column_stack([
            self.bin_centers_rel,
            self.ln_g,
            self.H,
        ])
        np.savetxt(out / "g_of_E.csv", rows, delimiter=',',
                   header='rel_eV_per_atom,ln_g,H', comments='')
        print(f"  Wrote g_of_E.csv (rel_eV_per_atom, ln_g, H) to {out}")
        return out
