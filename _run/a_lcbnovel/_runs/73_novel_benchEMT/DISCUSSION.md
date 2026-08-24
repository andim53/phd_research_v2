# DISCUSSION — Novelty-LCB vs Regular LCB Benchmark (EMT)

Project: `73_novel_benchEMT`
Benchmark: `main_benchmark.py` — Regular LCB vs Novelty-LCB (auto global-minimum window)
System: Ni8 on Au(4,4,2) fcc100 surface, **EMT** calculator
Results source: `benchmark_results/benchmark_results.json`, `benchmark_comparison.png`, `benchmark_differences.png`

---

## 1. What was benchmarked

Two acquisition strategies run on the **same** seeds, generators, sampler, relaxer and
evaluator — the only difference is the acquisitor:

| | Regular LCB | Novelty-LCB |
|---|---|---|
| Acquisition | `μ(x) − κ·σ(x)`, **minimized** | `σ(x) + λ·Novelty(x)`, **maximized** |
| `κ` | 2.0 | 2.0 |
| `λ` (novelty_weight) | — | 1.5 |
| Energy window | none (pure LCB) | auto global-min, `E/N ≤ E_min/N + 0.1` eV/atom (cap ≈ +4 eV on 40 atoms) |
| Diversity driver | none | Novelty = min fingerprint distance to all DB structures |

Setup: 5 seeds (41, 101, 201, 301, 401), 30 iterations / run, 60 evaluations per run.
`DUP_THRESHOLD = 1.5` (fingerprint distance) defines "distinct configuration".

---

## 2. Aggregate statistics (from `benchmark_results.json`)

| Metric | Regular LCB | Novelty-LCB | Δ (Nov − Reg) |
|---|---|---|---|
| Distinct configs (mean) | 1.80 (std 0.40) | 2.00 (std 0.00) | **+0.20** |
| Duplicate evals (mean) | 58.2 / 60 | 58.0 / 60 | −0.2 |
| Duplicate rate | 97% | 97% | ~0 |
| Best energy (mean, eV) | 18.966 (std 0.607) | 19.410 (std 0.669) | **+0.444** |
| Energy range (mean, eV) | 4.275 | 3.815 | −0.460 |
| Wall time (mean, s) | 28.4 | 29.3 | +0.9 |

Per-seed best energy (eV):

| seed | Regular | Novelty | Δ |
|---|---|---|---|
| 41 | 19.748 | 20.640 | +0.892 |
| 101 | 18.604 | 18.946 | +0.342 |
| 201 | 18.113 | 18.842 | +0.729 |
| 301 | 19.554 | 19.598 | +0.043 |
| 401 | 18.810 | 19.024 | +0.213 |

---

## 3. Graph 1 — `benchmark_comparison.png` (2×2 panel)

### 3a. Top-left — "Distinct Surface Configurations per Run" (bars, per seed)

**What it is.** A grouped bar chart; for each of the 5 seeds it shows how many
distinct configurations (fingerprint clusters, `DUP_THRESHOLD = 1.5`) each acquisitor
collected over its 60 evaluations — steelblue = Regular, coral = Novelty.

**What it means.** Distinct configurations is the diversity metric: how many genuinely
different structural basins the search visited, rather than how many times it
re-optimised the same one. Regular scores [1, 2, 2, 2, 2], Novelty [2, 2, 2, 2, 2].

**What it implies.** Novelty-LCB is at least as diverse as Regular LCB in every run, and
strictly better in one: seed 41, where Regular collapsed onto a **single** basin
(`n_distinct = 1`, `e_range = 0.0`) while Novelty still found 2. This is the one place
the novelty term does exactly what it was designed to do — it resists settling into one
basin. But the aggregate gain is tiny (1.8 → 2.0), so on this landscape the marginal
diversity benefit is small.

**Outcome.** Marginal diversity win for Novelty-LCB; no run where it finds fewer distinct
configurations than Regular. The headline effect is small because both strategies find
only 1–2 distinct minima out of 60 evaluations.

### 3b. Top-right — "Duplicate Evaluations per Run" (bars, per seed)

