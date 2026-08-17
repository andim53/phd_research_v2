# def calculate_boltzmann_probs(energies, kde_model, T):
#     """
#     Calc Pi = g_(E)exp(-A/kbT) / Z
#     """
#     kb = 8.6173e-5 # eV/K

#     rho_i = kde_model.evaluate(energies) + 1e-15

#     relative_e = energies - np.min(energies)
#     exponent = -relative_e / (kb * T)

#     weights = np.exp(exponent)
#     Z = np.sum(weights)

#     return rho_i * weights / Z

def calculate_boltzmann_probs(energies, kde_model, T):
    """
    Calculates normalized Pi = [rho(E) * exp(-dE/kbT)] / Z
    """
    kb = 8.6173e-5 # eV/K

    # Adding epsilon to avoid zero
    rho_i = kde_model.evaluate(energies) + 1e-15

    # 2. Calculate Boltzmann Weights
    relative_e = energies - np.min(energies)
    exponent = -relative_e / (kb * T)
    weights = np.exp(exponent)

    # 3. Calculate Partition Function Z 
    # Z must be the sum of (Density * Weights)
    numerator = rho_i * weights
    Z = np.sum(numerator)

    # 4. Return Normalized Probabilities
    return numerator / Z