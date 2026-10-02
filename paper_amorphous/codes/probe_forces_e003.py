#!/usr/bin/env python3
"""probe_forces_e003.py — count retained structures with converged DFT forces.

For each Pt(P) leaf: load all structures (iteration >= 10), apply the per-leaf
e_max = 0.3 eV/atom relative-energy cap (same filter as emit_cna_rdf.py /
CLAIMS), then count how many of the retained structures have
max|F| < 0.05 eV/A (the fmax target in main.py's LocalOptimizationEvaluator).

IMPORTANT (AGOX caveat): the evaluator runs optimizer_run_kwargs={"fmax": 0.05,
"steps": 1} — a SINGLE DFT step after surrogate relaxation. So stored forces are
NOT converged; max|F| ~ 1-40 eV/A is normal. This probe measures that reality.

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/probe_forces_e003.py
"""
from __future__ import annotations

__version__ = "1.0.0"

import glob
import json
import os

import numpy as np
from agox.databases import Database

START_ITER = 10
E_MAX = 0.3
FMAX = 0.05

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# leaf dataset dir (relative to data/17_PPt/) -> (cell, P)
LEAVES = {
    "1_plus0cell/0_0P":   ("+0", "0P"),
    "1_plus0cell/2_20P":  ("+0", "20P"),
    "1_plus0cell/3_30P":  ("+0", "30P"),
    "2_plus3cell/0_0P":   ("+3", "0P"),
    "2_plus3cell/2_20P":  ("+3", "20P"),
    "2_plus3cell/3_30P":  ("+3", "30P"),
    "0_plus5cell/3_3x3_0P":  ("+5", "0P"),
    "0_plus5cell/1_3x3_20P": ("+5", "20P"),
    "0_plus5cell/2_3x3_30P": ("+5", "30P"),
}


def load_leaf(dataset_dir: str, start_iter: int):
    """All structures (iteration >= start) + energies from seed_*/1_db/db_*.db."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    atoms_list, e_list, forced = [], [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        cands = db.get_all_candidates()
        data = db.get_all_structures_data()
        for c, m in zip(cands, data):
            if m.get("iteration", 0) >= start_iter:
                atoms_list.append(c)
                e_list.append(c.get_potential_energy())
                forced.append(np.linalg.norm(c.get_forces(), axis=1).max())
    return atoms_list, np.asarray(e_list, float), np.asarray(forced, float)


def main():
    out_rows = []
    for leaf, (cell, p) in LEAVES.items():
        ds = os.path.join(ROOT, "data", "17_PPt", leaf)
        atoms, energies, fmax = load_leaf(ds, START_ITER)
        if len(atoms) == 0:
            out_rows.append({"leaf": leaf, "cell": cell, "P": p, "error": "no structures"})
            continue
        natoms = len(atoms[0])
        per_atom = (energies - energies.min()) / natoms
        keep = per_atom < E_MAX
        n_ret = int(keep.sum())
        fmax_keep = fmax[keep]
        n_below = int((fmax_keep < FMAX).sum())
        out_rows.append({
            "leaf": leaf, "cell": cell, "P": p,
            "n_loaded_iter10": len(atoms), "n_retained_e003": n_ret,
            "n_force_below_0.05": n_below,
            "frac_force_below": round(n_below / n_ret, 4) if n_ret else None,
            "fmax_retained_median": round(float(np.median(fmax_keep)), 3) if n_ret else None,
            "fmax_retained_max": round(float(fmax_keep.max()), 3) if n_ret else None,
            "fmax_retained_min": round(float(fmax_keep.min()), 3) if n_ret else None,
        })
        print(f"[{cell} {p}] iter>=10: {len(atoms):>5} | retained<0.3eV/at: {n_ret:>5} | "
              f"max|F|<0.05: {n_below:>4} ({100*n_below/n_ret:.1f}%) | "
              f"fmax med/min/max: {np.median(fmax_keep):.2f}/{fmax_keep.min():.2f}/{fmax_keep.max():.2f}")

    tot_ret = sum(r.get("n_retained_e003", 0) for r in out_rows)
    tot_below = sum(r.get("n_force_below_0.05", 0) for r in out_rows)
    print(f"\nTOTAL retained<0.3 eV/atom: {tot_ret}, max|F|<0.05: {tot_below} "
          f"({100*tot_below/tot_ret:.2f}%)" if tot_ret else "TOTAL: no retained structures")

    out = os.path.join(ROOT, "analysis", "force_convergence_probe.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump({
            "description": {
                "name": "force-convergence probe (e_max=0.3, fmax=0.05)",
                "version": __version__,
                "produced_by": "codes/probe_forces_e003.py",
                "purpose": "count retained (iter>=10, per-leaf e_max<0.3 eV/atom) "
                           "structures whose stored DFT max|F| < 0.05 eV/A "
                           "(AGOX LocalOptimizationEvaluator fmax target)",
                "key_definitions": {
                    "n_loaded_iter10": "structures with AGOX iteration >= 10 loaded from seed_*/1_db",
                    "n_retained_e003": "kept after per-leaf (E - E_min)/natoms < 0.3 eV/atom",
                    "n_force_below_0.05": "retained structures with stored max|F| < 0.05 eV/A",
                },
                "caveats": [
                    "AGOX evaluator runs optimizer_run_kwargs={'fmax':0.05,'steps':1}: ONE DFT "
                    "step after surrogate relaxation, so stored forces are typically unconverged "
                    "(~1-40 eV/A)", "single stored force per structure, non-relaxed"],
            },
            "leaves": out_rows,
            "total": {"n_retained_e003": tot_ret, "n_force_below_0.05": tot_below},
        }, f, indent=2)
    print("\nJSON ->", out)


if __name__ == "__main__":
    main()
