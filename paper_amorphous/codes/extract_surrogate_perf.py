#!/usr/bin/env python3
"""extract_surrogate_perf.py — M-1e surrogate predictive performance.

Extracts the GPR surrogate's out-of-sample predictive performance from every
Pt(P) AGOX seed DB under data/17_PPt. For each retained structure
(iteration >= 10) it pairs the DFT energy (ground truth) with the surrogate's
prediction (model_energy) and its uncertainty (GPR sigma), both stored in the
DB at selection time (before the candidate is DFT-scored), so model_energy is a
genuine out-of-sample prediction.

Metrics, binned by per-leaf relative energy (eV/atom, relative to the leaf's
global minimum) across the 0 -> 1 eV/atom range:
  - MAE, RMSE (eV/atom) between model_energy and DFT energy
  - R^2 (variance explained) per window
  - Spearman rho (rank correlation) per window  -- the surrogate is used for
    selection, so rank accuracy matters more than absolute error
  - uncertainty calibration: mean |error| vs mean sigma per window (does the GPR
    uncertainty track the error? validates the LCB acquisition, kappa=2)

Writes analysis/surrogate_perf/surrogate_perf.json (per-leaf + per-window rows)
and prints a compact table. Grounds the M-1e claim.

Usage (agox_v2):
  /home/think/miniconda3/envs/agox_v2/bin/python codes/extract_surrogate_perf.py
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import glob
import json
import os
import sqlite3
import statistics

import numpy as np
from agox.databases import Database

START_ITER = 10
E_MAX = 1.0  # eV/atom, per-leaf relative-energy cap (the 0 -> 1 eV/atom range)
WINDOW = 0.1  # eV/atom window width

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "analysis", "surrogate_perf")

# leaf dataset dir (relative to data/17_PPt/) -> (cell, P)
LEAVES = {
    "1_plus0cell/0_0P": ("+0", "0P"), "1_plus0cell/2_20P": ("+0", "20P"),
    "1_plus0cell/3_30P": ("+0", "30P"),
    "2_plus3cell/0_0P": ("+3", "0P"), "2_plus3cell/2_20P": ("+3", "20P"),
    "2_plus3cell/3_30P": ("+3", "30P"),
    "0_plus5cell/3_3x3_0P": ("+5", "0P"), "0_plus5cell/1_3x3_20P": ("+5", "20P"),
    "0_plus5cell/2_3x3_30P": ("+5", "30P"),
}


def spearman(xs, ys):
    """Spearman rank correlation (ties averaged)."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / (vx * vy) ** 0.5


def load_leaf(dataset_dir: str, start_iter: int):
    """Return list of dicts (seed, iteration, energy, model, sigma, natoms)."""
    db_paths = sorted(glob.glob(os.path.join(dataset_dir, "seed_*/1_db/db_*.db")))
    rows = []
    for p in db_paths:
        seed = os.path.basename(os.path.dirname(os.path.dirname(p)))
        db = Database(filename=p)
        db.restore_to_memory()
        cands = db.get_all_candidates()
        data = db.get_all_structures_data()
        con = sqlite3.connect(p)
        cur = con.cursor()
        for c, m in zip(cands, data):
            if m.get("iteration", 0) < start_iter:
                continue
            sid = m.get("id")
            model = cur.execute(
                "SELECT value FROM float_key_values WHERE id=? AND key='model_energy'",
                (sid,)).fetchone()
            sigma = cur.execute(
                "SELECT value FROM float_key_values WHERE id=? AND key='uncertainty'",
                (sid,)).fetchone()
            if model is None or sigma is None:
                continue
            rows.append({
                "seed": seed,
                "iteration": m.get("iteration", 0),
                "energy": c.get_potential_energy(),
                "model": model[0],
                "sigma": sigma[0],
                "natoms": len(c),
            })
        con.close()
    return rows


