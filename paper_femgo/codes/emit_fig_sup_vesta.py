"""
emit_fig_sup_vesta.py — Fig S2 (Fig_sup) ground states as VESTA .vesta files.

Reads the same ground-state candidates that codes/draw_si_supercell.py renders
for Fig S2 (min-energy candidate of the FIRST db in sorted seed order, per
supercell) and writes them as VESTA 3.5.4 project files with the owner's custom
colors (Fe green #4C9F38, Mg orange #FF7F0E, O red #D62728) and the
space-filling (MODEL 1) display model.

Fe atoms are darkened progressively with height, replicating the
_analysist/scripts/plot_structure.py mechanism (darken_factor=0.8, max_cbar
rescaled to each structure's actual ΔZ, z_min = lowest Fe atom), so the top Fe
atom is fully darkened for strong visible contrast.

Output:
  analysis/fig_sup_vesta/fig_sup_3x3_gs.vesta
  analysis/fig_sup_vesta/fig_sup_4x4_gs.vesta

Environment: agox_v2 (/home/think/miniconda3/envs/agox_v2/bin/python).
"""
__version__ = "1.1.1"

import os
import sys
import glob
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR

from agox.databases import Database

SUPERCELL_ROOTS = {
    '3x3': os.path.join(DATA_DIR, 'femgo_3x3'),
    '4x4': os.path.join(DATA_DIR, 'femgo_4x4'),
}

OUT_DIR = os.path.join(os.path.dirname(DATA_DIR), 'analysis', 'fig_sup_vesta')

# Owner's custom colors (RGB 0-255) + covalent radii (Å).
COLORS = {'Fe': (76, 159, 56), 'Mg': (255, 127, 14), 'O': (214, 39, 40)}
RADII = {'Fe': 1.32, 'Mg': 1.41, 'O': 0.66}

# Height-darkening (replicates _analysist/scripts/plot_structure.py).
DARKEN_FACTOR = 0.8
# max_cbar is rescaled to each structure's actual ΔZ (z_max - z_min) so the
# top Fe atom is fully darkened (strongest visible contrast).


def _fe_darkened_colors(atoms):
    """Per-Fe-atom RGB darkened by height, matching plot_structure.

    For each Fe atom: atom_height = z - z_min (z_min = lowest Fe),
    norm_height = clip(atom_height / max_cbar, 0, 1) where max_cbar = ΔZ
    (z_max - z_min) of this structure, shade = 1.0 - norm_height * DARKEN_FACTOR,
    rgb = base_green * shade. The top Fe atom (norm_height=1) is fully darkened
    (shade = 1 - 0.8 = 0.2).
    Returns a dict {atom_index: (r, g, b)} for Fe atoms only.
    """
    fe_idx = [a.index for a in atoms if a.symbol == 'Fe']
    if not fe_idx:
        return {}
    z = [atoms[i].position[2] for i in fe_idx]
    z_min = min(z)
    max_cbar = max(z) - z_min
    if max_cbar <= 0:
        return {i: COLORS['Fe'] for i in fe_idx}
    base = np.array(COLORS['Fe'], float)
    out = {}
    for i in fe_idx:
        h = atoms[i].position[2] - z_min
        norm = min(max(h / max_cbar, 0.0), 1.0)
        shade = 1.0 - norm * DARKEN_FACTOR
        rgb = tuple(int(round(c)) for c in (base * shade))
        out[i] = rgb
    return out


def ground_state(db_path):
    """Min-potential-energy candidate of a single AGOX db (matches draw_si_supercell)."""
    db = Database(filename=db_path)
    db.restore_to_memory()
    cands = db.get_all_candidates()
    if not cands:
        return None
    return min(cands, key=lambda c: c.get_potential_energy())


def _labels(atoms):
    """Per-atom VESTA labels: element symbol + per-species counter, NO space (O1, Mg1, Fe1)."""
    counters = {}
    labels = []
    for atom in atoms:
        el = atom.symbol
        n = counters.get(el, 0) + 1
        counters[el] = n
        labels.append(f'{el}{n}')
    return labels


