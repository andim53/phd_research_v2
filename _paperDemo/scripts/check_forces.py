"""Check relaxation quality (force convergence) of the exported flat / ground structures."""
import numpy as np
from ase.io import read

for system in ['femgo','febmgo','fecomgo','fecobmgo']:
    for tag in ['flat_min','ground_min']:
        a = read(f'analysis/flat_structures/{system}_{tag}.xsf')
        f = a.get_forces()                     # XSF stored forces
        fnorm = np.linalg.norm(f, axis=1)
        print(f"{system:9s} {tag:11s} max|F|={fnorm.max():7.4f} eV/A  mean|F|={fnorm.mean():7.4f}  "
              f"rms|F|={np.sqrt((f**2).mean()):7.4f}")
