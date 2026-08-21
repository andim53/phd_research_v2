#!/usr/bin/env python3
"""
DFT re-relaxation of the novel-filter distinct structures, then a minima-only
partition function.

Why
---
The structures in the novel filter are surrogate-relaxed geometries with
single-point DFT energies (the original run's evaluator used only
``optimizer_run_kwargs={"fmax":0.05, "steps":1}``), so they are NOT converged
local minima (median max|force| ~1.5 eV/A). To build a partition function that
"captures only the minimum", each kept structure is re-relaxed here with real
DFT (GPAW) to a strict ``fmax`` so every surviving structure is a genuine local
minimum, and only those verified minima enter the partition function.

Method (faithful to dataset/main.py)
------------------------------------
- GPAW calculator uses the exact parameters from dataset/main.py (lcao/dzp,
  PBE, spin-polarised, pulay mixer, nbands='nao', etc.).
- The 50-atom MgO substrate (all Mg+O atoms at the bottom layer) is held fixed
  with FixAtoms, matching the original Environment's template constraint; only
  the 25 Fe atoms are relaxed (original physics preserved).
- Structures relaxed with ASE BFGS to ``--fmax`` (default 0.05 eV/A).
- A structure counts as a VERIFIED local minimum iff max|force| after
  relaxation is below ``--fmax``.
- Distinctness is already guaranteed by the fingerprint threshold; no extra
  check is added (per the chosen approach).

Partition function
------------------
Only the VERIFIED distinct minima enter:
    Z(T) = sum_i exp(-beta * (E_i - E_glob))   (minima-only; no KDE, no
    double counting), evaluated at the Stage-3 temperatures.

Caching
-------
Relaxation results are cached in ``<cache_dir>/relaxed_<fname>.json`` keyed by
the source XSF filename. Re-running on another (nested) threshold reuses
already-relaxed structures instead of recomputing them.

Run (agox_v2 env, on a node with GPAW):
    /home/think/miniconda3/envs/agox_v2/bin/python relax_and_partition.py \
        --thresholds 1.0 --fmax 0.05 --outdir ./novel_output
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ase.io import read, write
from ase.optimize import BFGS
from ase.constraints import FixAtoms

# --- GPAW parameters (verbatim from dataset/main.py) -------------------------
GPAW_PARAMS = dict(
    mode={"name": "lcao"},
    basis="dzp",
    xc="PBE",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    kpts=(1, 1, 1),
    symmetry="off",
    nbands="nao",
    maxiter=100,
    occupations={"name": "fermi-dirac", "width": 0.05},
    hund=True,
    spinpol=True,
)

# Stage-3 temperatures
TEMPS = [298.15, 348.60, 447.875, 547.15, 646.425]
KB = 8.6173e-5  # eV/K


# ---------------------------------------------------------------------------
def load_threshold_set(thr_dir: str):
    """Rank-ordered structures + energies for one threshold folder."""
    ns_dir = os.path.join(thr_dir, "novel_structures")
    struct_files = sorted(glob.glob(os.path.join(ns_dir, "novel_*.xsf")),
                          key=lambda p: int(os.path.basename(p).split("_")[1]))
    if not struct_files:
        raise FileNotFoundError(f"No novel_*.xsf in {ns_dir}")
    structures = [read(f) for f in struct_files]

    csv_path = os.path.join(thr_dir, "novel_structures_summary.csv")
    energies = {}
    with open(csv_path) as fh:
        next(fh)
        for line in fh:
            parts = line.strip().split(",")
            energies[int(parts[0])] = float(parts[2])
    e_arr = np.array([energies[r] for r in range(len(structures))], dtype=float)
    return structures, e_arr


def substrate_indices(atoms) -> np.ndarray:
    """Indices of the fixed MgO substrate = all Mg+O atoms (the bottom layer)."""
    return np.array([i for i, s in enumerate(atoms.get_chemical_symbols())
                     if s in ("Mg", "O")], dtype=int)


def relax_one(atoms, fmax, txt_path, ncores):
    """Re-relax one structure with GPAW + BFGS; return (relaxed_atoms, converged_bool)."""
    a = atoms.copy()
    a.set_constraint(FixAtoms(indices=substrate_indices(a)))

    from gpaw import GPAW
    calc = GPAW(**GPAW_PARAMS, txt=txt_path)
    a.set_calculator(calc)

    opt = BFGS(a, logfile=None, trajectory=None)
    try:
        opt.run(fmax=fmax)
    except Exception as e:
        print(f"    optimizer error: {e}")
    # converged iff final max force < fmax
    forces = a.get_forces()
    conv = bool(np.abs(forces).max() < fmax)
    a.calc = None  # drop calculator so it can be cached / written cleanly
    return a, conv


def relax_all(structures, energies, files, fmax, out_dir, cache_dir, ncores):
    """Relax each structure (cached), return list of relaxed atoms + conv flags."""
    os.makedirs(cache_dir, exist_ok=True)
    results = []   # dict per structure
    for idx, (a, E0, fname) in enumerate(zip(structures, energies, files)):
        cache = os.path.join(cache_dir, f"relaxed_{os.path.basename(fname)}.json")
        if os.path.exists(cache):
            with open(cache) as fh:
                d = json.load(fh)
            ra = read(d["xsf_path"])
            results.append({**d, "atoms": ra})
            print(f"  [{idx+1}/{len(structures)}] {os.path.basename(fname)}: "
                  f"cached  E={d['E_relaxed']:.4f}  fmax={d['max_force']:.4f}  "
                  f"conv={d['converged']}")
            continue

        print(f"  [{idx+1}/{len(structures)}] relaxing {os.path.basename(fname)} "
              f"(E0={E0:.4f}) ...", flush=True)
        txt = os.path.join(cache_dir, f"gpaw_{os.path.basename(fname)}.txt")
        ra, conv = relax_one(a, fmax, txt, ncores)
        forces = ra.get_forces()
        d = {
            "source_file": fname,
            "rank": idx,
            "E0": E0,
            "E_relaxed": float(ra.get_potential_energy()),
            "max_force": float(np.abs(forces).max()),
            "converged": conv,
            "xsf_path": None,  # filled below after writing
        }
        xsf = os.path.join(out_dir, "relaxed_structures",
                           f"relaxed_{os.path.basename(fname)}")
        os.makedirs(os.path.dirname(xsf), exist_ok=True)
        write(xsf, ra)
        d["xsf_path"] = xsf
        # cache WITHOUT the atoms object
        with open(cache, "w") as fh:
            json.dump({k: v for k, v in d.items() if k != "atoms"}, fh, indent=2)
        results.append({**d, "atoms": ra})
        print(f"    -> E={d['E_relaxed']:.4f}  fmax={d['max_force']:.4f}  "
              f"conv={d['converged']}", flush=True)
    return results


def minima_partition_function(relaxed_results, fmax, temps):
    """Z(T) over VERIFIED distinct minima only (max_force < fmax)."""
    verified = [d for d in relaxed_results if d["converged"]]
    if not verified:
        return None, None, verified
    E = np.array([d["E_relaxed"] for d in verified], dtype=float)
    E_glob = E.min()
    rel = E - E_glob
    rows = []
    for T in temps:
        beta = 1.0 / (KB * T)
        logZ = -beta * rel.max()  # placeholder; real below
        # log-sum-exp
        m = (-beta * rel).max()
        logZ = m + np.log(np.exp(-beta * rel - m).sum())
        rows.append((T, float(np.exp(logZ)), float(logZ)))
    return rows, E, verified


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--thresholds", default="1.0",
                   help="Comma-separated threshold folder suffixes to relax "
                        "(e.g. '0.5,1,2'). Default 1.0")
    p.add_argument("--fmax", type=float, default=0.05,
                   help="Force convergence (eV/A) for a verified local minimum. "
                        "Default 0.05.")
    p.add_argument("--outdir", default=os.path.join(_HERE, "novel_output"),
                   help="Run output dir containing thr_<v>/ folders (default novel_output)")
    p.add_argument("--ncores", type=int, default=1,
                   help="MPI cores for GPAW (default 1; on a node use --ncores N). "
                        "Ignored here; GPAW picks up MPI from the launch command.")
    p.add_argument("--limit", type=int, default=None,
                   help="Relax only the first N (lowest-energy) structures per "
                        "threshold (for a smoke test / to bound cost). Default: all.")
    args = p.parse_args()

    thr_suffixes = [v.strip() for v in args.thresholds.split(",") if v.strip()]
    all_rows = {}   # threshold -> (temps, logZ list, E array, verified list)

    for suf in thr_suffixes:
        thr_dir = os.path.join(args.outdir, f"thr_{suf}")
        if not os.path.isdir(thr_dir):
            print(f"WARNING: {thr_dir} not found, skipping")
            continue
        name = f"thr_{suf}"
        print(f"\n=== {name} ===")
        structures, energies = load_threshold_set(thr_dir)
        files = sorted(glob.glob(os.path.join(thr_dir, "novel_structures", "novel_*.xsf")),
                       key=lambda p: int(os.path.basename(p).split("_")[1]))
        if args.limit:
            structures = structures[:args.limit]
            energies = energies[:args.limit]
            files = files[:args.limit]
        print(f"  relaxing {len(structures)} structures (fmax={args.fmax})")

        out_dir = os.path.join(thr_dir, "relaxed")
        cache_dir = os.path.join(out_dir, "cache")
        results = relax_all(structures, energies, files, args.fmax,
                            out_dir, cache_dir, args.ncores)

        # ---- partition function over verified minima ----
        rows, E, verified = minima_partition_function(results, args.fmax, TEMPS)
        n_conv = sum(1 for d in results if d["converged"])
        print(f"  verified local minima: {n_conv}/{len(results)}")

        # save per-threshold partition function + summary
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "relax_summary.csv"), "w") as fh:
            fh.write("rank,source_file,E0_eV,E_relaxed_eV,max_force,converged,relaxed_xsf\n")
            for d in results:
                fh.write(f"{d['rank']},{d['source_file']},{d['E0']:.6f},"
                         f"{d['E_relaxed']:.6f},{d['max_force']:.6f},"
                         f"{d['converged']},{d['xsf_path']}\n")
        if rows:
            with open(os.path.join(out_dir, "minima_partition_function.csv"), "w") as fh:
                fh.write("temperature_K,Z,log_Z\n")
                for T, Z, lZ in rows:
                    fh.write(f"{T},{Z:.6e},{lZ:.6f}\n")
                    print(f"    T={T:7.2f} K   Z={Z:.6e}   log Z={lZ:.4f} "
                          f"({n_conv} verified minima)")
        all_rows[name] = (rows, E, verified)

    # cross-threshold summary
    if all_rows:
        comp = os.path.join(args.outdir, "minima_partition_function_comparison.csv")
        with open(comp, "w") as fh:
            fh.write("threshold,verified_minima,temperature_K,log_Z\n")
            for name, (rows, E, verified) in all_rows.items():
                if not rows:
                    continue
                for T, Z, lZ in rows:
                    fh.write(f"{name},{len(verified)},{T},{lZ:.6f}\n")
        print(f"\nComparison written to {comp}")
    print("\nDone.")


if __name__ == "__main__":
    main()
