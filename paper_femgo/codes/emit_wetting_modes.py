"""emit_wetting_modes.py — collective flat/island wetting analysis (Fe/MgO vs Fe-B/MgO).

Defines the flat gap as the MODE GAP: the KDE mode of the flat branch (dZ <= 1.0 A)
minus the KDE mode of the island branch (dZ > 1.0 A), computed on the pooled ensemble.
The multi-seed runs are treated as ONE collective sample that populates the PES, not
as independent runs — so no leave-one-out / per-replica statistics are used.

Also computes a per-system PCA landscape (psi_1d = first principal component of the
AGOX Fingerprint) for the Fig_wetLandscape panel. The fingerprint feature space is
species-locked (femgo 720-d, febmgo 1500-d), so each system gets its own PC1; the
sign is aligned so that flat (low dZ) sits on the negative (left) side in both panels.

Emits:
  analysis/Fig_wetModes.json      (per-system modes, mode gap, KDE density curves)
  analysis/Fig_wetLandscape.json  (per-system psi_1d, rel energy, dZ)

Run before draw_wetting_modes.py / draw_wet_landscape.py.
"""
__version__ = "1.3.0"

import os
import sys
import numpy as np
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (apply_style, ANALYSIS_DIR, emit_figure_json, pca_psi1d,
                    femgo_db_paths, febmgo_db_paths)

START_ITER = 10
FLAT_DZ = 1.0                     # flat = dZ <= 1.0 A (owner / _Demo convention)
GRID = np.linspace(-0.05, 0.8, 2000)
KDE_BW = None                     # Scott's rule (matches paper2's landscape KDE)

SYSTEMS = ('femgo', 'febmgo')
LABELS = {'femgo': 'Fe/MgO', 'febmgo': 'Fe-B/MgO'}
DB_PATHS = {'femgo': femgo_db_paths, 'febmgo': febmgo_db_paths}


def load_system(system):
    """Pool all iteration>=10 configs across completed runs.

    Returns (rel, dz, atoms, n_atoms, n_replicas). Multi-seed runs are pooled into
    one collective ensemble; no per-seed labels are kept.
    """
    from agox.databases import Database
    energies, dzs, atoms_list = [], [], []
    n_atoms = None
    n_replicas = 0
    for p in DB_PATHS[system]():
        n_replicas += 1
        db = Database(filename=p)
        db.restore_to_memory()
        cands = db.get_all_candidates()
        data = db.get_all_structures_data()
        for atoms, m in zip(cands, data):
            if m.get('iteration', 0) >= START_ITER:
                if n_atoms is None:
                    n_atoms = len(atoms)
                energies.append(atoms.get_potential_energy())
                # dZ = z-spread over Fe atoms (film species; B excluded) — _Demo convention
                sym = atoms.get_chemical_symbols()
                z = np.array([p[2] for p, s in zip(atoms.get_positions(), sym) if s == 'Fe'])
                dzs.append(z.max() - z.min() if len(z) else 0.0)
                atoms_list.append(atoms)
    energies = np.asarray(energies, float)
    dzs = np.asarray(dzs, float)
    rel = (energies - energies.min()) / n_atoms
    return rel, dzs, atoms_list, n_atoms, n_replicas


def kde_mode(x):
    if len(x) < 3:
        return np.nan
    return float(GRID[np.argmax(gaussian_kde(x, bw_method=KDE_BW).evaluate(GRID))])


def analyze_modes(rel, dz, n_atoms, n_replicas):
    flat = dz <= FLAT_DZ
    island = ~flat

    fm = kde_mode(rel[flat])
    im = kde_mode(rel[island])

    # branch KDE density curves, normalized to peak = 1 (mode comparison, not counts)
    fdens = gaussian_kde(rel[flat], bw_method=KDE_BW).evaluate(GRID)
    idens = gaussian_kde(rel[island], bw_method=KDE_BW).evaluate(GRID)
    fdens /= fdens.max()
    idens /= idens.max()

    return {
        'n_configs': int(len(rel)),
        'n_replicas': n_replicas,
        'n_atoms': n_atoms,
        'n_flat': int(flat.sum()),
        'n_island': int(island.sum()),
        'flat_mode': round(fm, 4),
        'island_mode': round(im, 4),
        'mode_gap': round(fm - im, 4),
        'kde_grid': [round(float(g), 4) for g in GRID],
        'flat_density': [round(float(v), 6) for v in fdens],
        'island_density': [round(float(v), 6) for v in idens],
    }


