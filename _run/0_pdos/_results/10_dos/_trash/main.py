from gpaw import GPAW, FermiDirac
from ase.io import read

def run_scf(atoms, seed, kpts=(12, 12, 1)):
    calc = GPAW(
            mode={"name": "lcao"},
            basis="dzp",
            xc="PBE",
            mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
            convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
            txt=f"output_seed_{seed}.txt",
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
    # Save the full state: 'mode=all' ensures wavefunctions are kept for PDOS
    calc.write(f"seed_{seed}.gpw", mode='all')
    print(f"SCF complete. Saved seed_{seed}.gpw")

structs = read("selected_structures_dos.traj", index=':')
for i, s in enumerate(structs):
    run_scf(s, seed=i)
