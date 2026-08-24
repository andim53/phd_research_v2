---
name: gpaw
description: Use when writing, running, or debugging GPAW DFT code (GPAW calculator, FD/LCAO/PW modes, DOS, band structure, relaxations, restart files) in the agox_v2 conda env. GPAW 25.7.0 + ASE 3.25.0.
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [gpaw, dft, ase, paw, density-functional-theory, materials-science, simulation]
    related_skills: [simulation-analysis]
---

# GPAW (DFT calculator for ASE)

## Overview

GPAW is a projector-augmented-wave (PAW) density-functional-theory code that runs
as an ASE calculator. This skill is grounded in the exact install in the `agox_v2`
conda env: **GPAW 25.7.0** paired with **ASE 3.25.0**, at
`/home/think/miniconda3/envs/agox_v2/lib/python3.11/site-packages/gpaw`.

The API in 25.x is version-sensitive — notably the **DOS/PDOS API was fully reworked**
(see "DOS" below); most older tutorials use `from gpaw import DOS`, which now fails.

## When to Use

- Writing a GPAW ground-state, relaxation, band-structure, or DOS calculation.
- Debugging GPAW errors, choosing a `mode` / `xc` / `kpts` / mixer / occupations.
- Working with `.gpw` restart files or `calc.write()` / `gpaw.restart()`.
- Answering "which GPAW class/function do I use for X".

Do NOT use for: non-GPAW ASE calculators (VASP/EMT/LJ), or general AGOX pipeline work
(see the `simulation-analysis` skill for that).

## Environment

Always invoke the env's Python by absolute path (the base `python3` has no GPAW/ASE):

```
/home/think/miniconda3/envs/agox_v2/bin/python
```

For headless runs, set `matplotlib.use('Agg')` before importing anything that plots.
PAW setup files (full periodic table: LDA/PBE/RPBE/revPBE/GLLBSC + dzp basis) ship in
`gpaw_data/setups`, auto-discovered via `gpaw.setup_paths`. No `gpaw install-data` needed
for standard elements.

## Architecture

- `GPAW` is an ASE `Calculator` subclass (`gpaw/calculator.py`). Top-level import is
  `from gpaw import GPAW`. Under the hood 25.x routes the actual SCF work through the
  modern engine in `gpaw/new/` (set `GPAW_NEW=1` to expose `gpaw.new.ase_interface.GPAW`
  directly as `gpaw.GPAW`).
- Three **wavefunction modes** (all passed via the `mode` parameter):
  - `'fd'` / `FD(nn=3, interpolation=3, force_complex_dtype=False)` — real-space finite
    difference. Default grid spacing via `h` (Å) or `gpts`.
  - `'lcao'` / `LCAO(atomic_correction=None, interpolation=3, force_complex_dtype=False)`
    — linear combination of atomic orbitals; fast, good for large systems / pre-convergence.
  - `'pw'` / `PW(ecut=340, *, fftwflags=0, cell=None, gammacentered=False,
    pulay_stress=None, dedecut=None, force_complex_dtype=False, interpolation='fft')`
    — plane-wave; plane-wave cutoff in eV via `ecut` (use **with** `h`/`gpts` for the
    density grid, or `dedecut` to auto-set it).
- The old `'fd'`/`'lcao'`/`'pw'` string forms are still accepted (aliases for the classes).

## Constructor parameters (GPAW)

`GPAW.__init__(self, restart=None, *, label=None, timer=None, communicator=None,
txt='?', parallel=None, **kwargs)` — everything else comes through `**kwargs`. The
authoritative defaults (from `GPAW.default_parameters`):