def write_vesta(atoms, out_path, title):
    """Write a P1 VESTA 3.5.4 project file (fractional coords, custom colors)."""
    cell = atoms.get_cell()
    a, b, c = cell.lengths()
    alpha, beta, gamma = cell.angles()
    scaled = atoms.get_scaled_positions()
    labels = _labels(atoms)
    fe_colors = _fe_darkened_colors(atoms)

    lines = []
    lines.append('#VESTA_FORMAT_VERSION 3.5.4')
    lines.append('')
    lines.append('')
    lines.append('CRYSTAL')
    lines.append('')
    lines.append('TITLE')
    lines.append(title)
    lines.append('')
    lines.append('GROUP')
    lines.append('1 1 P 1')
    lines.append('SYMOP')
    lines.append(' 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1   1')
    lines.append(' -1.0 -1.0 -1.0  0 0 0  0 0 0  0 0 0')
    lines.append('TRANM 0')
    lines.append(' 0.000000  0.000000  0.000000  1  0  0   0  1  0   0  0  1')
    lines.append('LTRANSL')
    lines.append(' -1')
    lines.append(' 0.000000  0.000000  0.000000  0.000000  0.000000  0.000000')
    lines.append('LORIENT')
    lines.append(' -1   0   0   0   0')
    lines.append(f' 1.000000  0.000000  0.000000 {a:.6f}  0.000000  0.000000')
    lines.append(' 0.000000  0.000000  1.000000  0.000000  0.000000 156.823828')
    lines.append('LMATRIX')
    lines.append(' 1.000000  0.000000  0.000000  0.000000')
    lines.append(' 0.000000  1.000000  0.000000  0.000000')
    lines.append(' 0.000000  0.000000  1.000000  0.000000')
    lines.append(' 0.000000  0.000000  0.000000  1.000000')
    lines.append(' 0.000000  0.000000  0.000000')
    lines.append('CELLP')
    lines.append(f' {a:.6f}  {b:.6f}  {c:.6f}  {alpha:.6f}  {beta:.6f}  {gamma:.6f}')
    lines.append('  0.000000   0.000000   0.000000   0.000000   0.000000   0.000000')
    lines.append('STRUC')
    for i, atom in enumerate(atoms, start=1):
        el = atom.symbol
        fx, fy, fz = scaled[i - 1]
        lines.append(f' {i:3d} {el:<2s} {labels[i-1]}  1.0000   {fx:.6f} {fy:.6f} {fz:.6f}  1a 1')
        lines.append('                           0.000000   0.000000   0.000000  0.00')
    lines.append('  0 0 0 0 0 0 0')
    lines.append('THERI 1')
    for i, atom in enumerate(atoms, start=1):
        lines.append(f' {i:3d} {labels[i-1]:>7s}  0.000000')
    lines.append('  0 0 0')
    lines.append('SHAPE')
    lines.append('  0       0       0       0   0.000000  0   192   192   192   192')
    lines.append('BOUND')
    lines.append('       0        1         0        1         0        1')
    lines.append('  0   0   0   0  0')
    lines.append('SBOND')
    lines.append('  0 0 0 0')
    lines.append('SITET')
    for i, atom in enumerate(atoms, start=1):
        el = atom.symbol
        r, g, b = fe_colors.get(i - 1, COLORS[el])
        rad = RADII[el]
        lines.append(f' {i:3d} {labels[i-1]:>7s}  {rad:.4f}  {r:3d} {g:3d} {b:3d}  {r:3d} {g:3d} {b:3d}  204  0')
    lines.append('  0 0 0 0 0 0')
    lines.append('STYLE')
    lines.append('DISPF 37753794')
    lines.append('MODEL   1  1  0')
    lines.append('SURFS   0  1  1')
    lines.append('SECTS  32  1')
    lines.append('FORMS   0  1')
    lines.append('ATOMS   0  0  1')
    lines.append('BONDS   1')
    lines.append('POLYS   1')
    lines.append('VECTS inf')

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print(f'  -> {out_path} ({len(atoms)} atoms)')


def main():
    for label, root in SUPERCELL_ROOTS.items():
        dbs = sorted(glob.glob(os.path.join(root, 'seed_*', '1_db', 'db_*.db')))
        if not dbs:
            print(f'  MISSING {label} dbs under {root}')
            continue
        gs = ground_state(dbs[0])
        if gs is None:
            print(f'  {label}: no candidates')
            continue
        out = os.path.join(OUT_DIR, f'fig_sup_{label}_gs.vesta')
        write_vesta(gs, out, f'Fig S2 ground state ({label} supercell)')


if __name__ == '__main__':
    main()
