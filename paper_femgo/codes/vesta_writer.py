"""
vesta_writer.py — canonical VESTA .vesta structure writer for paper_femgo.

The single source of truth for authoring VESTA 3.5.4 project files in this
project. Always import this module instead of hand-rolling a .vesta — it embeds
the project's conventions (custom colors, space-filling model, fractional
coords, O1/Mg1/Fe1 labels) and an optional Fe height-darkening.

VESTA is a GUI app with no headless render API, so this writer emits the native
`.vesta` text project; the owner opens it in VESTA to render a PNG.

Conventions (see references/vesta-format.md + paper-femgo-fig-sup.md in the
vesta-visualization skill):
- Colors: Fe=green #4C9F38 (76,159,56), Mg=orange #FF7F0E (255,127,14),
  O=red #D62728 (214,39,40). Radii (Å): Fe 1.32, Mg 1.41, O 0.66.
- Space-filling display model (MODEL 1 1 0).
- Fractional STRUC (from get_scaled_positions()), never Cartesian.
- Labels element+counter, NO space (O1, Mg1, Fe1); the whole label is
  right-padded only for column alignment.
- 11-field SITET (RGB twice, alpha 204, final 0).
- Optional opt-in Fe height-darkening (off by default):
  darken_factor 0.8, max_cbar = actual ΔZ (z_max - z_min), so the top Fe atom
  is fully darkened (shade = 1 - 0.8 = 0.2). Mg/O stay fixed. Flat layers
  (ΔZ <= 0) get no darkening.

API:
    write_vesta(atoms, out_path, title, darken_fe=False)

Example:
    write_vesta(atoms, 'analysis/fig_sup_vesta/gs.vesta',
                'ground state (3x3)', darken_fe=True)

Environment: any python with numpy + ase Atoms.
"""
__version__ = "2.0.0"

import os
import numpy as np

# Project-standard colors (RGB 0-255) + covalent radii (Å).
# Colors are the slightly-darker preset (~0.95x of the original
# Fe #4C9F38, Mg #FF7F0E, O #D62728), which matches the look in the Fig S2
# VESTA renders and is used as the default for all generated .vesta files.
COLORS = {'Fe': (72, 151, 53), 'Mg': (242, 121, 13), 'O': (203, 37, 38)}
RADII = {'Fe': 1.32, 'Mg': 1.41, 'O': 0.66}

# Height-darkening defaults (opt-in via darken_fe=True).
DARKEN_FACTOR = 0.8
# max_cbar is rescaled to each structure's actual ΔZ so the top Fe atom is
# fully darkened (strong visible contrast).
DARKEN_SYMBOL = 'Fe'


def _fe_darkened_colors(atoms):
    """Per-atom RGB darkened by height for DARKEN_SYMBOL, else {}.

    atom_height = z - z_min; norm_height = clip(atom_height / ΔZ, 0, 1);
    shade = 1.0 - norm_height * DARKEN_FACTOR; rgb = base * shade.
    Returns {atom_index: (r,g,b)}. Flat layers (ΔZ <= 0) -> no darkening.
    """
    idx = [a.index for a in atoms if a.symbol == DARKEN_SYMBOL]
    if not idx:
        return {}
    z = [atoms[i].position[2] for i in idx]
    z_min = min(z)
    dz = max(z) - z_min
    if dz <= 0:
        return {i: COLORS[DARKEN_SYMBOL] for i in idx}
    base = np.array(COLORS[DARKEN_SYMBOL], float)
    out = {}
    for i in idx:
        h = atoms[i].position[2] - z_min
        norm = min(max(h / dz, 0.0), 1.0)
        shade = 1.0 - norm * DARKEN_FACTOR
        rgb = tuple(int(round(c)) for c in (base * shade))
        out[i] = rgb
    return out


def _labels(atoms):
    """Per-atom VESTA labels: element symbol + per-species counter, NO space."""
    counters = {}
    labels = []
    for atom in atoms:
        el = atom.symbol
        n = counters.get(el, 0) + 1
        counters[el] = n
        labels.append(f'{el}{n}')
    return labels


def write_vesta(atoms, out_path, title, darken_fe=False):
    """Write a P1 VESTA 3.5.4 project file (fractional coords, custom colors).

    darken_fe=True applies the height-darkening gradient to Fe atoms
    (off by default).
    """
    cell = atoms.get_cell()
    a, b, c = cell.lengths()
    alpha, beta, gamma = cell.angles()
    scaled = atoms.get_scaled_positions()
    labels = _labels(atoms)
    fe_colors = _fe_darkened_colors(atoms) if darken_fe else {}

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

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print(f'  -> {out_path} ({len(atoms)} atoms)')