| Param | Default | Notes |
|---|---|---|
| `mode` | `None` | `'fd'`, `'lcao'`, `'pw'` (or the mode objects) |
| `xc` | `'LDA'` | e.g. `'PBE'`, `'RPBE'`, `'PBE0'`, `'HSE06'`, `'LDA'`, `'revPBE'` |
| `h` | `None` | grid spacing in Å (fd/pw density grid) |
| `gpts` | `None` | explicit grid `(nx, ny, nz)` |
| `kpts` | `[(0,0,0)]` | int (Monkhorst-Pack density), list/tuple of k-points, or dict `{'size':(..), 'gamma':..}` / `{'path':..,'npoints':..}` |
| `nbands` | `None` | extra empty bands above valence |
| `charge` | `0` | net charge (electrons) |
| `spinpol` | `None` | `True` for collinear spin-polarized |
| `setups` | `{}` | per-symbol PAW setup overrides |
| `basis` | `{}` | per-symbol LCAO basis overrides |
| `mixer` | `None` | `Mixer`, `MixerSum`, `MixerDif`, `MixerSum2`, `MixerFull` |
| `eigensolver` | `None` | `CG`, `Davidson`, `RMMDIIS`, `DirectLCAO` |
| `occupations` | `None` | `FermiDirac(width)`, `MethfesselPaxton(width)`, `MarzariVanderbilt(width)` |
| `maxiter` | `333` | SCF iteration cap |
| `symmetry` | dict (see api_index) | `{'point_group': True, 'time_reversal': True, ...}` |
| `convergence` | dict | `{'energy': 0.0005, 'density': 1e-4, 'eigenstates': 4e-8, 'bands': 'occupied'}` |
| `parallel` | dict | MPI decomposition: `{'domain':.., 'band':.., 'kpt':..}` |
| `txt` | `'?'` | log output; `'-'` = stdout, `None` = silent |

`GPAW` implements ASE methods `get_potential_energy`, `get_forces`, `get_stress`,
`get_dipole_moment`, `get_magnetic_moment(s)`, `get_eigenvalues(kpt, spin)`,
`get_fermi_level`, `get_ibz_k_points`, `get_number_of_spins`, `get_homo_lumo`,
`get_xc_functional`, `write`, `fixed_density`, `band_structure`, plus
`implemented_properties = ['energy','free_energy','forces','stress','dipole','magmom','magmoms']`.

## DOS (new API — replaces `DOS`/`PDOS`)

`gpaw.dos.DOS` and `gpaw.dos.PDOS` **no longer exist**. Use `DOSCalculator`:

```python
from gpaw.dos import DOSCalculator

dos = DOSCalculator.from_calculator('calc.gpw')          # or pass the calc object
energies = dos.get_energies(emin=-5, emax=5, npoints=200)
total = dos.raw_dos(energies, width=0.1)                 # width=0 -> tetrahedron
pdos = dos.raw_pdos(energies, a=0, l=1, m=None, spin=None, width=0.1)
```

Underlying helpers (also importable): `IBZWaveFunctions(calc)`, `BZWaveFunctions`
(from `gpaw.spinorbit`), `soc_eigenstates(calc)`, `gaussian_dos(...)`,
`linear_tetrahedron_dos(...)`, `get_projector_numbers(setup, l)`. Full signatures in
`references/api_index.md`.

## Band structure

```python
bs = calc.band_structure()        # returns ase.spectrum.BandStructure
bs.plot(filename='bs.png', show=True, emax=10)
```

Requires a `kpts={'path': ...}` or `{'density': ...}` specification during the calc
(with `npoints`), or a prior `calc.fixed_density(...)` run along a path.

## Restart / checkpoint

- `calc.write('x.gpw')` — write restart; `calc.write('x.gpw', mode='all')` also stores
  wavefunctions/density (needed to resume SCF).
- `atoms, calc = gpaw.restart('x.gpw')` — read back.
- `GPAW('x.gpw')` reads a prior calc; pass a different `xc` etc. to restart with changes.
- Plain-text outputs: `txt='x.txt'` or `'-'`.

## CLI

`gpaw` subcommands: `run`, `info`, `test`, `dos`, `gpw`, `atom`, `diag`, `python`,
`sbatch`, `dataset`, `plot-dataset`, `basis`, `plot-basis`, `symmetry`, `install-data`,
`completion`. Use `gpaw -P N` for N MPI ranks, `gpaw --version` for version.

## Canonical examples

**1. Ground state (LCAO, fast)**
```python
from ase.build import molecule
from gpaw import GPAW
h2 = molecule('H2'); h2.center(vacuum=3.0)
h2.calc = GPAW(mode='lcao', xc='PBE', h=0.25, txt=None)
print(h2.get_potential_energy(), h2.get_forces())
```

