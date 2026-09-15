import numpy as np
from ase.io import read

for f, tag in [('data/dos_femgo_flatngs/4.xsf','FLAT'),
               ('data/dos_femgo_flatngs/3.xsf','ISLAND')]:
    a = read(f); sym = np.array(a.get_chemical_symbols())
    pos = a.get_positions(); z = pos[:,2]
    mgo = np.isin(sym, ('Mg','O'))
    print(f"\n=== {tag} ===")
    print(f"  substrate z: Mg {z[sym=='Mg'].min():.2f}-{z[sym=='Mg'].max():.2f}, "
          f"O {z[sym=='O'].min():.2f}-{z[sym=='O'].max():.2f}")
    # Mg and O in-plane positions
    mgxy = pos[sym=='Mg'][:,:2]; oxy = pos[sym=='O'][:,:2]
    print(f"  n Mg {len(mgxy)}, n O {len(oxy)}")
    print(f"  Mg xy[0:3]: {np.round(mgxy[:3],3)}")
    print(f"  O  xy[0:3]: {np.round(oxy[:3],3)}")
    fe_idx = np.where(sym=='Fe')[0]
    fpos = pos[fe_idx]; fz = z[fe_idx]
    opos = pos[sym=='O']; mgpos = pos[sym=='Mg']
    # distance to nearest O and Mg (3D)
    dO = np.linalg.norm(fpos[:,None,:]-opos[None,:,:],axis=2).min(1)
    dMg = np.linalg.norm(fpos[:,None,:]-mgpos[None,:,:],axis=2).min(1)
    print(f"  Fe z sorted: {np.round(np.sort(fz),2)}")
    print(f"  Fe nearest-O dist sorted: {np.round(np.sort(dO),2)}")
    # xy-nearest substrate species + offset
    for j, i in enumerate(np.argsort(fz)):
        p = fpos[i]
        # nearest O in xy
        odo = np.linalg.norm(oxy - p[:2], axis=1); j_o = odo.argmin()
        mdo = np.linalg.norm(mgxy - p[:2], axis=1); j_m = mdo.argmin()
        who = 'O' if odo[j_o] < mdo[j_m] else 'Mg'
        off = min(odo[j_o], mdo[j_m])
        if j < 12:
            print(f"    Fe z={fz[i]:.2f} dO={dO[i]:.2f} dMg={dMg[i]:.2f}  xy-nearest={who} (offset {off:.2f})")
