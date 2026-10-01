#!/usr/bin/env python3
"""
emit_cna_rdf.py — Steinhardt q4/q6 crystalline fraction + partial RDF for Pt(P).

Runs in the **agox_v2** env (AGOX + ASE + scipy, NO pyscal). For one leaf
(dataset dir holding seed_*/1_db/db_*.db) it loads every structure, computes
per-atom Steinhardt bond-order parameters q4/q6 from the first-neighbour shell
(ASE NeighborList, cutoff = 1.3 * nearest-neighbour distance), classifies each
atom as fcc-like (crystalline) vs disordered, and computes the partial radial
distribution functions g_ij(r) for the Pt-P and P-P pairs (ASE Analysis.get_rdf).

This is the structural cross-check for the amorphization / cell-expansion claims
(MT-1..MT-3): the integrated-CI shift from XRD is small (~7%), so we need a
per-atom order metric to decide whether +3%/+5% cell expansion genuinely
promotes disorder relative to +0%.

An optional relative-energy cap (--e-max, eV/atom) keeps only structures within
that energy of the leaf's own global minimum (per-leaf reference), so the
crystalline fraction describes the low-energy amorphous basin rather than the
whole retained ensemble.

Writes, under --outdir:
  cna_rdf.json        : per-structure + leaf-aggregate crystalline fraction,
                        mean q4/q6, and partial RDF curves.
  cna_rdf_fraction.png: crystalline-fraction distribution (histogram).
  cna_rdf_partial.png : partial RDF g_PtP(r) and g_PP(r).

Usage (agox_v2):
  PY_A=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY_A emit_cna_rdf.py --dataset 17_PPt/1_plus0cell/2_20P \
        --outdir analysis/cna_rdf/1_plus0cell_2_20P --start-iter 10 --e-max 0.3
"""
from __future__ import annotations

__version__ = "1.1.0"

import argparse
import glob
import json
import os

import numpy as np
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agox.databases import Database
from ase.geometry.rdf import get_rdf as ase_get_rdf
from ase.neighborlist import neighbor_list
from scipy.special import sph_harm_y

# --- figure style (match _analysist) ---
plt.rcParams.update({
    "font.family": "serif", "font.size": 12,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "axes.grid": False, "figure.autolayout": True, "savefig.dpi": 300,
})


