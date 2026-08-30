# DISCUSSION — Kappa × Novelty_weight Sweep of Novelty-LCB (EMT)

Project: `74_novel_benchSweep`
Benchmark: `main_benchmark_sweep.py` — grid sweep of **kappa × novelty_weight** on the
Novelty-LCB acquisitor only
System: Ni8 on Au(4,4,2) fcc100 surface, **EMT** calculator (same stack as the
project-73 benchmark, `main_benchmark.py`)
Results source: `benchmark_results/sweep_kappa_lambda/sweep_results.json`,
`sweep_heatmaps.png`, `sweep_curves.png`, `sweep_discovery.png`

---

## 1. What was swept

A 2D grid of the two free parameters of the Novelty-LCB acquisitor:

| Parameter | Role in `a(x) = σ(x) + λ·Novelty(x)` | Values swept |
|---|---|---|
| `kappa` (κ) | Controls the **LCB relaxation surface** `E − κ·σ` used to pre-relax candidates | [0.5, 1.0, 2.0, 4.0] |
| `novelty_weight` (λ) | Weights the **novelty bonus** in the discrete selection score | [0.0, 0.5, 1.0, 1.5, 2.0] |

- 4 × 5 = **20 combos**, Novelty-LCB only.
- **1 fixed seed per combo** (seed 41), 30 iterations / 60 evaluations per run.
- Energy window: auto global-min, `E/N ≤ E_min/N + 0.1` eV/atom (per_atom), as in project 73.
- `DUP_THRESHOLD = 1.5` defines "distinct configuration".

A key design point (from `novelty_lcb/acquisitor.py`): the two parameters act at
**different stages**.
- `kappa` enters `get_acquisition_calculator()` and shapes the *continuous* surrogate
  surface on which every candidate is relaxed before scoring.
- `novelty_weight` enters only `calculate_acquisition_function()` — the *discrete*
  selection `a(x) = σ + λ·Novelty` used to pick one candidate per round.

Because the novelty term is a minimum-distance with no well-defined force, it cannot
drive relaxation; only `kappa` changes the search trajectory.

Notes:

What do you mean by kappa shapes the continuous surrogate surface on which every candidate is relaxed before scoring?

What do you mean by novelty weight used to pick on candidate per round? What different it makes with regular LCB? 

---

## 2. Aggregate results (from `sweep_results.json`)

Per-combo metrics (all λ rows within a kappa are identical — see Section 5):

| kappa | λ (all values) | Distinct | Duplicates | Best energy (eV) | Energy range (eV) |
|---|---|---|---|---|---|
| 0.5 | 0.0–2.0 | 1 | 59 | 20.775 | 0.0 |
| 1.0 | 0.0–2.0 | 1 | 59 | **20.481** | 0.0 |
| 2.0 | 0.0–2.0 | **2** | 58 | 20.640 | 0.685 |
| 4.0 | 0.0–2.0 | 1 | 59 | 20.751 | 0.0 |

Averaged over the 20 combos:

| Metric | Value |
|---|---|
| Distinct configs | 1.25 (mean); 15/20 combos find 1, only kappa=2.0 finds 2 |
| Duplicate rate | 97.9% of 60 evaluations |
| Best energy | lowest 20.481 (κ=1.0), highest 20.775 (κ=0.5); spread ~0.29 eV |

---

## 3. Graph 1 — `sweep_heatmaps.png` (1×3 heatmaps, metric vs kappa × λ)

### 3a. Left — "Distinct configs" heatmap

**What it is.** A 2D heatmap with `novelty_weight` (λ) on the x-axis and `kappa` on the
y-axis; each cell shows how many distinct configurations that (κ, λ) combo found. The
same data is printed inside each cell.

**What it means.** Diversity across the parameter grid. A hot (high-value) cell means
that parameter choice discovers several distinct structural basins; a cold (1-valued)
cell means the search collapsed onto a single basin.

**What it implies.** The entire column structure is **flat** — for a fixed kappa, every
λ gives the identical value (1 for κ=0.5/1.0/4.0, 2 for κ=2.0). There is **no vertical
gradient at all**: λ has zero influence on diversity. The only signal is a single hot row
at κ=2.0 (value 2), the one setting that discovers two distinct configurations.

**Outcome.** Diversity is governed entirely by `kappa`, not by `novelty_weight`. Only
κ=2.0 reaches 2 distinct basins; every other kappa finds just 1, regardless of λ.

### 3b. Middle — "Best energy [eV]" heatmap

