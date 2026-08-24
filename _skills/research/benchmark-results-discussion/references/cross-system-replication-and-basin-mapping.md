# Cross-system analysis replication + basin mapping (Fe/MgO work)

Session-derived recipes for AGOX DB analysis on this user's Fe/MgO research. Applies
when the user asks to "do the same <analysis> as <project> for seed <N>" (no new search)
or to "map the configurational space / basins" of one or more seed DBs.

## 1. "Same analysis, only the analysis" — the descriptor MUST match the system

When rerunning one project's *analysis* on another project's databases:

- Reuse the analysis FUNCTIONS verbatim — `get_distinct_configurations`,
  `compute_discovery_curve`, and the metrics (n_distinct, n_duplicates, best_E,
  e_range, duplicate rate) are portable across systems.
- The `Fingerprint` descriptor is NOT portable. It is built from an `Environment`
  that encodes the specific slab (symbols, cell, confinement). A Ni8/Au(4,4,2)
  descriptor is WRONG for Fe25Mg25O25/MgO (75 atoms). Build the TARGET project's own:
  ```
  slab_substrate, slab_deposition, strain = main.build_slabs()
  env = main.build_environment(slab_substrate.copy(), slab_deposition.copy())
  desc = Fingerprint(environment=env)
  ```
  and verify the feature shape (`(720,)` for Fe/MgO) before trusting any distance.
- Read the code's default `DUP_THRESHOLD` — there can be TWO defaults. The benchmark /
  analysis config sets `DUP_THRESHOLD = 1.5`; the `is_distinct()` helper in
  `novelty_lcb/acquisitor.py` defaults to `0.1`. When the user says "check the code's
  default and compare based on that", the analysis config (1.5) is what governs the
  distinct-count / discovery analysis, not the helper signature. State which you used.

## 2. Answering conceptual notes dropped into a DISCUSSION.md

The user pastes questions directly into the file ("what does duplicate rate mean?",
"what is DUP_THRESHOLD / NOVELTY_WEIGHT, how are they used in the code?"). Answer with a
dedicated in-place subsection grounded in the actual source files:

- `duplicate rate = n_duplicates / n_evals = (n_evals − n_distinct) / n_evals`
  → fraction of evaluations that re-visited a known basin instead of discovering a new
  one; a sample-efficiency / search-waste metric.
- `DUP_THRESHOLD`: post-hoc analysis cutoff in the greedy fingerprint clustering
  (lowest-energy-first; drop anything within Euclidean distance ≤ threshold). Does NOT
  affect the search itself.
- `NOVELTY_WEIGHT` (λ): search-time weight in `a(x) = σ(x) + λ·Novelty(x)` — steers which
  candidate the acquisitor picks. Separate from the energy-window mechanism.
- Key framing: search-time parameters (λ, kappa) vs post-hoc analysis parameters
  (DUP_THRESHOLD).

## 3. 2D PCA + clustering configurational/basin map

To map configurational space of one or more AGOX DBs into basins:

- Input: the 720-dim `Fingerprint` features of every stored structure.
- Pool both acquisitors' structures, fit ONE shared PCA (PC1/PC2) so both sit on the same
  subspace. **Non-whitened PCA** kept PC units in the raw feature-variance scale and gave
  better separation + interpretability here (whitened collapsed to a single blob). Report
  explained variance (Fe/MgO: PC1 67%, PC2 13%, cumulative 80%).
- **Calibrate clustering on the actual 2D coords — defaults give a useless single blob.**
  First pass with silhouette-best KMeans + a large DBSCAN eps collapsed everything into
  one cluster. Fix: scan DBSCAN eps across the PC coordinate range and inspect KMeans
  cluster *composition*. Pick a k that is slightly below silhouette-best but resolves the
  physically meaningful basins (k=4, sil 0.616 vs best-k=3, sil 0.622) — prefer basin
  resolution over a marginally higher silhouette.
- **DBSCAN is density-based on the 2D projection**: on Fe/MgO the low-energy region is one
  connected blob, so DBSCAN yields few basins + noise. State this honestly — KMeans finds
  a within-blob gradation DBSCAN cannot, and the greedy DUP_THRESHOLD count (48/75) is
  finer than any 2D reduction (PCA compresses 720-dim → 2 axes, 80% variance).
- Visualize: points colored by cluster, each basin annotated with its lowest-energy
  member + energy, acquisitor overlaid by marker (circle=Regular, star=Novelty) so you can
  read which search populated which basin.

### Recurring interpretation (Regular vs Novelty LCB on Fe/MgO)

- Regular LCB concentrates in the single deepest basin → better best_E (e.g. −435.3 eV).
- Novelty-LCB spreads across the low-energy basins → more distinct structures, ~half the
  duplicate rate (25% vs 52%), at the cost of a shallower single minimum (−432.0 eV).
- The diversity edge is LARGE on the rough Fe/MgO landscape (+56% distinct), unlike the
  smooth Ni8/Au EMT toy where novelty was marginal — a smooth few-basin surface gives the
  novelty term little to exploit.

## 4. Working patterns that were NOT the problem (environmental noise)

The AGOX `Environment` build prints a box-drawing "Environment report" to stdout on every
construction. When running analysis scripts, filter it out of captured logs (it is not an
error). The `agox_v2` conda env python is required (`base python3` has no ASE/AGOX).
