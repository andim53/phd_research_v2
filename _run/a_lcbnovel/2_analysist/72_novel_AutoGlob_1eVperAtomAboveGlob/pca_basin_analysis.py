#!/usr/bin/env python3
"""
Configurational-space (basin) analysis of the two Fe/MgO seed-3 databases of
project 72, comparing Regular LCB vs Novelty-LCB.

    Regular LCB : dataset/seed_3/1_db/db_3.db
    Novelty-LCB : output/seed_3/1_db/db_3.db

Approach (as clarified with the owner):
  1. Build the project-72 Fe/MgO Fingerprint descriptor (720-dim).
  2. Compute the 720-dim features of every structure in BOTH databases.
  3. Project all 200 structures (100 regular + 100 novelty) together onto a SHARED
     2D PCA subspace (PC1 x PC2) of the fingerprint features.
  4. Cluster the combined set into basins with BOTH KMeans (k chosen by silhouette)
     and DBSCAN (density-based), for comparison.
  5. Visualize each basin map: points colored by cluster (basin), the lowest-energy
     member of each basin annotated with its energy, and the acquisitor overlaid as
     symbol (circle = Regular, star = Novelty) so one can see which basins each
     search covered.

Run:
    /home/think/miniconda3/envs/agox_v2/bin/python pca_basin_analysis.py
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
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import main as M

# =============================================================================
# Configuration
# =============================================================================
REGULAR_DB = os.path.join(_HERE, "dataset", "seed_3", "1_db", "db_3.db")
NOVELTY_DB = os.path.join(_HERE, "output", "seed_3", "1_db", "db_3.db")

OUTDIR = _HERE
PCA_N_COMPONENTS = 2
# PCA on raw fingerprint features, not whitened: PC units retain the actual
# feature-space variance scale, which keeps the PCA axes physically interpretable.
PCA_WHITEN = False
# KMeans k chosen for basin resolution: k=4 separates the low-energy space into a
# Regular-dominated deepest basin (C0), a Novelty-dominated low basin (C3), a
# balanced mid basin (C1) and a balanced high basin (C2). (Silhouette is maximal at
# k=2-3, but k=4 is only slightly lower and far more physically informative.)
KMEANS_K = 4
# DBSCAN calibrated on the non-whitened 2D PCA coordinates (PC1 std~4.4, PC2 std~2.0).
DBSCAN_EPS = 0.9
DBSCAN_MIN_SAMPLES = 4


# =============================================================================
# Data loading
# =============================================================================

def load_features(db_path, desc):
    """Return (features, energies, structures) for a database, finite-energy only."""
    db = Database(filename=db_path, initialize=False)
    db.restore_to_memory()
    feats, energies, structs = [], [], []
    for c in db.get_all_candidates():
        try:
            e = c.get_potential_energy()
            if not np.isfinite(e):
                continue
            f = desc.get_features(c).ravel()
            feats.append(f); energies.append(e); structs.append(c)
        except Exception:
            continue
    return np.array(feats), np.array(energies), structs


def choose_kmeans_k(X2d, k_range=range(2, 10)):
    """Report silhouette score per k (for diagnostics); returns best k by silhouette."""
    best_k, best_s = None, -1.0
    scores = {}
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=0, n_init=10).fit(X2d)
        s = silhouette_score(X2d, km.labels_)
        scores[k] = s
        if s > best_s:
            best_s, best_k = s, k
    return best_k, best_s, scores


# =============================================================================
# Main
# =============================================================================

def main():
    # --- Build the Fe/MgO descriptor ---
    slab_substrate, slab_deposition, strain = M.build_slabs()
    env = M.build_environment(slab_substrate.copy(), slab_deposition.copy())
    desc = Fingerprint(environment=env)
    print(f"Fe/MgO Fingerprint descriptor ready (strain={strain:.2f}%).")

    # --- Load features for both DBs ---
    feats_reg, E_reg, structs_reg = load_features(REGULAR_DB, desc)
    feats_nov, E_nov, structs_nov = load_features(NOVELTY_DB, desc)
    print(f"Regular : {len(feats_reg)} structures")
    print(f"Novelty : {len(feats_nov)} structures")

    # --- Shared 2D PCA on the combined feature set ---
    all_feats = np.vstack([feats_reg, feats_nov])
    n_reg = len(feats_reg)
    pca = PCA(n_components=PCA_N_COMPONENTS, whiten=PCA_WHITEN, random_state=0)
    X2d = pca.fit_transform(all_feats)
    # index -> acquisitor: 0 = Regular (first n_reg), 1 = Novelty (rest)
    acq = np.array([0] * n_reg + [1] * (len(all_feats) - n_reg))
    E_all = np.concatenate([E_reg, E_nov])
    print(f"PCA explained variance (PC1, PC2): "
          f"{pca.explained_variance_ratio_[0]:.3f}, {pca.explained_variance_ratio_[1]:.3f} "
          f"(cumulative {pca.explained_variance_ratio_.sum():.3f})")

    # --- KMeans clustering (fixed k chosen for basin resolution) ---
    best_k, best_s, k_scores = choose_kmeans_k(X2d)
    print(f"KMeans silhouette best k={best_k} (s={best_s:.3f}); using k={KMEANS_K}")
    km = KMeans(n_clusters=KMEANS_K, random_state=0, n_init=10).fit(X2d)
    km_labels = km.labels_
    km_sil = silhouette_score(X2d, km_labels)
    print(f"KMeans: k={KMEANS_K} (silhouette={km_sil:.3f})")

    # --- DBSCAN clustering ---
    dbscan = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(X2d)
    db_labels = dbscan.labels_
    n_db_clusters = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    n_db_noise = int((db_labels == -1).sum())
    print(f"DBSCAN: eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES} -> "
          f"{n_db_clusters} clusters, {n_db_noise} noise points")

    # --- Basin summaries: lowest-energy member per cluster (for both clusterings) ---
    def basin_summary(labels):
        out = {}
        for lab in sorted(set(labels)):
            if lab == -1:  # DBSCAN noise
                continue
            idx = np.where(labels == lab)[0]
            e_cluster = E_all[idx]
            jmin = idx[np.argmin(e_cluster)]
            out[lab] = dict(n=len(idx), best_E=float(e_cluster.min()),
                            n_reg=int((acq[idx] == 0).sum()),
                            n_nov=int((acq[idx] == 1).sum()))
        return out

    km_summary = basin_summary(km_labels)
    db_summary = basin_summary(db_labels)

    print("\nKMeans basin summary (cluster: size, best_E, [reg, nov]):")
    for lab in sorted(km_summary):
        s = km_summary[lab]
        print(f"  C{lab}: n={s['n']}, best_E={s['best_E']:.3f}, reg={s['n_reg']}, nov={s['n_nov']}")
    print("\nDBSCAN basin summary (cluster: size, best_E, [reg, nov]):")
    for lab in sorted(db_summary):
        s = db_summary[lab]
        print(f"  C{lab}: n={s['n']}, best_E={s['best_E']:.3f}, reg={s['n_reg']}, nov={s['n_nov']}")

    # --- Save JSON ---
    out_data = {
        "parameters": {
            "SYSTEM": "Fe25Mg25O25 on MgO(001) (75 atoms)", "SEED": 3,
            "PCA_INPUT": "720-dim Fingerprint features",
            "PCA_N_COMPONENTS": PCA_N_COMPONENTS, "WHITEN": PCA_WHITEN,
            "explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
            "KMEANS_K": KMEANS_K, "KMEANS_SILHOUETTE": float(km_sil),
            "KMEANS_SILHOUETTE_BEST": int(best_k),
            "DBSCAN_EPS": DBSCAN_EPS, "DBSCAN_MIN_SAMPLES": DBSCAN_MIN_SAMPLES,
            "REGULAR_DB": REGULAR_DB, "NOVELTY_DB": NOVELTY_DB,
        },
        "kmeans_basins": {str(k): v for k, v in km_summary.items()},
        "dbscan_basins": {str(k): v for k, v in db_summary.items()},
        "pc_coords": {"pc1": [float(x) for x in X2d[:, 0]],
                      "pc2": [float(x) for x in X2d[:, 1]],
                      "acq": [int(a) for a in acq],
                      "energy": [float(e) for e in E_all],
                      "kmeans_label": [int(x) for x in km_labels],
                      "dbscan_label": [int(x) for x in db_labels]},
    }
    json_path = os.path.join(OUTDIR, "pca_basin_analysis_results.json")
    with open(json_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # --- Plot helper: one basin map ---
    def plot_basin_map(ax, labels, title, summary):
        acq_marker = {0: ("o", "Regular LCB"), 1: ("*", "Novelty-LCB")}
        acq_color = {0: "steelblue", 1: "coral"}
        # Draw cluster hulls / regions lightly
        cluster_colors = plt.cm.tab20(np.linspace(0, 1, len(summary)))
        # scatter per acquisitor, colored by cluster
        for a, (mk, aname) in acq_marker.items():
            sel = acq == a
            # color each point by cluster
            ax.scatter(X2d[sel, 0], X2d[sel, 1], c=labels[sel], cmap="tab20",
                       marker=mk, s=45, edgecolor="k", linewidth=0.4,
                       label=aname, zorder=3)
        # annotate each basin with its lowest-energy member
        for lab, s in summary.items():
            idx = np.where(labels == lab)[0]
            jmin = idx[np.argmin(E_all[idx])]
            ax.annotate(f"{lab}\n{s['best_E']:.1f} eV",
                        (X2d[jmin, 0], X2d[jmin, 1]),
                        fontsize=8, ha="center", va="bottom", zorder=5,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7),
                        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5))
        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
        ax.set_title(title)
        ax.grid(alpha=0.2)
        ax.legend(loc="best", fontsize=8)

    # --- Figure: 2 basin maps side by side (KMeans, DBSCAN) ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    plot_basin_map(axes[0], km_labels, f"KMeans basin map (k={KMEANS_K}, "
                                        f"silhouette={km_sil:.2f})", km_summary)
    plot_basin_map(axes[1], db_labels,
                   f"DBSCAN basin map (eps={DBSCAN_EPS}, min_samples="
                   f"{DBSCAN_MIN_SAMPLES}; noise={n_db_noise})", db_summary)
    plt.tight_layout()
    map_path = os.path.join(OUTDIR, "pca_basin_map.png")
    plt.savefig(map_path, dpi=150, bbox_inches="tight")
    print(f"Basin map: {map_path}")
    plt.close()

    # --- Figure: PCA explained variance + silhouette-vs-k ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    # explained variance
    pca_full = PCA().fit(all_feats)
    ev = pca_full.explained_variance_ratio_
    axes[0].bar(range(1, len(ev) + 1), ev, alpha=0.7, label="per-component")
    axes[0].plot(range(1, len(ev) + 1), np.cumsum(ev), "o-", color="coral",
                 label="cumulative")
    axes[0].set_xlabel("PC index"); axes[0].set_ylabel("Explained variance ratio")
    axes[0].set_title("PCA explained variance (first 20 PCs)")
    axes[0].set_xlim(0, 20); axes[0].legend(); axes[0].grid(alpha=0.3)
    # silhouette vs k
    ks = sorted(k_scores); svals = [k_scores[k] for k in ks]
    axes[1].plot(ks, svals, "o-", color="steelblue")
    axes[1].axvline(best_k, color="coral", linestyle="--", label=f"best k={best_k}")
    axes[1].set_xlabel("k"); axes[1].set_ylabel("Silhouette score")
    axes[1].set_title("KMeans silhouette vs k")
    axes[1].legend(); axes[1].grid(alpha=0.3)
    plt.tight_layout()
    aux_path = os.path.join(OUTDIR, "pca_basin_aux.png")
    plt.savefig(aux_path, dpi=150, bbox_inches="tight")
    print(f"Aux plot: {aux_path}")
    plt.close()

    print("\nDONE")


if __name__ == "__main__":
    main()
