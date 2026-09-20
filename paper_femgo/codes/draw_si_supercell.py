"""
draw_si_supercell.py — SI Fig_sup: finite-size ground states (3x3 and 4x4).

Renders the ground-state configurations for the 3x3 and 4x4 supercells,
matching the draft's Fig_sup. Source data lives in the sibling
_analysist/1_result tree (not in paper_femgo/data/).

Output: analysis/figures/Fig_sup.png
"""
__version__ = "1.0.0"

import os
import sys
import glob
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/think/Desktop/research/_analysist')
from common import apply_style, ANALYSIST_RESULT, ensure_fig_dir
from agox.databases import Database
from scripts.plot_structure import plot_structure

SUPERCELL_ROOTS = {
    '3x3': os.path.join(ANALYSIST_RESULT, '18_kappa2_iter100_trajNoSave_repSeedDat101'),
    '4x4': os.path.join(ANALYSIST_RESULT, '20_kappa2_iter100_trajNoSave_repSeedDat0_4x4'),
}


def ground_state(db_path):
    db = Database(filename=db_path)
    db.restore_to_memory()
    cands = db.get_all_candidates()
    if not cands:
        return None
    return min(cands, key=lambda c: c.get_potential_energy())


def main():
    apply_style()
    tmpdir = tempfile.mkdtemp()
    panels = []
    for label, root in SUPERCELL_ROOTS.items():
        dbs = sorted(glob.glob(os.path.join(root, 'seed_*', '1_db', 'db_*.db')))
        if not dbs:
            print(f"  MISSING {label} dbs under {root}")
            continue
        gs = ground_state(dbs[0])
        if gs is None:
            print(f"  {label}: no candidates")
            continue
        p = os.path.join(tmpdir, f'sup_{label}.png')
        plot_structure(gs, plane='xy', save_path=p, plot_show=False,
                       figsize=(6, 6))
        panels.append(Image.open(p).convert('RGB'))

    if not panels:
        print("  no panels produced")
        return

    w = sum(p.width for p in panels)
    h = max(p.height for p in panels)
    canvas = Image.new('RGB', (w, h), 'white')
    x = 0
    for p in panels:
        canvas.paste(p, (x, 0))
        x += p.width

    out = os.path.join(ensure_fig_dir(), 'Fig_sup.png')
    canvas.save(out)
    print(f"  -> {out}")


if __name__ == '__main__':
    main()
