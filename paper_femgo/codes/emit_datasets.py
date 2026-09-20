"""
emit_datasets.py — generate all analysis datasets (CSV + per-figure JSON) before plotting.

Two-step emit→plot pattern: run this first to write the datasets you and the
owner can inspect, then run the draw_*.py scripts which read from them.

Emits:
  analysis/dataset_femgo.csv        (all Fe-on-MgO configs, iter>=10)
  analysis/dataset_mgofe.csv         (reverse deposition, iter>=10)
  analysis/dataset_femgo_3x3.csv     (finite-size 3x3)
  analysis/dataset_femgo_4x4.csv     (finite-size 4x4)
  analysis/Fig_Prog.json             (per-seed best-so-far progression)
  analysis/Fig_ConDen.json           (rel-energy, delta_z, psi_1d + KDE peaks)
  analysis/Fig_Boltz.json           (temperature-dependent probabilities)
  analysis/Fig_dos.json             (Fe-3d PDOS island vs flat)
  analysis/Fig_convStateDens.json   (cumulative state-density curves)
  analysis/Fig_mgo.json             (reverse-deposition landscape)

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python emit_datasets.py
"""
__version__ = "1.0.0"

import os
import sys
import numpy as np
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (emit_combined_csv, emit_figure_json, femgo_db_paths,
                    mgofe_db_paths, load_agox_ensemble, rel_energy_per_atom,
                    delta_z, pca_psi1d, DATA_DIR, ANALYSIS_DIR)

E_LIMIT = (0.0 - 0.1, 1.5 + 0.1, 5)
KB = 8.617333262e-5
TEMPS = np.linspace(300, 10000, 10)


def emit_prog():
    db_paths = femgo_db_paths()
    per_seed = {}
    # renumber on-disk seeds (3..15) as independent runs 1..13
    run_map = {int(os.path.basename(os.path.dirname(os.path.dirname(p))).replace('seed_', '')):
               i + 1 for i, p in enumerate(db_paths)}
    for p in db_paths:
        energies, atoms, meta = load_agox_ensemble([p], start_iter=10)
        if len(energies) == 0:
            continue
        n_atoms = len(atoms[0])
        rel = rel_energy_per_atom(energies, n_atoms)
        order = np.argsort([m.get('iteration', 0) for m in meta])
        rel = rel[order]
        best = np.minimum.accumulate(rel)
        seed = int(os.path.basename(os.path.dirname(os.path.dirname(p))).replace('seed_', ''))
        run = run_map[seed]
        per_seed[f'Run {run}'] = {'candidate_count': list(range(1, len(best) + 1)),
                                  'best_rel_energy': [round(float(x), 6) for x in best]}
    emit_figure_json('Fig_Prog', per_seed,
                     {'x': 'Evaluated Candidate Count (N_i)',
                      'y': 'E_i - E_glob (eV/atom)',
                      'note': '13 independent runs (Run 1-13, on-disk seeds 3-15), iteration>=10'})


def emit_landscape():
    db_paths = femgo_db_paths()
    energies, atoms, _ = load_agox_ensemble(db_paths, start_iter=10)
    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    dz = delta_z(atoms)
    psi = pca_psi1d(atoms)
    grid = np.linspace(E_LIMIT[0], E_LIMIT[1], 200)
    density = gaussian_kde(rel).evaluate(grid)
    peaks, _ = find_peaks(density, prominence=np.max(density) * 0.05)
    peaks = sorted(peaks, key=lambda i: grid[i])
    emit_figure_json('Fig_ConDen', {
        'n_configs': int(len(rel)),
        'rel_energy': [round(float(x), 6) for x in rel],
        'delta_z_A': [round(float(x), 6) for x in dz],
        'psi_1d': [round(float(x), 6) for x in psi],
        'kde_grid': [round(float(x), 6) for x in grid],
        'kde_density': [round(float(x), 6) for x in density],
        'peaks_eV_per_atom': [round(float(grid[p]), 6) for p in peaks],
    }, {'note': '13 runs, iteration>=10; peaks are the island/flat basins'})


