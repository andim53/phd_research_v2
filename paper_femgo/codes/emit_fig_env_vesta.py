"""
emit_fig_env_vesta.py — Fig S1 (Fig_env) reference structure as a VESTA .vesta.

Reads the AGOX environment reference structure (Fe on MgO(001), full 5x5 cell)
that codes/draw_si_env.py uses for Fig_env, and writes it as a single VESTA 3.5.4
project file via the canonical codes/vesta_writer.py. Height-darkening is OFF
(the Fe reference layer is flat). The owner sets top/side views in VESTA's GUI.

Output:
  analysis/fig_env_vesta/fig_env.vesta

Environment: agox_v2 (/home/think/miniconda3/envs/agox_v2/bin/python).
"""
__version__ = "1.0.0"

import os
import sys

from ase.io import read as ase_read

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR
from vesta_writer import write_vesta

XSF = os.path.join(DATA_DIR, 'femgo', 'seed_3', '0_result', '0_xsf', 'heteroStruct.xsf')
OUT_DIR = os.path.join(os.path.dirname(DATA_DIR), 'analysis', 'fig_env_vesta')
OUT = os.path.join(OUT_DIR, 'fig_env.vesta')


def main():
    if not os.path.exists(XSF):
        print(f'  MISSING {XSF}')
        return 1
    atoms = ase_read(XSF)
    write_vesta(atoms, OUT, 'Fig S1 AGOX environment (5x5 reference cell)',
                darken_fe=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
