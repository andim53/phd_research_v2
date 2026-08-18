# GPAW API index (verified against 25.7.0)

Signatures captured with `inspect.signature` from the installed package.

## Calculator

```python
from gpaw import GPAW
GPAW(restart=None, *, label=None, timer=None, communicator=None,
     txt='?', parallel=None, **kwargs)
```
`GPAW` is `gpaw.calculator.GPAW` by default; set `GPAW_NEW=1` to alias it to
`gpaw.new.ase_interface.GPAW` (the "calculator-in-python" rewrite).

Key methods (ASE Calculator interface + GPAW extras):
- `get_potential_energy(atoms=None, force_consistent=False) -> float`
- `get_forces(atoms=None)`, `get_stress(atoms=None)`
- `get_dipole_moment(atoms=None)`, `get_magnetic_moment(atoms=None)`,
  `get_magnetic_moments(atoms=None)`
- `get_eigenvalues(kpt=0, spin=0, broadcast=True)`
- `get_fermi_level()`, `get_ibz_k_points()`, `get_number_of_bands()`,
  `get_number_of_spins()`
- `get_homo_lumo(spin=None)`, `get_xc_functional() -> str`
- `get_electrostatic_potential()`, `get_pseudodensity()`, `get_wigner_seitz_radius()`
- `write(filename, mode='')` — mode `'all'` stores wavefunctions/density
- `read(filename)`, `new(**kwargs)` (inherit params), `fixed_density(...)`,
  `band_structure()`, `set(**kwargs)`, `calculate(...)`, `icalculate(...)`,
  `initialize_positions`, `set_positions`, `close()`
- `implemented_properties = ['energy','free_energy','forces','stress','dipole','magmom','magmoms']`

`default_parameters` (full):
```python
{'mode': None, 'xc': 'LDA', 'occupations': None, 'poissonsolver': None,
 'h': None, 'gpts': None, 'kpts': [(0.0,0.0,0.0)], 'nbands': None,
 'charge': 0, 'setups': {}, 'basis': {}, 'spinpol': None, 'filter': None,
 'mixer': None, 'eigensolver': None, 'background_charge': None,
 'experimental': {'reuse_wfs_method': 'paw', 'niter_fixdensity': 0,
                  'magmoms': None, 'soc': None, 'kpt_refine': None},
 'external': None, 'random': False, 'hund': False, 'maxiter': 333,
 'symmetry': {'point_group': True, 'time_reversal': True, 'symmorphic': True,
              'tolerance': 1e-7, 'do_not_symmetrize_the_density': None},
 'convergence': {'energy': 0.0005, 'density': 1.0e-4, 'eigenstates': 4.0e-8,
                 'bands': 'occupied'},
 'verbose': 0, 'fixdensity': False, 'dtype': None}
```
`default_parallel` keys: `kpt, domain, band, order ('kdb'), stridebands,
augment_grids, sl_auto, sl_default, sl_diagonalize, sl_inverse_cholesky,
sl_lcao, sl_lrtddft, use_elpa, elpasolver ('2stage'), buffer_size`.

## Modes (gpaw.wavefunctions)

```python
from gpaw.wavefunctions.fd import FD
FD(nn=3, interpolation=3, force_complex_dtype=False)

from gpaw.wavefunctions.lcao import LCAO
LCAO(atomic_correction=None, interpolation=3, force_complex_dtype=False)

from gpaw.wavefunctions.pw import PW
PW(ecut=340.0, *, fftwflags=0, cell=None, gammacentered=False,
   pulay_stress=None, dedecut=None, force_complex_dtype=False,
   interpolation='fft')
```
String aliases: `mode='fd'`, `'lcao'`, `'pw'`. All three are also lazily exposed as
`gpaw.FD`, `gpaw.LCAO`, `gpaw.PW`.

## Mixers (gpaw.mixer)

`Mixer`, `MixerSum`, `MixerDif`, `MixerSum2`, `MixerFull`. Exposed lazily at
`gpaw.Mixer` etc. (wrappers defer to `gpaw.new.mixer`; `__init__(*args, **kwargs)`).

## Occupations / smearing (gpaw.occupations)

- `FermiDirac(width=0.1)` — default `width` is 0.1 eV (verify per use)
- `MethfesselPaxton(width=0.1)`
- `MarzariVanderbilt(width=0.1)`
Exposed at `gpaw.FermiDirac` etc. Also `ZeroWidth`, `FixedOccupations`, `OrbitalFree`.

## Eigensolvers (gpaw.eigensolvers)

`CG`, `Davidson`, `RMMDIIS`, `DirectLCAO` (all exposed at `gpaw.*`). `RMM_DIIS` is a
deprecated alias for `RMMDIIS` that emits a warning.

## Poisson solvers (gpaw.poisson)

`PoissonSolver` (lazy export), plus `FFTPoissonSolver`, `FDPoissonSolver` in
`gpaw.poisson`.

## DOS / band structure (gpaw.dos)

```python
from gpaw.dos import IBZWaveFunctions, DOSCalculator
IBZWaveFunctions(calc)                      # IBZ eigenvalues + PAW projections
DOSCalculator(wfs, setups=None, cell=None, shift_fermi_level=True)
DOSCalculator.from_calculator(filename, soc=False, theta=0.0, phi=0.0,
                              shift_fermi_level=True)  # filename = .gpw path or calc
dos.get_energies(emin=None, emax=None, npoints=100) -> ndarray
dos.raw_dos(energies, spin=None, width=0.1) -> ndarray
dos.raw_pdos(energies, a, l, m=None, spin=None, width=0.1) -> ndarray
```
`BZWaveFunctions` and `soc_eigenstates` live in `gpaw.spinorbit`.
Free functions: `gaussian_dos(eig_kn, weight_kn, weight_k, energies, width)`,
`linear_tetrahedron_dos(eig_kn, weight_kn, energies, cell, size, bz2ibz_map=None)`,
`get_projector_numbers(setup, ell) -> List[int]`.

Band structure (ASE):
```python
bs = calc.band_structure()   # -> ase.spectrum.band_structure.BandStructure
bs.plot(filename=..., show=True, emax=...)
```

## Restart / IO

```python
from gpaw import restart
atoms, calc = restart(filename, Class=None, **kwargs)  # Class defaults to gpaw.GPAW
```
Also `gpaw.read_rc_file()`, `gpaw.setup_paths`, `gpaw.initialize_data_paths()`.

## Exceptions

`ConvergenceError`, `KohnShamConvergenceError`, `PoissonConvergenceError`,
`KPointError`, `BadParallelization` (all in `gpaw` namespace).

## Environment variables

Boolean: `GPAW_NEW`, `GPAW_CPUPY`, `GPAW_USE_GPUS`, `GPAW_TRACE`,
`GPAW_NO_C_EXTENSION`, `GPAW_MPI4PY`. String: `GPAW_MPI`, `GPAW_MPI_OPTIONS`,
`GPAW_SETUP_PATH`.
