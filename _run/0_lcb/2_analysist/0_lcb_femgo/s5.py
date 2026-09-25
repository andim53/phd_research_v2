"""Stacking smoke: verify the Fe/MgO structure main.py would build has good MgO
stacking + correct Fe placement for the requested layer count.
Usage:  $PY smoke_stack.py    (edit N and VAC below per run dir)"""
import sys
import numpy as np
from ase.build import surface
sys.path.insert(0, 'scripts')
from build_mgo_stack import build_mgo_stack
from build_heteroStruct import build_heteroStruct
from build_fe_stack import build_fe_stack

N   = 5                     # EDIT per dir: 3 | 5 | 10
VAC = 28.4                  # EDIT per dir: 24.2 | 28.4 | 39.0
a_mgo, a_fe = 4.212, 2.870190
dist_z_fe2o, SC = 0.5, (5, 5, 1)

slab_fe_base = surface('Fe', (0, 0, 1), layers=1, vacuum=VAC)
sm = build_mgo_stack(slab_fe_base, num_layers=N, vacuum=VAC)
mgo = sm[[a.symbol != 'Fe' for a in sm]].repeat(SC)          # MgO substrate
fe  = build_fe_stack(slab_fe_base, num_layers=1, vacuum=VAC).repeat(SC)
het = build_heteroStruct(mgo.copy(), fe.copy(), dist_inter=dist_z_fe2o, vacuum=VAC)

ok = True
def chk(msg, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and cond

o   = het[[a.symbol == 'O'  for a in het]]
mg  = het[[a.symbol == 'Mg' for a in het]]
fea = het[[a.symbol == 'Fe' for a in het]]
oz  = np.sort(np.unique(np.round(o.positions[:, 2], 3)))
mz  = np.sort(np.unique(np.round(mg.positions[:, 2], 3)))
fz  = np.sort(np.unique(np.round(fea.positions[:, 2], 3)))
cz  = mgo.cell[2, 2]; zmax = het.positions[:, 2].max()

chk(f'{N} MgO layers (O planes={len(oz)})', len(oz) == N)
chk(f'{N} MgO layers (Mg planes={len(mz)})', len(mz) == N)
chk('O and Mg coplanar per plane', np.allclose(oz, mz, atol=0.01))
chk('plane spacing ~ 2.106 A', np.allclose(np.diff(oz), 2.106, atol=0.01))
chk('25 Mg + 25 O per plane (5x5)', len(o) == 25*N and len(mg) == 25*N)
chk('single Fe plane (25)', len(fea) == 25 and len(fz) == 1)
chk(f'Fe sits 0.50 A above top MgO (gap {fz.min()-oz.max():.2f})',
    np.isclose(fz.min() - oz.max(), dist_z_fe2o, atol=0.02))
chk(f'cell clearance above Fe >= 10 A (={cz-zmax:.1f})', cz - zmax >= 10.0)
chk('no atom below cell bottom / above cell top', zmax < cz - 1.0)

print('--- per-MgO-plane z (O and Mg coincide):', oz)
print('STACKING SMOKE ' + ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
