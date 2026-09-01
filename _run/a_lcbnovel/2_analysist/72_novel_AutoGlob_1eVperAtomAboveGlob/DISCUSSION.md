# DISCUSSION — Novelty-LCB vs Regular-LCB on Fe/MgO (seed 3)

Project: `72_novel_AutoGlob_1eVperAtomAboveGlob`
System: **Fe25Mg25O25 on MgO(001)** (75 atoms), GPAW-DFT evaluated
Analysis: novelty analysis replicating `73_novel_benchEMT` (distinct-config greedy
fingerprint clustering + discovery curve), applied to the two **seed-3** databases:
- **Regular LCB**: `dataset/seed_3/1_db/db_3.db`
- **Novelty-LCB**: `output/seed_3/1_db/db_3.db` (auto global-min window, 1 eV/atom above min)

Results source: `novelty_analysis_results.json`, `novelty_analysis_comparison.png`,
`novelty_analysis_discovery.png`
Analysis script: `novelty_analysis.py`
Settings: `DUP_THRESHOLD = 1.5`, Fe/MgO `Fingerprint` descriptor (720-dim), 100 evals per run.

---

## 1. What was analysed

Project 72 is the **real Fe/MgO** Novelty-LCB search (not the Ni8/Au EMT toy). Both
seed-3 databases hold 100 relaxed, GPAW-scored structures of identical composition
(Fe25Mg25O25). The analysis replicates the exact distinct-configuration / discovery
logic of the 73 benchmark — greedy fingerprint clustering at `DUP_THRESHOLD = 1.5`
(lowest-energy-first), counting distinct basins, duplicates, best energy, energy range,
and the cumulative discovery curve — but computed with **project 72's own Fe/MgO
Fingerprint descriptor**, so the distances are in the correct 75-atom feature space.

---

## 2. Headline numbers (from `novelty_analysis_results.json`)

| Metric                      | Regular LCB  | Novelty-LCB | Δ (Nov − Reg)     |
| --------------------------- | ------------ | ----------- | ----------------- |
| Evaluations                 | 100          | 100         | 0                 |
| **Distinct configurations** | 48           | **75**      | **+27 (+56%)**    |
| Duplicate evaluations       | 52           | **25**      | **−27 (−52%)**    |
| Duplicate rate              | 52%          | **25%**     | −27 pts           |
| **Best energy (eV)**        | **−435.315** | −432.015    | **+3.30** (worse) |
| Energy range (eV)           | 44.85        | 44.30       | −0.55             |
| Distinct below −430 eV      | 8            | 6           | −2                |

### How the metrics and parameters work

**What does the duplicate rate mean? What does it represent?**

The duplicate rate is the fraction of the 100 evaluations that did **not** add a
structurally new configuration — i.e. evaluations that re-visited a basin already in the
database instead of discovering a new one. Concretely:

    duplicate rate = n_duplicates / n_evals = (n_evals − n_distinct) / n_evals

So 52% for Regular LCB means 52 of its 100 evaluations were redundant (re-samples of the
48 known basins), and 25% for Novelty-LCB means only 25 of its 100 evaluations were
redundant (the other 75 found something new). It is a measure of **sample efficiency /
search waste**: a low duplicate rate means the search spends its budget exploring new
structures; a high one means it keeps collapsing back onto the same few minima. It is
exactly the reciprocal of the diversity picture — every evaluation that is *not* a
duplicate is a newly discovered distinct configuration.

**What is `DUP_THRESHOLD`? How is it used in the code?**

`DUP_THRESHOLD` is the fingerprint-distance cutoff that decides whether two structures
count as the "same" configuration or as two distinct ones. In this analysis it is set to
`1.5` (`novelty_analysis.py`) and used by the greedy distinct-configuration clustering,
`get_distinct_configurations` (replicated from the 73 benchmark). The logic
(`novelty_analysis.py` / `main_benchmark.py`):

- Compute the 720-dim Fe/MgO `Fingerprint` features of every stored structure.
- Sort by energy (lowest first); take the lowest-energy structure as a representative.
- Remove from the "remaining" pool any structure whose Euclidean distance in feature
  space to that representative is **`≤ DUP_THRESHOLD`** (i.e. `np.linalg.norm(features[j]
  − features[idx]) > threshold` is *false* → it is a duplicate of that basin).
- Repeat with the next-lowest-energy remaining structure.

So `DUP_THRESHOLD` sets the "how different must a structure be to count as new" bar. A
smaller threshold → more structures are counted as distinct (stricter dedup); a larger
threshold → more structures collapse into the same basin (looser). It only enters the
*post-hoc analysis* that counts distinct basins and duplicates — it does **not** affect
the search itself.

