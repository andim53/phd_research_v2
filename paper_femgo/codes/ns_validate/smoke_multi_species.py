#!/usr/bin/env python3
"""Smoke check (spec 202610091851, fold M2): multi-species generator parity.

Loads one structure per alloy dataset, builds DeltaZGenerator with the matching
mobile_symbols + sample_ordering=True, and asserts:
  (a) composition preserved across ordering shuffles,
  (b) sample_ordering actually reshuffles species across sites,
  (c) film_height / z_spread finite.
No GPR train, no NS run.
"""
import sys, os
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.join(_HERE, "ns_validate")
if NS not in sys.path:
    sys.path.insert(0, NS)

from agox.databases import Database
from ns_validate.generator import DeltaZGenerator

DATA = os.path.join(_HERE, "..", "..", "data")

CASES = [
    ("femgo",    "seed_10/1_db/db_10.db", ("Fe",)),
    ("fecomgo",  "seed_0/1_db/db_0.db",  ("Fe", "Co")),
    ("fecobmgo", "seed_0/1_db/db_0.db",  ("Fe", "Co", "B")),
    ("febmgo",   "seed_0/1_db/db_0.db",  ("Fe", "B")),
]

ok = True
for name, sub, symbols in CASES:
    path = os.path.join(DATA, name, sub)
    if not os.path.exists(path):
        print(f"[SKIP] {name}: {path} not found")
        continue
    db = Database(filename=path)
    db.restore_to_memory()
    traj = db.restore_to_trajectory()
    ref = traj[0]
    syms = np.asarray(ref.get_chemical_symbols())
    for s in symbols:
        assert s in syms, f"{name}: species {s} absent from reference"
    gen = DeltaZGenerator(ref, mobile_symbols=symbols,
                          sample_ordering=True,
                          rng=np.random.default_rng(1234))
    n_mob = len(gen.mobile_indices)
    # composition of the mobile set as an invariant sorted tuple
    ref_comp = tuple(sorted(syms[gen.mobile_indices]))

    # sample several candidates; assert composition preserved and ordering moved
    dZ = gen.film_height(ref)
    fh_vals, spread_vals = [], []
    seen_orderings = set()
    for _ in range(20):
        a = gen(dZ)
        a_syms = np.asarray(a.get_chemical_symbols())
        comp = tuple(sorted(a_syms[gen.mobile_indices]))
        assert comp == ref_comp, f"{name}: composition changed {ref_comp}->{comp}"
        seen_orderings.add(tuple(a_syms[gen.mobile_indices]))
        fh_vals.append(gen.film_height(a))
        spread_vals.append(gen.z_spread(a))

    assert np.all(np.isfinite(fh_vals)), f"{name}: film_height non-finite"
    assert np.all(np.isfinite(spread_vals)), f"{name}: z_spread non-finite"
    # sample_ordering must actually produce distinct orderings when >1 species
    if len(symbols) > 1:
        assert len(seen_orderings) > 1, f"{name}: sample_ordering did not shuffle"
    print(f"[OK] {name}: mobile={symbols}, n_mobile={n_mob}, "
          f"film_height={fh_vals[0]:.3f} A, z_spread={spread_vals[0]:.3f} A, "
          f"orderings={len(seen_orderings)}")

print("\nALL SMOKE CHECKS PASSED" if ok else "\nSMOKE CHECKS FAILED")