def window_stats(rows, emin, nat):
    """Bin rows by per-atom relative energy; return per-window metric dicts."""
    windows = {}
    for r in rows:
        dE = (r["energy"] - emin) / nat
        if dE < 0 or dE >= E_MAX:
            continue
        w = int(dE // WINDOW)
        windows.setdefault(w, []).append(r)
    out = []
    for w in sorted(windows):
        rs = windows[w]
        errs = [(r["model"] - r["energy"]) / nat for r in rs]
        preds = [(r["model"] - emin) / nat for r in rs]
        trues = [(r["energy"] - emin) / nat for r in rs]
        sigmas = [r["sigma"] / nat for r in rs]
        mae = statistics.mean(abs(e) for e in errs)
        rmse = (sum(e * e for e in errs) / len(errs)) ** 0.5
        mt, mp = statistics.mean(trues), statistics.mean(preds)
        ss_res = sum((t - p) ** 2 for t, p in zip(trues, preds))
        ss_tot = sum((t - mt) ** 2 for t in trues)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
        rho = spearman(trues, preds)
        out.append({
            "window_lo_eV_per_atom": round(w * WINDOW, 2),
            "window_hi_eV_per_atom": round((w + 1) * WINDOW, 2),
            "n": len(rs),
            "mae_eV_per_atom": round(mae, 5),
            "rmse_eV_per_atom": round(rmse, 5),
            "r2": round(r2, 4) if r2 is not None else None,
            "spearman_rho": round(rho, 4) if rho is not None else None,
            "mean_sigma_eV_per_atom": round(statistics.mean(sigmas), 5),
            "mean_abs_err_eV_per_atom": round(mae, 5),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="data/17_PPt")
    ap.add_argument("--out", default="analysis/surrogate_perf/surrogate_perf.json")
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    leaves = []
    for leaf, (cell, p) in LEAVES.items():
        ds = os.path.join(ROOT, args.data_root, leaf)
        rows = load_leaf(ds, START_ITER)
        if not rows:
            print(f"[{leaf}] no structures with model_energy")
            continue
        nat = rows[0]["natoms"]
        emin = min(r["energy"] for r in rows)
        wins = window_stats(rows, emin, nat)
        # overall (0 -> 1 eV/atom pooled)
        all_errs = [(r["model"] - r["energy"]) / nat for r in rows
                    if 0 <= (r["energy"] - emin) / nat < E_MAX]
        all_preds = [(r["model"] - emin) / nat for r in rows
                     if 0 <= (r["energy"] - emin) / nat < E_MAX]
        all_trues = [(r["energy"] - emin) / nat for r in rows
                     if 0 <= (r["energy"] - emin) / nat < E_MAX]
        overall = {
            "n": len(all_errs),
            "mae_eV_per_atom": round(statistics.mean(abs(e) for e in all_errs), 5),
            "rmse_eV_per_atom": round((sum(e * e for e in all_errs) / len(all_errs)) ** 0.5, 5),
            "r2": round(1.0 - sum((t - p) ** 2 for t, p in zip(all_trues, all_preds))
                        / sum((t - statistics.mean(all_trues)) ** 2 for t in all_trues), 4),
            "spearman_rho": round(spearman(all_trues, all_preds), 4),
        }
        rec = {
            "leaf": leaf, "cell": cell, "P_loading": p, "natoms": nat,
            "n_retained": len(rows),
            "global_min_eV": float(emin),
            "overall_0_1_eV_per_atom": overall,
            "windows": wins,
        }
        leaves.append(rec)
        print(f"[{cell} {p}] {leaf}: retained {len(rows)}, "
              f"overall MAE={overall['mae_eV_per_atom']:.4f} eV/atom, "
              f"R2={overall['r2']:.3f}, rho={overall['spearman_rho']:.3f}")

    payload = {
        "description": {
            "name": "GPR surrogate predictive performance (M-1e)",
            "version": __version__,
            "produced_by": "codes/extract_surrogate_perf.py",
            "purpose": "citable per-window surrogate predictive-performance data "
                       "(MAE/RMSE/R2/Spearman/uncertainty-calibration) the "
                       "surrogate-performance figure imports",
            "filters": {
                "iteration_min": START_ITER,
                "e_max_eV_per_atom": E_MAX,
                "window_eV_per_atom": WINDOW,
                "reference": "per-leaf global energy minimum",
                "units": {"energy": "eV/atom relative to leaf E_min",
                          "error": "model_energy - DFT energy, eV/atom"},
            },
            "caveats": [
                "model_energy/uncertainty are stored at selection time (before "
                "the candidate is DFT-scored) -> out-of-sample predictions",
                "DFT ground truth for P leaves is on under-relaxed geometries "
                "(single-DFT-step evaluator); measured error includes that noise",
                "early surrogate-building iterations (< 10) excluded"],
        },
        "leaves": leaves,
    }
    with open(os.path.join(ROOT, args.out), "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\n-> {os.path.join(ROOT, args.out)}")


if __name__ == "__main__":
    main()
