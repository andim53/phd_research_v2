raw_energies = np.array([atoms.get_potential_energy() for atoms in traj if hasattr(atoms, 'get_potential_energy')])
e_global = np.min(raw_energies)
intensive_energies = (raw_energies - e_global)

intensive_energies