def landscape(rel, dz, atoms):
    """Per-system PCA landscape: psi_1d (sign-aligned), rel energy, dZ, branch modes."""
    psi = pca_psi1d(atoms)
    flat = dz <= FLAT_DZ
    # align sign so flat (low dZ) sits on the negative (left) side
    if psi[flat].mean() > psi[~flat].mean():
        psi = -psi
    return {
        'n_configs': int(len(rel)),
        'psi_1d': [round(float(x), 4) for x in psi],
        'rel_energy': [round(float(x), 4) for x in rel],
        'delta_z_A': [round(float(x), 4) for x in dz],
        'flat_mode': round(kde_mode(rel[flat]), 4),
        'island_mode': round(kde_mode(rel[~flat]), 4),
        'psi_flat_mean': round(float(psi[flat].mean()), 4),
        'psi_island_mean': round(float(psi[~flat].mean()), 4),
    }


def main():
    apply_style()
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # load once per system
    data = {system: load_system(system) for system in SYSTEMS}

    # --- mode-gap dataset ---
    results = {}
    for system in SYSTEMS:
        rel, dz, atoms, n_atoms, n_replicas = data[system]
        r = analyze_modes(rel, dz, n_atoms, n_replicas)
        results[system] = r
        print(f"{LABELS[system]:10s} pool={r['n_configs']:5d} cfg "
              f"({r['n_replicas']} completed runs)  flat {r['n_flat']:4d} / island {r['n_island']:4d}")
        print(f"    flat mode {r['flat_mode']:.4f}   island mode {r['island_mode']:.4f}   "
              f"MODE GAP {r['mode_gap']:.4f}")

    fe, fb = results['femgo'], results['febmgo']
    boron = {
        'mode_gap_femgo': fe['mode_gap'],
        'mode_gap_febmgo': fb['mode_gap'],
        'delta_mode_gap': round(fb['mode_gap'] - fe['mode_gap'], 4),
        'flat_mode_shift': round(fb['flat_mode'] - fe['flat_mode'], 4),
        'island_mode_shift': round(fb['island_mode'] - fe['island_mode'], 4),
    }
    results['boron_effect'] = boron
    print(f"\nboron effect: mode gap {fe['mode_gap']} -> {fb['mode_gap']} = "
          f"{boron['delta_mode_gap']:+.4f} eV/atom")
    print(f"   = flat-mode shift {boron['flat_mode_shift']:+.4f} "
          f"- island-mode shift {boron['island_mode_shift']:+.4f}")

    emit_figure_json('Fig_wetModes', results, {
        'note': 'flat gap = flat-branch KDE mode - island-branch KDE mode (collective density), '
                f'dZ<=1.0 A flat, iter>=10; multi-seed runs pooled as ONE PES sample '
                '(no per-replica/LOOCV statistics, no p-value); '
                'boron effect = mode-gap change Fe/MgO -> Fe-B/MgO'})

    # --- PCA landscape dataset ---
    land = {system: landscape(*data[system][:3]) for system in SYSTEMS}
    for system in SYSTEMS:
        s = land[system]
        print(f"\n{LABELS[system]} landscape: psi flat {s['psi_flat_mean']:.3f} / "
              f"island {s['psi_island_mean']:.3f} (sign-aligned, flat on left)")
    emit_figure_json('Fig_wetLandscape', land, {
        'note': 'per-system PC1 (AGOX Fingerprint) vs rel energy, colored by dZ; '
                'feature spaces are species-locked (femgo 720-d, febmgo 1500-d) so each '
                'system has its own PC1; psi sign aligned so flat (low dZ) is on the left'})


if __name__ == '__main__':
    main()
