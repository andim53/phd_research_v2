import numpy as np

def calculate_relative_energy(all_e, is_percentage=False):
    """
    Calculates normalized relative energies from a list of total energies.

    Parameters:
        all_e (list or ndarray): List or array of total energy values.

    Returns:
        list: List of normalized relative energies.
    """

    if is_percentage:
        min_energy = np.nanmin(all_e)
        # Use a small epsilon to avoid division by zero if min_energy is exactly 0
        normalization_factor = abs(min_energy) if abs(min_energy) > 1e-9 else 1.0
        rel_energies = [((e - min_energy) / normalization_factor) * 100 if not np.isnan(e) else np.nan for e in all_e]
    else:
        sorted_e = np.argsort(all_e)
        min_e = all_e[sorted_e[0]]
        rel_energies = [e - min_e for e in all_e]

    return rel_energies