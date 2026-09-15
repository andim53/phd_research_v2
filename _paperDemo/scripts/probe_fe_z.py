import numpy as np
from ase.io import read

for f, tag in [('data/dos_femgo_flatngs/4.xsf','FLAT'),
               ('data/dos_femgo_flatngs/3.xsf','ISLAND')]:
    a = read(f); sym = np.array(a.get_chemical_symbols()); z = a.get_positions()[:,2]
    fe_idx = np.where(sym=='Fe')[0]
    fz = z[fe_idx]
    print(f"{tag}: Fe idx {fe_idx.min()}-{fe_idx.max()}, z sorted:", np.round(np.sort(fz),2))
