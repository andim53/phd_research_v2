#!/usr/bin/env python3
"""
Novelty analysis (replicating 73_novel_benchEMT) applied to the two Fe/MgO seed-3
databases of project 72 (Novelty-LCB auto-global-min, 1 eV/atom above global min):

    Regular LCB : dataset/seed_3/1_db/db_3.db
    Novelty-LCB : output/seed_3/1_db/db_3.db

Analysis logic copied from main_benchmark.py of 73_novel_benchEMT (the "analysis
only", no AGOX search):
  - get_distinct_configurations(db, descriptor, DUP_THRESHOLD) : greedy fingerprint
    clustering into distinct configurations (lowest-E first).
  - compute_discovery_curve(results, desc, DUP_THRESHOLD)      : cumulative distinct
    vs cumulative evaluations.
  - metrics: n_distinct, n_duplicates, best_E, e_range, n_evals.

Uses project 72's OWN Fe/MgO Fingerprint descriptor (main.build_environment +
Fingerprint) so distances are computed in the correct 75-atom Fe/MgO feature space.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python novelty_analysis.py
"""

import matplotlib
matplotlib.use("Agg")

import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
import main as M

# =============================================================================
# Configuration (same default DUP_THRESHOLD as the 73 benchmark)
# =============================================================================
DUP_THRESHOLD = 1.5   # fingerprint-distance threshold for "distinct configuration"

REGULAR_DB = os.path.join(_HERE, "dataset", "seed_3", "1_db", "db_3.db")
NOVELTY_DB = os.path.join(_HERE, "output", "seed_3", "1_db", "db_3.db")

OUTDIR = _HERE  # write results + plots into the project 72 dir


# =============================================================================
# Analysis functions (replicated from 73_novel_benchEMT/main_benchmark.py)
# =============================================================================

def get_distinct_configurations(db, descriptor, threshold=DUP_THRESHOLD):
    """Greedy cluster of DB candidates into distinct configurations (lowest-E first)."""
    structures = db.get_all_candidates()
    if not structures:
        return []
    features, energies, valid = [], [], []
    for s in structures:
        try:
            e = s.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = descriptor.get_features(s).ravel()
            features.append(f); energies.append(e); valid.append(s)
        except Exception:
            continue
    if not features:
        return []
    features = np.array(features); energies = np.array(energies)
    selected, remaining = [], list(np.argsort(energies))
    while remaining:
        idx = remaining.pop(0)
        selected.append(idx)
        remaining = [j for j in remaining
                     if np.linalg.norm(features[j] - features[idx]) > threshold]
    return [(valid[i], energies[i]) for i in selected]


def compute_discovery_curve(all_c, desc, threshold=DUP_THRESHOLD):
    """Cumulative distinct configs vs cumulative evaluations for a single DB."""
    cum_distinct, cum_total, seen_features = [], [], []
    for i, c in enumerate(all_c):
        try:
            e = c.get_potential_energy()
            if not np.isfinite(e):
                cum_distinct.append(cum_distinct[-1] if cum_distinct else 0)
                cum_total.append(i + 1)
                continue
            f = desc.get_features(c).ravel()
            is_new = True
            for sf in seen_features:
                if np.linalg.norm(f - sf) <= threshold:
                    is_new = False
                    break
            if is_new:
                seen_features.append(f)
            cum_distinct.append(len(seen_features))
            cum_total.append(i + 1)
        except Exception:
            cum_distinct.append(cum_distinct[-1] if cum_distinct else 0)
            cum_total.append(i + 1)
    return np.array(cum_total), np.array(cum_distinct)


def analyze_db(db_path, label, desc):
    db = Database(filename=db_path, initialize=False)
    db.restore_to_memory()
    all_c = db.get_all_candidates()

    distinct = get_distinct_configurations(db, desc, DUP_THRESHOLD)
    distinct_energies = [e for _, e in distinct]
    n_distinct = len(distinct)
    n_evals = len(all_c)
    n_duplicates = n_evals - n_distinct

    if distinct_energies:
        best_E = min(distinct_energies)
        e_range = max(distinct_energies) - min(distinct_energies)
    else:
        best_E = e_range = np.nan

    all_energies = []
    for c in all_c:
        try:
            e = c.get_potential_energy()
            if np.isfinite(e):
                all_energies.append(e)
        except Exception:
            pass

    print(f"[{label}] distinct={n_distinct}, evals={n_evals}, "
          f"duplicates={n_duplicates} ({n_duplicates / n_evals * 100:.1f}%), "
          f"best_E={best_E:.3f} eV, e_range={e_range:.3f} eV")

    return dict(label=label, db_file=db_path, n_evals=n_evals,
                n_distinct=n_distinct, n_duplicates=n_duplicates,
                best_E=best_E, e_range=e_range,
                distinct_energies=[float(e) for e in distinct_energies],
                all_energies=[float(e) for e in all_energies])


