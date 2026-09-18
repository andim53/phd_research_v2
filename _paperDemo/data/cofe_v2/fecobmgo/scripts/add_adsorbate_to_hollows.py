import numpy as np
from itertools import combinations
from ase import Atoms


def canonical_square_symmetry_key(frac_xy, decimals=3):
    x, y = frac_xy
    x = x % 1.0
    y = y % 1.0

    sym_equiv = np.array([
        [ x,  y],
        [ y,  x],
        [1-x, y],
        [x, 1-y],
        [1-x, 1-y],
        [1-y, 1-x],
        [y, 1-x],
        [1-y, x],
    ]) % 1.0

    sym_equiv = np.round(sym_equiv, decimals)
    sym_equiv = sorted(map(tuple, sym_equiv))

    return sym_equiv[0]


def add_adsorbate_to_hollows(
    atoms: Atoms,
    symbol: str,
    height: float,
    num_atoms: int = 1,
    seed: int = None,
    target_symbols= ("Fe"), # ("Fe", "Co"),
    surface_depth: float = 0.5,
    distance_tol: float = 0.2,
    min_adsorbate_distance: float = 0.5,
    avoid_symmetry_equivalent: bool = True,
):
    rng = np.random.default_rng(seed)

    positions = atoms.get_positions()
    symbols = np.array(atoms.get_chemical_symbols())

    target_indices = np.array([
        i for i, s in enumerate(symbols)
        if s in target_symbols
    ])

    target_z = positions[target_indices, 2]
    top_z = np.max(target_z)

    surface_indices = target_indices[
        target_z > top_z - surface_depth
    ]

    if len(surface_indices) < 4:
        raise ValueError("Not enough surface atoms to form hollow sites.")

    hollow_positions = []

    for site in combinations(surface_indices, 4):
        site = np.array(site)
        site_pos = positions[site]

        xy = site_pos[:, :2]
        center_xy = np.mean(xy, axis=0)

        distances = np.linalg.norm(xy - center_xy, axis=1)

        if np.max(distances) - np.min(distances) < distance_tol:
            center_z = np.mean(site_pos[:, 2]) + height
            # hollow_positions.append([
            #     center_xy[0],
            #     center_xy[1],
            #     center_z
            # ])

            candidate_pos = np.array([center_xy[0], center_xy[1], center_z])
            dist_to_atoms = np.linalg.norm(
                positions - candidate_pos,
                axis=1
            )
            if np.min(dist_to_atoms) < 0.5:
                continue
            hollow_positions.append(candidate_pos)


    if len(hollow_positions) == 0:
        raise ValueError("No hollow sites found.")

    hollow_positions = np.array(hollow_positions)

    # remove exactly duplicated hollow positions
    scaled_hollows = atoms.cell.scaled_positions(hollow_positions)
    scaled_hollows = scaled_hollows % 1.0

    _, unique_indices = np.unique(
        np.round(scaled_hollows[:, :2], 4),
        axis=0,
        return_index=True
    )

    hollow_positions = hollow_positions[unique_indices]
    scaled_hollows = scaled_hollows[unique_indices]

    # random order
    order = rng.permutation(len(hollow_positions))
    hollow_positions = hollow_positions[order]
    scaled_hollows = scaled_hollows[order]

    selected_positions = []
    used_symmetry_keys = set()

    for pos, frac in zip(hollow_positions, scaled_hollows):

        # -----------------------------
        # Symmetry-equivalent check
        # -----------------------------
        if avoid_symmetry_equivalent:
            sym_key = canonical_square_symmetry_key(frac[:2])

            if sym_key in used_symmetry_keys:
                continue

        # -----------------------------
        # Distance check
        # -----------------------------
        if len(selected_positions) > 0:
            selected_xy = np.array(selected_positions)[:, :2]
            distances_xy = np.linalg.norm(
                selected_xy - pos[:2],
                axis=1
            )

            if not np.all(distances_xy >= min_adsorbate_distance):
                continue

        selected_positions.append(pos)

        if avoid_symmetry_equivalent:
            used_symmetry_keys.add(sym_key)

        if len(selected_positions) == num_atoms:
            break

    if len(selected_positions) < num_atoms:
        raise ValueError(
            f"Could only place {len(selected_positions)} adsorbates. "
            f"Try reducing min_adsorbate_distance or set "
            f"avoid_symmetry_equivalent=False."
        )

    adsorbates = Atoms(
        symbols=[symbol] * len(selected_positions),
        positions=selected_positions,
        cell=atoms.cell,
        pbc=atoms.pbc
    )

    return atoms + adsorbates
# import numpy as np
# from ase.build import bulk, surface
# from ase.visualize import view


# # -----------------------------
# # Build FeCo(001) slab
# # -----------------------------
# a = 2.86  # approximate Fe lattice constant

# atoms = surface(
#     bulk(
#         "Fe",
#         crystalstructure="bcc",
#         a=a,
#         cubic=True,     # important
#     ),
#     (0, 0, 1),
#     layers=1,
#     vacuum=10.0,
# )

# z = atoms.positions[:, 2]
# z_min = np.min(z)

# tol = 0.1
# keep = z > z_min + tol
# atoms = atoms[keep]

# atoms = atoms.repeat((4, 4, 1))

# # -----------------------------
# # Randomly replace 50% Fe -> Co
# # -----------------------------
# rng = np.random.default_rng(0)

# fe_indices = [i for i, atom in enumerate(atoms)
#               if atom.symbol == "Fe"]

# n_co = len(fe_indices) // 2

# co_indices = rng.choice(
#     fe_indices,
#     size=n_co,
#     replace=False
# )

# for idx in co_indices:
#     atoms[idx].symbol = "Co"

# # -----------------------------
# # Add O adsorbates
# # -----------------------------
# new_atoms = add_adsorbate_to_hollows(
#     atoms,
#     symbol="B",
#     height=0,
#     num_atoms=5,
#     seed=0,
#     target_symbols=("Fe", "Co")
# )

# from ase.io import write

# write("new_atoms.xsf",new_atoms)

# # -----------------------------
# # Visualize
# # -----------------------------
# # view(new_atoms)
