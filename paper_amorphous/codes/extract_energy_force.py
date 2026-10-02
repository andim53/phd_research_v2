#!/usr/bin/env python3
"""extract_energy_force.py — persist per-structure (ΔE, max|F|) to JSON/CSV.

Reads every Pt(P) leaf's AGOX DBs (seed_*/1_db/db_*.db), applies the standard
analysis filters (iteration >= 10, per-leaf e_max = 0.3 eV/atom relative-energy
cap), and writes the per-structure energy-vs-force data to disk as the citable
source that the figures read from (same role as analysis/cna_rdf/*/cna_rdf.json).

Outputs (under analysis/energy_vs_force/):
  energy_vs_force.csv              : one row per retained structure (all leaves)
  <leaf>.json                      : per-leaf record with per-structure arrays of
                                     (seed, iteration, dE_eV_per_atom, fmax_eV_A)

The figure scripts (emit_fig_energy_vs_force.py, emit_fig_energy_vs_force_3x3.py)
must import these JSON files rather than re-reading the DBs, so the plotted data
is traceable and re-derivable.

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/extract_energy_force.py
"""
from __future__ import annotations

__version__ = "1.0.0"

import csv
import glob
import json
import os

import numpy as np
from agox.databases import Database

START_ITER = 10
E_MAX = 0.3  # eV/atom, per-leaf relative-energy cap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "analysis", "energy_vs_force")

# leaf dataset dir (relative to data/17_PPt/) -> (cell, P)
LEAVES = {
    "1_plus0cell/0_0P": ("+0", "0P"), "1_plus0cell/2_20P": ("+0", "20P"),
    "1_plus0cell/3_30P": ("+0", "30P"),
    "2_plus3cell/0_0P": ("+3", "0P"), "2_plus3cell/2_20P": ("+3", "20P"),
    "2_plus3cell/3_30P": ("+3", "30P"),
    "0_plus5cell/3_3x3_0P": ("+5", "0P"), "0_plus5cell/1_3x3_20P": ("+5", "20P"),
    "0_plus5cell/2_3x3_30P": ("+5", "30P"),
}


def load_leaf(dataset_dir: str, start_iter: int):
    """Return list of (seed, iteration, energy, fmax, natoms) for iteration >= start."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    rows = []
    for p in db_paths:
        seed = os.path.basename(os.path.dirname(os.path.dirname(p)))
        db = Database(filename=p)
        db.restore_to_memory()
        cands = db.get_all_candidates()
        data = db.get_all_structures_data()
        for c, m in zip(cands, data):
            if m.get("iteration", 0) >= start_iter:
                rows.append((seed, m.get("iteration", 0),
                             c.get_potential_energy(),
                             float(np.linalg.norm(c.get_forces(), axis=1).max()),
                             len(c)))
    return rows


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    leaf_count = 0
    with open(os.path.join(OUTDIR, "energy_vs_force.csv"), "w", newline="") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["leaf", "cell", "P_loading", "seed", "iteration",
                    "dE_eV_per_atom", "fmax_eV_A"])
        for leaf, (cell, p) in LEAVES.items():
            ds = os.path.join(ROOT, "data", "17_PPt", leaf)
            rows = load_leaf(ds, START_ITER)
            if not rows:
                print(f"[{leaf}] no structures")
                continue
            nat = rows[0][4]
            energies = np.asarray([r[2] for r in rows])
            emin = energies.min()
            records = []
            for seed, it, e, fmax, n in rows:
                dE = (e - emin) / nat
                if dE >= E_MAX:
                    continue
                records.append({"seed": seed, "iteration": it,
                                "dE_eV_per_atom": round(float(dE), 6),
                                "fmax_eV_A": round(float(fmax), 6)})
                w.writerow([leaf, cell, p, seed, it, round(dE, 6), round(fmax, 6)])
            leaf_json = {
                "description": {
                    "name": "energy-vs-force per-structure data",
                    "version": __version__,
                    "produced_by": "codes/extract_energy_force.py",
                    "purpose": "citable per-structure (dE, max|F|) data the "
                               "energy-vs-force figures import (instead of "
                               "re-reading AGOX DBs)",
                    "filters": {
                        "iteration_min": START_ITER,
                        "e_max_eV_per_atom": E_MAX,
                        "reference": "per-leaf global energy minimum",
                        "units": {"dE_eV_per_atom": "eV/atom relative to leaf E_min",
                                  "fmax_eV_A": "eV/angstrom, max |F| over all atoms"},
                    },
                    "caveats": [
                        "fmax is the STORED force after the AGOX evaluator's "
                        "single DFT step (optimizer_run_kwargs={'fmax':0.05,'steps':1}); "
                        "P-doped leaves are not force-converged (0.7-40 eV/A)",
                        "dE evaluated per leaf against that leaf's own global minimum"],
                },
                "leaf": leaf, "cell": cell, "P_loading": p, "natoms": nat,
                "n_retained": len(records),
                "global_min_eV": float(emin),
                "structures": records,
            }
            with open(os.path.join(OUTDIR, f"{leaf.replace('/', '_')}.json"), "w") as f:
                json.dump(leaf_json, f, indent=2)
            print(f"[{cell} {p}] {leaf}: retained {len(records)} -> "
                  f"{leaf.replace('/', '_')}.json + energy_vs_force.csv")
            leaf_count += len(records)

    print(f"\nTOTAL retained per-structure rows written: {leaf_count}")
    print("->", os.path.join(OUTDIR, "energy_vs_force.csv"), "and",
          os.path.join(OUTDIR, "<leaf>.json"))


if __name__ == "__main__":
    main()
