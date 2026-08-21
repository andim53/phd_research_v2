# Novel Structure Filter — distinct set for a partition-function representation

**Date:** 2026-08-20
**Agent:** Calyx
**Run dir:** `/home/think/Desktop/research/_run/9_novelFilter/`
**Env:** `agox_v2` conda (AGOX 3.10.2 + ASE 3.25.0), Python 3.11
**Python:** `/home/think/miniconda3/envs/agox_v2/bin/python` (base `python3` has no AGOX/ASE)

---

## 1. Purpose of this file

This is the self-contained operational reference for the **novel-structure
filter** that collapses a multi-seed AGOX search database into a **distinct
(non-repeating) set** suitable for building a representation of the partition
function. It documents the methodology, the exact code layout, how the
similarity threshold was calibrated, the verified results, and the pitfalls
encountered. Use it as the starting point next time you need to filter an AGOX
database for uniqueness, or extend/adapt this workflow (different system,
different descriptor, different partition-function representation).

It complements `README.md` (short usage) and the related multi-seed nested
sampling work in `_run/8_nested_sampling/` and its guide in
`_md/for-agent/nested_sampling_multiseed_guide.md`.

---

## 2. Motivation — why filter for "novel" structures

The raw AGOX database is the output of a stochastic global-optimization search
(13 independent seeds, 100 iterations each, GPAW DFT). Across seeds the search
**re-finds the same local minima many times**, each time as a slightly different
relaxation. If you naively sum over *every* stored structure,

    Z(T) = Σ_i exp(−β·E_i),

you **double count** the same structural basin multiple times, which inflates
the low-energy weight of that basin far beyond its true thermodynamic
contribution. The partition function needs the number of *distinct physical
states*, not the number of search visits.

This filter removes the redundancy: it keeps, for every structurally distinct
region of the energy landscape, a single representative (the **lowest-energy**
member of each basin), so each state is counted **exactly once**.

---

## 3. The novelty measure (what "alike" means)

Two structures are considered "alike" when they are close in **descriptor
feature space**. Each structure is mapped to a fixed-length fingerprint vector,
and novelty is the **minimum Euclidean distance** from a candidate to every
already-accepted structure:

    Novelty(x) = min_{i ∈ accepted} ‖ fingerprint(x) − fingerprint(x_i) ‖₂

This is the **exact same measure** used by `NoveltyLCBAcquisitor` and the
standalone `is_distinct` / `fingerprint_distance` helpers in
`_run/6_lcbnovel_benchmark/novelty_lcb/` — so the two tools are directly
composable (the same threshold semantics apply in both).