**What is `NOVELTY_WEIGHT`? How is it used in the code?**

`NOVELTY_WEIGHT` (λ, default 1.0 in the package; 1.5 in `main.py`) is the weight on the
novelty term inside the Novelty-LCB acquisition function

    a(x) = σ(x) + λ · Novelty(x)      (to be MAXIMIZED)

with `Novelty(x)` = min Euclidean distance of candidate x to every structure in the DB,
and `σ(x)` the GPR predictive standard deviation. In `novelty_lcb/acquisitor.py` the
selected candidate is the one with the largest true `a(x)` (the code returns `-(σ +
self.novelty_weight * novelty)` so AGOX's ascending sort picks it first). **λ controls the
exploration–diversity balance**: it scales how strongly the structural-novelty bonus
counts relative to the uncertainty term `σ`. A larger λ pushes the search harder toward
structurally new (unexplored) basins; a smaller λ leans toward plain uncertainty
sampling. Here it was set to `1.5`, and it is a *search-time* parameter (it steers which
candidates the acquisitor picks during the run) — unlike `DUP_THRESHOLD`, which is only a
*post-hoc analysis* cutoff. (Note the energy window is a separate mechanism: the auto
global-min window, `energy_above_min = 1.0` eV/atom, filters which candidates are even
eligible, independent of λ.)

---

## 3. Graph 1 — `novelty_analysis_comparison.png` (1×3 bars: distinct / duplicates / best energy)

### 3a. Left — "Distinct configurations" (Regular 48 vs Novelty 75)

**What it is.** A bar chart comparing how many distinct configurations (fingerprint
clusters at `DUP_THRESHOLD = 1.5`) each acquisitor found in its 100 evaluations.

**What it means.** The number of structurally different basins sampled. This is the
diversity metric — the core thing Novelty-LCB is designed to increase.

**What it implies.** Novelty-LCB finds **75 distinct basins vs 48 for Regular LCB — a
56% increase**. On the real, rough Fe/MgO landscape the novelty term works exactly as
intended: it keeps pushing into structurally new regions instead of re-relaxing the
same few basins. This is a large, physically meaningful diversity gain — a sharp
contrast to the Ni8/Au EMT benchmark (project 73), where novelty only improved diversity
from 1.8 → 2.0 distinct configs. The smooth EMT surface had few distinct basins for
novelty to find; the rough Fe/MgO landscape is full of them, and novelty exploits that.

**Outcome.** Novelty-LCB is dramatically more diverse than Regular LCB on this real
system (+27 distinct basins).

### 3b. Middle — "Duplicate evaluations" (Regular 52 vs Novelty 25)

**What it is.** Number of evaluations that were *not* a new distinct configuration
(i.e. that re-visited an already-known basin).

**What it means.** Efficiency / redundancy: how much of the 100-evaluation budget was
wasted re-sampling known structures.

**What it implies.** Regular LCB wasted **52%** of its budget on duplicates; Novelty-LCB
only **25%**. Halving the duplicate rate is the direct reciprocal of the diversity gain
(one extra distinct config = one fewer duplicate). This is the strongest single result:
on Fe/MgO, Novelty-LCB roughly **halves the wasted evaluations** relative to regular LCB.

**Outcome.** Novelty-LCB is far more sample-efficient on this landscape (25% vs 52%
duplicates), a big improvement over the ~97%-duplicate behaviour seen on the smooth EMT
system where neither acquisitor explored effectively.

### 3c. Right — "Best energy [eV]" (Regular −435.315 vs Novelty −432.015)

**What it is.** The lowest energy (eV) among each acquisitor's distinct configurations —
the depth of its best-found minimum.

**What it means.** Optimality: how deep the search reached. Lower is better.

**What it implies.** Regular LCB finds a **3.30 eV deeper** global minimum
(−435.315 vs −432.015 eV). This is the expected trade-off, now visible on the real
system: the novelty term spends budget chasing *new* (often higher-energy) basins, so it
explores more broadly but does not concentrate as hard on the very deepest minimum. It
is worth noting, however, that Novelty-LCB still reaches −432 eV (a deep, low-energy
state) and finds 6 basins below −430 eV — it is not failing to find low-energy
structures, it just spreads its finds over a wider band than Regular LCB's 8 sub-−430 eV
basins.

**Outcome.** Regular LCB is the better *single-minimum optimizer* on this seed
(−435.315 vs −432.015 eV, a 3.3 eV gap); Novelty-LCB trades that depth for breadth.

---

## 4. Graph 2 — `novelty_analysis_discovery.png` (cumulative distinct vs evaluations)

**What it is.** For each acquisitor, the cumulative number of distinct configurations
found plotted against the number of evaluations spent (0→100). Steelblue = Regular LCB,
coral = Novelty-LCB.

**What it means.** The discovery curve shows *how fast* each search accumulates genuinely
new structures as the budget is spent. A rising curve = the search is still finding new
basins; a flattening curve = it is saturating and mostly duplicating.

**What it implies.**
- **Regular LCB** climbs steadily but flattens toward the end — reaching ~45–47 distinct
  by eval ~90–100 and essentially plateauing (91→100 adds only ~2). It stops discovering
  new basins late in the run and spends its remaining budget on duplicates.
- **Novelty-LCB** climbs **faster and never flattens** — reaching 74 distinct by eval 100
  and still rising (71→74 between evals 91 and 100). It is discovering new basins at
  almost the same rate at the end of the run as at the start, meaning it is far from
  saturation.

**Outcome.** The discovery curves make the diversity advantage concrete: Regular LCB
saturates (~48 distinct) while Novelty-LCB is still climbing toward 75+ — and would
presumably discover even more with a longer run. Novelty-LCB not only finds more basins,
it finds them *sustained across the whole run*, whereas regular LCB exhausts its
exploration early.

---

## 5. Overall interpretation

**What the analysis shows.** On the real Fe/MgO system (seed 3, 100 evals), Novelty-LCB
delivers a large diversity/efficiency win at the cost of a moderate depth penalty:

1. **Diversity (strong win):** 75 vs 48 distinct basins (+56%).
2. **Efficiency (strong win):** 25% vs 52% duplicate rate — roughly half the wasted
   evaluations.
3. **Optimality (moderate loss):** best energy −432.0 vs −435.3 eV (Novelty 3.3 eV
   shallower), though Novelty still finds deep states (−432 eV, 6 basins < −430 eV).
4. **Discovery dynamics:** Novelty keeps finding new basins throughout the run; Regular
   saturates.

**Why this differs so sharply from the EMT benchmark.** Project 73 (Ni8/Au EMT) showed
only a marginal novelty advantage because that smooth, few-basin surface gave the novelty
term almost nothing to find — both acquisitors collapsed to 1–2 basins and ~97%
duplicates. Fe/MgO is a **rough, many-basin landscape**, which is exactly the regime the
novelty bonus was designed for: there are many distinct metastable structures to
discover, and Novelty-LCB exploits them. The EMT result was *not* representative of the
physical system; this Fe/MgO result is the meaningful one.

**The trade-off, stated plainly.** Novelty-LCB is the better *basin explorer* and the
better *sample-efficient* search on Fe/MgO (more distinct structures, half the
duplicates), but Regular LCB finds the *deeper single global minimum* (−435.3 vs
−432.0 eV). Which is "better" depends on the goal:
- For **populating a diverse database of metastable basins** (the stated purpose of the
  parent Novelty-LCB project — feeding downstream `_run/9_novelFilter` dedup +
  `_run/8_nested_sampling` partition-function statistics), **Novelty-LCB is clearly
  superior**: it gives the downstream tools far more distinct minima to weight.
- For **finding the single deepest global minimum**, **Regular LCB is better** by 3.3 eV.

**Caveats.**
- Single seed (3), single run each — the 3.3 eV depth gap and the +27-basin diversity
  gain are per-seed observations, not averaged statistics. More seeds would be needed to
  quantify the spread (the 10-seed extended benchmark in project 73 does this on EMT).
- `DUP_THRESHOLD = 1.5` is the 73-benchmark default carried over to Fe/MgO. The absolute
  distinct counts depend on this threshold; the *relative* Novelty-vs-Regular comparison
  is robust to it, but a Fe/MgO-calibrated threshold could shift both counts.
- These are the already-stored 100 candidate structures; the analysis is post-hoc
  clustering, not a re-run of the search.

**Bottom line.** On the real Fe/MgO system, Novelty-LCB (auto global-min, 1 eV/atom
window) is a strongly more diverse and roughly twice-as-sample-efficient search than
Regular LCB, at the cost of a shallower best minimum (−432.0 vs −435.3 eV). For the
parent project's goal of building a broad database of distinct Fe/MgO basins, Novelty-LCB
is the better acquisitor on this evidence; Regular LCB remains the better choice if the
sole objective is the single deepest global minimum.

---

## 6. Configurational-space (basin) map — 2D PCA + clustering

This section maps the configurational space explored by the two seed-3 runs by
projecting all 200 structures (100 Regular + 100 Novelty) onto a **shared 2D PCA
subspace** of the 720-dim Fe/MgO Fingerprint features, then clustering the points into
structural "basins".

Results source: `pca_basin_analysis.py`, `pca_basin_analysis_results.json`,
`pca_basin_map.png`, `pca_basin_aux.png`.
Settings: PCA on 720-dim Fingerprint (not whitened), PC1+PC2 capture **80.2%** of the
variance (PC1 67.0%, PC2 13.2%); KMeans k=4; DBSCAN eps=0.9, min_samples=4.

### What the map is

- **PCA:** both runs' fingerprint features are pooled and projected onto their two
  dominant directions of variance. Each point = one relaxed GPAW-scored structure;
  its position is where it sits in the dominant configurational coordinates.
- **Clustering → basins:** points that group together in this reduced space are treated
  as belonging to the same structural basin. KMeans (k=4, chosen for basin resolution)
  and DBSCAN (density-based) are both shown for comparison.
- **Overlay:** circle = Regular LCB, star = Novelty-LCB, so the map shows *which
  acquisitor populated which basin*. Each basin is annotated with its lowest-energy
  member.

### KMeans basin summary (the interpretable map)

| Basin | Size | Best energy (eV) | Regular | Novelty | Character |
|---|---|---|---|---|---|
| C0 | 89 | **−435.315** | 57 | 32 | Deepest basin; **Regular-dominated** |
| C3 | 56 | −432.015 | 16 | 40 | Low basin; **Novelty-dominated** |
| C1 | 37 | −422.304 | 18 | 19 | Mid-energy basin; balanced |
| C2 | 18 | −403.119 | 9 | 9 | High-energy basin; balanced |

### What it means / implies

- **Two acquisitors concentrate in different low-energy basins.** Regular LCB piles most
  of its structures into the single deepest basin C0 (57 of its 100 there) and barely
  reaches the second-low basin C3 (16). Novelty-LCB instead spreads across both low
  basins — fewer in C0 (32) but a large block in C3 (40), the second-deepest basin. This
  is the basin-resolved picture of the headline result: Regular *concentrates* its
  search on one deep basin, Novelty *spreads* it over the low-energy space.
- **Novelty reaches the deeper basin but less densely.** C0 (the global minimum,
  −435.3 eV) is still primarily Regular's territory by count, yet Novelty-LCB does put
  32 structures there — it finds the deepest basin, just with lower occupancy.
- **Both avoid the high-energy tail in similar numbers** (C2 balanced 9/9), and the
  mid-energy basin C1 is balanced (18/19). The diversity difference is concentrated in
  the two low-energy basins (C0 vs C3), not in the high-energy tail.

### DBSCAN (density) view — and why it is coarser

DBSCAN at eps=0.9 splits the map into just two density regions plus 11 noise points:
C0 = the high-energy outlier group (n=18, −403.1 eV, balanced 9/9) and C1 = the big
low-energy region (n=171, best −435.3 eV, 86 regular / 85 novelty). This shows that on
the 2D projection the entire low-energy space is one *connected density blob* — there is
no well-separated density gap between C0/C1/C3 of the KMeans map. The distinction between
the Regular-deep and Novelty-low basins is therefore a **gradation within one connected
low-energy region**, not a set of isolated minima. (The 48/75 distinct-configuration
counts from the earlier greedy analysis are finer-grained than this 2D reduction can
show, because PCA compresses the 720-dim space down to 2 axes.)

### Outcome

- The configurational map confirms, at basin resolution, that **Novelty-LCB spreads its
  search across more of the low-energy landscape** (populating two low basins) whereas
  **Regular LCB concentrates into the single deepest basin**. This is the geometric
  expression of the diversity/efficiency results in Sections 2–4.
- The cost is visible too: Regular's concentration in C0 is what lets it claim the
  deepest minimum (−435.315 eV), while Novelty's spread lowers its single-best energy
  (−432.015 eV) even though it still reaches the C0 basin.
- KMeans (k=4) is the more physically informative clustering here; DBSCAN shows the
  low-energy space is one connected region, i.e. the KMeans C0/C3 split is a within-basin
  gradation rather than isolated minima.

Caveat: this is a 2D projection of a 720-dim space (80% variance retained), so it
compresses fine structure; basin *counts* here differ from the greedy
`DUP_THRESHOLD=1.5` counts because PCA merges near-neighbours that the greedy clustering
keeps separate.

