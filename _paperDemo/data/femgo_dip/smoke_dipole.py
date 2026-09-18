"""Smoke: prove poissonsolver={'dipolelayer':'xy'} is ACCEPTED by GPAW 25.7
(there is no basis-in-mode error and the SCF loop actually starts). Full
convergence is NOT required — reaching the SCF loop without a config error is
the pass condition."""
import sys
from ase.build import fcc111, add_adsorbate
from gpaw import GPAW, KohnShamConvergenceError

# Tiny asymmetric slab carrying a net dipole along z; not periodic in z.
slab = fcc111('Pt', size=(1, 1, 3), a=3.975534, vacuum=8.0)
add_adsorbate(slab, 'O', height=1.6, position='ontop')
slab.center(vacuum=8.0, axis=2)
slab.pbc = [True, True, False]

# NOTE: basis is a TOP-LEVEL GPAW kwarg, NOT a key inside mode={...}.
calc = GPAW(mode={'name': 'lcao'}, basis='dzp', xc='PBE',
            kpts=(1, 1, 1), poissonsolver={'dipolelayer': 'xy'},
            txt='smoke_dipole.txt', maxiter=8, hund=True, spinpol=True)
slab.calc = calc

try:
    e = slab.get_potential_energy()
    print(f'converged (unexpected): E={e:.4f} eV')
except KohnShamConvergenceError:
    # Reached the SCF loop and ran its iterations — the dipole kwarg was
    # accepted and no config error fired. That is the smoke pass.
    print('SCF loop reached (dipole kwarg accepted, not converged) -> DIPOLE KWARG ACCEPTED')
except Exception as ex:
    print(f'FAIL {type(ex).__name__}: {ex}')
    sys.exit(1)