**What it is.** The same kappa × λ grid, but the cell value is the lowest energy (eV)
that combo found (lower is better).

**What it means.** Optimality / exploitation across the grid.

**What it implies.** Again each row is flat across λ. The column structure shows a clear
kappa dependence: κ=1.0 → 20.481 (best), κ=2.0 → 20.640, κ=4.0 → 20.751, κ=0.5 → 20.775
(worst). The optimality ordering is κ=1.0 < κ=2.0 < κ=4.0 < κ=0.5.

**Outcome.** The best energy is decided by kappa alone: κ=1.0 finds the deepest minimum
(20.481 eV), and λ does not affect it. The spread across kappa (~0.29 eV) is small but
consistent.

### 3c. Right — "Duplicates" heatmap

**What it is.** The kappa × λ grid showing duplicate evaluation counts (60 − distinct).

**What it means.** Redundancy / efficiency. High values = most of the budget wasted
re-visiting the same structures.

**What it implies.** Flat rows again — λ never changes the duplicate count (59 everywhere
except κ=2.0, which has 58). Every combo sits at ~97–98% duplicates.

**Outcome.** Redundancy is also purely a function of kappa (κ=2.0 is marginally less
redundant, 58 vs 59), and λ has no effect. Both findings mirror the distinct-config
heatmap (one extra distinct config ⇔ one fewer duplicate).

---

## 4. Graph 2 — `sweep_curves.png` (1×3 curves, metric vs λ, one line per kappa)

### 4a. Left — "Distinct configs vs lambda (per kappa)"

**What it is.** Distinct-configuration count plotted against λ, with a separate line for
each of the four kappa values.

**What it means.** Shows how diversity changes as λ is dialled 0 → 2, holding kappa fixed.

**What it implies.** Every one of the four lines is **perfectly horizontal** — distinct
configs do not change as λ goes from 0.0 to 2.0. κ=2.0 sits at 2, the other three at 1,
for the whole λ range.

**Outcome.** This is the cleanest visual statement of the null result: λ has no effect on
diversity; only the vertical separation between kappa-lines (i.e. kappa itself) matters.

### 4b. Middle — "Best energy vs lambda (per kappa)"

**What it is.** Best energy (eV) vs λ, one line per kappa.

**What it means.** Shows how the found minimum's depth depends on λ.

**What it implies.** All four lines are flat in λ; they sit at distinct heights ordered
κ=1.0 (20.481) < κ=2.0 (20.640) < κ=4.0 (20.751) < κ=0.5 (20.775). The λ axis carries no
information.

**Outcome.** The best energy is a function of kappa only, with κ=1.0 optimal; λ is inert.

### 4c. Right — "Duplicates vs lambda (per kappa)"

**What it is.** Duplicate count vs λ, one line per kappa.

**What it means.** Redundancy as a function of λ.

**What it implies.** Flat horizontal lines again — 59 duplicates for κ=0.5/1.0/4.0, 58 for
κ=2.0, across all λ.

**Outcome.** Redundancy is independent of λ; only κ=2.0 is marginally less wasteful.

---

## 5. The central finding — why λ (novelty_weight) has no effect

**What the sweep shows.** Across all three metrics and all 20 combos, changing
`novelty_weight` from 0.0 to 2.0 changes **nothing**. The `all_energies` arrays are
byte-identical across the five λ values for every kappa — i.e. the entire search
trajectory is literally the same. Only `kappa` moves any metric.

**What it means (grounded in the code).** The two parameters act at different stages of
the pipeline:

1. **Candidates are pre-relaxed on the LCB surface** `E − κ·σ`
   (`get_acquisition_calculator()` → `LowerConfidenceBoundCalculator`, using only
   `kappa`). The novelty term `λ·Novelty` has **no force** (it is a discrete min-distance,
   not differentiable), so it cannot change where a candidate relaxes to.
2. **λ enters only the discrete selection** `a(x) = σ + λ·Novelty` that picks which
   candidate to evaluate. With a **single fixed seed (41)** the generated candidate pool
   is identical for every combo, and for this smooth EMT surface the relaxed candidates
   all fall into the same 1–2 low basins. Among those in-window candidates the ranking is
   dominated by `σ` (and the energy window), so the argmax — and hence the whole
   trajectory — does not change as λ varies. Result: λ is effectively inert here.

**What it implies.**

- In this benchmark, **κ is the only effective knob**. Its role is via the relaxation
  surface, not the acquisition score: κ=2.0 changes which basin candidates fall into
  (→ 2 distinct), and κ=1.0 lands on the deepest minimum (20.481 eV).
