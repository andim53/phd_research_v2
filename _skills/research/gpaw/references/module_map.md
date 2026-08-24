# GPAW subpackage map (25.7.0)

One-line purpose per module/package under `gpaw/`. Full tree is large; the ones most
likely to matter for authoring calculations are listed first.

## Core (used by every calculation)

- `calculator.py` — `GPAW` class, the ASE Calculator frontend (`default_parameters`,
  `parallel`, `set`, `calculate`, `initialize`, `write`/`read`).
- `new/` — modern "calculator-in-python" engine: `ase_interface.py` (`ASECalculator`),
  `density.py`, `hamiltonian.py`, `potential.py`, `eigensolver.py`, `scf.py`, `xc.py`,
  `smearing.py`, `brillouin.py`, `ibzwfs.py`, `gpw.py`, `timer.py`, plus `fd/`, `pw/`,
  `lcao/`, `pwfd/`, `tb/` sub-mode implementations.
- `wavefunctions/` — mode objects: `fd.py` (`FD`), `lcao.py` (`LCAO`), `pw.py` (`PW`),
  `mode.py` (base `Mode`), `base.py`, `arrays.py`, `fdpw.py` (`FDPW` mixed mode).
- `eigensolvers/` — `cg.py` (`CG`), `davidson.py`, `rmmdiis.py` (`RMMDIIS`),
  `direct.py` (`DirectLCAO`), `eigensolver.py`, `diagonalizerbackend.py`.
- `mixer.py` — density/potential mixing: `Mixer`, `MixerSum`, `MixerDif`, `MixerSum2`,
  `MixerFull`.
- `occupations.py` — Fermi-Dirac / Methfessel-Paxton / Marzari-Vanderbilt smearing and
  fixed/zero-width occupations.
- `xc/` — exchange-correlation: `lda.py`, `gga.py`, `mgga.py`, `hybrid.py`, `libxc.py`
  (libxc bindings), `vdw.py` (dispersion), `sic.py`, `tb09.py`, `gllb/`, `rpa.py`,
  `fxc.py` / `fxc_kernels.py` (response kernels), `ri/` (resolution-of-identity),
  `pawcorrection.py`, `noncollinear.py`.
- `poisson.py` — `PoissonSolver`, `FFTPoissonSolver`, `FDPoissonSolver`.
- `dft.py` — the DFT Hamiltonian/functional assembly layer.
- `setup.py` / `setup_data.py` — PAW setup (`Setup`, `create_setup`) loading.

## Post-processing / analysis

- `dos.py` — `DOSCalculator`, `IBZWaveFunctions`, `gaussian_dos`,
  `linear_tetrahedron_dos`, `get_projector_numbers`.
- `spinorbit.py` — `soc_eigenstates`, `BZWaveFunctions` (spin-orbit coupling).
- `dos.py` + `ase.spectrum.band_structure` — band structure plotting.
- `analyse/` — analysis (Hirshfeld charges, etc.).
- `berryphase.py` — Berry phase / electric polarization.
- `borncharges.py` — Born effective charges.
- `hyperfine.py` — hyperfine parameters.
- `xas.py` — X-ray absorption spectra.
- `elf.py` — electron localization function.
- `unfold.py` — band unfolding.

## Response / excited states

- `response/` — density-functional perturbation theory (DFPT), dielectric/GW.
- `lrtddft.py` / `lrtddft2.py` — linear-response TDDFT.
- `tddft/`, `lcaotddft/` — real-time TDDFT propagation.
- `fdtd/` — finite-difference time-domain electrodynamics (not DFT).
- `inducedfield/` — induced-field DFT.

## Structure / magnetism / defects

- `symmetry.py`, `point_groups/`, `rotation.py`, `atomrotations.py` — symmetry analysis.
- `hubbard.py` — DFT+U (Hubbard U corrections).
- `bfield.py`, `zero_field_splitting.py`, `mom.py` — magnetic field / moments.
- `defects/` — charged-defect corrections.
- `cdft/` — constrained DFT.
- `pes/` — potential energy surfaces / NEB.
- `directmin/`, `nlopt/` — direct (orbital) minimization, non-linear optimization.

## Coupling / embedding

- `wannier.py`, `wannier90.py`, `wannier/` — maximally-localized Wannier functions.
- `elph/` — electron-phonon coupling.
- `raman/` — Raman intensities.
- `solvation/` — implicit solvation models.
- `external.py` — external potentials.
- `dipole_correction.py` — dipole correction for slabs.

## I/O / infrastructure

- `io/` — file readers/writers (e.g. GPAW, VASP, spglib formats).
- `cli/` — `gpaw` command subcommands (`run`, `info`, `dos`, `gpw`, `atom`, `dataset`,
  `sbatch`, `symmetry`, `install-data`, ...).
- `mpi.py`, `mpi4pywrapper.py`, `blacs.py` — MPI / ScaLAPACK / BLACS parallelism.
- `utilities/` — misc helpers (`gradient`, `unpack`, `grid`).
- `atom/` — isolated all-electron atom solver (`gpaw atom`).
- `sphere/`, `spherical_harmonics.py`, `spline.py` — radial grids / spherical harmonics.
- `core/` — PAW core-region radial integrals.
- `gpu/` — GPU (CuPy) acceleration.
- `hybrids/` — hybrid-functional support.
- `data/` — bundled data tables.
- `test/` — test suite; `doctools/` — doctest helpers; `benchmark/` — benchmarks.