**What it is.** Grouped bars of the number of evaluations that were *not* new distinct
configurations (i.e. 60 − distinct), per seed and per acquisitor.

**What it means.** This is the redundancy / waste metric. A value near 60 means the
search kept re-visiting the same few basins instead of exploring new ones.

**What it implies.** Both acquisitors sit at **58–59 duplicates (≈97%)** — essentially
every run wastes almost all of its budget re-sampling the same structures. The novelty
bonus did **not** reduce redundancy meaningfully (−0.2 on average; only seed 41 differs,
and only by 1). This is the most striking, and most sobering, feature of the whole
benchmark: neither strategy is efficient at exploring this EMT surface.

**Outcome.** Novelty-LCB does not fix the duplicate problem. ~97% of evaluations in
*both* strategies are redundant, so the "diversity" advantage seen in 3a is measured on
a tiny base of distinct structures.

### 3c. Bottom-left — "Best Energy Found per Run" (lines, per seed)

**What it is.** Two line plots (steelblue = Regular, coral = Novelty) of the lowest
energy (eV) each acquisitor found, per seed. Lower is better.

**What it means.** This is the exploitation / optimality metric: did the search reach the
deepest minimum on the surface?

**What it implies.** Regular LCB finds a **lower** minimum than Novelty in **all 5 seeds**
(Δ = +0.89, +0.34, +0.73, +0.04, +0.21; mean +0.44 eV). The gap is largest on seed 41
(where Regular got stuck on one basin — a *low* one) and smallest on seed 301. This is
the classic exploration–exploitation tension made concrete: Novelty-LCB spends budget
chasing *structurally new* (often higher-energy) regions, so it lands in shallower
minima; Regular LCB concentrates on the low-energy region it already knows.

**Outcome.** On this surface, Regular LCB is the better optimizer of the single global
minimum — it beats Novelty on all 5 seeds, by ~0.44 eV on average.

### 3d. Bottom-right — "Discovery Curves (average ± individual runs)"

**What it is.** Cumulative distinct configurations plotted against cumulative
evaluations. The two solid lines are the average over the 5 seeds for each acquisitor
(steelblue = Regular, coral = Novelty); the faint lines behind them are the individual
per-seed runs.

**What it means.** The curve shows *how fast* each strategy accumulates genuinely new
structures as the budget is spent. A steep curve = efficient exploration; a flat curve =
the search has saturated and everything after is duplication.

**What it implies.** Both curves rise sharply over the first ~1–2 evaluations and then go
**almost completely flat** — the search finds essentially all of its distinct
configurations almost immediately, then spends the remaining ~58 evaluations rediscovering
them. Novelty's curve sits at or just above Regular's (2 vs ~1.8 distinct), reflecting the
small diversity edge, but the two curves are structurally identical: fast initial
discovery, then saturation with ~97% wasted evaluations.

**Outcome.** The discovery dynamics of the two acquisitors are nearly identical — both
are fast to find their (small) set of distinct minima and then saturate. Novelty's
marginal diversity edge shows up as a slightly higher plateau.

---

## 4. Graph 2 — `benchmark_differences.png` (1×3 panel, Novelty − Regular)

### 4a. Left — "Distinct configs (novelty − regular)"

**What it is.** Per-seed signed difference in distinct configurations, novelty minus
regular. Blue bar = novelty found more, grey = tie, red = novelty found fewer.

**What it means / implies.** Values are [**+1**, 0, 0, 0, 0]. Novelty is never worse; it
gains exactly one extra distinct configuration on seed 41 and ties the other four.

**Outcome.** A clean (if small) positive signal for diversity: Novelty-LCB adds diversity
in 1/5 runs and never subtracts it. Consistent with 3a.

### 4b. Middle — "Duplicates (novelty − regular)"

**What it is.** Per-seed signed difference in duplicate counts, novelty minus regular.
Negative = novelty produced fewer duplicates.