- The `novelty_weight` parameter, as wired, does **not** measurably steer the search on
  this system. This does **not** prove λ is useless in general — it reflects that, with
  a single seed and a smooth few-minima EMT surface, the novelty term never changes the
  winning candidate. It is a **null result under these conditions**, not a proof that λ
  has no role on the rough Fe/MgO landscape.

---

## 6. Graph 3 — `sweep_discovery.png` (all 20 discovery curves)

**What it is.** A single plot of cumulative distinct configurations vs cumulative
evaluations, with one curve per combo (20 curves, labelled by k and λ).

**What it means.** Each curve shows how fast that combo accumulates genuinely new
structures as the evaluation budget is spent — steep = efficient exploration, flat =
saturation/duplication.

**What it implies.** Because the trajectory is identical across λ for a given kappa, the
20 curves collapse to **only 4 distinct curves** — one per kappa value (κ=2.0 reaches a
plateau of 2, the other three a plateau of 1). Every curve rises over the first ~1–2
evaluations and then goes essentially flat, spending the remaining ~58 evaluations
re-visiting the same basin.

**Outcome.** The discovery dynamics confirm the null result visually: the λ axis
contributes no spread; only kappa distinguishes the curves, and all of them saturate
almost immediately (~97–98% of evaluations are duplicates).

---

## 7. Overall interpretation

**What the sweep shows.**

1. **λ (novelty_weight) is inert in this benchmark.** No metric varies with λ over the
   full 0.0–2.0 range; all energy trajectories are identical per kappa. This follows from
   the code structure (λ only affects the discrete selection; with one fixed seed and a
   smooth EMT surface it never changes the winning candidate) combined with the
   single-seed design.
2. **κ (kappa) is the only effective parameter.** It shapes the LCB relaxation surface
   and therefore the trajectory: κ=1.0 gives the deepest minimum (20.481 eV), κ=2.0 is
   the only setting that finds a second distinct basin (2 vs 1), κ=0.5 and 4.0 are
   slightly worse on energy.
3. **Efficiency is poor across the board.** Every combo wastes ~97–98% of its 60
   evaluations on duplicates; discovery saturates after 1–2 distinct minima.

**Outcome / verdict.** As a study of the *interaction* of κ and λ, the sweep is
inconclusive on λ: the parameter the study was designed to interrogate
(`novelty_weight`) produced a clean null result, while the one that was mostly a control
(`kappa`) is the sole driver of differences. The practical takeaway is that for this
system the search is controlled by the relaxation parameter κ, and that the 
`novelty_weight` bonus has no measurable steering effect under a single-seed, smooth-surface
setup.

**Implication for the Fe/MgO target.** The parent project's reason for using
Novelty-LCB is *basin diversity* on a rough surface. This sweep does not support (or
refute) that motivation — its null λ result is specific to this smooth, few-minima EMT
test and its single-seed design. To genuinely map λ's role, the sweep needs (a) multiple
seeds per combo (so λ can be seen to alter selection at least sometimes) and/or (b) a
rough landscape (the real Fe/MgO surface) where distinct basins actually differ in
novelty. As-is, the sweep's main actionable findings are: **κ ≈ 1–2 eV is the sensible
operating range** (best energy at κ=1.0, best diversity at κ=2.0), and the ~97% duplicate
rate again makes downstream deduplication (`_run/9_novelFilter`) essential before any
basin statistics.

**Caveats / limitations.**

- **Single seed per combo (41).** With identical RNG, λ cannot exhibit any stochastic
  influence, and a single seed gives no statistical power — the flatness in λ may be
  partly an artefact of this design, not a fundamental property.
- **Smooth EMT landscape.** Few distinct basins, so novelty rarely differentiates
  candidates; not representative of the rough Fe/MgO surface.
- **λ has no force.** Because novelty cannot drive relaxation, λ only re-ranks the
  already-LCB-relaxed candidates; on a surface where relaxation is the dominant step, λ
  is structurally disadvantaged.

**Bottom line.** The sweep shows a clean null result for `novelty_weight` (λ is inert
here) and a modest but real `kappa` effect (κ=1.0 → best energy 20.481 eV; κ=2.0 → only
setting with 2 distinct basins). All 20 combos run at ~97–98% duplicate rate, so database
deduplication remains the indispensable post-processing step. The λ question is not
settled in general — only for this single-seed, smooth-surface configuration — and a
multi-seed sweep on a rough landscape (the real Fe/MgO system) would be the proper
follow-up to map λ's actual role.
