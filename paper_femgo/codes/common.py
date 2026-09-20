"""
common.py — shared plotting style + data loading for paper_femgo figure regeneration.

Matches the _analysist researcher style (rcParams) and the paper's minimum-ensemble
definition (AGOX iteration >= 10). All figure scripts import from here.

Environment: agox_v2 (/home/think/miniconda3/envs/agox_v2/bin/python).
Set matplotlib.use('Agg') before importing anything that plots.
"""
__version__ = "1.0.0"

import os
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')
FIG_DIR = os.path.join(ANALYSIS_DIR, 'figures')

# Finite-size (3x3/4x4) and reverse-deposition source data live in the sibling
# _analysist/1_result tree (not in paper_femgo/data/).
ANALYSIST_RESULT = '/home/think/Desktop/research/_analysist/1_result'

# ---------------------------------------------------------------------------
# Researcher plotting style (mirrors _analysist/run_stage0_style.py + codes/07)
# ---------------------------------------------------------------------------
CUSTOM_RC_PARAMS = {
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif', 'Times New Roman', 'Computer Modern'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.linewidth': 1.0,
    'axes.edgecolor': 'black',
    'axes.facecolor': 'white',
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    'axes.grid': False,
    'figure.autolayout': True,
    'figure.dpi': 300,
}

E_LABEL = r'$E_{i}-E_{glob}$ (eV/atom)'
DENSITY_LABEL = 'State Density\n(config./eV)'
SCATTER_LABEL = r'$\psi_{1d}(a.u.)$'


def apply_style():
    plt.rcParams.update(CUSTOM_RC_PARAMS)


# ---------------------------------------------------------------------------
# Data loading (AGOX databases)
# ---------------------------------------------------------------------------
def load_agox_ensemble(db_paths, start_iter=10):
    """Load (energies, atoms) from AGOX dbs keeping only iteration >= start_iter.

    Returns (energies_eV, atoms_list, meta_list). energies are raw total energies.
    """
    from agox.databases import Database
    energies, atoms_list, meta_list = [], [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()          # REQUIRED before get_all_candidates()
        data = db.get_all_structures_data()
        cands = db.get_all_candidates()
        for atoms, meta in zip(cands, data):
            if meta.get('iteration', 0) >= start_iter:
                energies.append(atoms.get_potential_energy())
                atoms_list.append(atoms)
                meta_list.append(meta)
    return np.array(energies, float), atoms_list, meta_list


def rel_energy_per_atom(energies, n_atoms):
    """(E_i - E_glob)/N, global min -> 0."""
    return (np.asarray(energies, float) - np.min(energies)) / n_atoms


def delta_z(atoms_list, film_symbols=('Fe',)):
    """z(film_max) - z(film_min) over the film species (flatness / island height)."""
    dz = []
    for atoms in atoms_list:
        z = np.array([a.position[2] for a in atoms if a.symbol in film_symbols])
        dz.append(z.max() - z.min() if len(z) else 0.0)
    return np.array(dz, float)


def pca_psi1d(atoms_list):
    """First principal component of AGOX Fingerprint descriptors (psi_1d)."""
    from agox.models.descriptors.fingerprint import Fingerprint
    fp = Fingerprint.from_atoms(atoms_list[0])
    data = np.array([fp.create_features(a).flatten() for a in atoms_list])
    Xc = data - np.mean(data, axis=0)
    cov = np.cov(Xc, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    return Xc @ evecs[:, order[0]]


def femgo_db_paths():
    """Fe-on-MgO minimum-ensemble dbs (seeds 3-15; stop_16 excluded as truncated)."""
    return sorted(glob.glob(os.path.join(DATA_DIR, 'femgo', 'seed_*', '1_db', 'db_*.db')))


def mgofe_db_paths():
    """Reverse-deposition (MgO-on-Fe) dbs (seeds 0-4; seed_5 truncated)."""
    return sorted(glob.glob(os.path.join(DATA_DIR, 'mgofe', 'seed_*', '1_db', 'db_*.db')))


def ensure_fig_dir():
    os.makedirs(FIG_DIR, exist_ok=True)
    return FIG_DIR
