# Fingerprint feature dimension — how "720" for Fe/MgO is built

`Fingerprint.create_features(atoms).shape[1]` returns a fixed integer per
system/composition (default params `rc1=6, rc2=4, binwidth=0.2, Nbins=30,
use_angular=True`). For the 3-species Fe/MgO system it is **720**, verified from the
descriptor internals (`agox/models/descriptors/fingerprint_cython/angular_fingerprintFeature_cy.pyx`).

## Breakdown
- **2-body / radial = 180**: 6 pair ("bond") types × 30 radial bins
  (`Nbins1 = ceil(rc1/binwidth) = ceil(6/0.2) = 30`).
  - 6 pairs = 3 same-species (Fe–Fe, Mg–Mg, O–O) + 3 cross (Fe–Mg, Fe–O, Mg–O), with pbc.
  - `Nelements_2body = Nbondtypes_2body * Nbins1`.
- **3-body / angular = 540**: 18 triple types × 30 angular bins
  (`Nbins2 = 30`, from `binwidth2 = π/Nbins2`).
  - `Nelements_3body = Nbondtypes_3body * Nbins2`.
- **Total = 180 + 540 = 720.**

## Meaning
"Feature dim 720" = the length of the descriptor vector representing each structure,
capturing radial distance (2-body) and bond-angle (3-body) distributions around atoms.
It is fixed regardless of geometry, which is what lets GPR treat structures as points
in 720-D feature space and measure similarity via the kernel. When `use_angular=False`,
only the 2-body part is kept (180 for this system).