### Descriptor
`agox.models.descriptors.fingerprint.Fingerprint` — default parameters
(`rc1=6, rc2=4, binwidth=0.2, Nbins=30, use_angular=True`). For the Fe/MgO
system this produces a **720-dimensional** vector per structure
(2-body radial part 180 + 3-body angular part 540; see the feature-dimension
breakdown in `_run/8_nested_sampling`'s guide). Constructed via
`Fingerprint.from_atoms(traj[0])` — the reliable pattern.

### Raw vs. normalised features (important calibration finding)
I first tried **row-normalising** each feature vector to unit length before
measuring distance. That compressed all inter-structure distances (max
nearest-neighbour ≈ 0.167) and, with a threshold of 0.35, kept only **7**
structures — far too aggressive. The reference `novelty_lcb` code uses **raw**
Euclidean distances, and in raw units distinct Fe/MgO minima sit >1 apart while
near-duplicate relaxations are far closer. **The final implementation uses raw
feature vectors** and a threshold in raw distance units.

---

## 4. The greedy filtering algorithm

Inputs: feature matrix `F` (n×720) and the energies `E`.

1. Order the structures **lowest-energy first** (`order = argsort(E, stable)`).
2. Maintain an empty "accepted" list.
3. Walk the order; for each structure, compute its minimum Euclidean distance
   to every accepted feature vector.
   - If that minimum distance `≤ threshold` → **skip** (it is a near-duplicate
     of something already kept).
   - Else → **keep** it and add its feature vector to the accepted set.
4. The first (global-minimum-energy) structure is always kept.

This greedy, energy-ordered selection guarantees that the **lowest-energy
representative** of every distinct basin is the one retained, which is the
correct representative for Boltzmann-weighting. The nearest-neighbour
computation is chunked so it never materialises an n×n distance matrix in
memory.

---

## 5. Code layout

```
_run/9_novelFilter/
├── run_filter.py            # entry point / CLI (loads, filters, saves)
├── novel_filter/
│   ├── __init__.py          # package exports
│   └── filter.py            # load, descriptor, filter_novel, partition_function, save
├── README.md                # short usage + threshold guidance
└── NOVEL_FILTER_RUN.md      # this document
```

### `run_filter.py`
- Globs `dataset/seed_*/1_db/db_*.db`.
- `--threshold` (default **1.0**), `--temp` (300 K), `--output` (`./novel_output`), `--rng` (42).
- Prints the nearest-neighbour-distance distribution before filtering so the
  threshold can be sanity-checked, then runs the greedy filter and evaluates the
  partition function over the kept set.

### `novel_filter/filter.py` — key functions
| Function | Purpose |
|---|---|
| `load_all_seeds(dataset_dir, pattern)` | Concatenate all structures, energies, per-structure source DB |
| `verify_uniform_composition(structures)` | Assert one composition / atom count (prereq for a single global descriptor) |
| `build_features(descriptor, structures)` | Stack raw feature vectors into an (n, 720) array |
| `filter_novel(features, order, threshold)` | Greedy distinct-subset selection; returns kept indices + min-dist-to-kept |
| `nearest_neighbour_distances(features)` | Chunked nearest-neighbour distance for threshold calibration |
| `partition_function(energies, temperature)` | Log-space Z, log_Z, weights, log-weights |
| `save_novel_subset(...)` | Write `.xsf` structures, summary CSV, partition CSV, summary txt |

---

## 6. Run command (as executed)

Single threshold:
```bash
cd /home/think/Desktop/research/_run/9_novelFilter
/home/think/miniconda3/envs/agox_v2/bin/python run_filter.py \
    --threshold 1.0 --temp 300 --output ./novel_output --rng 42
```

Threshold sweep (one output folder of ALL kept `.xsf` per threshold):
```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_filter.py \
    --thresholds 0.25,0.5,0.75,1.0,1.25,1.5,2.0 \
    --temp 300 --output ./novel_output --rng 42
```

`--thresholds` accepts a comma-separated list. Each value writes to its own
`thr_<v>/` folder; `threshold_comparison.csv` at the top level collates every
threshold's n_kept / n_removed / E range / log_Z / Z for side-by-side reading.

---

## 7. Verified results (this run)

### Dataset (identical to `_run/8_nested_sampling`)
- Seeds **3–15** → **13** databases, **1297** structures.
- Composition **Fe25Mg25O25** (75 atoms), uniform across every seed (verified).
- Energy range **−436.909 .. −386.292 eV**.

### Nearest-neighbour distance distribution (raw units)
```
min    = 0.0100
median = 0.4029
p95    = 0.9407
max    = 1.7957
fraction with a near-twin within 1.0 : 95.7%
```
The dataset is extremely dense with near-duplicates — the median structure has
another structure within 0.40 of it.

### Novel filtering at threshold = 1.0 (energy-ordered)
| Quantity | Value |
|---|---|
| Input structures | 1297 |
| **Novel (distinct) kept** | **164** |
| Removed as duplicates | 1133 |
| Kept E range | −436.909 .. −386.905 eV |

### Partition function at T = 300 K over the 164 distinct structures
```
Z        = 1.063335e+00
log Z    = 0.0614
```
Boltzmann weights (top 3): the ground state dominates at **0.940**,
the first excited (ΔE = 0.071 eV) at **0.0596**, everything else ~1e-44.
At 300 K the partition function is essentially the ground-state Boltzmann
factor — expected given the large gaps to higher distinct minima.

### Threshold sweep — verified (this run, `--thresholds 0.25,0.5,0.75,1.0,1.25,1.5,2.0`)

| threshold | n_kept | n_removed | kept E min | kept E max | log_Z | Z |
|---|---|---|---|---|---|---|
| 0.25 | 1161 | 136 | −436.909 | −386.292 | 0.3734 | 1.453e+00 |
| 0.50 | 655 | 642 | −436.909 | −388.934 | 0.0614 | 1.063e+00 |
| 0.75 | 291 | 1006 | −436.909 | −386.600 | 0.0614 | 1.063e+00 |
| **1.00** | **164** | 1133 | −436.909 | −386.905 | 0.0614 | 1.063e+00 |
| 1.25 | 99 | 1198 | −436.909 | −392.888 | 0.0000 | 1.000e+00 |
| 1.50 | 61 | 1236 | −436.909 | −390.466 | 0.0000 | 1.000e+00 |
| 2.00 | 32 | 1265 | −436.909 | −390.466 | 0.0000 | 1.000e+00 |

Each threshold's full distinct set is in its own `thr_<v>/novel_structures/`
folder (e.g. `thr_0.25/` = 1161 xsf, `thr_2/` = 32 xsf). Compare e.g. the
rank-0/1/2 files across folders to see how the low-energy representatives
change with the filter parameter.

---

## 8. Outputs (in `--output`, here `novel_output/`)

When run as a sweep, outputs are organised per threshold:

```
novel_output/
├── threshold_comparison.csv        # all thresholds: n_kept, n_removed, E range, log_Z, Z
├── thr_0.25/
│   ├── novel_structures/novel_<rank>_E<e>.xsf     # 1161 distinct structures
│   ├── novel_structures_summary.csv
│   ├── partition_function.csv
│   └── filter_summary.txt
├── thr_0.5/   ...   (655 xsf)
├── thr_0.75/  ...   (291 xsf)
├── thr_1/     ...   (164 xsf)
├── thr_1.25/  ...   (99 xsf)
├── thr_1.5/   ...   (61 xsf)
└── thr_2/     ...   (32 xsf)
```

Per-threshold files:
| File | Contents |
|---|---|
| `novel_structures/novel_<rank>_E<e>.xsf` | all distinct structures for that threshold, energy-ordered (rank 0000 = lowest E). XSF with forces (75 atoms). |
| `novel_structures_summary.csv` | rank, dataset index, energy, source DB (`seed_#/1_db/db_#.db`), min distance to the kept set |
| `partition_function.csv` | rank, energy, Boltzmann weight, log Boltzmann weight over the distinct set |
| `filter_summary.txt` | threshold, temperature, input/kept/removed counts, final Z and log Z |

## 8b. Side-by-side comparison helper (`compare_xsf.py`)

To eyeball how the same structural rank changes across thresholds, copy the
top-N structures from every threshold folder into one tree:
```bash
cd /home/think/Desktop/research/_run/9_novelFilter
python3 compare_xsf.py --outdir ./novel_output --n 5 --dest ./side_by_side
```

Produces:
```
side_by_side/
├── rank0/thr_0.25_novel_0000_E-436.909.xsf, thr_0.5_..., thr_1_..., thr_2_...
├── rank1/thr_0.25_novel_0001_E-436.885.xsf, ...
├── rank2/...
├── rank3/...
└── rank4/...
```

Open a `rank<r>/` folder and cycle the `thr_<v>_*` files. Rank 0 is the same
structure for every threshold (the global minimum is always kept), but the
higher ranks differ — e.g. rank 1 is `-436.885` at thr 0.25 but jumps to
`-432.168` at thr 2.0, showing how stricter thresholds discard more of the
low-energy near-duplicate basin and keep only the most diverse structures.
No AGOX/ASE needed — pure filesystem copy.

## 8c. Landscape & probability analysis per threshold (`run_analysis_thresholds.py`)

This applies the existing `_analysist` Stage-2 (landscape) and Stage-3
(probability) analysis to **each threshold's filtered structure set**, so the
"evolution" of the energy landscape and the Boltzmann probability distribution
can be followed as the filter goes loose → strict.

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py --outdir ./novel_output
```

For each `thr_<v>/` it reads the structures (`novel_structures/*.xsf`, ordered
by rank) and their energies (`novel_structures_summary.csv` — the xsf carries
no energy) and writes to `novel_output/analysis/thr_<v>/`:
- `conf_space.png` — PCA on fingerprint descriptors (top-eigenvector
  projection) vs per-atom relative energy `(E_i−E_glob)/N`, with a KDE
  state-density panel. Reuses `plot_structure_landscape`.
- `binding_probability_vs_temperature.png` — Boltzmann
  `P(E) = ρ(E)·exp(−ΔE/kT)/Z` at 5 temperatures (298.15…646.4 K), per-atom
  relative-energy axis.

Verified run (all 7 thresholds):
| threshold | structures | rel-E max (eV/atom) |
|---|---|---|
| 0.25 | 1161 | 0.6749 |
| 0.50 | 655 | 0.6397 |
| 0.75 | 291 | 0.6708 |
| 1.00 | 164 | 0.6667 |
| 1.25 | 99 | 0.5870 |
| 1.50 | 61 | 0.6192 |
| 2.00 | 32 | 0.6192 |

All 14 figures produced (7 × {conf_space, binding_probability}).

Key notes for interpreting the "evolution":
- **Landscape (conf_space.png)**: each panel shows the distinct structures of
  that threshold in PCA-projection space vs relative energy. As the threshold
  rises, the number of points drops and the state-density KDE changes shape —
  near-duplicate low-energy basin members vanish first, so the landscape loses
  its dense low-energy cluster and retains only widely-spread distinct minima.
- **Probability (binding_probability_vs_temperature.png)**: the Boltzmann curve
  at each temperature. Because the ground state always dominates at these
  temperatures, the low-temperature curves are pinned near the ground state
  (peak at ΔE=0); as the threshold removes higher-energy near-duplicates, the
  high-temperature tail redistributes weight. Compare e.g. thr 0.25 vs thr 2.0.
- Per-atom relative energies are used (divide by N=75), matching the reference
  scripts, so the x-axis is in eV/atom.

Options: `--thresholds` (subset, folder-name suffixes), `--e-max` (common energy
axis across all thresholds so panels are directly comparable), `--normalize-density`.

## 8d. Example structures separated by each threshold (`save_example_pairs.py`)

The novelty filter keeps structures whose minimum distance to the kept set is
STRICTLY greater than the threshold, so the closest pair among a threshold's
kept structures always sits just ABOVE the threshold value. This script finds,
for each threshold, that closest pair (the two structures separated by ~the
threshold distance) and saves both XSFs:

```bash
/home/think/miniconda3/envs/agox_v2/bin/python save_example_pairs.py --outdir ./novel_output
```

Writes `novel_output/example_pairs/thr_<v>/pair_A_rank<r>_E<e>.xsf` +
`pair_B_rank<r>_E<e>.xsf` (two files per threshold) and `pairs_summary.csv`.

Verified results (closest kept pair per threshold):
| threshold | pair (rank A ↔ B) | energies (eV) | pair distance |
|---|---|---|---|
| 0.25 | 24 ↔ 33 | −435.453 ↔ −435.263 | 0.2502 |
| 0.50 | 172 ↔ 229 | −430.542 ↔ −429.011 | 0.5000 |
| 0.75 | 6 ↔ 11 | −434.477 ↔ −433.872 | 0.7503 |
| 1.00 | 10 ↔ 28 | −432.689 ↔ −426.915 | 1.0002 |
| 1.25 | 20 ↔ 52 | −422.607 ↔ −414.777 | 1.2534 |
| 1.50 | 11 ↔ 15 | −421.186 ↔ −419.346 | 1.5007 |
| 2.00 | 6 ↔ 13 | −419.512 ↔ −415.363 | 2.0001 |

Each pair distance lands essentially on its threshold (0.25→0.2502, 0.5→0.5000,
…, 2.0→2.0001), confirming the interpretation: these two structures are the pair
closest to being merged into one, i.e. the two distinct structures that are
separated by about the threshold. As the threshold rises, the chosen pair moves
to higher-energy, more structurally-diverse structures (the near-duplicate
low-energy basin is progressively discarded).

---

## 8e. Force filter + nested novel filter (`run_force_novel_filter.py`)

Because the raw structures are surrogate-relaxed with single-point DFT energies
(large residual forces — the original evaluator used only ~1 DFT step), a
**force filter** is applied BEFORE the novel filter to keep only the structures
closest to being genuine minima. The force measure is `max|F|` over the 25
mobile **Fe** atoms only — the 50-atom MgO substrate is fixed by the original
constraints and its forces are excluded. A **novel filter** (fixed threshold
1.0) is then applied inside each force threshold to keep only distinct minima.

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_force_novel_filter.py --outdir ./force_output
# then analyse each force-filtered set:
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_thresholds.py \
    --outdir ./force_output --prefix force_
```

`run_analysis_thresholds.py` gained a `--prefix` flag so it can discover
`force_<v>/` folders as well as the default `thr_<v>/`.

Verified results (raw dataset 1297 structures, novel thr 1.0):
| force thr (eV/Å) | force survivors | novel distinct kept | kept E range (eV) |
|---|---|---|---|
| 0.5 | 27 (2.1%) | 6 | −418.6 … −417.1 |
| 1.0 | 338 (26.1%) | 44 | −436.9 … −404.1 |
| 1.5 | 786 (60.6%) | 87 | −436.9 … −391.5 |
| 2.0 | 1006 (77.6%) | 124 | −436.9 … −391.5 |
| 2.5 | 1086 (83.7%) | 138 | −436.9 … −391.5 |
| 3.0 | 1133 (87.4%) | 139 | −436.9 … −391.5 |

Key observations:
- The median max|Fe force| across the raw set is ~1.30 eV/Å (min 0.18, max 10.1),
  confirming few structures are near-converged.
- At the tightest threshold (0.5 eV/Å) the global minimum (−436.9) does NOT
  survive — the ground-state geometry in the raw DB is not well-relaxed. The
  most relaxed structures cluster around −418 eV.
- As the force threshold loosens, more structures (and the true ground state)
  enter, and the novel filter still collapses them to distinct minima.
- All 6 force thresholds produced landscape + probability figures under
  `force_output/analysis/force_<v>/` (12 figures total).

---

## 9. Pitfalls & key learnings

1. **Normalising the fingerprint vectors destroys the distance scale.** The raw
   feature vectors have norm ≈ 10 (min 9.71, med 10.76, max 12.29); after
   normalisation all inter-structure distances collapse below ~0.17 and a
   sensible-looking threshold over-filters to a handful of structures. Use raw
   Euclidean distances, matching `novelty_lcb`.
2. **Threshold calibration must be data-driven.** Always print the
   nearest-neighbour-distance distribution first (the script does). For Fe/MgO
   the "knee" separating near-duplicates from genuinely distinct minima is
   around **1.0** (median NN 0.40, p95 0.94). A threshold far below the median
   keeps almost everything; far above the max keeps only the most diverse.
3. **`np.savetxt` cannot write mixed string/float rows** — writing the source-DB
   column (a string) alongside floats with a single `fmt` array raises
   `ValueError: could not convert string to float`. The summary CSV is written
   manually with a plain `for` loop instead.
4. **Log-space partition function is mandatory.** Energies ~ −400 eV, β ~ 40 →
   exp(β·E) overflows/underflows. Compute `log w = −β·(E − E_ref)` and accumulate
   via the log-sum-exp trick; return weights AND log-weights (log-weights avoid
   the `divide by zero`/`log(0)` warnings from underflowed weights on hot tails).
5. **Uniform composition is a hard prerequisite.** A single global `Fingerprint`
   only supports one stoichiometry/atom count. `verify_uniform_composition`
   checks this and raises rather than silently producing a broken descriptor.
6. **`Fingerprint.from_atoms()` is the reliable constructor** — the
   `Fingerprint(environment=...)` form can fail to parse space-joined symbols.
7. **This is a dedup of already-relaxed structures — no GPR is trained.** Unlike
   `_run/8_nested_sampling`, this filter does not build a surrogate. It works
   directly on the stored DFT-optimized geometries and energies. If you want a
   *surrogate-sampled* partition function (new structures, not just the DB
   ones), that is the nested-sampling path, not this filter.
8. **Energy-ordered greedy keeps the basin's lowest representative**, which is
   the correct choice for Boltzmann weighting. If you instead want diversity
   independent of energy (e.g. farthest-point sampling), swap `order` — the
   `filter_novel` function takes any order array.

---

## 10. Related work / files

| Item | Path |
|---|---|
| This run's README | `_run/9_novelFilter/README.md` |
| Multi-seed nested sampling (combines DBs into one GPR) | `_run/8_nested_sampling/` |
| Nested-sampling guide | `_md/for-agent/nested_sampling_multiseed_guide.md` |
| Novelty-LCB acquisitor + `is_distinct` / `fingerprint_distance` | `_run/6_lcbnovel_benchmark/novelty_lcb/` |
| Novelty-LCB × AGOX troubleshooting | `_md/for-agent/novelty_lcb_agox_troubleshooting.md` |

---

## 11. Extending / adapting

- **Different system**: point `DATASET_DIR` / `DB_PATTERN` at the new DBs and
  re-calibrate `--threshold` from the printed NN distribution.
- **Different descriptor**: swap `Fingerprint` for `SOAP`, `SimpleFingerprint`,
  etc. in `build_features`; the greedy filter and partition function are
  descriptor-agnostic (they only need an (n, d) feature matrix).
- **Different representative**: to keep the *median* or *most central* member of
  a basin instead of the lowest-energy one, change the ordering passed to
  `filter_novel`.
- **Partition function**: the weights are normalised over the kept set; you can
  also save the un-normalised `exp(−β(E−E_ref))` factors to combine with an
  absolute density of states later.
