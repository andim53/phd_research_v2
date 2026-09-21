"""
common.py — shared plotting style + data loading for paper_femgo figure regeneration.

Matches the _analysist researcher style (rcParams) and the paper's minimum-ensemble
definition (AGOX iteration >= 10). All figure scripts import from here.

Environment: agox_v2 (/home/think/miniconda3/envs/agox_v2/bin/python).
Set matplotlib.use('Agg') before importing anything that plots.
"""
__version__ = "1.3.0"

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
# Plotting style — TRIAL: owner's sans-serif rcParams (2026-09-20).
# Pending owner review (accept or reject). To revert, restore the OLD_SOURCE_STYLE
# dict below (the previous _analysist serif style).
# ---------------------------------------------------------------------------
OLD_SOURCE_STYLE = {
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

CUSTOM_RC_PARAMS = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "axes.linewidth": 1.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    # top/right (inner) ticks removed per owner (2026-09-20)
    "legend.frameon": True,
    "legend.edgecolor": "black",
    # kept for good headless output / layout:
    "axes.edgecolor": "black",
    "axes.facecolor": "white",
    "axes.grid": False,
    "figure.autolayout": True,
    "figure.dpi": 300,
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
    """Load (energies, atoms, meta) from AGOX dbs keeping only iteration >= start_iter.

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
    """Fe-on-MgO minimum-ensemble dbs (seeds 3-15; stop_16 excluded by seed_* glob)."""
    return sorted(glob.glob(os.path.join(DATA_DIR, 'femgo', 'seed_*', '1_db', 'db_*.db')))


def mgofe_db_paths():
    """Reverse-deposition (MgO-on-Fe) dbs (seeds 0-4; seed_5 truncated)."""
    return sorted(glob.glob(os.path.join(DATA_DIR, 'mgofe', 'seed_*', '1_db', 'db_*.db')))


def ensure_fig_dir():
    os.makedirs(FIG_DIR, exist_ok=True)
    return FIG_DIR


# ---------------------------------------------------------------------------
# Emit → plot: dataset generation (CSV/JSON) before plotting
# ---------------------------------------------------------------------------
def emit_combined_csv(system='femgo', start_iter=10, out_name=None):
    """Write a combined per-configuration CSV for a system.

    Columns: seed, iteration, energy_eV, rel_energy_eV_per_atom, delta_z_A, psi_1d.
    femgo -> data/femgo/seed_* (stop_16 excluded by seed_* glob)
    mgofe -> data/mgofe/seed_* (seed_5 truncated, still listed with its count)
    femgo_3x3 / femgo_4x4 -> data/<system>/seed_*

    Returns the output path.
    """
    import csv
    from agox.databases import Database
    if system == 'femgo':
        db_paths = femgo_db_paths()
    elif system == 'mgofe':
        db_paths = mgofe_db_paths()
    else:
        db_paths = sorted(glob.glob(os.path.join(DATA_DIR, system, 'seed_*', '1_db', 'db_*.db')))

    energies, atoms, meta = load_agox_ensemble(db_paths, start_iter=start_iter)
    if len(energies) == 0:
        print(f"  no {system} data")
        return None

    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    dz = delta_z(atoms)
    psi = pca_psi1d(atoms)

    # per-config seed label, aligned to the iter>=10 filtered subset
    seed_labels = []
    for p in db_paths:
        seed = os.path.basename(os.path.dirname(os.path.dirname(p)))
        db = Database(filename=p)
        db.restore_to_memory()
        data = db.get_all_structures_data()
        seed_labels.extend([seed] * sum(1 for m in data if m.get('iteration', 0) >= start_iter))

    out_name = out_name or f'dataset_{system}.csv'
    out_path = os.path.join(ANALYSIS_DIR, out_name)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    with open(out_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['seed', 'iteration', 'energy_eV', 'rel_energy_eV_per_atom',
                    'delta_z_A', 'psi_1d'])
        for i, m in enumerate(meta):
            w.writerow([seed_labels[i], m.get('iteration', 0),
                        round(float(energies[i]), 6),
                        round(float(rel[i]), 6),
                        round(float(dz[i]), 6),
                        round(float(psi[i]), 6)])
    print(f"  -> {out_path} ({len(rel)} configs)")
    return out_path


def emit_figure_json(name, data, description=None):
    """Write a self-describing per-figure JSON dataset."""
    import json
    out_path = os.path.join(ANALYSIS_DIR, f'{name}.json')
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    payload = {
        'name': name,
        'version': '1.0.0',
        'produced_by': f'codes/{name}.py',
        'description': description or {},
        'data': data,
    }
    with open(out_path, 'w') as fh:
        json.dump(payload, fh, indent=2)
    print(f"  -> {out_path}")
    return out_path
