#!/usr/bin/env python3
"""LandauPlusSampler — basin-hopping (inherent-structure) Wang-Landau sampling
on a GPR surrogate.

Adapted from `c_landausampling`'s ``WangLandauSampler``. The three differences:

1. **Markov walk over basin minima.** Each proposal is a rattle of the *current*
   structure (all mobile Fe atoms, uniform-in-volume radius ``rattle``) followed
   by a **mandatory GPR relaxation** (BFGS on the surrogate, substrate fixed by
   ``FixAtoms`` and the Fe atoms confined by ``BoxConstraint``). The accepted
   structure becomes the new current state, so the walk is a genuine Markov
   chain; the DOS it recovers is the *inherent-structure* (basin-minimum) DOS,
   not the configurational DOS.

2. **Flat-reference initialisation.** The walker starts from the highest-energy
   (flat monolayer) database structure and descends; Wang-Landau's flat-histogram
   pressure pushes it back up in energy so it traverses the flat<->island
   barrier in both directions.

3. **Ensemble collection + flat/island labelling.** Every accepted (relaxed)
   structure is tagged with its Fe z-spread (the flat/island order parameter:
   spread < 1.0 Angstrom = flat monolayer; >= 1.0 = 3D island) and recorded.

The acceptance rule, ``ln(r) < ln_g[cur] - ln_g[trial]``, the standard ``f -> f/2``
flatness schedule, and the 1/t tail (Belardinelli & Pereyra 2007) are unchanged.

IMPORTANT (from the spec): the recovered flat/island weight is delta-sensitive —
the rattle amplitude ``rattle`` controls how far the walk can hop between basins.
ALWAYS test multiple ``--rattle`` values before trusting the flat/island ratio.
"""

from __future__ import annotations

__version__ = "1.0.0"

import os
from typing import List, Optional

import numpy as np
from ase import Atoms

from agox.utils.constraints.box_constraint import BoxConstraint


