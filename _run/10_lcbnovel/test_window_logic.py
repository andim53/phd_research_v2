"""Standalone test of the auto global-minimum energy window (no Ray/AGOX stack).

Verifies the new `energy_above_min` mode in NoveltyLCBAcquisitor without the
heavy AGOX/ParallelRelax/Ray machinery (which OOMs on this node). Builds the
acquisitor via object.__new__ + attribute assignment to bypass the strict
DatabaseBaseClass type check / observer attach in __init__.
"""
import os, sys, numpy as np
_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import matplotlib; matplotlib.use("Agg")
from novelty_lcb import NoveltyLCBAcquisitor


class MockModel:
    def predict_energy_and_uncertainty(self, cand):
        return cand._E, 0.1


class MockDescriptor:
    def get_features(self, cand):
        return np.array([cand._f])


class MockDB:
    def __init__(self, energies):
        self._e = energies
    def get_all_candidates(self):
        class C: pass
        out = []
        for e in self._e:
            c = C(); c.get_potential_energy = (lambda e=e: e); out.append(c)
        return out


class MockCand:
    def __init__(self, E, f=1.0):
        self._E = E; self._f = f; self.meta = {}
    def add_meta_information(self, k, v): self.meta[k] = v


def make_acq(energy_above_min=None, target=None, delta_E=1.0, db_energies=[]):
    acq = object.__new__(NoveltyLCBAcquisitor)
    acq.model = MockModel()
    acq.descriptor = MockDescriptor()
    acq.database = MockDB(db_energies)
    acq.target_energy = target
    acq.delta_E = delta_E
    acq.energy_above_min = energy_above_min
    acq.novelty_weight = 1.0
    acq.kappa = 2.0
    acq._db_features = None
    return acq


def check(name, got, want):
    ok = got == want
    print(f"[{'OK ' if ok else 'FAIL'}] {name}: got {got}, want {want}")
    return ok


ok = True
# ---- Mode 1: auto global-min, live E_min from DB ----
# DB global min = -436.9, window = (-inf, -436.9+5.0] = (-inf, -431.9]
acq = make_acq(energy_above_min=5.0, db_energies=[-400.0, -436.9, -420.0])
ok &= check("auto: _global_min_energy", acq._global_min_energy(), -436.9)
vals = acq.calculate_acquisition_function([MockCand(-430.0)])
ok &= check("auto: E=-430 (>-431.9) excluded", np.isinf(vals[0]), True)
vals = acq.calculate_acquisition_function([MockCand(-432.0)])
ok &= check("auto: E=-432 (<=-431.9) included", not np.isinf(vals[0]), True)
vals = acq.calculate_acquisition_function([MockCand(-437.5)])
ok &= check("auto: E=-437.5 below min allowed", not np.isinf(vals[0]), True)

# ---- Mode 1b: empty DB -> no cap, everything allowed ----
acq_empty = make_acq(energy_above_min=5.0, db_energies=[])
vals = acq_empty.calculate_acquisition_function([MockCand(-430.0), MockCand(100.0)])
ok &= check("auto: empty DB no cap (both included)",
            not np.isinf(vals[0]) and not np.isinf(vals[1]), True)

# ---- Mode 1c: live update of E_min as DB grows ----
acq2 = make_acq(energy_above_min=3.0, db_energies=[-436.9])
vals = acq2.calculate_acquisition_function([MockCand(-433.0)])  # > -436.9+3=-433.9 excluded
ok &= check("auto: live E_min tracked (excluded)", np.isinf(vals[0]), True)

# ---- Mode 2: backward-compatible centered mode ----
acq3 = make_acq(target=0.0, delta_E=2.0, db_energies=[-400.0])
vals = acq3.calculate_acquisition_function([MockCand(1.0), MockCand(5.0), MockCand(-3.0)])
ok &= check("centered: in-window incl, outside excl",
            not np.isinf(vals[0]) and np.isinf(vals[1]) and np.isinf(vals[2]), True)

# ---- Mode 3: no constraint ----
acq4 = make_acq(target=None, delta_E=None, db_energies=[-400.0])
vals = acq4.calculate_acquisition_function([MockCand(1.0), MockCand(999.0)])
ok &= check("none: no constraint, both included", not np.isinf(vals[0]) and not np.isinf(vals[1]), True)

print("\nRESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