def emit_boltzmann():
    db_paths = femgo_db_paths()
    energies, atoms, _ = load_agox_ensemble(db_paths, start_iter=10)
    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    kde = gaussian_kde(rel)
    grid = np.linspace(rel.min(), rel.max(), 1000)
    rho = kde.evaluate(grid) + 1e-15
    curves = {}
    for T in TEMPS:
        weights = rho * np.exp(-grid / (KB * T))
        Z = np.sum(weights)
        probs = weights / Z
        probs = probs / probs.max()
        curves[str(int(T))] = {'energy': [round(float(x), 6) for x in grid],
                               'prob': [round(float(x), 6) for x in probs]}
    emit_figure_json('Fig_Boltz', curves,
                     {'note': 'peak-normalized P(E); 300-10000 K'})


def emit_dos():
    import pandas as pd
    import re
    out = {}
    for seed, name in [(3, 'island'), (4, 'flat')]:
        path = os.path.join(DATA_DIR, 'dos_femgo_flatngs', f'dos_seed_{seed}.csv')
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        up_cols = [c for c in df.columns if re.match(r'Fe\d+_dz2_up$', c)]
        down_cols = [c for c in df.columns if re.match(r'Fe\d+_dz2_down$', c)]
        out[name] = {
            'energy': [round(float(x), 6) for x in df['energy']],
            'fe_dz2_up': [round(float(x), 6) for x in df[up_cols].sum(axis=1)],
            'fe_dz2_down': [round(float(x), 6) for x in df[down_cols].sum(axis=1)],
        }
    emit_figure_json('Fig_dos', out,
                     {'note': 'Fe-3d (dz2) PDOS; island=seed_3, flat=seed_4; 2 seeds only'})


def emit_conv():
    db_paths = femgo_db_paths()
    per_seed = []
    for p in db_paths:
        energies, atoms, _ = load_agox_ensemble([p], start_iter=10)
        if len(energies) == 0:
            continue
        n_atoms = len(atoms[0])
        per_seed.append(rel_energy_per_atom(energies, n_atoms))
    grid = np.linspace(E_LIMIT[0], E_LIMIT[1], 200)
    curves = {}
    curves['seed_0'] = [round(float(x), 6) for x in gaussian_kde(per_seed[0]).evaluate(grid)]
    cum = np.concatenate(per_seed[:1])
    for i in range(1, len(per_seed)):
        cum = np.concatenate([cum, per_seed[i]])
        curves[f'seeds_0_{i}'] = [round(float(x), 6) for x in gaussian_kde(cum).evaluate(grid)]
    emit_figure_json('Fig_convStateDens', {
        'grid': [round(float(x), 6) for x in grid],
        'curves': curves,
    }, {'note': 'single seed vs cumulative; 13 runs'})


def emit_mgo():
    db_paths = mgofe_db_paths()
    energies, atoms, _ = load_agox_ensemble(db_paths, start_iter=10)
    n_atoms = len(atoms[0])
    rel = rel_energy_per_atom(energies, n_atoms)
    dz = delta_z(atoms, film_symbols=('Mg', 'O'))
    psi = pca_psi1d(atoms)
    grid = np.linspace(E_LIMIT[0], E_LIMIT[1], 200)
    density = gaussian_kde(rel).evaluate(grid)
    emit_figure_json('Fig_mgo', {
        'n_configs': int(len(rel)),
        'rel_energy': [round(float(x), 6) for x in rel],
        'delta_z_A': [round(float(x), 6) for x in dz],
        'psi_1d': [round(float(x), 6) for x in psi],
        'kde_grid': [round(float(x), 6) for x in grid],
        'kde_density': [round(float(x), 6) for x in density],
    }, {'note': 'reverse deposition, seeds 0-4 (seed_5 truncated excluded)'})


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    print("=== combined CSVs ===")
    emit_combined_csv('femgo')
    emit_combined_csv('mgofe')
    emit_combined_csv('femgo_3x3')
    emit_combined_csv('femgo_4x4')
    print("=== per-figure JSONs ===")
    emit_prog()
    emit_landscape()
    emit_boltzmann()
    emit_dos()
    emit_conv()
    emit_mgo()
    print("done.")


if __name__ == '__main__':
    main()