**What it means / implies.** Values are [−1, 0, 0, 0, 0]. Novelty has one fewer duplicate
on seed 41 and ties elsewhere — the mirror image of the distinct-config difference (one
extra distinct configuration necessarily means one fewer duplicate).

**Outcome.** The duplicate reduction is exactly the reciprocal of the diversity gain:
−1 duplicate on seed 41, 0 elsewhere. Negligible in aggregate. Confirms that novelty does
not meaningfully cut redundancy on this surface.

### 4c. Right — "Best energy [eV] (novelty − regular)"

**What it is.** Per-seed signed difference in best energy, novelty minus regular.
Positive (red) = novelty's best minimum is **higher** (worse).

**What it means / implies.** Values are [+0.89, +0.34, +0.73, +0.04, +0.21] — **all
positive / red**. Novelty-LCB lands on a worse (higher-energy) minimum in every single
run. The smallest gap (+0.04, seed 301) is essentially a tie, but the others are
0.2–0.9 eV worse.

**Outcome.** This is the decisive negative result: on every seed, the diversity that
Novelty-LCB buys comes at a real cost to the lowest-energy minimum found. The energy
penalty (~+0.44 eV mean) is larger and more consistent than the diversity benefit.

---

## 5. Overall interpretation

**What the benchmark shows.**

1. **Diversity:** Novelty-LCB gives a small, never-negative diversity edge (mean distinct
   2.0 vs 1.8; +1 on one seed), exactly matching its design intent of resisting
   re-optimising a single basin.

2. **Optimality:** Regular LCB reliably finds the deeper minimum — it wins the best-energy
   comparison on all 5 seeds (mean Δ ≈ +0.44 eV). Novelty-LCB trades energy for novelty.

3. **Efficiency:** Both acquisitors are dominated by redundancy — **~97% of the 60
   evaluations in every run are duplicates**. Neither strategy is an efficient explorer
   of this surface; discovery saturates after the first couple of distinct minima.

**Outcome / verdict.** On this Ni8/Au(4,4,2)-EMT benchmark, the auto-window Novelty-LCB
acquisitor works (it runs, it finds distinct structures, it is never less diverse than
Regular LCB) but it does **not** beat Regular LCB at finding the global minimum, and its
diversity advantage is marginal while the energy cost is consistent and larger in
magnitude. The headline numbers: Novelty is +0.2 distinct configs but +0.44 eV worse in
best energy, with both strategies wasting ~97% of evaluations on duplicates.

**Implication for the Fe/MgO physics target.** The point of Novelty-LCB in the parent
project is *basin diversity* — populating the database with many distinct metastable
configurations for the downstream local-minimum / partition-function analysis
(`_run/9_novelFilter` dedup + `_run/8_nested_sampling`). For that goal, the diversity
(not the single-minimum optimality) is what matters, and Novelty-LCB does deliver a
(weak) diversity edge. But two things follow from this benchmark:

- If the search goal is the **single global minimum**, plain LCB is the better choice.
- Whatever the acquisitor, the ~97% duplicate rate means the raw database is dominated by
  re-sampled structures — the **dedup / representative-set step downstream is essential**
  before any basin statistics, and the novelty term itself should ideally be measured
  against a *deduplicated representative set* rather than the raw DB (as noted in the
  project README).

**Caveats.** This is a small, fast EMT benchmark (5 seeds, 30 iterations, 1 seed per run,
a single λ = 1.5 and window cap +0.1 eV/atom = +4 eV). The balance between novelty and
optimality depends strongly on λ and on the energy-window height; the results here are a
single point in that space (the dedicated kappa × novelty_weight sweep benchmark —
`main_benchmark_sweep.py` — is the follow-up that maps that trade-off). EMT also has a
very smooth, few-minima landscape compared with the rough Fe/MgO surface, so the small
diversity spread here is not necessarily representative of the harder physical system.

**Bottom line.** Novelty-LCB is a working diversity-oriented alternative to LCB that is
never less diverse but is consistently worse at finding the global minimum on this
surface; both acquisitors are ~97% duplicate-heavy, so database deduplication is the
indispensable post-processing step for any basin-level analysis.
