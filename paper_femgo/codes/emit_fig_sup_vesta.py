"""
emit_fig_sup_vesta.py — Fig S2 (Fig_sup) ground states as VESTA .vesta files.

Reads the same ground-state candidates that codes/draw_si_supercell.py renders
for Fig S2 (min-energy candidate of the FIRST db in sorted seed order, per
supercell) and writes them as VESTA 3.5.4 project files using the canonical
codes/vesta_writer.py (custom colors, space-filling MODEL 1), with Fe
height-darkening enabled (Fe-on-MgO case).

Output:
  analysis/fig_sup_vesta/fig_sup_3x3_gs.vesta
  analysis/fig_sup_vesta/fig_sup_4x4_gs.vesta

Environment: agox_v2 (/home/think/miniconda3/envs/agox_v2/bin/python).
"""
__version__ = "2.0.0"

import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR
from vesta_writer import write_vesta

from agox.databases import Database

SUPERCELL_ROOTS = {
    '3x3': os.path.join(DATA_DIR, 'femgo_3x3'),
    '4x4': os.path.join(DATA_DIR, 'femgo_4x4'),
}

OUT_DIR = os.path.join(os.path.dirname(DATA_DIR), 'analysis', 'fig_sup_vesta')


def ground_state(db_path):
    """Min-potential-energy candidate of a single AGOX db (matches draw_si_supercell)."""
    db = Database(filename=db_path)
    db.restore_to_memory()
    cands = db.get_all_candidates()
    if not cands:
        return None
    return min(cands, key=lambda c: c.get_potential_energy())


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
        write_vesta(gs, out, f'Fig S2 ground state ({label} supercell)',
                    darken_fe=True)


if __name__ == '__main__':
    main()
