"""
PDOS calculation for the FeB/MgO ground state (Fe25/Mg25/O25/B3, 78 atoms).

Adapted from _results/10_dos/main.py (which ran DOS/PDOS on the Fe/MgO Island
and Flat structures). Differences for this run:
  * Input is the single global ground state structure extracted from the
    dataset_boron3 AGOX databases (gs_boron3.traj), not a multi-structure traj.
  * PDOS is summed PER ELEMENT (l=2 -> d for Fe; l=1 -> p for O and B; m=None
    sums all magnetic quantum numbers), matching the 37_dos output layout
    (total_Fe_d / total_O_p), plus the requested total_B_p.
  * All GPAW settings are kept identical to 10_dos/main.py:
      LCAO, basis=dzp, xc=PBE, spinpol, hund, symmetry off, nbands='nao',
      kpts=(12,12,1), occupations fermi-dirac width=0.05, maxiter=500.
    DOS grid: emin=-15, emax=10, npts=2000, width=0.15, Fermi-shifted
    (raw_dos / raw_pdos called on energies_grid + e_fermi).

Output: dos_gs.csv with columns
    energy, total_dos_up, total_dos_down, total_dos_sum,
    total_Fe_d_up, total_Fe_d_down, total_O_p_up, total_O_p_down,
    total_B_p_up, total_B_p_down.

Usage (HPC, gpaw_env):  python ./main.py
"""

from gpaw import GPAW
from ase.io import read
import numpy as np
import pandas as pd


def run_workflow(atoms, kpts=(12, 12, 1), npts=2000, width=0.15):
    calc = GPAW(
        mode={"name": "lcao"},
        basis="dzp",
        xc="PBE",
        mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
        convergence={"energy": 1e-4, "density": 1e-3},
        txt="output_gs.txt",
        kpts=kpts,
        symmetry='off',
        nbands='nao',
        maxiter=500,
        occupations={"name": "fermi-dirac", "width": 0.05},
        hund=True,
        spinpol=True
    )

    atoms.calc = calc
    atoms.get_potential_energy()

    e_fermi = calc.get_fermi_level()
    emin, emax = -15, 10
    energies_grid = np.linspace(emin, emax, npts)

    results = {'energy': energies_grid}

    doscalc = calc.dos()
    spins = range(calc.get_number_of_spins())

    total_dos_all_spins = np.zeros(npts)
    for s in spins:
        dos_s = doscalc.raw_dos(energies_grid + e_fermi, spin=s, width=width)
        label = "up" if s == 0 else "down"
        results[f'total_dos_{label}'] = dos_s
        total_dos_all_spins += dos_s
    results['total_dos_sum'] = total_dos_all_spins

    # Per-element summed PDOS: Fe-d (l=2), O-p and B-p (l=1); m=None sums all m.
    symbols = atoms.get_chemical_symbols()
    element_l = {'Fe': 2, 'O': 1, 'B': 1}
    for element, l in element_l.items():
        for s in spins:
            label = "up" if s == 0 else "down"
            total = np.zeros(npts)
            for i, symbol in enumerate(symbols):
                if symbol == element:
                    total += doscalc.raw_pdos(
                        energies_grid + e_fermi, a=i, l=l, m=None,
                        spin=s, width=width)
            col = f'total_{element}_{"d" if l == 2 else "p"}_{label}'
            results[col] = total

    df = pd.DataFrame(results)
    csv_name = "dos_gs.csv"
    df.to_csv(csv_name, index=False)
    print(f"Analysis for ground state saved to {csv_name}.")


structs = read("gs_boron3.traj", index=':')
print(f"Loaded {len(structs)} ground-state structure(s)")
for s in structs:
    run_workflow(s)
