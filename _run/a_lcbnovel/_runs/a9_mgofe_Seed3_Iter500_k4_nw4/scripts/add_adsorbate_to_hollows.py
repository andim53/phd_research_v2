import numpy as np
from ase import Atoms

__version__ = "1.1.0"

def _find_square_hollows(fe_positions, tol_frac=0.1):
    """Find the hollow sites in a square-lattice Fe layer.

    A hollow is the centroid of 4 Fe atoms that form a square (4 nearest-neighbour
    edges). Returns a list of (centroid, sorted_atom_indices) hollow sites.
    """
    pos = np.asarray(fe_positions, dtype=float)
    n = len(pos)
    if n < 4:
        return []

    # all pair distances; nearest-neighbour spacing defines the square side
    d = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=2)
    dd = d.copy()
    np.fill_diagonal(dd, np.inf)
    nn = dd.min()
    eps = tol_frac * nn
    adj = np.abs(d - nn) < eps

    hollows = []
    seen = set()
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i, j]:
                continue
            # edge i-j is a square side; compute the two possible square completions
            edge = pos[j] - pos[i]
            L = np.linalg.norm(edge)
            if L == 0:
                continue
            perp = np.array([-edge[1], edge[0], 0.0]) / L
            for sgn in (+1.0, -1.0):
                c1 = pos[i] + sgn * perp * nn
                c2 = pos[j] + sgn * perp * nn
                k1 = _find_near(pos, c1, eps)
                k2 = _find_near(pos, c2, eps)
                if k1 is not None and k2 is not None:
                    quad = tuple(sorted((i, j, k1, k2)))
                    if quad not in seen:
                        seen.add(quad)
                        hollows.append((pos[list(quad)].mean(axis=0), quad))
    return hollows


def _find_near(pos, target, eps):
    """Return the index of the atom nearest `target` if within `eps`, else None."""
    dist = np.linalg.norm(pos - target, axis=1)
    k = int(np.argmin(dist))
    return k if dist[k] <= eps else None


def add_adsorbate_to_hollows(
    atoms: Atoms, 
    symbol: str, 
    height: float, 
    num_atoms: int = 1,
    seed: int = None,
):
    rng = np.random.default_rng(seed)
    fe_indices = np.array([a.index for a in atoms if a.symbol == 'Fe'])

    # Real hollow sites: centroids of 4 adjacent Fe atoms forming a square.
    hollows = _find_square_hollows(atoms.get_positions()[fe_indices])
    if not hollows:
        raise ValueError("No square hollow sites found in the Fe layer.")

    rng.shuffle(hollows)
    num_atoms = min(num_atoms, len(hollows))
    selected = hollows[:num_atoms]

    # Reject any hollow whose centroid would land on (or too close to) an existing atom.
    all_pos = atoms.get_positions()
    new_positions = []
    for centroid, _ in selected:
        new_pos = np.array([centroid[0], centroid[1], centroid[2] + height])
        if len(all_pos) > 0:
            dist = np.linalg.norm(all_pos - new_pos, axis=1).min()
            # skip sites that would overlap an existing atom (allow 0.5 A margin)
            if dist < 0.5:
                continue
        new_positions.append(new_pos)

    adsorbates = Atoms(symbol * len(new_positions), positions=new_positions)
    return atoms + adsorbates