**2. Ground state (plane-wave) + DOS**
```python
from ase.build import bulk
from gpaw import GPAW
from gpaw.dos import DOSCalculator
si = bulk('Si', 'diamond', a=5.43)
si.calc = GPAW(mode='pw', xc='PBE', kpts=(4,4,4), txt=None)
si.get_potential_energy()
dos = DOSCalculator.from_calculator(si.calc)
e = dos.get_energies(npoints=200)
d = dos.raw_dos(e, width=0.1)
```

**3. Structure relaxation**
```python
from ase import Atoms
from ase.optimize import BFGS
from gpaw import GPAW
atoms = Atoms('H2O', positions=[(0,0,0),(0.77,0,0),(0,0.77,0)])
atoms.center(vacuum=2.0)
atoms.calc = GPAW(mode='lcao', xc='PBE', h=0.25, txt=None)
BFGS(atoms).run(fmax=0.05)
```

**4. Restart / checkpoint**
```python
from gpaw import GPAW, restart
atoms.calc = GPAW(mode='pw', xc='PBE', kpts=(4,4,4), txt='run.txt')
atoms.get_potential_energy()
atoms.calc.write('run.gpw', mode='all')   # resume-able
atoms2, calc2 = restart('run.gpw')
```

**5. Spin-polarized metal with smearing**
```python
from ase.build import bulk
from gpaw import GPAW, FermiDirac
fe = bulk('Fe', 'bcc', a=2.87)
fe.set_initial_magnetic_moments([2.2])
fe.calc = GPAW(mode='pw', xc='PBE', kpts=(8,8,8),
               occupations=FermiDirac(width=0.1), spinpol=True, txt=None)
fe.get_potential_energy()
print(fe.get_magnetic_moment())
```

## Common Pitfalls

1. **`from gpaw import DOS` / `gpaw.dos.DOS` is gone in 25.x.** Use `DOSCalculator`.
2. **Don't run Python from inside the `gpaw/` source dir** — `gpaw/typing.py` shadows
   stdlib `typing` and import fails (`cannot import name 'Any' from partially initialized
   module 'typing'`). Run from any other cwd.
3. **`mode='pw'` needs a density grid too** — pass `h`/`gpts` or `dedecut`; `ecut` alone
   (plane-wave cutoff) does not set the real-space grid. Default `ecut=340` eV.
4. **`mode` is version-specific with `kpts`**: FD mode wants a real-space grid and works
   with any k-points; PW uses `gammacentered`/`cell` kwargs; LCAO is cheapest but
   approximate for the density grid.
5. **Metals need smearing**: use `occupations=FermiDirac(width=0.1)` (or MethfesselPaxton)
   with dense `kpts`, or SCF may not converge / energy may be wrong.
6. **Symmetry + k-points**: GPAW symmetrizes by default (`symmetry={'point_group': True}`).
   A `{'path':...}` band structure needs `npoints`; small Monkhorst-Pack grids may collapse
   to fewer IBZ points than expected — check `calc.get_ibz_k_points()`.
7. **Restart files are binary and env-specific**: `.gpw` from a different GPAW/ASE version
   or MPI layout may not load. Use `mode='all'` to store wavefunctions, else a restart
   re-does the SCF from scratch.
8. **Parallelism**: pass `parallel={'domain':.., 'band':.., 'kpt':..}` (a `dict`, distinct
   from the top-level kwargs). Run MPI scripts with `gpaw -P N script.py` or
   `mpiexec -n N gpaw python script.py`; not plain `python`.

## Reference files

- `references/api_index.md` — signatures for GPAW, modes, mixers, occupations, eigensolvers,
  DOS, and convenience functions.
- `references/module_map.md` — one-line purpose of each subpackage.

## Verification Checklist

- [ ] Env Python invoked by absolute path `/home/think/miniconda3/envs/agox_v2/bin/python`
- [ ] `mode` matches the intended `FD`/`LCAO`/`PW` semantics and gets its grid params
- [ ] Metals have `occupations=` smearing; spin systems set `spinpol=True`
- [ ] DOS uses `DOSCalculator`, not the removed `DOS`/`PDOS`
- [ ] `matplotlib.use('Agg')` set before any plotting in headless runs
- [ ] Restart written with `mode='all'` when wavefunctions must be preserved