class LandauPlusSampler:
    """Basin-hopping Wang-Landau sampler over a GPR energy surrogate."""

    def __init__(
        self,
        gpr,
        db_structures: List[Atoms],
        db_energies: np.ndarray,
        n_bins: int = 50,
        e_min: float = 0.0,
        e_max: float = 0.75,
        e_reject: Optional[float] = None,
        rattle: float = 1.5,
        relax_steps: int = 100,
        perturb_symbols: str = "Fe",
        flat_island_spread_aa: float = 1.0,
        box_z_spread_floor: float = 2.1,
        box_z_height_mult: float = 4.0,
        corner_z_offset: float = 0.5,
        flatness_criterion: float = 0.80,
        check_interval: int = 5000,
        n_stages_standard: int = 14,
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

        # Rattle amplitude (Angstrom) — the basin-hopping "hop" scale.
        self.rattle = float(rattle)
        self.relax_steps = int(relax_steps)

        # Extrapolation-rejection threshold (default 5*e_max): a trial whose rel
        # energy exceeds e_reject is treated as an unphysical GPR extrapolation
        # and REJECTED (revisits current bin) instead of being capped into the
        # top bin (which would trap the walk).
        if e_reject is not None and float(e_reject) > self.e_max:
            self.e_reject = float(e_reject)
        else:
            self.e_reject = 5.0 * self.e_max
        print(f"[LandauPlus] extrapolation guard: reject rel E > {self.e_reject:.4f} "
              f"eV/atom (moderate over-window up to e_max {self.e_max:.3f} is capped "
              f"into the top bin)")

        # Mobile (rattle/relax) vs fixed (substrate) atom split by species.
        perturb_list = [s.strip() for s in str(perturb_symbols).split(",")
                        if s.strip()]
        symbols = np.array(db_structures[0].get_chemical_symbols())
        self.perturb_indices = np.where(np.isin(symbols, perturb_list))[0]
        if len(self.perturb_indices) == 0:
            raise ValueError(
                f"No atoms with symbol(s) {perturb_list} found in the dataset.")
        self.fixed_indices = np.setdiff1d(np.arange(self.n_atoms),
                                          self.perturb_indices)

        # --- Relaxation constraints (mirror the GO run's environment.get_constraints)
        # FixAtoms on the substrate (Mg/O) + BoxConstraint confining the Fe atoms
        # to the deposition box, pbc = [True, True, False].
        from ase.constraints import FixAtoms
        self._fix = FixAtoms(indices=list(map(int, self.fixed_indices)))
        self._box = self._build_box_constraint(
            db_structures[0], box_z_spread_floor, box_z_height_mult,
            corner_z_offset)
        self._relax_constraints = [self._box, self._fix]

        # Flat/island order-parameter threshold (Fe z-spread, Angstrom).
        self.flat_island_spread_aa = float(flat_island_spread_aa)

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

        # Current walker
        self.x_current: Optional[Atoms] = None
        self.E_current = float("nan")
        self.bin_current = -1

        # Ensemble of accepted (relaxed) structures: parallel lists.
        self.ensemble_structs: List[Atoms] = []
        self.ensemble_rows = []   # (energy, rel_eV_per_atom, fe_z_spread, label)

        print(f"[LandauPlus] bins={self.n_bins} over [{e_min}, {e_max}] "
              f"eV/atom rel (width {self.bin_width:.4f})")
        print(f"[LandauPlus] rattle={self.rattle:.3f} A (uniform-in-volume) on "
              f"{len(self.perturb_indices)} {perturb_list} atoms; "
              f"GPR relax {self.relax_steps} BFGS steps; fixing "
              f"{len(self.fixed_indices)} substrate atoms")

    # -- Helpers --------------------------------------------------------------

    def _build_box_constraint(self, ref: Atoms, z_spread_floor, z_height_mult,
                              corner_z_offset) -> BoxConstraint:
        """Reconstruct the GO run's BoxConstraint from a reference structure.

        confinement_corner = [0, 0, substrate_z_max + corner_z_offset]
        confinement_cell[2,2] = max(Fe z-spread, z_spread_floor) * z_height_mult
        indices = Fe (mobile) atoms; pbc = [True, True, False].
        """
        z = ref.positions[:, 2]
        fe_z = z[self.perturb_indices]
        sub_z = z[self.fixed_indices]
        substrate_z_max = sub_z.max()
        h_dep = max(fe_z.max() - fe_z.min(), z_spread_floor)

        cell = ref.get_cell().copy()
        cell[2, 2] = h_dep * z_height_mult
        corner = np.array([0.0, 0.0, substrate_z_max + corner_z_offset])

        box = BoxConstraint(confinement_cell=cell, confinement_corner=corner,
                            indices=self.perturb_indices,
                            pbc=[True, True, False])
        print(f"[LandauPlus] BoxConstraint: corner={corner}, cell_z={cell[2,2]:.3f} A "
              f"(h_dep={h_dep:.3f}); Fe confined, pbc=[T,T,F]")
        return box

    def rel_energy(self, atoms: Atoms) -> float:
        """Relative energy per atom above the training minimum (eV/atom)."""
        E = self.gpr.predict_energy(atoms)
        return (E - self.E_ref) / self.n_atoms

    def get_bin(self, rel: float) -> int:
        """0-indexed bin for a relative energy; -1 if below the range floor.

        Energies above ``e_max`` are capped into the top bin.
        """
        if rel < self.e_min:
            return -1
        b = int((rel - self.e_min) / self.bin_width)
        return min(b, self.n_bins - 1)

    def fe_z_spread(self, atoms: Atoms) -> float:
        """Fe z-spread (max - min of Fe z-coords) — the flat/island order param."""
        z = atoms.positions[self.perturb_indices, 2]
        return float(z.max() - z.min())

    def label(self, atoms: Atoms) -> str:
        """'flat' (monolayer) vs 'island' (3D cluster) by Fe z-spread."""
        return "flat" if self.fe_z_spread(atoms) < self.flat_island_spread_aa \
            else "island"

    # -- Moves -----------------------------------------------------------------

    def _propose(self) -> Atoms:
        """Uniform-in-volume rattle of all mobile (Fe) atoms about the current
        structure (radius ``rattle``). Mirrors the GO ``HeteroStructRandomize``
        displacement: radius = rattle * U^(1/3) with a uniformly random
        direction, i.e. each Fe atom is displaced uniformly within a ball of
        radius ``rattle``."""
        trial = self.x_current.copy()
        n = len(self.perturb_indices)
        # radius uniform in ball volume
        radius = self.rattle * self.rng.random(n) ** (1.0 / 3.0)
        # random unit direction
        v = self.rng.normal(0.0, 1.0, (n, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        disp = radius[:, None] * v
        trial.positions[self.perturb_indices] += disp
        return trial

    def _energy_of(self, atoms: Atoms) -> float:
        E = self.gpr.predict_energy(atoms)
        if abs(E) > 1e4:
            return float("nan")
        return E

    def _relax(self, atoms: Atoms) -> Atoms:
        """Relax a trial structure on the GPR potential (basin-hopping step).

        Attaches the GPR as the ASE calculator, applies FixAtoms(substrate) +
        BoxConstraint(Fe), and runs BFGS for ``relax_steps`` (default 100, the
        GO run's cap). Termination is ``fmax OR steps``, whichever first, so a
        structure that hits the step cap or a constraint wall still returns.
        """
        import ase.optimize

        relaxed = atoms.copy()
        relaxed.set_constraint(self._relax_constraints)
        relaxed.calc = self.gpr
        try:
            opt = ase.optimize.BFGS(relaxed, logfile=None)
            opt.run(fmax=0.05, steps=self.relax_steps)
        except Exception as e:  # relaxation failure -> return unrelaxed
            print(f"[LandauPlus] relax failed ({e}); using unrelaxed trial")
            return atoms
        return relaxed

    # -- Wang-Landau bookkeeping ---------------------------------------------

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
        """Standard f->f/2 scheme, then switch to the 1/t algorithm."""
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
            self.ln_f = 1.0 / max(self.step - self.step_at_switch, 1)

    # -- Initialisation & run --------------------------------------------------

    def initialize(self):
        """Initialise the walker at the FLAT reference: the highest-energy
        database structure (the flat monolayer, rel E ~ e_max-ward)."""
        idx = int(np.argmax(self.db_energies))
        s = self.db_structures[idx]
        rel = self.rel_energy(s)
        self.x_current = s.copy()
        self.E_current = self._energy_of(s)
        self.bin_current = self.get_bin(rel)
        # record the initial structure as the first ensemble member
        self._record(s, rel)
        print(f"[LandauPlus] init (flat reference): rel E = {rel:.4f} eV/atom "
              f"(bin {self.bin_current}), Fe z-spread = {self.fe_z_spread(s):.3f} A "
              f"({self.label(s)})")

    def _record(self, atoms: Atoms, rel: float):
        """Append an accepted structure + its row to the ensemble."""
        self.ensemble_structs.append(atoms.copy())
        E = float(self.gpr.predict_energy(atoms))
        spread = self.fe_z_spread(atoms)
        self.ensemble_rows.append(
            (E, float(rel), spread, self.label(atoms)))

    def run(self, n_steps: int, progress_every: int = 5000):
        """Run the basin-hopping Wang-Landau walk for ``n_steps`` MC steps."""
        print(f"\nLandau-Plus: {n_steps} MC steps, {self.n_bins} bins, "
              f"ln_f_init=1.0")
        print("=" * 60)
        for _ in range(n_steps):
            self.step += 1
            trial = self._propose()
            trial = self._relax(trial)          # basin-hopping, always
            E_trial = self._energy_of(trial)
            rel_trial = (E_trial - self.E_ref) / self.n_atoms \
                if np.isfinite(E_trial) else float("nan")

            # Extrapolation guard
            if np.isfinite(rel_trial) and rel_trial > self.e_reject:
                self._visit(self.bin_current)
                self._maybe_refine()
                continue
            bin_trial = self.get_bin(rel_trial) if np.isfinite(rel_trial) else -1
            if bin_trial < 0:
                self._visit(self.bin_current)
                self._maybe_refine()
                continue

            # Wang-Landau acceptance
            r = self.rng.random()
            if np.log(r) < self.ln_g[self.bin_current] - self.ln_g[bin_trial]:
                self.x_current = trial
                self.E_current = E_trial
                self.bin_current = bin_trial
                self._record(trial, rel_trial)

            self._visit(self.bin_current)
            self._maybe_refine()

            if self.step % progress_every == 0:
                visited = int((self.H > 0).sum())
                print(f"  step {self.step:9d}  stage {self.stage:2d}  "
                      f"ln_f {self.ln_f:.3e}  visited {visited}/{self.n_bins}")

        print(f"\nTotal MC steps = {self.step}, stages reached = {self.stage}")
        print(f"  accepted ensemble size = {len(self.ensemble_structs)}")
        if self.switched_to_1_over_t:
            print("Used the 1/t algorithm for the final stage.")
        else:
            print("NOTE: standard f->f/2 scheme; did not reach the 1/t switch. "
                  "Increase n_steps or lower n_stages_standard.")

    # -- Results --------------------------------------------------------------

    def g_of_E(self):
        """Return (bin_centers_rel, ln_g)."""
        return self.bin_centers_rel.copy(), self.ln_g.copy()

    def save(self, output_dir: str):
        """Write g(E), the histogram, and the ensemble (traj + csv) to disk."""
        from pathlib import Path
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        np.savetxt(out / "g_of_E.csv",
                   np.column_stack([self.bin_centers_rel, self.ln_g, self.H]),
                   delimiter=',', header='rel_eV_per_atom,ln_g,H', comments='')
        print(f"  Wrote g_of_E.csv (rel_eV_per_atom, ln_g, H)")

        # Ensemble of accepted structures
        from ase.io import write as ase_write
        ase_write(str(out / "ensemble.traj"), self.ensemble_structs)
        rows = [[E, rel, sp, lab] for (E, rel, sp, lab) in self.ensemble_rows]
        np.savetxt(out / "ensemble.csv", np.asarray(rows, dtype=object),
                   delimiter=',', fmt='%s',
                   header='energy_eV,rel_eV_per_atom,fe_z_spread_A,flat_island',
                   comments='')
        print(f"  Wrote ensemble.traj + ensemble.csv "
              f"({len(self.ensemble_structs)} accepted structures)")
        return out