def main():
    # Build the Fe/MgO descriptor (project 72's own environment)
    slab_substrate, slab_deposition, strain = M.build_slabs()
    env = M.build_environment(slab_substrate.copy(), slab_deposition.copy())
    desc = Fingerprint(environment=env)
    print(f"Fe/MgO Fingerprint descriptor ready (strain={strain:.2f}%), "
          f"feature dim from test.")

    results = {}
    results["regular_lcb"] = analyze_db(REGULAR_DB, "regular_lcb_seed3", desc)
    results["novelty_lcb"] = analyze_db(NOVELTY_DB, "novelty_lcb_seed3", desc)

    # ---- Save JSON ----
    out_data = {
        "parameters": {
            "SYSTEM": "Fe25Mg25O25 on MgO(001) (75 atoms)",
            "SEED": 3,
            "DUP_THRESHOLD": DUP_THRESHOLD,
            "REGULAR_DB": REGULAR_DB,
            "NOVELTY_DB": NOVELTY_DB,
            "NOTE": ("Novelty analysis replicating 73_novel_benchEMT (distinct-config "
                     "greedy clustering + discovery curve, DUP_THRESHOLD=1.5) applied "
                     "to project 72 seed-3 DBs. Regular = dataset/seed_3; Novelty = "
                     "output/seed_3. Uses the Fe/MgO Fingerprint descriptor."),
        },
        "results": results,
    }
    json_path = os.path.join(OUTDIR, "novelty_analysis_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # ---- Plots ----
    # Load candidate order for discovery curves
    db_reg = Database(filename=REGULAR_DB, initialize=False); db_reg.restore_to_memory()
    db_nov = Database(filename=NOVELTY_DB, initialize=False); db_nov.restore_to_memory()

    # Plot 1: comparison of metrics (distinct, duplicates, best E) - 1x3
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    labels = ["Regular LCB", "Novelty-LCB"]
    r = results["regular_lcb"]; n = results["novelty_lcb"]
    for ax, key, title, ylab in [
        (axes[0], "n_distinct", "Distinct configurations", "n_distinct"),
        (axes[1], "n_duplicates", "Duplicate evaluations", "n_duplicates"),
        (axes[2], "best_E", "Best energy [eV]", "best_E [eV]"),
    ]:
        vals = [r[key], n[key]]
        ax.bar(labels, vals, color=["steelblue", "coral"])
        ax.set_title(title); ax.set_ylabel(ylab)
        for i, v in enumerate(vals):
            ax.text(i, v + (0.01 * abs(v) if v >= 0 else -0.02 * abs(v)),
                    f"{v:.3f}" if isinstance(v, float) else f"{v}",
                    ha="center", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    comp_path = os.path.join(OUTDIR, "novelty_analysis_comparison.png")
    plt.savefig(comp_path, dpi=150, bbox_inches="tight")
    print(f"Comparison plot: {comp_path}")
    plt.close()

    # Plot 2: discovery curves (cumulative distinct vs cumulative evals)
    fig, ax = plt.subplots(figsize=(9, 6))
    for db, color, lbl in [(db_reg, "steelblue", "Regular LCB"),
                           (db_nov, "coral", "Novelty-LCB")]:
        all_c = db.get_all_candidates()
        x, y = compute_discovery_curve(all_c, desc, DUP_THRESHOLD)
        if len(x):
            ax.plot(x, y, "o-", color=color, linewidth=2, markersize=4, label=lbl)
    ax.set_xlabel("Cumulative evaluations")
    ax.set_ylabel("Cumulative distinct configurations")
    ax.set_title("Discovery Curves (seed 3)")
    ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout()
    disc_path = os.path.join(OUTDIR, "novelty_analysis_discovery.png")
    plt.savefig(disc_path, dpi=150, bbox_inches="tight")
    print(f"Discovery plot: {disc_path}")
    plt.close()

    print("\nDONE")


if __name__ == "__main__":
    main()
