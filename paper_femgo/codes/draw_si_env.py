"""
draw_si_env.py — SI Fig_env: AGOX environment schematic for Fe-on-MgO.

Renders the reference hetero-structure (Fe on MgO(001)) in top and side views,
matching the draft's Fig_env. Uses the reference XSF from data/femgo/seed_3.

Output: analysis/figures/Fig_env.png
"""
__version__ = "1.0.0"

import os
import sys
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from ase.io import read

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/think/Desktop/research/_analysist')
from common import apply_style, DATA_DIR, ensure_fig_dir
from scripts.plot_structure import plot_structure

XSF = os.path.join(DATA_DIR, 'femgo', 'seed_3', '0_result', '0_xsf', 'heteroStruct.xsf')


def main():
    apply_style()
    if not os.path.exists(XSF):
        print(f"  MISSING {XSF}")
        return
    atoms = read(XSF)

    tmpdir = tempfile.mkdtemp()
    panels = []
    for plane in ('xy', 'yz'):
        p = os.path.join(tmpdir, f'env_{plane}.png')
        plot_structure(atoms, plane=plane, save_path=p, plot_show=False,
                       figsize=(6, 6))
        panels.append(Image.open(p).convert('RGB'))

    w = panels[0].width + panels[1].width
    h = max(p.height for p in panels)
    canvas = Image.new('RGB', (w, h), 'white')
    canvas.paste(panels[0], (0, 0))
    canvas.paste(panels[1], (panels[0].width, 0))

    out = os.path.join(ensure_fig_dir(), 'Fig_env.png')
    canvas.save(out)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