def load_leaf(dataset_dir: str, start_iter: int = 10):
    """All structures + DFT energies from dataset_dir/seed_*/1_db/db_*.db,
    iteration >= start_iter. Returns list[atoms], np energies, seed labels."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    if not db_paths:
        raise FileNotFoundError(
            f"No DBs matched {os.path.join(dataset_dir, 'seed_*/1_db/db_*.db')}")
    atoms_list, e_list, labels = [], [], []
    for p in db_paths:
        db = Database(filename=p)
        db.restore_to_memory()
        raw = db.get_all_structures_data()
        kept = [d for d in raw if d.get("iteration", 0) >= start_iter]
        for d in kept:
            a = db.db_to_atoms(d)
            atoms_list.append(a)
            e_list.append(a.get_potential_energy())
            rel = os.path.relpath(p, dataset_dir)
            labels.append(rel.split(os.sep)[0])
    return atoms_list, np.asarray(e_list, dtype=float), labels


def steinhardt_q(atoms, l: int, cutoff_scale: float = 1.3):
    """Per-atom Steinhardt q_l for a periodic Atoms object (vectorized).

    Neighbour shell = first-neighbour distance * cutoff_scale. Uses
    atoms.get_neighbor_list() (single call for all pairs, bothways). q_lm(i) =
    (1/N_i) sum_j Y_lm(theta_ij, phi_ij); q_l(i) = sqrt(4pi/(2l+1) * sum_m
    |q_lm|^2).
    """
    pos = atoms.get_positions()
    cell = atoms.get_cell()
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    r_nn = d.min()
    cutoff = r_nn * cutoff_scale

    i, j, S, dist = neighbor_list("ijSd", atoms, cutoff=cutoff, self_interaction=False)
    if len(i) == 0:
        return np.zeros(len(atoms))
    rv = pos[j] + S @ cell - pos[i]
    r = np.linalg.norm(rv, axis=1)
    theta = np.arccos(np.clip(rv[:, 2] / r, -1, 1))
    phi = np.arctan2(rv[:, 1], rv[:, 0])

    q = np.zeros(len(atoms))
    for m in range(-l, l + 1):
        ylm = sph_harm_y(l, m, theta, phi)
        # sum over neighbours per atom i
        s = np.bincount(i, weights=ylm.real, minlength=len(atoms)) + \
            1j * np.bincount(i, weights=ylm.imag, minlength=len(atoms))
        q += np.abs(s) ** 2
    # normalize by neighbour count per atom
    ncount = np.bincount(i, minlength=len(atoms)).astype(float)
    ncount[ncount == 0] = 1.0
    q = np.sqrt(4 * np.pi / (2 * l + 1) * q) / ncount
    return q


def crystalline_fraction(atoms, q6_threshold: float = 0.5):
    """Fraction of atoms with q6 above threshold (fcc q6 ~= 0.5745)."""
    q6 = steinhardt_q(atoms, 6)
    return float(np.mean(q6 > q6_threshold)), q6


def partial_rdf(atoms, pair, rmax: float = 5.0, nbins: int = 200):
    """Partial RDF g_ij(r) for an element pair via ase.geometry.rdf.get_rdf.

    pair = (symbol_a, symbol_b). Uses the builtin two-element mask (atomic
    numbers) so only A-B pairs contribute. Returns (r, g) arrays. If either
    element is absent (e.g. P in a 0P leaf), returns (None, None).
    """
    syms = atoms.get_chemical_symbols()
    if not all(s in syms for s in pair):
        return None, None
    z = {s: atoms.numbers[syms.index(s)] for s in pair}
    el = (z[pair[0]], z[pair[1]])
    rdf, dists = ase_get_rdf(atoms, rmax, nbins, elements=el, no_dists=False)
    r = np.linspace(0, rmax, nbins)
    return r, np.asarray(rdf)


def main():
    parser = argparse.ArgumentParser(
        description="Steinhardt q4/q6 crystalline fraction + partial RDF (agox_v2).")
    parser.add_argument("--dataset", required=True,
                        help="leaf dataset dir holding seed_*/1_db/db_*.db")
    parser.add_argument("--outdir", required=True, help="output dir")
    parser.add_argument("--start-iter", type=int, default=10,
                        help="keep structures with AGOX iteration >= this. Default 10.")
    parser.add_argument("--e-max", type=float, default=None,
                        help="keep only structures within this relative energy per atom "
                             "(eV/atom) of the leaf's own global minimum. Default: None (no cap).")
    parser.add_argument("--q6-threshold", type=float, default=0.5,
                        help="q6 above which an atom is fcc-like. Default 0.5.")
    parser.add_argument("--rmax", type=float, default=5.0,
                        help="RDF max radius (Angstrom); must be <= half the "
                             "smallest cell (11.927/2 ~= 5.96 for +0%). Default 5.0.")
    parser.add_argument("--nbins", type=int, default=200,
                        help="RDF bins. Default 200.")
    args = parser.parse_args()

    print("=" * 70)
    print("CNA/RDF (agox_v2) — Steinhardt crystalline fraction + partial RDF")
    print("dataset:", args.dataset)
    print("outdir :", args.outdir)
    print("=" * 70)

    atoms_list, energies, labels = load_leaf(args.dataset, start_iter=args.start_iter)
    if not atoms_list:
        raise SystemExit("No structures loaded.")
    natoms = len(atoms_list[0])
    comp = Counter(atoms_list[0].get_chemical_symbols())
    print(f"leaf: {natoms} atoms/struct, comp={dict(comp)}, "
          f"n_structures={len(atoms_list)}")

    # Optional relative-energy cap: keep only structures within e_max eV/atom of
    # the leaf's own global minimum (per-leaf reference).
    n_full = len(atoms_list)
    if args.e_max is not None:
        per_atom = (energies - energies.min()) / natoms
        keep = per_atom < args.e_max
        atoms_list = [a for a, k in zip(atoms_list, keep) if k]
        energies = energies[keep]
        print(f"e_max={args.e_max} eV/atom (per-leaf min ref): "
              f"kept {len(atoms_list)}/{n_full} structures "
              f"({100*len(atoms_list)/n_full:.1f}%)")
        if not atoms_list:
            raise SystemExit("No structures within the e_max cap.")

    os.makedirs(args.outdir, exist_ok=True)

    fracs, q6_means, q4_means = [], [], []
    r_ptp = g_ptp = r_pp = g_pp = None
    for k, a in enumerate(atoms_list):
        q6 = steinhardt_q(a, 6)
        q4 = steinhardt_q(a, 4)
        frac = float(np.mean(q6 > args.q6_threshold))
        fracs.append(frac)
        q6_means.append(float(q6.mean()))
        q4_means.append(float(q4.mean()))
        # partial RDF on the first structure only (representative; cheap)
        if k == 0:
            r_ptp, g_ptp = partial_rdf(a, ("Pt", "P"), args.rmax, args.nbins)
            r_pp, g_pp = partial_rdf(a, ("P", "P"), args.rmax, args.nbins)
        if (k + 1) % 20 == 0:
            print(f"  {k+1}/{len(atoms_list)} structures")

    fracs = np.asarray(fracs)
    q6_means = np.asarray(q6_means)
    q4_means = np.asarray(q4_means)

    result = {
        "leaf": os.path.basename(os.path.normpath(args.dataset)),
        "natoms": natoms, "composition": dict(comp),
        "n_structures": len(atoms_list),
        "n_structures_full": n_full,
        "e_max": args.e_max,
        "q6_threshold": args.q6_threshold,
        "crystalline_fraction": {
            "mean": float(fracs.mean()),
            "std": float(fracs.std()),
            "median": float(np.median(fracs)),
            "per_structure": [round(float(x), 4) for x in fracs],
        },
        "q6_mean": {"mean": float(q6_means.mean()), "std": float(q6_means.std())},
        "q4_mean": {"mean": float(q4_means.mean()), "std": float(q4_means.std())},
        "partial_rdf": {
            "r": [round(float(x), 4) for x in r_ptp] if r_ptp is not None else None,
            "g_PtP": [round(float(x), 4) for x in g_ptp] if g_ptp is not None else None,
            "g_PP": [round(float(x), 4) for x in g_pp] if g_pp is not None else None,
        },
    }
    jpath = os.path.join(args.outdir, "cna_rdf.json")
    with open(jpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nDONE. JSON -> {jpath}")
    print(f"crystalline fraction: mean={fracs.mean():.3f} "
          f"std={fracs.std():.3f} median={np.median(fracs):.3f}")
    print(f"q6 mean={q6_means.mean():.3f}  q4 mean={q4_means.mean():.3f}")

    # --- figures ---
    fig, ax = plt.subplots()
    ax.hist(fracs, bins=20, color="tab:blue", edgecolor="k", alpha=0.8)
    ax.axvline(fracs.mean(), color="tab:red", ls="--", lw=1.5,
               label=f"mean = {fracs.mean():.3f}")
    ax.set_xlabel("crystalline fraction (q6 > %.2f)" % args.q6_threshold)
    ax.set_ylabel("count")
    ax.legend()
    fig.savefig(os.path.join(args.outdir, "cna_rdf_fraction.png"))
    plt.close(fig)

    if r_ptp is not None:
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        ax1.plot(r_ptp, g_ptp, color="tab:red")
        ax1.set_ylabel("g$_{Pt-P}$(r)")
        ax2.plot(r_pp, g_pp, color="tab:purple")
        ax2.set_ylabel("g$_{P-P}$(r)")
        ax2.set_xlabel("r (Å)")
        fig.savefig(os.path.join(args.outdir, "cna_rdf_partial.png"))
        plt.close(fig)
    print("figures ->", os.path.join(args.outdir, "cna_rdf_fraction.png"),
          os.path.join(args.outdir, "cna_rdf_partial.png"))


if __name__ == "__main__":
    main()
