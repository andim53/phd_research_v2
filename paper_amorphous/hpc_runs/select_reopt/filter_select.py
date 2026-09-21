"""select.py — Run A (stage 1): novelty + force filter over amorphous Pt(P) leaves.

Runs in the **agox_v2** env (AGOX 3.10.2 + ASE 3.25 + GPAW). For each amorphous
Pt-P leaf it:
  1. loads every seed DB (restore_to_memory, iteration-filtered),
  2. computes relative energy (eV/atom), force metrics (max, mean, P-sublattice max),
  3. applies the per-leaf force gate (percentile + leaf-adaptive absolute cutoff),
  4. dedups by AGOX Fingerprint (raw Euclidean, per-leaf pool — see spec C1/M6a),
  5. picks the top `n` most novel + low-force distinct minima per leaf,
  6. writes the selected structures as XSF (one per rank) + a provenance JSON.

It does NOT relax anything (that is reopt.py) and writes NO traj here. It is a
read-only consumer of data/17_PPt (never modifies it).

Selection rule (spec M1/M5/C3/m7):
  keep  max|F| in lowest FORCE_PCT%  AND  max|F| < leaf_thr  (leaf-adaptive)
  fallback: if < MIN_PER_LEAF survivors, raise leaf_thr by +0.5 stepwise until >=1.
The leaf-adaptive threshold defaults come from the measured force distribution:
  20P leaves ~1.0 eV/A, 30P leaves ~2.0 eV/A (30P force scales ~2x higher).
Both max|F| and mean|F| and P-sublattice max|F| are recorded (m7).

Outputs under --outdir:
  selected/<leaf>/<rank>.xsf           one XSF per chosen structure
  selection_<leaf>.json                provenance (leaf, rank, source db, candidate
                                       index, energy, force metrics, novelty dist)

Usage (agox_v2):
  PY_A=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY_A select.py --outdir ./out --n-per-leaf 3
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import json
import os
from pathlib import Path

import numpy as np

MATPLOTLIB_HEADLESS = True  # no plotting in this stage; keep import-free of mpl

from agox.databases import Database


# ============================================================================
# Per-leaf adaptive force thresholds (measured frac<1.0: 20P ~17%, 30P ~0-1%)
# If a leaf dir name contains '30P' -> 30P; else 20P default.
# ============================================================================
def leaf_force_thr(leaf_dir: str, explicit: float | None = None) -> float:
    if explicit is not None:
        return explicit
    if "30P" in leaf_dir:
        return 2.0
    return 1.0


def force_metrics(forces):
    """Per-structure force metrics. forces: (N,3) array."""
    n = np.linalg.norm(forces, axis=1)
    # P sublattice indices passed in by caller via symbols
    return {
        "max_force": float(n.max()),
        "mean_force": float(n.mean()),
    }


def load_leaf(leaf_dir: str, it_min: int, e_max: float):
    """Load all candidates from a leaf's seed DBs, iteration-filtered.

    Returns list of dicts: {atoms, energy, iteration, source_db, max_f, mean_f,
    rel_energy (eV/atom), p_max_f}.
    """
    dbs = sorted(glob.glob(os.path.join(leaf_dir, "seed_*/1_db/db_*.db")))
    out = []
    for dbp in dbs:
        db = Database(filename=dbp)
        db.restore_to_memory()  # REQUIRED before get_all_candidates()
        cands = db.get_all_candidates()
        metas = db.get_all_structures_data()
        if not cands:
            continue
        # composition guard
        comp = cands[0].get_chemical_formula()
        symbols = cands[0].get_chemical_symbols()
        p_idx = [i for i, s in enumerate(symbols) if s == "P"]
        for c, m in zip(cands, metas):
            if m["iteration"] < it_min:
                continue
            F = np.asarray(c.get_forces())
            n = np.linalg.norm(F, axis=1)
            p_max = float(n[p_idx].max()) if p_idx else float(n.max())
            out.append({
                "atoms": c,
                "energy": c.get_potential_energy(),
                "iteration": m["iteration"],
                "source_db": dbp,
                "max_f": float(n.max()),
                "mean_f": float(n.mean()),
                "p_max_f": p_max,
            })
    if not out:
        return [], None
    comps = {c["atoms"].get_chemical_formula() for c in out}
    if len(comps) > 1:
        raise RuntimeError(f"mixed composition across leaf {leaf_dir}: {comps}")
    # relative energy per atom
    energies = np.array([o["energy"] for o in out])
    emin = energies.min()
    n_atoms = len(out[0]["atoms"])
    for o in out:
        o["rel_energy"] = (o["energy"] - emin) / n_atoms
    return out, sorted(comps)[0]


def fingerprint_features(out, leaf_dir):
    """Per-structure AGOX Fingerprint feature vector (raw, un-normalised)."""
    from agox.models.descriptors import Fingerprint
    from agox.environments import Environment

    first = out[0]["atoms"]
    symbols_comp = first.get_chemical_formula()
    env = Environment(
        template=first.get_template(),
        symbols=symbols_comp,
        use_box_constraint=False,
        print_report=False,
    )
    fp = Fingerprint(environment=env)
    feats = []
    for o in out:
        f = fp.create_features(o["atoms"]).ravel()
        feats.append(np.asarray(f, dtype=float))
    return np.vstack(feats)


def greedy_distinct(features, tol):
    """Lowest-energy-first greedy dedup. Returns kept feature-row indices.

    `order` ranks candidate structures by (their offset in the candidate list is the
    row index); the caller pre-sorts candidates by rel_energy so greedy walks lowest
    energy first and keeps a structure only if its fingerprint is > tol from every
    already-kept one.
    """
    kept = []
    order = [i for i in range(len(features))]
    for idx in order:
        f = features[idx]
        if all(np.linalg.norm(f - features[k]) > tol for k in kept):
            kept.append(idx)
    return kept


def calibrate_tol(candidates, feats, n_per_leaf, tol_default):
    """Calibrate a fingerprint tolerance that yields ~n_per_leaf distinct structures.

    Raw fingerprint distances here are compressed (measured on Pt-P low-force
    survivors: NN median ~0.26, max ~0.74), so a fixed tol=1.0 collapses a leaf to one
    distinct structure. Start at tol_default; if greedy keeps fewer than n_per_leaf,
    scale the tol down (toward the lower NN-distance tail) until we retain >= n_per_leaf
    distinct OR the tol hits the minimum pairwise NN distance. Records the used tol.
    """
    from scipy.spatial.distance import pdist
    if len(feats) < 2:
        return tol_default, list(range(len(feats)))
    D = pdist(feats)
    dmin = float(D.min()) if D.size else 0.0
    d_p50 = float(np.percentile(D, 50))
    tol = tol_default
    kept = greedy_distinct(feats, tol)
    # tighten until we have enough distinct
    for _ in range(40):
        if len(kept) >= n_per_leaf or tol <= dmin * 1.0001:
            break
        tol = max(dmin * 1.05, tol * 0.75)
        kept = greedy_distinct(feats, tol)
    return tol, kept


def select_leaf(leaf_dir, it_min, e_max, force_pct, n_per_leaf, tol, force_thr_explicit):
    out, comp = load_leaf(leaf_dir, it_min, e_max)
    if not out:
        return [], comp, 0, {}
    # composition single => already enforced
    # --- force gate (percentile + leaf-adaptive absolute cutoff, with fallback) ---
    maxfs = np.array([o["max_f"] for o in out])
    thr = leaf_force_thr(leaf_dir, force_thr_explicit)
    pct_cut = np.percentile(maxfs, 100 - force_pct)  # lowest force_pct% keep
    candidates = [o for o in out if o["max_f"] <= pct_cut and o["max_f"] < thr]
    used_thr = thr
    # fallback (M5): relax threshold stepwise until >=1 survivor
    step = 0
    while not candidates and step < 6:
        used_thr += 0.5
        candidates = [o for o in out if o["max_f"] <= pct_cut and o["max_f"] < used_thr]
        step += 1
    if not candidates:
        # absolute last resort: lowest max|F| structure
        m = min(out, key=lambda o: o["max_f"])
        candidates = [m]

    # --- novelty dedup (per-leaf pool, raw Euclidean, calibrated tol) ---
    candidates.sort(key=lambda o: o["rel_energy"])  # greedy walks lowest energy first
    feats = fingerprint_features(candidates, leaf_dir)
    tol_used, kept_idx = calibrate_tol(candidates, feats, n_per_leaf, tol)
    kept = [candidates[i] for i in kept_idx]
    # --- pick top n by rel energy (lowest energy among distinct, low-force) ---
    chosen = kept[:n_per_leaf]
    chosen = [c for c in chosen if c["rel_energy"] <= e_max] or chosen[:1]
    return chosen, comp, len(out), {
        "leaf_thr_start": thr,
        "leaf_thr_used": used_thr,
        "tol_default": tol,
        "tol_used": tol_used,
        "force_gate_survivors": len(candidates),
        "distinct_after_dedup": len(kept),
    }


def write_leaf(outputs, leaf_dir, leaf_key, chosen, comp, gate, n_total):
    sel_dir = Path(outputs) / "selected" / leaf_key
    sel_dir.mkdir(parents=True, exist_ok=True)
    from ase.io import write as ase_write
    rows = []
    for rank, o in enumerate(chosen, start=1):
        xsf = sel_dir / f"{rank}.xsf"
        ase_write(str(xsf), o["atoms"])
        rows.append({
            "leaf": leaf_key,
            "rank": rank,
            "formula": o["atoms"].get_chemical_formula(),
            "energy_eV": o["energy"],
            "rel_energy_ev_per_atom": o["rel_energy"],
            "max_force_eV_per_A": o["max_f"],
            "mean_force_eV_per_A": o["mean_f"],
            "P_max_force_eV_per_A": o["p_max_f"],
            "iteration": o["iteration"],
            "source_db": o["source_db"],
            "xsf": f"selected/{leaf_key}/{rank}.xsf",
        })
    payload = {
        "leaf": leaf_key,
        "leaf_dir": leaf_dir,
        "composition": comp,
        "n_chosen": len(rows),
        "n_total_in_leaf": n_total,
        "gate": gate,
        "description": {
            "kind": "Run A stage-1 selection: novelty + force filter over an amorphous "
                     "Pt-P leaf (read-only from data/17_PPt).",
            "method": "force gate (per-leaf percentile + leaf-adaptive max|F| cutoff) "
                      "then AGOX Fingerprint greedy decup (raw Euclidean, per-leaf pool) "
                      "then top-n lowest relative energy.",
            "units": "energy eV / rel eV per atom; forces eV/A.",
            "fields": {
                "energy_eV": "total DFT energy of the (surrogate-relaxed) db structure",
                "rel_energy_ev_per_atom": "(E - leaf global min)/n_atoms",
                "max_force_eV_per_A": "max atom |F| (heavy-tailed; see mean)",
                "P_max_force_eV_per_A": "max |F| over P sublattice only",
            },
        },
        "selected": rows,
    }
    json_path = Path(outputs) / f"selection_{leaf_key}.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--leaves", nargs="*", required=True,
                    help="leaf dirs or 'leaf_key:dir' pairs")
    ap.add_argument("--data-root", default=None, dest="data_root",
                    help="root holding the leaf DBs (default: this dir's ./data)")
    ap.add_argument("--it-min", type=int, default=10, dest="it_min")
    ap.add_argument("--e-max", type=float, default=0.5, dest="e_max")
    ap.add_argument("--force-pct", type=float, default=25.0, dest="force_pct")
    ap.add_argument("--n-per-leaf", type=int, default=3, dest="n_per_leaf")
    ap.add_argument("--tol", type=float, default=1.0, help="fingerprint distance tol")
    ap.add_argument("--force-thr", type=float, default=None, dest="force_thr",
                    help="optional explicit per-leaf force cutoff (overrides 20P/30P)")
    args = ap.parse_args()

    # Standalone: default data root is THIS dir's ./data (all inputs in-dir).
    if args.data_root is None:
        args.data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    for spec in args.leaves:
        if ":" in spec:
            directory, key = spec.split(":", 1)
        else:
            directory = spec
            key = os.path.basename(os.path.normpath(directory))
        # Resolve leaf dir against the in-dir data root if it's a bare leaf key.
        if not os.path.isdir(directory):
            candidate = os.path.join(args.data_root, key)
            if os.path.isdir(candidate):
                directory = candidate
        chosen, comp, n_total, gate = select_leaf(
            directory, args.it_min, args.e_max, args.force_pct,
            args.n_per_leaf, args.tol, args.force_thr,
        )
        rows = write_leaf(args.outdir, directory, key, chosen, comp, gate, n_total)
        print(f"[{key}] comp={comp} chosen={len(rows)} gate={gate}")


if __name__ == "__main__":
    main()
